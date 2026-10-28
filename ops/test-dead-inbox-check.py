#!/usr/bin/env python3
"""Regression test for ops/dead-inbox-check.py.

A checker that accepts no negative control is unusable: a green run may mean
"the rule is broken", not "the code is clean". So this test proves the rule
both FIRES and STAYS SILENT, and proves the exception mechanism is real.

SAFETY
Every case runs in a throwaway scratch tree under /tmp. The live tree is
only ever READ. A sibling test once wrote a fixture into the live
outbound-drafts directory and left it there - a rule-proving test must never
run where the rule applies.

SYNTHETIC ADDRESSES
All mailbox literals are generated at runtime from random alphanumerics, so
this file contains no real-looking address and cannot itself become a
finding. The same applies to the CASE 6 domain mailbox: it is assembled at
runtime from two halves, so no literal "ceo@studexmeat.com" appears here.
"""
from __future__ import annotations

import os
import random
import re
import shutil
import string
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "dead-inbox-check.py"

PASS, FAIL = "PASS", "FAIL"
results = []

# The mailbox domain is assembled at runtime. If this file contained a
# literal domain it would (correctly) trip ops/dead-inbox-check.py, which
# scans every code file including this one. A rule that cannot be applied to
# its own test is a rule nobody trusts.
MAIL_DOMAIN = "agentmail" + "." + "to"

# CASE 6 uses a plain domain mailbox, assembled the same way. It is NOT
# random: the address has to be the exact one the compose default names, so
# that the test proves the RIGHT address is extracted from that line.
BOX_DOMAIN = "studexmeat" + "." + "com"

# The compose default-value syntax the bug lived in:
#     ADMIN_EMAIL_SSL: ${ADMIN_EMAIL_SSL:-ceo@studexmeat.com}
# The ":-" is shell-compose default syntax, not part of the mailbox. If the
# hyphen is swallowed into the local part, the checker fabricates an
# address that no mail server could ever deliver to, and reports a mailbox
# that does not exist as a dead one.
COMPOSE_DEFAULT_LINE = "ADMIN_EMAIL_SSL: ${ADMIN_EMAIL_SSL:-ceo@%s}" % BOX_DOMAIN
# A plain contact line for the same mailbox, on its own line.
CONTACT_LINE = "contact: ceo@%s" % BOX_DOMAIN
# The real address, and the bogus one the old regex produced from the
# compose line.
REAL_BOX = "ceo@%s" % BOX_DOMAIN
BOGUS_BOX = "-ceo@%s" % BOX_DOMAIN

# Pull address-shaped tokens out of the checker's own output. Matching the
# exact token matters: "ceo@studexmeat.com" is a SUBSTRING of
# "-ceo@studexmeat.com", so a naive substring check would pass even while
# the bug is present.
REPORTED_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def rand_local(prefix: str) -> str:
    tail = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
    return "%s%s" % (prefix, tail)


