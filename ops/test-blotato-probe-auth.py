#!/usr/bin/env python3
"""Regression test: the Blotato read path must not silently read as 'nothing published'.

WHY THIS EXISTS
---------------
The 2026-10-26 content audit found four staged captions that never reached
any platform. To confirm that against the Blotato API we needed a read
probe, and the first version of `ops/probe-blotato-posts.py` used the WRONG
AUTH HEADER:

    Authorization: Bearer <key>     -> HTTP 401, empty list

The repo's own `scripts/blotato-accounts.py` and `scripts/blotato-posts.py`
already use the correct header, and HEARTBEAT.md records the trap verbatim:
"the auth header is `blotato-api-key` (not Authorization). My first query
matched an empty key and reported '0 posts' - wrong."

🔑 **A failed read is indistinguishable from an empty read if the tool
reports them the same way.** That is not a cosmetic bug. A probe that
answers "we published nothing" when the API actually rejected the call
manufactures a duplicate publish on every channel - exactly what the
2026-10-22 memory note warns about.

SECOND TRAP: the posts endpoint IGNORES `?accountId=` and returns the GLOBAL
post list. Filtering by account must happen client-side on
`post["account"]["id"]`. Getting this wrong attributes another account's
posts to ours.

RULES CHECKED HERE
------------------
  1. The probe authenticates with the `blotato-api-key` header.
  2. It never authenticates with an `Authorization: Bearer` header.
  3. It never reports an empty/failed read as a success - an unreachable or
     empty API must be an explicit ERROR with a non-zero exit code.
  4. It filters accounts client-side (it does not trust `?accountId=`).
  5. It reads the key from .env IN-PROCESS - no key literal in the file and
     no key interpolated into a command line (a literal in argv is written
     to the gateway log by the probe itself).
  6. The probe is read-only: no POST/PUT/PATCH/DELETE and no publish/send
     endpoint.

The scan is AST-based and docstring-aware, so PROSE ABOUT THE TRAP (including
this file and the probe's own docstring, which names `Authorization: Bearer`
and `?accountId=`) cannot trip it. Only real code can.

No network. Pure static analysis of the probe source.
"""
from __future__ import annotations

import ast
import os
import re
import sys

PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe-blotato-posts.py")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def _docstring_nodes(tree):
    """The Constant nodes that are docstrings (module/class/function)."""
    out = set()
    holders = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    for node in ast.walk(tree):
        if isinstance(node, holders):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                out.add(id(body[0].value))
    return out


def code_strings(tree):
    """Every string literal in the file EXCEPT docstrings."""
    docs = _docstring_nodes(tree)
    out = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docs
        ):
            out.append(node.value)
    return out


def dict_keys(tree):
    """Every string used as a dict key anywhere in the file."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    out.append(k.value)
    return out


def main() -> int:
    if not os.path.isfile(PROBE):
        print("FAIL: probe not found: %s" % PROBE)
        return 1
    with open(PROBE, encoding="utf-8") as fh:
        src = fh.read()

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print("FAIL: probe does not parse: %s" % e)
        return 1

    keys = dict_keys(tree)
    consts = code_strings(tree)

    # 1. correct auth header is used as a real header key
    check(
        "probe authenticates with the blotato-api-key header",
        "blotato-api-key" in keys,
        "expected 'blotato-api-key' as a header dict key",
    )

    # 2. wrong auth header is never used as a real header key
    bearer = [k for k in keys if k.lower() == "authorization"]
    check(
        "probe never uses an Authorization: Bearer header (401 -> false '0 posts')",
        not bearer,
        "found Authorization header key(s): %s" % bearer,
    )

    # 3. a failed/empty API read must be an explicit error, not a success
    nonzero_returns = re.findall(r"return\s+([1-9]\d*)", src)
    check(
        "empty or failed API read is an explicit ERROR with a non-zero exit",
        any("ERROR" in c for c in consts) and bool(nonzero_returns),
        "expected an explicit ERROR path and a non-zero return",
    )
    zero_post_prints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if "0 posts" in arg.value:
                        zero_post_prints.append(arg.value)
    check(
        "probe never prints a '0 posts' line",
        not zero_post_prints,
        "an empty result must not be printed as a successful answer",
    )

    # 4. accounts filtered client-side
    reads_account_key = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "account"
        for node in ast.walk(tree)
    )
    check(
        "probe filters accounts client-side (the API ignores ?accountId=)",
        reads_account_key,
        "expected a client-side read of post['account']",
    )
    check(
        "probe does not pass ?accountId= to the API",
        not any("accountId=" in c for c in consts),
        "the API ignores ?accountId=; filtering must be client-side",
    )

    # 5. key read in-process, no literal key
    check(
        "probe reads the key from .env in-process",
        any(".env" in c for c in consts) and "env_key" in src,
        "expected an in-process .env read",
    )
    check(
        "probe contains no key literal",
        not re.search(r"BLOTATO_API_KEY\s*=\s*['\"][A-Za-z0-9_\-]{12,}", src),
        "a key literal must never live in the file",
    )

    # 6. read-only
    mutating_methods = {"POST", "PUT", "PATCH", "DELETE"}
    mut_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "method" and isinstance(kw.value, ast.Constant):
                    if str(kw.value.value).upper() in mutating_methods:
                        mut_calls.append(kw.value.value)
                if kw.arg == "data":
                    mut_calls.append("data=")
    endpoint_like = [c for c in consts if re.search(r"/(publish|send|messages)\b", c)]
    check(
        "probe is read-only (no POST/PUT/PATCH/DELETE, no publish/send endpoint)",
        not mut_calls and not endpoint_like,
        "found %d mutating construct(s) / %d endpoint-like literal(s)"
        % (len(mut_calls), len(endpoint_like)),
    )

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    for name, ok, detail in results:
        print(
            "  [%s] %s%s"
            % ("PASS" if ok else "FAIL", name, (" - " + detail) if detail and not ok else "")
        )
    print("  %d passed, %d failed" % (passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
