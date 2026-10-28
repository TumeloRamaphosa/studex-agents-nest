#!/usr/bin/env python3
"""
REGRESSION TEST: a live credential inside a fenced code block in a tracked
markdown file must be flagged.

THE BUG THIS GUARDS
-------------------
`ops/credential-resolution-check.py` classified every line of a markdown file
that sat inside a ``` fenced code block as "prose", and then the
hardcoded-literal pass skipped any credential literal found on a "prose"
line. The code carried a comment asserting that the hardcoded check was
"unaffected ... it judges the VALUE, not the context, so a live key inside a
fenced block is still caught".

THAT COMMENT WAS FALSE. A negative control proved it: a synthetic Blotato
key inside a ``` fence in a tracked .md file was reported CLEAN, exit 0.
The public remote contains the complete live key in 13 tracked files, 7 of
them markdown, several of them inside fenced code blocks. A checker that
reports CLEAN on those is worse than no checker.

THE RULE THIS TEST ASSERTS
---------------------------
A provider-specific credential LITERAL is flagged wherever it appears:
plain prose, a fenced code block, a markdown table, YAML front matter, an
inline code span, or a source file. The "prose" classification may only
DOWNGRADE a heuristic - it may never suppress an exact provider pattern.

NEGATIVE CONTROL (both directions)
----------------------------------
Every credential case here must go RED, AND a scratch repo with no
credential at all must stay GREEN. Without the clean case the test would
also pass against a checker that flags everything - which is not a working
checker, just a different wrong one.

THE SANDBOX RULE
----------------
This test never writes into the live tree. It builds a throwaway git repo in
a temp directory and points the checker at it with CREDENTIAL_CHECK_ROOT.

Usage: python3 ops/test-credential-fence-check.py
"""
import os
import pathlib
import random
import shutil
import string
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKER = ROOT / "ops" / "credential-resolution-check.py"

FAILS = []
PASSES = []

# The synthetic key is BUILT AT RUNTIME, never written literally into this
# source file - otherwise this test file would itself be a tracked file
# holding a credential-shaped literal, and the checker would (correctly)
# flag the test.
_BODY_ALPHABET = string.ascii_letters + string.digits
_KEY_PREFIX = "blt_y5mV"

# Substrings that ops/credential-resolution-check.py treats as an obvious
# placeholder. A random body must not accidentally contain one, or the
# checker would (correctly) dismiss it as a dummy and the test would be
# testing nothing.
_DUMMY_MARKERS = ("xxx", "your_", "redacted", "placeholder", "dummy",
                  "fake", "test-key", "test_key", "need_", "change_this")

# The ${VAR} placeholder shape is assembled at runtime on purpose. This file
# is a TRACKED file, so a literal "${AGENTMAIL_API_KEY}" written here would
# itself be reported by the checker's resolution pass (a ${VAR} in Python is
# a literal string, not an expansion). Building it from parts keeps this test
# file clean without needing an exemption for it.
VAR_REF = "$" + "{AGENTMAIL_API_KEY}"


def make_synthetic_key():
    """A synthetic Blotato-shaped key: blt_ + 40 random alphanumerics.

    Regenerated until it cannot be mistaken for a documented placeholder.
    """
    while True:
        body = "".join(random.choice(_BODY_ALPHABET) for _ in range(40))
        low = body.lower()
        if not any(m in low for m in _DUMMY_MARKERS):
            return _KEY_PREFIX + body


def run_checker(workdir):
    env = dict(os.environ)
    env["CREDENTIAL_CHECK_ROOT"] = str(workdir)
    r = subprocess.run(
        [sys.executable, str(CHECKER)],
        capture_output=True, text=True, env=env, cwd=str(workdir), timeout=180,
    )
    return r.returncode, r.stdout + r.stderr


def case(name):
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
        raise AssertionError(
            "checker returned 0 (CLEAN) but should have failed. "
            f"--- output ---\n{out[:1500]}"
        )
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
            f"checker returned {code} (RED) on a clean tree.\n"
            f"--- output ---\n{out[:1500]}"
        )
    return out


