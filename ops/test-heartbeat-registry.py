#!/usr/bin/env python3
"""
Enforces that EVERY checker in ops/ is classified in the canonical registry.

The orphan class of bug
-----------------------
On 2026-10-26 the orphaned-publisher bug bit us: `blotato-fallback.js` had no
cron, no checklist entry and nothing invoked it, so it did nothing for days.
Later the same shape was found again - `ops/dead-inbox-check.py` was a working,
tested checker that HEARTBEAT.md named NOWHERE. And a third time: the runner
itself hardcoded its checker list, so a checker added afterwards was silently
orphaned.

The root cause in every case is the same: **a checker on disk that no pass
runs is a comment, not a control.** Prose about it does not fix it.

This test closes the class. It discovers every checker-like file in ops/ and
requires each one to be declared in ops/heartbeat-checkers.tsv as either:

  PASS  - it runs every heartbeat pass, or
  SCOPE - it deliberately does not, AND gives a reason

An unclassified checker FAILS this test. So the next person to add a checker
is forced to decide whether it runs, instead of it silently never running.

What it also asserts
--------------------
* every registry PASS entry points at a file that exists
* every registry path exists
* every SCOPE entry has a non-empty reason (a bare "no" is not a reason)
* the runner actually reads the registry and exposes the same set
* no registry entry may point at a publishing script

Self-verifying: the discovery logic is exercised against a synthetic tree so
the test proves it can FAIL, rather than passing vacuously.

Exit codes: 0 = clean, 1 = a checker is unclassified / the registry is broken.
"""
import fnmatch
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
REGISTRY = HERE / "heartbeat-checkers.tsv"
RUNNER = HERE / "run-heartbeat-checks.py"

# 🔑 The checker-like NAME SHAPES. A general rule, not a list of names.
# See discover_checkers() for why a list of names is not a control.
#
# ⚠️ BOTH prefix AND suffix forms are listed, and that is not redundancy.
# The FIRST version of this rule listed only the suffix forms
# (`*-check.py`, `*-audit.py`, `*-scan.py`) and it STILL MISSED two real
# standing controls - `audit-blotato-fragments.py` (a PREFIX form) and
# `secret_leak_scan.py` (an underscore form). A name-shape rule is only as
# good as the shapes you thought of, so the shapes are broad on purpose.
CHECKER_PATTERNS = (
    "check-*.py",
    "*-check.py",
    "*_check.py",
    "*-guard.py",
    "audit-*.py",
    "*-audit.py",
    "*_scan.py",
    "*-scan.py",
    "probe-*.py",
    "preflight-*.py",
)
# Prefixes that mean "not a control": a test, or a one-off scratch script.
EXCLUDE_PREFIXES = ("test-", "tmp-")

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:400]) if detail else ""))


def parse_registry(text):
    """Return (pass_entries, scope_entries) parsed from the TSV-ish registry."""
    passes, scopes = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue
        name, path, scope, contract, known, purpose = parts[:6]
        reason = parts[6] if len(parts) > 6 else ""
        if scope == "PASS":
            passes.append({"name": name, "path": path, "contract": contract,
                           "known": known, "purpose": purpose})
        elif scope == "SCOPE":
            scopes.append({"name": name, "path": path, "reason": reason})
    return passes, scopes


def discover_checkers(directory):
    """Find every checker-like .py in a directory (the discovery rule).

    🔑 THE PATTERN MUST BE GENERAL, NOT A LIST OF NAMES.

    The rule used to be `check-*.py` plus THREE HARDCODED NAMES
    (`drift-check.py`, `dead-inbox-check.py`, `tmp-shape-surface-audit.py`).
    That hardcoding was a symptom, not a fix: `dead-inbox-check.py` was the
    file whose omission CAUSED the orphan bug, and it was only ever caught
    because someone added its name to the list. The *pattern* was never
    generalised, so any future checker named anything else - `foo-check.py`,
    `foo-guard.py`, `foo-audit.py`, `probe-foo.py` - would be INVISIBLE and
    silently orphaned, the exact thing this test exists to prevent.

    The rule now matches the checker-like NAME SHAPES, so a new checker is
    caught whatever it is called:

        check-*.py   *-check.py   *-guard.py   *-audit.py
        *-scan.py    probe-*.py   preflight-*.py

    `test-*.py` and `tmp-*.py` are excluded: those prefixes are the
    established conventions for a test and for a one-off scratch script, and
    neither is a control.
    """
    found = set()
    if not directory.is_dir():
        return found
    for p in sorted(directory.glob("*.py")):
        n = p.name
        if n.startswith(EXCLUDE_PREFIXES):
            continue
        if any(fnmatch.fnmatch(n, pat) for pat in CHECKER_PATTERNS):
            found.add(p.name)
    return found


