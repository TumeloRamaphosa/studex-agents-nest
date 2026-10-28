#!/usr/bin/env python3
"""Test the pre-flight's TARGET-DATE clock logic.

🔴 THE BUG THIS WAS WRITTEN FOR (found 2026-10-27, 19:58 SAST)
-------------------------------------------------------------
`ops/preflight-daily-post.py` decided whether a MISSING path-B pending file
was expected or a failure by comparing the CURRENT wall clock to 08:55 SAST
- and never looked at WHICH DATE was being checked.

So checking a FUTURE date produced a FALSE BLOCKING FAILURE:

    $ python3 ops/preflight-daily-post.py 2026-10-28     # at 19:58 SAST
    FAIL  no pending file at 2026-10-28.json - it should have been written
          at 08:55 SAST. The content agent did not run, so the fallback path
          (path B) has nothing to publish.

The content agent had not "failed to run" - it was scheduled to run the
NEXT MORNING. The gate reported a defect for something not yet due.

🔑 **A gate that reports a defect for something that has not been due yet
teaches the next reader to ignore the gate** - which is precisely how a
REAL failure gets missed. A false alarm is not a harmless false alarm.

The same bug was in the RESULT line: it said "the 09:00 SAST publish has
already run" about a date whose publish had not happened yet.

THE FIX
-------
`pending_absence_verdict(target_date, now_sast)` decides:
  * target in the FUTURE              -> expected (not due yet)
  * target TODAY, before 08:55 SAST   -> expected (not due yet)
  * target TODAY after 08:55          -> failed (the agent should have run)
  * target in the PAST                -> failed (the agent should have run)

NEGATIVE CONTROL
----------------
This test has a built-in NEGATIVE CONTROL: it applies the original buggy
comparison to copies of the real file and asserts the checker catches it. A
checker that cannot fail is worthless.
"""

import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "ops" / "preflight-daily-post.py"

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


def _verdict_fn(text):
    """Extract pending_absence_verdict() from the source so the test drives
    the REAL function rather than a copy of it."""
    m = re.search(r"def pending_absence_verdict\(.*?\n(?=\ndef |\nclass )", text,
                  re.S)
    if not m:
        return None
    src = m.group(0)
    ns = {}
    try:
        exec(compile(src, "<verdict>", "exec"), ns)
    except Exception:
        return None
    return ns.get("pending_absence_verdict")


def buggy_verdict(target_date, now_sast):
    """The ORIGINAL comparison - ignores the target date entirely.

    This is the bug, preserved so the negative control can prove the
    checker would have caught it.
    """
    if now_sast.hour * 60 + now_sast.minute < 8 * 60 + 55:
        return "expected"
    return "failed"


