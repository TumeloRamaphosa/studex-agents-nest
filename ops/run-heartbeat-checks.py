#!/usr/bin/env python3
"""
CANONICAL HEARTBEAT RUNNER — one command, every read-only checker.

Why this exists
---------------
The orphaned-publisher bug on 2026-10-26 was not a code bug. `blotato-fallback.js`
had no cron, no checklist entry, and nothing invoked it — so it did nothing, and
nobody noticed for days. The failure was structural: **a checker that nothing
runs is a comment, not a control.**

Auditing HEARTBEAT.md against the checkers actually present in ops/ found the
same shape recurring:
  * `dead-inbox-check.py` — a working, tested checker — was named **nowhere** in
    HEARTBEAT.md. A reader following the file strictly would never run it.
  * `check-cost-model-exposure.py`, `tmp-shape-surface-audit.py` and
    `check-tracked-live-credentials.py` were mentioned only in **narrative**
    sections, never in the checklist, so they were run by hand when noticed but
    not as part of the pass.

So the fix is not "add more prose". It is to make ONE command the pass, and make
the checklist name that command.

What it does
------------
Runs every read-only checker in a fixed order, captures each one's exit code
and its own printed verdict, and prints one summary table. It NEVER publishes,
never sends, never writes to a live surface, and never edits anything. All it
does is run read-only checkers and read their output.

Exit code contract of THIS script:
  0 = every checker proved its answer was clean (or is a known, already-escalated
      finding that is recorded below)
  1 = a checker returned a NEW finding that has not been escalated
  2 = a checker could not prove its answer (unreachable API, truncated page,
      ambiguous response shape) — this is NOT clean and must be surfaced
  3 = a checker crashed or is missing (the runner itself failed)

🔑 **"Could not prove" is not "clean."** Several of these checkers exist
*precisely* because a probe that printed a reassuring zero while proving
nothing was the original bug. A runner that collapses "unproven" into "clean"
reintroduces that bug at the runner level.

Known, already-escalated findings
----------------------------------
These checkers return non-zero for conditions that have ALREADY been posted to
Discord #ops. They are reported here as EXPECTED so a pass is not mistaken for
a new incident — but they are still shown, because a change in their content is
exactly the signal that something moved.

  * check-price-on-feed.py       -> rule [10] price on a public feed (escalated)
  * check-staged-publish.py      -> staged captions that never published (escalated)
  * check-cost-model-exposure.py -> exposed cost model at awyjxfplygag (owner action)

The scanner-log checker is NOT a known escalation: it must be clean. It found
the FEEDHIVE recurrence on 2026-10-26 only because it was added to the runner
after the leak had already survived two remediation passes.

Usage:
  python3 ops/run-heartbeat-checks.py
  python3 ops/run-heartbeat-checks.py --list
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REGISTRY = os.path.join(ROOT, "ops", "heartbeat-checkers.tsv")


REGISTRY = os.path.join(ROOT, "ops", "heartbeat-checkers.tsv")


def load_registry():
    """Read the registry: the single source of truth for the checker set.

    The list used to be hardcoded here, which meant a checker added to ops/
    later was silently ORPHANED - never run, never reported. That is the same
    structural bug that hid blotato-fallback.js. Now the registry file is
    authoritative and ops/test-heartbeat-registry.py fails if any checker on
    disk is unclassified.
    """
    checkers, known = [], set()
    if not os.path.isfile(REGISTRY):
        return None, None
    with open(REGISTRY, encoding="utf8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6:
                continue
            name, path, scope, contract, knownflag, purpose = parts[:6]
            reason = parts[6] if len(parts) > 6 else ""
            if scope != "PASS":
                continue
            codes = []
            for c in contract.split(","):
                c = c.strip()
                codes.append(None if c == "-" else int(c))
            while len(codes) < 3:
                codes.append(None)
            checkers.append((name, path, tuple(codes), purpose))
            if knownflag.lower() == "yes":
                known.add(name)
    return checkers, known


# Populated at IMPORT time, not just inside main(), so that anything
# importing this module (the contract test) sees the real checker set. This
# is NOT a hand-maintained list: an earlier version of this file hardcoded
# it, which is exactly how a checker ends up orphaned.
# ops/test-heartbeat-registry.py fails if a hardcoded list reappears here.
CHECKERS, KNOWN_ESCALATED = load_registry()
if CHECKERS is None:
    CHECKERS, KNOWN_ESCALATED = [], set()


def list_checkers():
    checkers, known = load_registry()
    if checkers is None:
        print("*** REGISTRY MISSING: %s" % REGISTRY)
        return 3
    print("CANONICAL HEARTBEAT CHECKS (%d)" % len(checkers))
    for name, path, _c, purpose in checkers:
        full = os.path.join(ROOT, path)
        state = "present" if os.path.isfile(full) else "*** MISSING ***"
        flag = " (known escalation)" if name in known else ""
        print("  %-20s %-42s %-12s %s%s" % (name, path, state, purpose, flag))
    print("\nRun: python3 ops/run-heartbeat-checks.py")
    return 0


def verdict_line(out):
    """Pull the checker's own verdict line out of its output."""
    best = ""
    for line in out.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("VERDICT") or "VERDICT:" in s or s.startswith("RESULT"):
            best = s
    if not best:
        for line in reversed(out.splitlines()):
            s = line.strip()
            if s and not s.startswith("=") and not s.startswith("-"):
                best = s
                break
    return best[:150]