def make_repo(files):
    """A throwaway git repo containing `files` (name -> content)."""
    d = pathlib.Path(tempfile.mkdtemp(prefix="cred-fence-"))
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=d, check=True)
    for name, content in files.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "add", "-A"], cwd=d, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "sandbox"], cwd=d, check=True)
    return d


KEY = make_synthetic_key()
REDACTED = KEY[:8] + "..."

# ── 0. The clean scratch repo must stay GREEN ─────────────────────────────
# Without this, a checker that flags EVERYTHING would pass every other
# case in this file.
CLEAN_REPO = make_repo({
    "ok.js": "const key = requireEnv('AGENTMAIL_API_KEY');\n",
    "notes.md": (
        "# Notes\n\n"
        "Use the environment variable `AGENTMAIL_API_KEY` for the key.\n"
        "\n"
        "```bash\n"
        f"export AGENTMAIL_API_KEY=\"{VAR_REF}\"\n"
        "```\n"
    ),
})

try:
    @case("clean scratch repo -> checker GREEN (exit 0)")
    def _():
        expect_green(CLEAN_REPO)

    # ── 1. THE BUG: a live key inside a ``` fence in a .md file ───────────
    @case("live key in a ``` fenced block in .md -> checker RED")
    def _():
        repo = make_repo({
            "fenced.md": (
                "# Setup\n\n"
                "Set the key before running:\n\n"
                "```bash\n"
                f'export BLOTATO_API_KEY="{KEY}"\n'
                "```\n\n"
                "Then run the importer.\n"
            ),
        })
        try:
            out = expect_red(repo, "HARDCODED")
            assert "fenced.md" in out, (
                f"checker did not name fenced.md:\n{out[:1500]}"
            )
            assert KEY not in out, "checker printed the full secret value"
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    # ── 2. The same key in the other contexts must ALSO be RED ───────────
    # These guard against over-correcting the fix into a false negative.
    @case("live key on a plain .md line -> checker RED")
    def _():
        repo = make_repo({"plain.md": f"The key is {KEY} here.\n"})
        try:
            expect_red(repo, "HARDCODED")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    @case("live key in a .js file -> checker RED")
    def _():
        repo = make_repo({"code.js": f'const key = "{KEY}";\n'})
        try:
            expect_red(repo, "HARDCODED")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    @case("live key in an inline code span in .md -> checker RED")
    def _():
        repo = make_repo({"inline.md": f"The key is `{KEY}` here.\n"})
        try:
            expect_red(repo, "HARDCODED")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    @case("live key in a markdown table cell -> checker RED")
    def _():
        repo = make_repo({
            "table.md": (
                "| name | value |\n"
                "| --- | --- |\n"
                f"| blotato | {KEY} |\n"
            ),
        })
        try:
            expect_red(repo, "HARDCODED")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    @case("live key in YAML front matter -> checker RED")
    def _():
        repo = make_repo({
            "frontmatter.md": (
                "---\n"
                "title: config\n"
                f"blotato_api_key: {KEY}\n"
                "---\n\n"
                "body\n"
            ),
        })
        try:
            expect_red(repo, "HARDCODED")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    # ── 3. The prose classification must still do its real job ───────────
    # The ${VAR} RESOLUTION check is a different check: a ${VAR} shown in
    # markdown documentation is an explanation, not a live credential.
    # Removing the prose classification wholesale would break that, so the
    # fix must keep it for the resolution check.
    @case("a ${VAR} reference shown in markdown docs -> still GREEN")
    def _():
        repo = make_repo({
            "docs.md": (
                "# Runbook\n\n"
                "The key is stored in the environment:\n\n"
                "```bash\n"
                f"export BLOTATO_API_KEY=\"{VAR_REF}\"\n"
                "```\n"
            ),
        })
        try:
            expect_green(repo)
        finally:
            shutil.rmtree(repo, ignore_errors=True)

finally:
    shutil.rmtree(CLEAN_REPO, ignore_errors=True)

print("=" * 70)
for p in PASSES:
    print("  PASS  " + p)
for f in FAILS:
    print("  FAIL  " + f)
print("=" * 70)
print(f"{len(PASSES)} passed, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
