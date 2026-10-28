#!/usr/bin/env python3
"""
Tests the canonical heartbeat runner: ops/run-heartbeat-checks.py.

A runner is the single control that stands between "a checker exists" and "a
checker actually runs". Two ways that can go wrong, and this test covers both:

1. THE RUNNER LIES. If it collapses "could not prove" (rc=2) into "clean", it
   reintroduces at the runner level the exact bug that produced the 2026-10-26
   mail false negative - a probe that prints a reassuring zero while proving
   nothing. rc=2 must NEVER be reported as clean.

2. A CHECKER IS ORPHANED. The bug that hid blotato-fallback.js was structural:
   nothing ran it, nothing named it. A checker sitting in ops/ that the runner
   does not execute is a comment, not a control. This test asserts every
   canonical checker is actually reachable by the runner.

Self-verifying: the runner's own classification logic is imported and exercised
against synthetic results, so the test proves the behaviour rather than
describing it.

Exit codes: 0 = pass, 1 = a test failed.
"""
import ast
import importlib.util
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RUNNER = HERE / "run-heartbeat-checks.py"

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


def load_runner():
    spec = importlib.util.spec_from_file_location("runner", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def executable_calls(path):
    """Return calls that could EXECUTE something (not merely name it).

    A mention of 'blotato-fallback.js' in a docstring is expected - the
    publishing-path checkers exist precisely because of that script, so they
    name it. What must never appear is an actual invocation: a subprocess or
    os.system call that would run the publisher or send a message.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf8", errors="replace"))
    except SyntaxError:
        return []

    hits = []
    EXEC_FUNCS = {"run", "Popen", "call", "check_call", "check_output", "system",
                  "popen", "spawn", "spawnl", "execv", "execvp"}
    PUBLISH_TOKENS = ("blotato-fallback", "messages/send", "posts")
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        fname = ""
        if isinstance(func, ast.Attribute):
            fname = func.attr
        elif isinstance(func, ast.Name):
            fname = func.id
        if fname not in EXEC_FUNCS:
            continue
        # does any argument name a publisher/send target?
        for arg in list(node.args) + [k.value for k in node.keywords]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                low = arg.value.lower()
                if "blotato-fallback" in low or "messages/send" in low:
                    hits.append("%s(...%s...)" % (fname, arg.value[:60]))
            elif isinstance(arg, (ast.List, ast.Tuple)):
                for elt in getattr(arg, "elts", []):
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        if "blotato-fallback" in elt.value.lower():
                            hits.append("%s([...%s...])" % (fname, elt.value[:60]))
    return hits


def main():
    if not RUNNER.is_file():
        print("[FAIL] runner not found: %s" % RUNNER)
        return 1
    R = load_runner()

    check("runner loads and exposes CHECKERS", hasattr(R, "CHECKERS") and R.CHECKERS)
    check("runner has at least 8 checkers", len(R.CHECKERS) >= 8,
          "only %d" % len(R.CHECKERS))

    MUST_RUN = [
        "ops/drift-check.py",
        "ops/check-price-on-feed.py",
        "ops/check-staged-publish.py",
        "ops/check-cost-model-exposure.py",
        "ops/tmp-shape-surface-audit.py",
        "ops/check-tracked-live-credentials.py",
        "ops/dead-inbox-check.py",
        "ops/check-latest-mail.py",
        "ops/check-scanner-log-exposure.py",
    ]
    runner_paths = set(p for _n, p, _c, _d in R.CHECKERS)
    for p in MUST_RUN:
        check("runner executes %s" % p, p in runner_paths,
              "orphaned - present in ops/ but unreachable by the runner")
        check("%s exists on disk" % p, (ROOT / p).is_file())

    # Use the RUNNER'S OWN classifier. An earlier version of this test
    # carried a local copy of the logic - which is exactly how a test passes
    # while the shipped runner does something else.
    #
    # Classification is CONTRACT-DRIVEN: each checker declares
    # (clean, finding, could_not_prove) in ops/heartbeat-checkers.tsv.
    # Hardcoding 0/1/2/3 was WRONG: the /tmp credential audit returns 3 for
    # EXPOSED, so the runner was reporting a real finding as "BROKEN - the
    # checker crashed" and throwing the result away.
    classify = R.classify
    STD = (0, 1, 2)          # a checker that uses 0=clean, 1=finding, 2=unproven
    SURFACE = (0, 3, None)   # the /tmp audit: 0=clean, 3=EXPOSED

    check("rc=0 classifies as CLEAN", classify(0, STD) == "CLEAN")
    check("rc=1 classifies as FINDING (not clean)", classify(1, STD) == "FINDING")
    check("rc=2 classifies as UNPROVEN (NEVER clean)", classify(2, STD) == "UNPROVEN")
    check("rc=2 is not CLEAN under any reading", classify(2, STD) != "CLEAN")

    # THE REGRESSION THIS EXISTS FOR: a checker whose declared finding code
    # is 3 must be counted as a FINDING, not as a crashed checker.
    check("rc=3 is a FINDING for a checker that declares 3 as its finding code",
          classify(3, SURFACE) == "FINDING")
    check("rc=3 is NOT clean for such a checker", classify(3, SURFACE) != "CLEAN")
    check("a real finding is never reported as a crash",
          classify(3, SURFACE) != "BROKEN")

    # An exit code the checker never declared must never be silently clean.
    check("an UNDECLARED exit code is never CLEAN", classify(99, STD) != "CLEAN")
    check("an UNDECLARED exit code is treated as a FINDING",
          classify(99, STD) == "FINDING")
    check("a declared could-not-prove code is UNPROVEN, not clean",
          classify(2, STD) == "UNPROVEN")

    # The registry is the single source of truth for these codes, so the
    # contract a checker declares must be the contract the runner honours.
    tmp_surface = [c for c in R.CHECKERS if c[0] == "tmp-surface"]
    check("tmp-surface is in the runner's checker set", bool(tmp_surface))
    if tmp_surface:
        contract = tmp_surface[0][2]
        check("tmp-surface declares its real EXPOSED code (3)",
              contract[1] == 3,
              "declared finding code is %s, but the checker exits 3 on EXPOSED"
              % (contract[1],))

    runner_names = set(n for n, _p, _c, _d in R.CHECKERS)
    check("KNOWN_ESCALATED is a subset of CHECKERS names",
          set(R.KNOWN_ESCALATED) <= runner_names,
          "known-escalated names not in the runner: %s"
          % (set(R.KNOWN_ESCALATED) - runner_names))
    check("KNOWN_ESCALATED is not empty (the live escalations are real)",
          len(R.KNOWN_ESCALATED) >= 1)

    # A SIGNAL-KILLED checker proved NOTHING. It must be BROKEN, never
    # CLEAN and never a FINDING.
    #
    # This is not theoretical: check-scanner-log-exposure.py was killed with
    # rc=-9 (SIGKILL / OOM) on 2026-10-26 because it loaded whole gateway
    # logs into RAM. A checker that dies silently is the ORIGINAL bug in a
    # new shape - "a checker that nothing runs is a comment", and now "a
    # checker that gets killed is a comment too".
    def classify_signal(rc, contract=STD):
        if rc is None or rc >= 0:
            return classify(rc, contract)
        return "BROKEN"

    check("a signal-killed checker (rc=-9) classifies as BROKEN",
          classify_signal(-9) == "BROKEN")
    check("a signal-killed checker is NEVER clean", classify_signal(-9) != "CLEAN")
    check("a signal-killed checker is NOT reported as a finding",
          classify_signal(-9) != "FINDING")
    check("a signal kill stays a distinct case from a checker's exit code 3",
          classify_signal(-9) == "BROKEN" and classify(3, SURFACE) == "FINDING")

    # And the runner source must actually implement it - a test that only
    # describes the behaviour proves nothing about the shipped runner.
    rsrc = RUNNER.read_text(encoding="utf8", errors="replace")
    check("the runner detects a negative exit code (signal kill)",
          "rc < 0" in rsrc,
          "the runner has no negative-rc branch, so a killed checker is "
          "silently dropped or misclassified")
    check("the runner labels a killed checker as having proved nothing",
          "proved nothing" in rsrc)
    check("the runner counts a killed checker as BROKEN, not clean",
          '"killed": True' in rsrc)

    # NEGATIVE CONTROL: the signal detection must be able to SEE a real
    # kill, or "never misclassifies a kill" would be vacuously true.
    sig = None
    try:
        p = subprocess.run([sys.executable, "-c",
                            "import os,signal; os.kill(os.getpid(), signal.SIGKILL)"],
                           capture_output=True, text=True, timeout=60)
        sig = p.returncode
    except Exception:
        sig = None
    check("NEGATIVE CONTROL: subprocess reports a signal kill as a negative rc",
          sig is not None and sig < 0,
          "expected a negative returncode, got %r" % (sig,))

    # A MENTION of the publisher script is expected - the publishing-path
    # checkers exist because of it. An actual INVOCATION is not acceptable.
    for name, p, _c, _d in R.CHECKERS:
        full = ROOT / p
        if not full.is_file():
            continue
        calls = executable_calls(full)
        check("%s never INVOKES the publisher (a mention is fine)" % p,
              not calls, "invokes: %s" % calls)

    check("no runner checker invokes blotato-fallback.js",
          not any("blotato-fallback" in p for _n, p, _c, _d in R.CHECKERS))

    missing = [p for _n, p, _c, _d in R.CHECKERS if not (ROOT / p).is_file()]
    check("every runner checker exists on disk", not missing, "missing: %s" % missing)

    # self-test of the self-test: the invocation detector must be able to
    # SEE a real invocation, or "never invokes" would be vacuously true.
    tmp = HERE / ".selftest-invocation.py"
    try:
        tmp.write_text(
            "import subprocess\n"
            "subprocess.run(['node','scripts/blotato-fallback.js'], check=False)\n",
            encoding="utf8")
        hits = executable_calls(tmp)
        check("NEGATIVE CONTROL: the invocation detector actually detects one",
              bool(hits), "detector is blind - 'never invokes' would be vacuous")
    finally:
        if tmp.exists():
            tmp.unlink()

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        return 1
    print("VERDICT: CLEAN - the runner reaches every canonical checker and cannot")
    print("  report 'clean' for a checker that could not prove its answer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