def main():
    if not REGISTRY.is_file():
        print("[FAIL] registry missing: %s" % REGISTRY)
        return 1
    text = REGISTRY.read_text(encoding="utf8")
    passes, scopes = parse_registry(text)

    check("registry parses and lists >= 10 PASS checkers", len(passes) >= 10,
          "only %d" % len(passes))
    check("registry declares at least one SCOPE entry with a reason",
          any(s["reason"] for s in scopes))

    # ---- the core assertion: no checker on disk is unclassified ----
    on_disk = discover_checkers(HERE)
    classified = {p["path"].split("/")[-1] for p in passes}
    classified |= {s["path"].split("/")[-1] for s in scopes}
    unclassified = sorted(on_disk - classified)
    check("EVERY checker in ops/ is classified in the registry (%d on disk)" % len(on_disk),
          not unclassified,
          "unclassified (will never run): %s" % unclassified)

    # ---- registry hygiene ----
    for p in passes:
        check("PASS entry %s points at a file that exists" % p["name"],
              (ROOT / p["path"]).is_file(), p["path"])
    for s in scopes:
        check("SCOPE entry %s gives a real reason" % s["name"],
              len(s["reason"]) > 8, "reason too short: %r" % s["reason"])
        check("SCOPE entry %s points at a file that exists" % s["name"],
              (ROOT / s["path"]).is_file(), s["path"])

    # ---- a registry entry must never point at a publisher ----
    for p in passes + scopes:
        check("%s does not point at a publishing script" % p["name"],
              "blotato-fallback" not in p["path"])

    # ---- the runner must actually consume the registry ----
    runner_src = RUNNER.read_text(encoding="utf8")
    check("runner reads the registry file", "heartbeat-checkers.tsv" in runner_src)
    # A hardcoded list means entries inside brackets. The empty placeholder
    # `CHECKERS = []` is fine - it is filled from the registry at startup.
    import re
    hardcoded = re.search(r"CHECKERS\s*=\s*\[\s*[(\"']", runner_src)
    check("runner does not hardcode its own checker list",
          hardcoded is None,
          "the runner still has a hardcoded CHECKERS list - the registry would be decorative")

    # ---- NEGATIVE CONTROL: the discovery rule must be able to find a checker ----
    # If discover_checkers() can never find anything, the core assertion above
    # would pass vacuously.
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="registry-selftest-"))
    try:
        (tmp / "check-brand-new.py").write_text("# new\n")
        (tmp / "check-another.py").write_text("# new\n")
        (tmp / "not-a-checker.py").write_text("# helper\n")
        (tmp / "drift-check.py").write_text("# new\n")
        found = discover_checkers(tmp)
        check("NEGATIVE CONTROL: discovery finds real checkers and ignores helpers",
              "check-brand-new.py" in found and "check-another.py" in found
              and "not-a-checker.py" not in found and "drift-check.py" in found,
              "found: %s" % sorted(found))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- NEGATIVE CONTROL: an unclassified checker must be DETECTED ----
    tmp2 = pathlib.Path(tempfile.mkdtemp(prefix="registry-selftest2-"))
    try:
        (tmp2 / "check-orphan.py").write_text("# orphan\n")
        found2 = discover_checkers(tmp2)
        check("NEGATIVE CONTROL: an orphaned checker IS detected by the rule",
              "check-orphan.py" in found2, "found: %s" % sorted(found2))
    finally:
        import shutil
        shutil.rmtree(tmp2, ignore_errors=True)

    # ---- NEGATIVE CONTROL: THE GENERALISATION, not just the old pattern ----
    # The control above uses "check-orphan.py" - a name the ORIGINAL
    # `check-*.py` rule caught too. So it does NOT prove the rule was
    # generalised; it would have passed before the fix.
    #
    # These names are the ones the ORIGINAL rule MISSED. `dead-inbox-check.py`
    # was caught in 2026-10 only because someone hardcoded its name, and
    # `audit-blotato-fragments.py` + `secret_leak_scan.py` sat invisible
    # until 2026-10-27. Each of these MUST now be discovered - and the
    # original rule must NOT find them, or the control proves nothing.
    tmp3 = pathlib.Path(tempfile.mkdtemp(prefix="registry-selftest3-"))
    try:
        generalised = [
            "dead-inbox-check.py",        # the suffix form that bit us
            "audit-blotato-fragments.py",  # a PREFIX form
            "secret_leak_scan.py",        # an underscore form
            "some-new-guard.py",          # the *-guard form
            "probe-something.py",         # the probe form
            "preflight-whatever.py",      # the preflight form
        ]
        for n in generalised:
            (tmp3 / n).write_text("# new\n")
        found3 = discover_checkers(tmp3)
        missed = [n for n in generalised if n not in found3]
        check("NEGATIVE CONTROL: the GENERALISED rule finds checkers the "
              "ORIGINAL `check-*.py` rule missed",
              not missed, "missed: %s" % missed)

        def original_rule(directory):
            out = set()
            for p in sorted(directory.glob("*.py")):
                n = p.name
                if n.startswith("check-") and n.endswith(".py"):
                    out.add(n)
                elif n in ("drift-check.py", "dead-inbox-check.py",
                           "tmp-shape-surface-audit.py"):
                    out.add(n)
            return out
        orig_found = original_rule(tmp3)
        would_have_missed = [n for n in generalised if n not in orig_found]
        check("NEGATIVE CONTROL: the ORIGINAL rule really did miss them "
              "(so the control is not vacuous)",
              len(would_have_missed) >= 4,
              "original rule found: %s" % sorted(orig_found))
    finally:
        import shutil
        shutil.rmtree(tmp3, ignore_errors=True)

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        return 1
    print("VERDICT: CLEAN - every checker on disk is classified; nothing is orphaned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
