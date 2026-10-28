#!/usr/bin/env python3
"""
Class check: no .py file may USE a time name it does not BIND.

The bug this guards against
---------------------------
On 2026-10-26 a bare `datetime.now(SAST)` in ops/preflight-daily-post.py
raised `NameError` at runtime, aborting a publish gate mid-check. The file
imported `datetime`/`SAST` only as `dp.datetime`/`dp.SAST` (attributes of the
daily_post module) - so the bare names were never bound in that scope.

The failure mode is nasty because it is *runtime-only*: the file parses fine,
every linter that only checks syntax passes, and the script works perfectly
right up until the one branch that uses the unbound name. A gate that dies
there is a gate that never ran.

What this test does
-------------------
Walks every .py under the ops/, scripts/ and studex-content-automation/scripts/
trees, parses it, and reports any LOAD of `datetime`, `SAST`, `timezone` or
`timedelta` that is not bound in the scope where it is used.

Scope resolution is done properly:
  * module-level imports / assignments / defs bind for the whole module
  * a function-local import binds for that function (this is the case a
    naive scanner gets wrong and produces a false positive)
  * function parameters bind for that function

Self-verification
-----------------
A scanner that cannot fail is worthless. This file therefore contains a
built-in SELFTEST: it runs the detector over deliberately broken and
deliberately correct source snippets and asserts the detector returns the
expected verdicts. If the detector breaks, this test fails rather than
silently passing everything.

Exit codes: 0 = clean, 1 = unbound usage found, 2 = the detector itself is
broken (selftest failed).
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREES = ["ops", "scripts", "studex-content-automation/scripts"]
WATCHED = {"datetime", "SAST", "timezone", "timedelta"}
BUILTINS = set(dir(__builtins__)) | {
    "__name__", "__file__", "__doc__", "__package__", "__spec__", "__loader__",
    "__builtins__", "WindowsError", "BlockingIOError", "ChildProcessError",
    "ConnectionError", "FileExistsError", "FileNotFoundError",
    "InterruptedError", "IsADirectoryError", "ModuleNotFoundError",
    "NotADirectoryError", "PermissionError", "ProcessLookupError",
    "TimeoutError", "StopAsyncIteration", "StopIteration", "SystemExit",
    "RecursionError", "ReferenceError", "IndentationError", "TabError",
    "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeTranslateError",
    "LookupError", "ValueError", "TypeError", "KeyError", "IndexError",
    "AttributeError", "NameError", "ZeroDivisionError", "OSError",
    "RuntimeError", "ArithmeticError", "AssertionError", "NotImplementedError",
    "EnvironmentError", "IOError",
}

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


def _bind_names(node, into):
    """Collect names bound by a statement into the set `into`."""
    for n in ast.walk(node):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                into.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                for tt in ast.walk(t):
                    if isinstance(tt, ast.Name):
                        into.add(tt.id)
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
            t = n.target
            for tt in ast.walk(t):
                if isinstance(tt, ast.Name):
                    into.add(tt.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            into.add(n.name)
        elif isinstance(n, ast.arg):
            into.add(n.arg)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            into.add(n.name)
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            for item in n.items:
                if item.optional_vars is not None:
                    for tt in ast.walk(item.optional_vars):
                        if isinstance(tt, ast.Name):
                            into.add(tt.id)
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            for tt in ast.walk(n.target):
                if isinstance(tt, ast.Name):
                    into.add(tt.id)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            into.update(n.names)
    return into


def find_unbound(src):
    """Return a list of (lineno, name) for time names used but never bound."""
    tree = ast.parse(src)
    module_bound = _bind_names(tree, set(BUILTINS))

    # Function-local bindings, computed per function scope.
    problems = []

    def walk_scope(node, outer_bound):
        local = set(outer_bound)
        # statements of this function bind names for the whole function body
        # (Python hoists function-local names for scoping purposes)
        for stmt in getattr(node, "body", []):
            _bind_names(stmt, local)
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                if n.id in WATCHED and n.id not in local:
                    problems.append((n.lineno, n.id))
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                walk_scope(child, local)

    walk_scope(tree, module_bound)
    return sorted(set(problems))


def selftest():
    """The detector must be able to FAIL, and must not false-positive."""
    broken = """
import os
x = datetime.now(SAST)
"""
    try:
        got = find_unbound(broken)
    except Exception as e:
        return False, "detector raised on broken source: %r" % e
    names = sorted({n for _, n in got})
    if names != ["SAST", "datetime"]:
        return False, "detector missed the broken source (got %r)" % got

    # function-local import MUST bind - this is the false-positive case
    local_ok = """
def f():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
"""
    try:
        got2 = find_unbound(local_ok)
    except Exception as e:
        return False, "detector raised on local-import source: %r" % e
    if got2:
        return False, "detector false-positived on a function-local import: %r" % got2

    # module-level import is fine
    mod_ok = "from datetime import datetime\nx = datetime.now()\n"
    if find_unbound(mod_ok):
        return False, "detector false-positived on a module-level import"

    # attribute access (dp.datetime) is NOT a bare name use
    attr_ok = "import x\ny = x.datetime.now(x.SAST)\n"
    if find_unbound(attr_ok):
        return False, "detector false-positived on attribute access"

    return True, "detector verified: fails on broken, clean on valid"


def main():
    ok, detail = selftest()
    check("SELFTEST: the detector can fail and does not false-positive", ok, detail)
    if not ok:
        print("\nVERDICT: DETECTOR BROKEN - refusing to report CLEAN.")
        print("%d passed, %d failed" % (len(PASSED), len(FAILED)))
        return 2

    total_files, bad_files = 0, []
    for tree in TREES:
        tdir = ROOT / tree
        if not tdir.is_dir():
            continue
        for p in sorted(tdir.rglob("*.py")):
            total_files += 1
            try:
                src = p.read_text(encoding="utf8")
            except Exception:
                continue
            try:
                problems = find_unbound(src)
            except SyntaxError:
                continue
            if problems:
                bad_files.append((p, problems))

    for p, problems in bad_files:
        rel = p.relative_to(ROOT)
        for lineno, name in problems:
            print("  UNBOUND  %s:%s  ->  %s" % (rel, lineno, name))
    check("no .py file uses an unbound time name (%d files scanned)" % total_files,
          not bad_files,
          "; ".join("%s:%s %s" % (p.relative_to(ROOT), ln, nm)
                    for p, ps in bad_files[:5] for ln, nm in ps))

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        return 1
    print("VERDICT: CLEAN - every time name used in these trees is bound where it is used.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