def run_one(name, path, contract, purpose):
    full = os.path.join(ROOT, path)
    if not os.path.isfile(full):
        return {"name": name, "rc": None, "verdict": "CHECKER MISSING",
                "missing": True}

    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    try:
        p = subprocess.run([sys.executable, full], cwd=ROOT, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=900, text=True)
        rc, out = p.returncode, p.stdout or ""
    except subprocess.TimeoutExpired:
        return {"name": name, "rc": None, "verdict": "TIMEOUT - could not prove",
                "timeout": True}
    except Exception as e:
        return {"name": name, "rc": None, "verdict": "CRASH: %s" % str(e)[:80],
                "crash": True}

    v = verdict_line(out)
    # A NEGATIVE rc means the process was killed by a signal (subprocess
    # reports -SIGNAL). -9 is SIGKILL, which on this host means the OOM
    # killer: the checker never finished, so it proved NOTHING. It must be
    # BROKEN, not FINDING - a killed checker is not a "finding", and it is
    # certainly not clean. Classifying it as a finding would let a dead
    # checker masquerade as a real signal.
    if rc < 0:
        return {"name": name, "rc": None,
                "verdict": "KILLED by signal %d - proved nothing" % (-rc),
                "killed": True}
    return {"name": name, "rc": rc, "verdict": v, "raw": out}


def classify(rc, contract):
    """Classify a checker's exit code using ITS OWN declared contract.

    The contract is (clean, finding, could_not_prove) as declared for that
    checker in ops/heartbeat-checkers.tsv. Hardcoding 0/1/2/3 here is wrong
    the moment a checker uses a different code - and it ALREADY was: the /tmp
    credential audit returns 3 for EXPOSED, so the runner was reporting a real
    finding as "BROKEN - the checker crashed" and throwing the result away.

    An exit code the checker never declared is treated as a FINDING, never as
    clean: an unknown code must never be silently reported as "all good".
    """
    clean_code, finding_code, unproven_code = contract
    if rc == clean_code:
        return "CLEAN"
    if finding_code is not None and rc == finding_code:
        return "FINDING"
    if unproven_code is not None and rc == unproven_code:
        return "UNPROVEN"
    return "FINDING"


def main():
    global CHECKERS, KNOWN_ESCALATED
    loaded, known = load_registry()
    if loaded is None:
        print("*** REGISTRY MISSING: %s" % REGISTRY)
        print("VERDICT: BROKEN - the checker registry is gone, so the pass proves nothing.")
        return 3
    CHECKERS, KNOWN_ESCALATED = loaded, known

    if "--list" in sys.argv:
        return list_checkers()

    print("=" * 78)
    print("CANONICAL HEARTBEAT PASS — %d read-only checkers" % len(CHECKERS))
    print("=" * 78)

    results = []
    for name, path, contract, purpose in CHECKERS:
        r = run_one(name, path, contract, purpose)
        results.append(r)
        rc = r["rc"]
        if r.get("missing") or r.get("crash") or r.get("killed"):
            tag = "BROKEN"
        elif r.get("timeout"):
            tag = "UNPROVEN"
        else:
            tag = classify(rc, contract)
        r["tag"] = tag
        print("\n[%s] %-14s (rc=%s)  %s" % (tag, name, rc, purpose))
        if tag == "FINDING" and rc is not None:
            clean_c, find_c, unpro_c = contract
            if rc not in [c for c in (clean_c, find_c, unpro_c) if c is not None]:
                print("       *** rc=%s is NOT in %s's declared contract %s ***"
                      % (rc, name, (clean_c, find_c, unpro_c)))
        print("       %s" % r["verdict"])
        if r.get("missing"):
            print("       *** CHECKER FILE MISSING ***")

    # ---------------- summary ----------------
    # Classification comes from the per-checker contract, not from hardcoded
    # exit codes, so a checker that returns 3 for a real finding is counted
    # as a finding and not as "the checker crashed".
    findings = [r for r in results if r.get("tag") == "FINDING"]
    unproven = [r for r in results if r.get("tag") == "UNPROVEN"]
    broken = [r for r in results if r.get("tag") == "BROKEN"]

    new_findings = [f for f in findings if f["name"] not in KNOWN_ESCALATED]

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print("  checkers run        : %d" % len(results))
    print("  clean               : %d" % sum(1 for r in results if r.get("tag") == "CLEAN"))
    print("  known escalations   : %d  (%s)" % (
        len(findings) - len(new_findings),
        ", ".join(f["name"] for f in findings if f["name"] in KNOWN_ESCALATED) or "none"))
    print("  NEW findings        : %d  (%s)" % (
        len(new_findings), ", ".join(f["name"] for f in new_findings) or "none"))
    print("  could NOT prove     : %d  (%s)" % (
        len(unproven), ", ".join(f["name"] for f in unproven) or "none"))
    print("  broken/missing      : %d  (%s)" % (
        len(broken), ", ".join(f["name"] for f in broken) or "none"))
    for b in broken:
        if b.get("killed"):
            print("  \u26a0\ufe0f  %s was KILLED (signal) - it proved NOTHING, not 'clean'" % b["name"])

    if broken:
        print("\nVERDICT: BROKEN - a checker is missing or crashed. This pass proves nothing.")
        return 3
    if unproven:
        print("\nVERDICT: COULD NOT PROVE - refusing to report a clean pass.")
        print("  An unproven checker is NOT clean. Surface it, do not silence it.")
        return 2
    if new_findings:
        print("\nVERDICT: NEW FINDING(S) - not previously escalated.")
        for f in new_findings:
            print("  - %s: %s" % (f["name"], f["verdict"]))
        return 1
    print("\nVERDICT: CLEAN - every checker proved its answer. No new findings.")
    print("  (Known escalations still open - see the summary above. Post to #ops")
    print("   only when a finding's CONTENT changes, never on every pass.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
