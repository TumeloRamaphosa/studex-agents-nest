#!/usr/bin/env python3
"""
Locks the two facts the 08:00 SAST pre-flight gate depends on.

Why this exists
---------------
Two pieces of documentation about this gate were wrong, and both wrongnesses
were actively misleading:

1. scripts/preflight-cron.sh carried the comment
       "If today's queue file does not exist yet, fall back to tomorrow's."
   ...but the script has no such branch and never had. TARGET is always
   today's SAST date. A reader who believed the comment would expect the
   gate to check tomorrow's post, and would be wrong about which post the
   gate governs.

2. ops/preflight-daily-post.py's NO QUEUE FILE warning said
       "the publish will legitimately skip ('No post queued for today')"
   ...which is false. The 09:00 SAST publish job STAGES the queue file
   itself. On 2026-10-26 the 08:00 run warned, and the 09:00 job then wrote
   memory/post-queue/2026-10-26-monday-knowledge.md and published. The
   publish does not skip; the 08:00 gate is simply a no-op on an un-staged
   day.

A gate that misdescribes what it protects is worse than a gate that is
known to be inert, because it teaches the next reader that the check
matters when it cannot.

What this test asserts
----------------------
A. preflight-cron.sh contains no "fall back to tomorrow" claim, and its
   TARGET is always today's SAST date.
B. The NO QUEUE FILE branch WARNS (does not FAIL) - an un-staged day must
   not page Discord, because that would train us to ignore the page.
C. The NO QUEUE FILE warning does not claim the publish will skip, and does
   state that the 09:00 job stages the file.

Negative control
----------------
This test has a built-in NEGATIVE CONTROL: it applies each forbidden
mutation to a copy of the real file in a temp dir and asserts the checker
catches it. A checker that cannot fail is worthless.

Exit codes: 0 = clean, 1 = a fact drifted, 2 = the checker itself is broken.
"""
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CRON = ROOT / "scripts" / "preflight-cron.sh"
PREFLIGHT = ROOT / "ops" / "preflight-daily-post.py"

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


# ---------------------------------------------------------------- facts

def cron_has_no_tomorrow_fallback(text):
    """The comment must not claim a fallback that does not exist."""
    bad = re.search(r"fall\s*back\s*to\s*tomorrow", text, re.I)
    return bad is None


def cron_targets_today(text):
    """TARGET must be today's SAST date - there is no tomorrow branch."""
    if "TARGET=" not in text:
        return False
    # a tomorrow branch would assign TARGET from a date other than SAST_DATE
    for line in text.splitlines():
        if line.strip().startswith("TARGET="):
            if "SAST_DATE" not in line:
                return False
    return True


def _branch_block(text):
    """Return the whole 'if not qf:' branch, including the warn()/fail() call.

    Anchoring on the 'NO QUEUE FILE' string alone would capture only the
    string literal - the warn( or fail( call sits BEFORE it, so a warn branch
    would look like it had no call at all. Anchor on the statement instead.
    """
    m = re.search(r"if not qf:.*?(?=\n\s*return report\(\))", text, re.S)
    return m.group(0) if m else None


def no_queue_branch_is_a_warn(text):
    """The NO QUEUE FILE branch must warn, not fail."""
    block = _branch_block(text)
    if block is None:
        return None  # cannot locate the branch at all
    if re.search(r"^\s*fail\s*\(", block, re.M):
        return False
    return bool(re.search(r"^\s*warn\s*\(", block, re.M))


def warning_does_not_claim_skip(text):
    """The warning must not say the publish will skip."""
    block = _branch_block(text)
    if block is None:
        return None
    if re.search(r"publish will\s+legitimately skip", block, re.I):
        return False
    if re.search(r"\bskip\b", block, re.I):
        # "skip" is only acceptable in a clearly negated context, e.g.
        # "does NOT skip". Anything else is a claim we cannot prove.
        if not re.search(r"does\s+NOT\s+skip", block, re.I):
            return False
    return True


def warning_states_the_09_job_stages(text):
    """The warning must say who actually stages the file."""
    block = _branch_block(text)
    if block is None:
        return None
    return bool(re.search(r"09:00", block) and re.search(r"stag", block, re.I))


# ------------------------------------------------- negative control

def negative_control():
    """Mutate copies of the real files and prove the checker catches it."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="preflight-gate-"))
    try:
        (tmp / "scripts").mkdir()
        (tmp / "ops").mkdir()
        shutil.copy(CRON, tmp / "scripts" / "preflight-cron.sh")
        shutil.copy(PREFLIGHT, tmp / "ops" / "preflight-daily-post.py")
        cron = (tmp / "scripts" / "preflight-cron.sh")
        pf = (tmp / "ops" / "preflight-daily-post.py")

        results = {}

        # mutation 1: re-introduce the bogus "fall back to tomorrow" comment
        c = cron.read_text()
        c = c.replace(
            "# The target is ALWAYS today's SAST date.",
            "# If today's queue file does not exist yet, fall back to tomorrow's.",
        )
        cron.write_text(c)
        results["cron tomorrow-comment"] = not cron_has_no_tomorrow_fallback(c)

        # mutation 2: re-introduce the bogus "skip" claim
        p = pf.read_text()
        p = p.replace(
            "the 09:00 SAST publish job stages the queue file itself, so this ",
            "the publish will legitimately skip, so this ")
        pf.write_text(p)
        results["preflight skip-claim"] = (
            warning_does_not_claim_skip(p) is False)

        # mutation 3: turn the WARN into a FAIL (would page Discord daily)
        p2 = pf.read_text()
        p2 = p2.replace(
            'warn(f"NO QUEUE FILE for {date_str} ({pillar}) - nothing to pre-flight: "',
            'fail(f"NO QUEUE FILE for {date_str} ({pillar}) - nothing to pre-flight: "',
        )
        results["preflight warn-as-fail"] = (
            no_queue_branch_is_a_warn(p2) is False)

        missing = [k for k, v in results.items() if not v]
        if missing:
            return False, "checker failed to catch: %s" % ", ".join(missing)
        return True, "checker caught all %d mutations" % len(results)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ok, detail = negative_control()
    check("NEGATIVE CONTROL: the checker catches each forbidden mutation", ok, detail)
    if not ok:
        print("\nVERDICT: CHECKER BROKEN - refusing to report CLEAN.")
        print("%d passed, %d failed" % (len(PASSED), len(FAILED)))
        return 2

    cron_text = CRON.read_text(encoding="utf8")
    pf_text = PREFLIGHT.read_text(encoding="utf8")

    check("A1. preflight-cron.sh makes no 'fall back to tomorrow' claim",
          cron_has_no_tomorrow_fallback(cron_text))
    check("A2. preflight-cron.sh always targets today's SAST date",
          cron_targets_today(cron_text))
    check("A3. preflight-cron.sh documents that the 09:00 job stages the file",
          "09:00" in cron_text and "stag" in cron_text.lower())

    b = no_queue_branch_is_a_warn(pf_text)
    check("B. the NO QUEUE FILE branch WARNS (never FAILs) - no daily false page",
          b is True, "branch not found" if b is None else "branch FAILS")
    c = warning_does_not_claim_skip(pf_text)
    check("C1. the NO QUEUE FILE warning does not claim the publish will skip",
          c is True, "branch not found" if c is None else "skip claim present")
    d = warning_states_the_09_job_stages(pf_text)
    check("C2. the NO QUEUE FILE warning states the 09:00 job stages the file",
          d is True, "branch not found" if d is None else "no 09:00/stage mention")

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        return 1
    print("VERDICT: CLEAN - the gate's description matches what the gate does.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
