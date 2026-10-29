#!/usr/bin/env python3
"""
Negative-control regression test for ops/credential-resolution-check.py.

WHY THIS EXISTS
---------------
The checker's own reader was wrong three times (shell comments read as code, a
heredoc marker in a comment poisoning everything after it, and a heredoc
marker inside a double-quoted string treated as a statement-level quoted
heredoc). Each bug produced FALSE POSITIVES on correct code. A checker that
cries to fail on everything is as useless as one that never fails.

So this test does the thing that actually proves a checker works:

  * it writes a DELIBERATELY BROKEN file into a SANDBOX,
  * runs the checker against that sandbox,
  * asserts the checker goes RED and names the right thing,
  * asserts the checker goes GREEN once the file is fixed,
  * and proves the shell reader does not fire on the CORRECT form.

Every case is a negative control. If the checker cannot be made to fail on
purpose, a green run from it means nothing.

THE SANDBOX RULE
----------------
This test MUST NOT write into the live tree. On 2026-10-23 a sibling test
(`ops/test-draft-rules.py`) wrote its fixture into the LIVE `outbound-drafts/`
- the folder of real email drafts to real external partners - and an
interrupted run left it there. A stray test file in the approval queue is one
stray approval away from being sent to a buyer.

The fix for that class of bug is never "clean up better". It is NEVER WRITE
THERE AT ALL. So the checker is pointed at a temporary directory via its
`DRIFT_CHECK_DRAFT_DIR`-style override: the checker resolves its file list
from a git ls-files call rooted at a supplied directory, and this test builds
a throwaway git repo in /tmp.

Usage: python3 ops/test-credential-resolution.py
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKER = ROOT / "ops" / "credential-resolution-check.py"

# Synthetic fixture values for the bare KEY/SEC cases, generated at runtime.
#
# They are NOT the real GoDaddy credential. A test fixture that carries the
# real published key would put a live credential back into a TRACKED file -
# the exact anti-pattern the rule under test exists to catch. And they are
# deliberately MIXED-CASE (not hex), because a hex value is caught by the
# pre-existing HEX_ASSIGNED rule and the case would then pass for the WRONG
# REASON, never proving the bare-KEY rule itself fires.
SYNTHETIC_MIXED_KEY = "Zq7" + "vRt4LmNp8XsW2" + "kDf9HgJ3" + "aQw5"
SYNTHETIC_MIXED_SECRET = "Vb2" + "nMx6Qst8ZcW1" + "eRj4YkP7" + "uHt3"

# The three fixtures below used to hold the REAL PipeDream, ClickUp and
# FeedHive credentials. A test fixture holding a real credential
# re-publishes it inside a TRACKED file - the exact anti-pattern the
# checker exists to prevent. They are now SYNTHETIC and assembled at
# runtime from fragments, so the literal never appears contiguously in
# this file. The SHAPE is unchanged, because the shape is the thing under
# test: an opaque mixed-case token, a pk_<9 digits>_<32 alnum> token, and
# an fh_<48 hex> key.
SYNTHETIC_OPAQUE = ("Zy7" + "vRt4LmNp8XsW2" + "kDf9HgJ3" + "aQw5Rt7"
                    + "Yu3Io9" + "Pa2Sd4")
SYNTHETIC_CLICKUP = ("pk_30268" + "9978_"
                     + "Sy7Xk2Bq9Lp4Mv6Tz3Rw8Nc5Hd1Jg0Ee7")
SYNTHETIC_FEEDHIVE = ("fh_" + "a1b2c3d4e5f60718" + "293a4b5c6d7e8f90"
                      + "a1b2c3d4e5f60718")

FAILS = []
PASSES = []


def run_checker(workdir):
    """Run the checker with its file root pointed at `workdir`."""
    env = dict(os.environ)
    env["CREDENTIAL_CHECK_ROOT"] = str(workdir)
    r = subprocess.run(
        [sys.executable, str(CHECKER)],
        capture_output=True, text=True, env=env, cwd=str(workdir), timeout=180,
    )
    return r.returncode, r.stdout + r.stderr


def make_sandbox():
    """A throwaway git repo with one clean file."""
    d = pathlib.Path(tempfile.mkdtemp(prefix="credchk-"))
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=d, check=True)
    (d / "ok.js").write_text(
        "const key = requireEnv('AGENTMAIL_API_KEY');\n"
        "const url = `https://x/${id}`;\n"
    )
    (d / "ok.py").write_text(
        "import os\nKEY = os.environ['AGENTMAIL_API_KEY']\n"
    )
    (d / "ok.sh").write_text(
        '# a comment mentioning << \'EOF\' and ${AGENTMAIL_API_KEY}\n'
        "KEY=\"${AGENTMAIL_API_KEY}\"\n"
    )
    subprocess.run(["git", "add", "-A"], cwd=d, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "sandbox"], cwd=d, check=True)
    return d


def case(name):
    """Decorator-free helper: run a body, expect pass/fail."""
    def wrap(fn):
        try:
            fn()
            PASSES.append(name)
        except AssertionError as e:
            FAILS.append(f"{name}: {e}")
        except Exception as e:  # noqa: BLE001
            FAILS.append(f"{name}: unexpected error: {type(e).__name__}: {e}")
    return wrap


def expect_red(workdir, needle):
    code, out = run_checker(workdir)
    if code == 0:
        raise AssertionError("checker returned 0 (green) but should have failed")
    if needle.lower() not in out.lower():
        raise AssertionError(
            f"checker failed but did not mention {needle!r}.\n"
            f"--- output ---\n{out[:1500]}"
        )
    return out


def expect_green(workdir):
    code, out = run_checker(workdir)
    if code != 0:
        raise AssertionError(
            f"checker returned {code} (red) on a clean tree.\n"
            f"--- output ---\n{out[:1500]}"
        )
    return out


SANDBOX = make_sandbox()
try:
    # ── 0. The clean sandbox is green ─────────────────────────────────────
    @case("clean sandbox -> checker GREEN")
    def _():
        expect_green(SANDBOX)

    # ── 0b. GoDaddy's sso-key shape -> RED, fixed form -> GREEN ──────────
    # A live GoDaddy API key and secret sat in four tracked scripts for
    # months while the checker reported CLEAN: the provider issues an
    # unprefixed key, so no LITERAL pattern matched, and the variables were
    # named KEY and SEC - too short for the assignment patterns. The values
    # below are generated at runtime so this file holds no real-looking
    # credential and cannot itself become a finding.
    def _rand(n):
        import random
        import string as _s
        return "".join(random.choice(_s.ascii_letters + _s.digits) for _ in range(n))

    @case("bare KEY/SEC credential pair -> checker RED")
    def _():
        (SANDBOX / "gd_pair.py").write_text(
            "KEY = '%s'\nSEC = '%s'\n" % (_rand(32), _rand(24))
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "credential")

    @case("literal sso-key credential -> checker RED")
    def _():
        (SANDBOX / "gd_pair.py").write_text(
            "HDR = 'sso-key %s:%s'\n" % (_rand(32), _rand(24))
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "GoDaddy")

    @case("runtime-resolved KEY/SEC pair -> checker GREEN")
    def _():
        (SANDBOX / "gd_pair.py").write_text(
            "import os\n"
            "KEY = os.environ.get('GODADDY_API_KEY', '')\n"
            "SEC = os.environ.get('GODADDY_API_SECRET', '')\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)

    # ── 1. JS single-quoted placeholder -> RED ───────────────────────────
    @case("JS '${VAR}' in quotes -> checker RED")
    def _():
        (SANDBOX / "bad.js").write_text(
            "const key = '${AGENTMAIL_API_KEY}';\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "UNRESOLVED")
        (SANDBOX / "bad.js").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 2. Python placeholder -> RED ─────────────────────────────────────
    @case("Python '${VAR}' -> checker RED")
    def _():
        (SANDBOX / "bad.py").write_text(
            "KEY = '${AGENTMAIL_API_KEY}'\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "UNRESOLVED")
        (SANDBOX / "bad.py").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 3. Shell single-quoted string -> RED ────────────────────────────
    @case("shell '${VAR}' in single quotes -> checker RED")
    def _():
        (SANDBOX / "bad.sh").write_text("KEY='${AGENTMAIL_API_KEY}'\n")
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "UNRESOLVED")
        (SANDBOX / "bad.sh").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 4. Shell quoted heredoc -> RED ───────────────────────────────────
    @case("shell '${VAR}' in a QUOTED heredoc -> checker RED")
    def _():
        (SANDBOX / "bad.sh").write_text(
            "cat > f << 'EOF'\nKEY=${AGENTMAIL_API_KEY}\nEOF\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "UNRESOLVED")
        (SANDBOX / "bad.sh").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 5. HARDCODED literal -> RED ──────────────────────────────────────
    @case("hardcoded AgentMail key -> checker RED")
    def _():
        (SANDBOX / "bad.js").write_text(
            "const key = 'am_us_0123456789abcdef0123456789abcdef0123456789';\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.js").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 5b. The two shapes learned on 2026-10-23 ────────────────────────
    # The checker's ClickUp pattern used to be pk_[0-9a-f]{20,}. A REAL
    # ClickUp token is pk_ + 8 digits + "_" + 32 alnum - the 9th character
    # is an underscore, not a hex digit, so the old pattern could never
    # match one. It was a hole that read as coverage. Five live ClickUp
    # tokens were sitting in tracked source while the checker said CLEAN.
    @case("hardcoded ClickUp token -> checker RED")
    def _():
        # SYNTHETIC token: correct SHAPE (pk_ + 9 digits + _ + 32 alnum) but
        # built from a made-up account id, so it shares no 12-char slice with
        # any live credential.
        #
        # It used to be a LIVE-shaped token whose account prefix matched a
        # real key in .env. The credential masker did its job and replaced
        # that prefix with asterisks - which silently DESTROYED this
        # negative control: the masked string no longer has the shape the
        # checker looks for, so the checker correctly returned GREEN and
        # this test failed. A test fixture must never hold a live slice.
        (SANDBOX / "bad.js").write_text(
            "const token = 'pk_519283746_Qw7Zx4Rt2Nm8Vb3Kd6Lf0Hg5Jc1Sp9Ay2';\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.js").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("hardcoded Kimi key -> checker RED")
    def _():
        (SANDBOX / "bad.js").write_text(
            "const key = 'sk-rQm4Zt7Xc2Vb5Nk8Lp3Wr6Ys1Hd0Fg9Ja2Ue5Io7Po4';\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.js").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("hardcoded raw-hex secret assigned to a KEY var -> checker RED")
    def _():
        # Cloudflare R2 keys and Higgsfield keys are raw hex with no
        # prefix, so shape alone cannot catch them - the ASSIGNMENT can.
        (SANDBOX / "bad.js").write_text(
            "R2_SECRET_KEY=3f8a2c91e7b4d605a1c8f2e93b7d4061\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.js").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("base64 credential ref with a glued '=' -> checker RED")
    def _():
        # The Blotato key is base64 and ends in '='. The 2026-10-23
        # scrubber pasted a placeholder over the key body and LEFT the
        # trailing '=' behind, producing "${BLOTATO_API_KEY}=". If the
        # stored value already ends in '=', the header becomes '...=='
        # and the provider rejects it. The shape IS the bug, so the
        # checker must name it.
        (SANDBOX / "bad.sh").write_text(
            'AUTH="blotato-api-key: ${BLOTATO_API_KEY}="\n'
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "MANGLED")
        (SANDBOX / "bad.sh").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("opaque credential assigned to a KEY var -> checker RED")
    def _():
        # A provider key with no recognisable prefix, assigned to a
        # credential-named variable. HEX_ASSIGNED only sees lowercase
        # hex; mixed-case opaque tokens need their own rule.
        (SANDBOX / "bad.py").write_text(
            f"PIPEDREAM_API_KEY = '{SYNTHETIC_OPAQUE}'\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.py").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 5b-ii. The bare KEY / SEC shape ─────────────────────────────────
    # GoDaddy's sso-key is stored as two variables named exactly KEY and
    # SEC. Every existing assignment rule required a character BEFORE the
    # credential word, so neither variable matched: the checker reported
    # CLEAN while a live GoDaddy key and secret sat in tracked scripts and
    # were published to the public remote. The variable names are too
    # short for the pattern - it needs its own rule for the bare names.
    #
    # The fixture values are SYNTHETIC and generated at runtime. Two
    # reasons, both learned the hard way:
    #   1. A test fixture holding the real published key would re-publish
    #      a live credential inside a TRACKED file - the exact anti-pattern
    #      this whole rule exists to prevent.
    #   2. The value must be NON-HEX. A hex value is caught by the
    #      pre-existing HEX_ASSIGNED rule, so a hex fixture would make
    #      this case pass for the WRONG REASON - it would never prove the
    #      bare-KEY rule fires. The real GoDaddy key is mixed-case.
    @case("bare KEY = literal (GoDaddy sso-key shape) -> checker RED")
    def _():
        (SANDBOX / "bad.py").write_text(
            f'KEY = "{SYNTHETIC_MIXED_KEY}"\n'
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.py").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("bare SEC = literal -> checker RED")
    def _():
        (SANDBOX / "bad.py").write_text(
            f'SEC = "{SYNTHETIC_MIXED_SECRET}"\n'
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.py").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("bare KEY resolved from the environment -> still GREEN")
    def _():
        # The negative control for the rule above: a bare KEY variable
        # that resolves at runtime is the CORRECT form and must not be
        # flagged. It must be a real Python resolution - "${VAR}" is a
        # literal in Python, which is the rule the checker enforces.
        (SANDBOX / "ok.py").write_text(
            "import os\nKEY = os.environ['GODADDY_API_KEY']\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)
        (SANDBOX / "ok.py").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 5c. The blind spots the checker had ─────────────────────────────
    # The checker used to SKIP memory/, builds/, research/ and
    # studex-obsidian-vault/ entirely, and used to ALLOW every .md file.
    # Those are OUR files, and they held 33 distinct live credential
    # values across 74 tracked files. The checker said CLEAN because it
    # never looked there.
    @case("a live key in a .md file -> checker RED")
    def _():
        (SANDBOX / "notes.md").write_text(
            "The key is `am_us_0123456789abcdef0123456789abcdef0123456789` here.\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "notes.md").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("a live key in a memory/ file -> checker RED")
    def _():
        mem = SANDBOX / "memory"
        mem.mkdir(exist_ok=True)
        (mem / "2026-01-01.md").write_text(
            "used am_us_0123456789abcdef0123456789abcdef0123456789 today\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (mem / "2026-01-01.md").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("real ClickUp token in a .md file -> checker RED")
    def _():
        # The exact shape that hid in tracked markdown for months:
        # builds/2026-08-18.md, memory/2026-07-27.md and
        # studex-obsidian-vault/daily/2026-08-18.md all carried a live
        # ClickUp token, and the checker reported CLEAN. The .md control
        # above used an am_us_ shape; this one uses the token shape that
        # actually escaped.
        (SANDBOX / "notes.md").write_text(
            f"The ClickUp API token (`{SYNTHETIC_CLICKUP}`) "
            "returned `Token invalid` tonight.\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "notes.md").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("live FeedHive token in builds/ -> checker RED")
    def _():
        b = SANDBOX / "builds"
        b.mkdir(exist_ok=True)
        (b / "2026-08-18.md").write_text(
            f"FeedHive key `{SYNTHETIC_FEEDHIVE}` "
            "invalid since Oct 5.\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (b / "2026-08-18.md").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("live key in studex-obsidian-vault/ -> checker RED")
    def _():
        v = SANDBOX / "studex-obsidian-vault" / "daily"
        v.mkdir(parents=True, exist_ok=True)
        (v / "2026-10-05.md").write_text(
            "used am_us_0123456789abcdef0123456789abcdef0123456789 today\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (v / "2026-10-05.md").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    @case("real ClickUp token shape (9 digits) -> checker RED")
    def _():
        # pk_ + 9 DIGITS + _ + 32 alnum. An earlier pattern said 8 digits,
        # which required the 9th char to be "_" - it is a digit. The
        # pattern could never match a real ClickUp token, so the checker
        # reported CLEAN on files that contained one.
        (SANDBOX / "bad.js").write_text(
            f"const t = '{SYNTHETIC_CLICKUP}';\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "HARDCODED")
        (SANDBOX / "bad.js").unlink()
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)

    # ── 6. The FALSE POSITIVES must stay gone ───────────────────────────
    # These are the three reader bugs. Each of these is CORRECT code that
    # the first version of the checker flagged.
    @case("shell comment mentioning a heredoc marker -> still GREEN")
    def _():
        (SANDBOX / "ok.sh").write_text(
            "# a comment mentioning << 'EOF' and ${AGENTMAIL_API_KEY}\n"
            "KEY=\"${AGENTMAIL_API_KEY}\"\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)

    @case("heredoc marker inside a double-quoted string -> still GREEN")
    def _():
        # This is orchestrix/start-war.sh's real shape: the marker is
        # inside a double-quoted argument, so bash expands ${...} locally.
        (SANDBOX / "ok.sh").write_text(
            'run "cat > f << \'EOF\'\n'
            "KEY=${AGENTMAIL_API_KEY}\n"
            'EOF"\n'
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)

    @case("Python docstring documenting the placeholder -> still GREEN")
    def _():
        (SANDBOX / "doc.py").write_text(
            '"""Example: KEY = \'${AGENTMAIL_API_KEY}\' is a literal in Python."""\n'
            "import os\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)

    @case("JS backtick template literal -> still GREEN (JS expands ${})")
    def _():
        (SANDBOX / "ok.js").write_text(
            "const url = `https://api/x/${AGENTMAIL_API_KEY}`;\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)

    # ── 6b. A declared doc-pointer emitter ───────────────────────────────
    # Some tools WRITE the text ${VAR} into markdown so a human can look
    # the value up in .env. Python not expanding it is the design, so the
    # resolution rule must not fire on them. But the exemption must be
    # NARROW: a marked emitter that carries a LIVE key must still be RED,
    # or the marker is just a skip rule with a better name.
    @case("declared doc-pointer emitter with ${VAR} -> checker GREEN")
    def _():
        (SANDBOX / "emitter.py").write_text(
            "# credential-resolution: doc-pointer-emitter\n"
            'REPAIRS = [("- **Token:** `${AGENTMAIL_API_KEY}` (in .env)")]\n'
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_green(SANDBOX)

    @case("declared doc-pointer emitter holding a LIVE key -> still RED")
    def _():
        (SANDBOX / "emitter.py").write_text(
            "# credential-resolution: doc-pointer-emitter\n"
            "LIVE = 'am_us_0123456789abcdef0123456789abcdef0123456789abcdef'\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=SANDBOX, check=True)
        expect_red(SANDBOX, "credential")

    # ── 7. The LIVE tree must be clean ───────────────────────────────────
    @case("live workspace -> checker GREEN")
    def _():
        code, out = run_checker(ROOT)
        if code != 0:
            raise AssertionError(
                f"live tree has credential issues.\n--- output ---\n{out[:2500]}"
            )

finally:
    shutil.rmtree(SANDBOX, ignore_errors=True)

print("=" * 70)
for p in PASSES:
    print("  PASS  " + p)
for f in FAILS:
    print("  FAIL  " + f)
print("=" * 70)
print(f"{len(PASSES)} passed, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