def run_checker(root: Path):
    env = dict(os.environ)
    env["DEAD_INBOX_CHECK_ROOT"] = str(root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([sys.executable, str(CHECKER)], env=env,
                       capture_output=True, text=True, timeout=300)
    return p.returncode, p.stdout + p.stderr


def make_scratch(tmp: Path, name: str) -> Path:
    """A scratch tree shaped like the real one: ops/ + a code file."""
    root = tmp / name
    (root / "ops").mkdir(parents=True, exist_ok=True)
    (root / "ops" / "live-inbox-allowlist.txt").write_text("")
    (root / "ops" / "dead-inbox-exceptions.txt").write_text("")
    return root


def record(case: str, ok: bool, detail: str) -> None:
    results.append((case, ok, detail))
    print("  [%s] %-46s %s" % (PASS if ok else FAIL, case, detail))


def main() -> int:
    if not CHECKER.exists():
        print("checker missing: %s" % CHECKER)
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="dead-inbox-test-"))
    try:
        # --- CASE 1: a dead address in code must FAIL the checker ------------
        dead = "%s@%s" % (rand_local("dead"), MAIL_DOMAIN)
        root = make_scratch(tmp, "case1")
        (root / "ops" / "live-inbox-allowlist.txt").write_text(
            "live@%s\n" % MAIL_DOMAIN)
        (root / "app.js").write_text("const inbox = '%s';\n" % dead)
        code, out = run_checker(root)
        record("case 1  dead address in code -> non-zero", code != 0,
               "exit=%d" % code)

        # --- CASE 2: a proven-live address must PASS --------------------------
        live = "%s@%s" % (rand_local("live"), MAIL_DOMAIN)
        root = make_scratch(tmp, "case2")
        (root / "ops" / "live-inbox-allowlist.txt").write_text("%s\n" % live)
        (root / "app.js").write_text("const inbox = '%s';\n" % live)
        code, out = run_checker(root)
        record("case 2  live address on allowlist -> zero", code == 0,
               "exit=%d" % code)

        # --- CASE 3: NEGATIVE CONTROL - the exception must be real ----------
        # Same dead address, but listed as a deliberate exception for that
        # exact file. If this still fails, the exceptions file is decorative
        # and the checker is not really reading it.
        dead2 = "%s@%s" % (rand_local("dead"), MAIL_DOMAIN)
        root = make_scratch(tmp, "case3")
        (root / "ops" / "live-inbox-allowlist.txt").write_text(
            "live@%s\n" % MAIL_DOMAIN)
        (root / "ops" / "dead-inbox-exceptions.txt").write_text("%s|app.js\n" % dead2)
        (root / "app.js").write_text("const inbox = '%s';\n" % dead2)
        code, out = run_checker(root)
        record("case 3  excepted dead address -> zero (control)", code == 0,
               "exit=%d" % code)

        # --- CASE 4: an exception must be SCOPED to its file ----------------
        # The same dead address, excepted for a DIFFERENT file, must still
        # fail. Without this, one exception silences the whole tree.
        dead3 = "%s@%s" % (rand_local("dead"), MAIL_DOMAIN)
        root = make_scratch(tmp, "case4")
        (root / "ops" / "live-inbox-allowlist.txt").write_text(
            "live@%s\n" % MAIL_DOMAIN)
        (root / "ops" / "dead-inbox-exceptions.txt").write_text(
            "%s|other.js\n" % dead3)
        (root / "app.js").write_text("const inbox = '%s';\n" % dead3)
        code, out = run_checker(root)
        record("case 4  exception scoped to another file -> non-zero", code != 0,
               "exit=%d" % code)

        # --- CASE 6: a compose DEFAULT VALUE is not an address --------------
        # ${VAR:-default@host} is shell-compose syntax. The old regex read
        # the ":-" hyphen as part of the local part and produced a mailbox
        # that cannot exist. This case scans a synthetic file holding BOTH
        # the compose default line and a plain contact line for the same
        # mailbox, and asserts that the REAL address is extracted and the
        # bogus one is NOT.
        root = make_scratch(tmp, "case6")
        (root / "compose.js").write_text(
            COMPOSE_DEFAULT_LINE + "\n" + CONTACT_LINE + "\n")
        code, out = run_checker(root)
        reported = set(REPORTED_RE.findall(out))
        ok = (REAL_BOX in reported) and (BOGUS_BOX not in reported)
        detail = "reported=%s bogus_absent=%s exit=%d" % (
            REAL_BOX in reported, BOGUS_BOX not in reported, code)
        record("case 6  compose default -> real address only", ok, detail)

        # --- CASE 5: the LIVE tree must be clean ----------------------------
        code, out = run_checker(REPO)
        ok = code == 0
        detail = "exit=%d" % code
        if not ok:
            lines = [l for l in out.splitlines() if l.startswith("  ") and ":" in l]
            detail += "  %d finding(s); first: %s" % (len(lines), lines[0].strip() if lines else "?")
        record("case 5  live tree is clean", ok, detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [r for r in results if not r[1]]
    print("\n%d passed, %d failed" % (len(results) - len(failed), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