def main():
    text = PREFLIGHT.read_text(encoding="utf8")

    verdict = _verdict_fn(text)
    check("the pre-flight exposes pending_absence_verdict()", verdict is not None,
          "could not extract the function")
    if verdict is None:
        print("\nVERDICT: CHECKER BROKEN - refusing to report CLEAN.")
        print("%d passed, %d failed" % (len(PASSED), len(FAILED)))
        return 2

    import datetime

    def dt(y, m, d, hh=0, mm=0):
        return datetime.datetime(y, m, d, hh, mm)

    # --- 1. a FUTURE date is EXPECTED, not a failure ---
    # 19:58 on 27 Oct, checking 28 Oct. This is the exact false failure.
    check("a FUTURE date is 'expected' (not a failure), even late in the day",
          verdict(dt(2026, 10, 28), dt(2026, 10, 27, 19, 58)) == "expected",
          verdict(dt(2026, 10, 28), dt(2026, 10, 27, 19, 58)))
    check("a FUTURE date is 'expected' at 23:59 too",
          verdict(dt(2026, 10, 28), dt(2026, 10, 27, 23, 59)) == "expected")
    check("a FUTURE date far ahead is 'expected'",
          verdict(dt(2026, 12, 25), dt(2026, 10, 27, 19, 58)) == "expected")

    # --- 2. TODAY before 08:55 is expected ---
    check("TODAY before 08:55 is 'expected'",
          verdict(dt(2026, 10, 27), dt(2026, 10, 27, 8, 0)) == "expected")
    check("TODAY at 08:54 is still 'expected'",
          verdict(dt(2026, 10, 27), dt(2026, 10, 27, 8, 54)) == "expected")

    # --- 3. TODAY after 08:55 is a REAL failure ---
    check("TODAY at 08:55 is a failure (the agent was due)",
          verdict(dt(2026, 10, 27), dt(2026, 10, 27, 8, 55)) == "failed")
    check("TODAY at 19:58 is a failure",
          verdict(dt(2026, 10, 27), dt(2026, 10, 27, 19, 58)) == "failed")

    # --- 4. a PAST date is a failure (the agent should have run) ---
    check("a PAST date is a failure",
          verdict(dt(2026, 10, 26), dt(2026, 10, 27, 19, 58)) == "failed")
    check("a PAST date is a failure even at 08:00",
          verdict(dt(2026, 10, 26), dt(2026, 10, 27, 8, 0)) == "failed")

    # --- 5. the call site uses the target date ---
    # ⚠️ A non-greedy `.*?` would stop at the first ")" and capture
    # "day.date(" instead of "day.date()" - so match the whole line and
    # collapse whitespace first.
    flat = re.sub(r"\s+", " ", text)
    call = re.search(r"verdict = pending_absence_verdict\(([^)]*\)[^)]*)\)",
                     flat)
    check("the call site passes the TARGET date, not today's date",
          call is not None and "day.date()" in call.group(1),
          call.group(1) if call else "call site not found")

    # --- 6. the RESULT wording is target-date aware ---
    # ⚠️ Assert on substrings that do NOT cross a string-literal boundary:
    # the source is `"...has not run " "yet."`, so collapsing whitespace
    # still leaves a `" "` between the two halves.
    check("the RESULT line distinguishes a FUTURE date",
          "in the FUTURE" in flat and "publish has not run" in flat)
    check("the RESULT line distinguishes a PAST date",
          "in the PAST" in flat)
    fut = re.search(r"in the FUTURE.{0,400}", flat)
    check("the FUTURE branch does NOT claim the publish already ran",
          fut is not None and "already run" not in fut.group(0),
          fut.group(0)[:200] if fut else "FUTURE branch not found")

    # --- 7. report() cannot see main()'s locals ---
    # 🔑 A bug I introduced while fixing this one: the RESULT block lives in
    # report(), which takes NO arguments, so it cannot see main()'s local
    # `day` or `date_str`. Using them there raised
    #   NameError: name 'day' is not defined
    # and killed the whole report AFTER the checks had run - so the gate
    # printed nothing at all and exited non-zero. The existing media-check
    # test caught it; this pins it so it cannot come back.
    rep = re.search(r"\ndef report\(\):(.*?)(?=\nif __name__|\ndef |\Z)", text,
                    re.S)
    rep_body = rep.group(1) if rep else ""
    # 🔑 The precise rule is not "report() must not mention these names" -
    # it is "report() must not READ a name it never assigns". A local
    # assignment makes the name local to report() and is perfectly safe.
    # (My own first fix assigned date_str locally in report(); that is
    # correct code, and a naive "must not appear" rule would have failed it.)
    def reads_unassigned(body, name):
        used = re.search(r"(?<![A-Za-z_.])%s\b" % name, body) is not None
        assigned = re.search(r"(?<![A-Za-z_.])%s\s*=" % name, body) is not None
        return used and not assigned

    check("report() does not READ main()'s local `day` unbound",
          rep_body is not None and not reads_unassigned(rep_body, "day"),
          "report() reads `day` without assigning it - NameError")
    check("report() does not READ main()'s local `date_str` unbound",
          rep_body is not None and not reads_unassigned(rep_body, "date_str"),
          "report() reads `date_str` without assigning it - NameError")
    check("the RESULT block resolves the target date from TARGET_DATE",
          "TARGET_DATE" in flat and "TARGET_DATE = day.date()" in flat)

    # --- 8. NEGATIVE CONTROL: the original bug must be caught ---
    buggy = buggy_verdict(dt(2026, 10, 28), dt(2026, 10, 27, 19, 58))
    check("NEGATIVE: the ORIGINAL buggy comparison DOES produce the false "
          "failure this test exists for",
          buggy == "failed", "the bug did not reproduce - the test is invalid")
    check("NEGATIVE: the FIXED comparison differs from the buggy one exactly "
          "on the future date",
          verdict(dt(2026, 10, 28), dt(2026, 10, 27, 19, 58)) != buggy)

    # --- 9. NEGATIVE CONTROL: mutate a copy of the real file and confirm the
    #        checker catches the regression ---
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="preflight-date-"))
    try:
        (tmp / "ops").mkdir()
        (tmp / "ops" / "preflight-daily-post.py").write_text(text)
        p = tmp / "ops" / "preflight-daily-post.py"
        mutated = p.read_text().replace(
            'verdict = pending_absence_verdict(day.date(), now_sast)',
            'verdict = "failed" if now_sast.hour * 60 + now_sast.minute '
            '>= 8 * 60 + 55 else "expected"')
        p.write_text(mutated)
        m_verdict = _verdict_fn(p.read_text())
        # The mutated call site no longer consults the target date, so the
        # checker must reject it.
        m_flat = re.sub(r"\s+", " ", p.read_text())
        m_call = re.search(r"verdict = pending_absence_verdict\(([^)]*\)[^)]*)\)",
                           m_flat)
        caught = (m_call is None
                  or "day.date()" not in m_call.group(1))
        check("NEGATIVE: the checker catches a call site that ignores the "
              "target date", caught)

        # mutation 2: put main()'s local `day` back into report() - the
        # NameError I introduced and fixed. The checker must catch it.
        p2 = tmp / "ops" / "preflight-daily-post.py"
        p2.write_text(text.replace(
            "target_date = TARGET_DATE if TARGET_DATE is not None "
            "else now_sast.date()",
            "target_date = day.date()"))
        p2_flat = re.sub(r"\s+", " ", p2.read_text())
        m_rep = re.search(r"\ndef report\(\):(.*?)(?=\nif __name__|\ndef |\Z)",
                           p2.read_text(), re.S)
        caught2 = (m_rep is not None
                   and re.search(r"(?<![A-Za-z_.])day\b", m_rep.group(1)))
        check("NEGATIVE: the checker catches report() reaching for main()'s "
              "local `day`", caught2)
        check("NEGATIVE: the mutated file is the one the mutation intended",
              "target_date = day.date()" in p2_flat)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        print("VERDICT: BROKEN - the pre-flight's date logic is wrong.")
        return 1
    print("VERDICT: CLEAN - the pre-flight measures its clock against the "
          "TARGET date, so a future date is expected rather than a failure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
