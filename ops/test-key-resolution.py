#!/usr/bin/env python3
"""Negative tests for the credential-resolution + truncation guards.

The bug this guards: several checker scripts were committed with literal
`${AGENTMAIL_MAIN_API_KEY}` / `${BLOTATO_API_KEY}` placeholder strings. Run
them as-is and they send the placeholder AS the credential, get HTTP 403/401,
and print "0 messages" / "0 posts" -- byte-identical to "nothing there".
Three separate false all-clears have already come out of that family.

A checker that cannot fail is worthless. So we prove these guards go RED on
purpose before trusting a green run.

Usage: python3 ops/test-key-resolution.py
"""
import io
import pathlib
import sys
import contextlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import agentmail_keys as ak  # noqa: E402

FAILS = []
PASSES = []


def check(name, fn, expect_raises=True, expect_in=None):
    buf = io.StringIO()
    raised = None
    try:
        with contextlib.redirect_stdout(buf):
            fn()
    except BaseException as e:  # SystemExit included
        raised = e
    out = buf.getvalue()
    if expect_raises:
        if raised is None:
            FAILS.append(f"{name}: expected a failure, got a clean return")
        else:
            msg = str(raised)
            if expect_in and expect_in.lower() not in msg.lower():
                FAILS.append(f"{name}: raised but message lacked {expect_in!r}: {msg[:160]}")
            else:
                PASSES.append(f"{name}: raised as expected -> {msg[:110]}")
    else:
        if raised is not None:
            FAILS.append(f"{name}: unexpected failure: {raised}")
        else:
            PASSES.append(f"{name}: returned cleanly -> {out.strip()[:110]}")


# 1. A dead key must never reach a sweep.
def dead_key():
    ak.live_agentmail_keys.__globals__["_load_env"] = lambda: {
        "AGENTMAIL_MAIN_API_KEY": "am_us_dead_key_0000000000000000000000000000",
        "AGENTMAIL_API_KEY": "am_us_dead_key_1111111111111111111111111111",
        "AGENTMAIL_CIIE_KEY_DEAD_TEST": "am_us_dead_key_2222222222222222222222222222",
    }
    ak.live_agentmail_keys.__globals__["CIIE_KEY_ENV"] = "AGENTMAIL_CIIE_KEY_DEAD_TEST"
    ak.live_agentmail_keys()


orig_load = ak._load_env
orig_ciie = ak.CIIE_KEY_ENV


def restore():
    ak._load_env = orig_load
    ak.CIIE_KEY_ENV = orig_ciie


try:
    check("dead key -> refuses to report zero", dead_key, expect_raises=True,
          expect_in="no live agentmail key")
finally:
    restore()

# 2. A truncated sweep must be detected, not silently accepted.
check("truncated sweep -> detected",
      lambda: ak.assert_not_truncated(1000, 1000), expect_raises=True, expect_in="truncated")
check("exactly-at-limit -> detected",
      lambda: ak.assert_not_truncated(200, 200), expect_raises=True, expect_in="truncated")
check("under limit -> passes",
      lambda: ak.assert_not_truncated(199, 200), expect_raises=False)

# 3. The real keys must actually resolve and be live.
def real_keys():
    keys = ak.live_agentmail_keys()
    if not keys:
        raise SystemExit("no live keys resolved")


check("real keys resolve and are live", real_keys, expect_raises=False)

# 4. The blotato key must resolve.
def real_blotato():
    k = ak.blotato_key()
    if not k.startswith("blt_"):
        raise SystemExit("unexpected blotato key shape")


check("blotato key resolves", real_blotato, expect_raises=False)

# 5. No script may still contain a literal unresolved placeholder.
#    Exempt: one-off migration scripts whose literal is a SEARCH ANCHOR (the
#    string they look for in another file), not a credential they use.
#
#    LANGUAGE-AWARE: a docstring or comment that DOCUMENTS the placeholder
#    bug is not a bug. `scripts/cred_env.py` explains the failure mode in its
#    module docstring, and a line-scan used to flag its own documentation.
#    Same lesson as the shell parser in ops/credential-resolution-check.py:
#    a checker's reader is part of the check, and a checker that fires on
#    prose teaches people to ignore it.
ANCHOR_FILES = {
    "fix-ciii-env-loader.py",
    # One-shot migration scripts. Their literals are the strings they
    # SEARCH FOR in other files, not credentials they use.
    "_migrate_credentials.py",
    "_migrate_credentials2.py",
}


def prose_lines(text):
    """Line numbers that are docstrings or comments, not code."""
    prose = set()
    try:
        import ast
        tree = ast.parse(text)
    except SyntaxError:
        return prose
    for node in ast.walk(tree):
        # Only nodes that HAVE a body can own a docstring. ast.walk also
        # yields the docstring's own Constant node, which has no .body -
        # asking for one and then subscripting it is a TypeError.
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                and isinstance(first.value.value, str):
            start = first.value.lineno
            end = getattr(first.value, "end_lineno", start) or start
            for ln in range(start, end + 1):
                prose.add(ln)
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("#"):
            prose.add(i)
    return prose


PLACEHOLDER_FILES = []
for f in sorted((ROOT / "scripts").glob("*.py")):
    if f.name in ANCHOR_FILES or f.name == "agentmail_keys.py":
        continue
    text = f.read_text(errors="replace")
    prose = prose_lines(text)
    for i, line in enumerate(text.splitlines(), 1):
        if i in prose:
            continue
        if "${" in line and "API_KEY" in line:
            PLACEHOLDER_FILES.append(f"{f.name}:{i}: {line.strip()[:80]}")

if PLACEHOLDER_FILES:
    FAILS.append("scripts still contain literal key placeholders:\n    " +
                 "\n    ".join(PLACEHOLDER_FILES))
else:
    PASSES.append("no script contains a literal ${...API_KEY} placeholder")

print("=" * 68)
for p in PASSES:
    print("  PASS  " + p)
for f in FAILS:
    print("  FAIL  " + f)
print("=" * 68)
print(f"{len(PASSES)} passed, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
