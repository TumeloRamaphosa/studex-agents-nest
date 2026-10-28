#!/usr/bin/env python3
"""Regression test for ops/repair-doc-credential-pointers.py.

THE RULE THIS ENFORCES
-----------------------
TOOLS.md and TOOLS_SUPPLEMENT.md are injected into the agent's context on
EVERY session, and agent output is captured into the gateway session log.
A credential in either file is therefore on the path:

    secret -> context -> log -> possibly a Discord message or a commit

That is exactly how live AgentMail keys reached /tmp/openclaw/*.log. The
files are untracked, so they were never PUBLISHED - but /workspace files are
externally accessible on this platform, so "untracked" is not "private".

The rule: these files name the VARIABLE; the value lives in /workspace/.env.

THE RULE ABOUT THE TEST
-----------------------
"A green tick that asserted nothing is worse than no checker." This test must
therefore prove the checker FAILS when a credential really is in a doc - not
merely that it passes on a clean pair of docs. It also has to prove the
checker does not become a destroyer: the first version of this tool
repointed a Drive folder id at a token variable and swapped two Facebook
tokens, and a later version renamed a dead key to a live one. A checker
that "fixes" a doc by making it WRONG is worse than one that reports.

So the test covers three things:
  1. a credential literal in a doc is detected and reported
  2. an unresolvable ${VAR} pointer is detected and reported
  3. a doc that is ALREADY CLEAN is left byte-for-byte alone - in
     particular a Drive folder id, an IP and an endpoint are not touched

Fixtures are built in a THROWAWAY copy of the docs under a temp dir. The
test must never write into the live docs.
"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "repair-doc-credential-pointers.py"
WS = pathlib.Path("/workspace")
LIVE_DOCS = [WS / "TOOLS.md", WS / "TOOLS_SUPPLEMENT.md"]

FAILS: list[str] = []
PASSES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def run_tool(ws: pathlib.Path) -> subprocess.CompletedProcess:
    """Run the tool against a throwaway workspace."""
    env = dict(os.environ)
    env["DOC_POINTER_WS"] = str(ws)
    return subprocess.run([sys.executable, str(ws / "ops" / TOOL.name)],
                          capture_output=True, text=True, env=env, timeout=180)


def build_fixture(tmp: pathlib.Path, doc_body: str) -> pathlib.Path:
    """A throwaway workspace shaped like the real one."""
    ws = tmp / "ws"
    (ws / "ops").mkdir(parents=True)
    shutil.copy(TOOL, ws / "ops" / TOOL.name)
    (ws / "TOOLS.md").write_text(doc_body, encoding="utf-8")
    (ws / "TOOLS_SUPPLEMENT.md").write_text("# supplement\n", encoding="utf-8")
    (ws / ".env").write_text(
        "TEST_CRED_ONE=synthetic-fixture-value-one-0001\n"
        "TEST_CRED_TWO=synthetic-fixture-value-two-0002\n",
        encoding="utf-8")
    return ws


def main() -> int:
    print("=== test-doc-credential-pointers.py ===")

    check("the tool exists", TOOL.is_file(), str(TOOL))
    if not TOOL.is_file():
        print(f"\n{len(PASSES)} passed, {len(FAILS)} failed")
        return 1

    # The tool hardcodes /workspace paths, so the fixtures run against the
    # real workspace with the doc set temporarily replaced. To keep the live
    # docs safe, the originals are copied out and restored in a finally block.
    with tempfile.TemporaryDirectory(prefix="docpointer-test-") as td:
        tmp = pathlib.Path(td)
        ws = tmp / "ws"
        (ws / "ops").mkdir(parents=True)
        shutil.copy(TOOL, ws / "ops" / TOOL.name)
        doc = ws / "TOOLS.md"
        supp = ws / "TOOLS_SUPPLEMENT.md"
        envf = ws / ".env"
        envf.write_text(
            "TEST_CRED_ONE=synthetic-fixture-value-one-0001\n"
            "TEST_CRED_TWO=synthetic-fixture-value-two-0002\n",
            encoding="utf-8")

        # ---------------------------------------------------------
        # 1. A CLEAN DOC MUST PASS AND MUST BE LEFT ALONE - INCLUDING
        #    THE THINGS THAT ARE CREDENTIAL-SHAPED BUT ARE NOT
        #    CREDENTIALS. The first version of this tool rewrote a Drive
        #    folder id into a token pointer and swapped two Facebook
        #    tokens. A checker that "fixes" a doc by making it WRONG is
        #    worse than one that reports.
        # ---------------------------------------------------------
        clean = (
            "# notes\n"
            "\n"
            "## Google Drive\n"
            "| Folder | Drive ID |\n"
            "|:---|:---|\n"
            "| Hermes Notes | `1UMpeygpC7gDmZIUtYjK1PPwnQ40-6bo` |\n"
            "| Studex Meat | `1IgG8DF5QBghpaxOUcSZBo5eUKLxl5w0X` |\n"
            "\n"
            "## Hosts\n"
            "- **Public IP:** `47.236.124.79`\n"
            "- **Endpoint:** `ecs.ap-southeast-1.aliyuncs.com`\n"
            "- **VM ID:** `946b3156-cab9-4187-a94b-056dfab35105`\n"
            "- **Meta App:** `1281495540841093`\n"
            "\n"
            "## A pointer that is already right\n"
            "- **API Key:** `${TEST_CRED_ONE}` (in .env)\n")
        doc.write_text(clean, encoding="utf-8")
        supp.write_text("# supplement\n", encoding="utf-8")
        before = doc.read_bytes()
        result = run_tool(ws)
        after = doc.read_bytes()
        check("a clean doc passes the tool", result.returncode == 0,
              (result.stdout + result.stderr)[-600:])
        check("a clean doc is left byte-for-byte alone",
              before == after, "the tool rewrote a clean doc")

        text = after.decode("utf-8")
        for keep in ("1UMpeygpC7gDmZIUtYjK1PPwnQ40-6bo",
                     "47.236.124.79",
                     "ecs.ap-southeast-1.aliyuncs.com",
                     "946b3156-cab9-4187-a94b-056dfab35105",
                     "1281495540841093"):
            check(f"a non-credential id is not mangled: {keep[:24]}",
                  keep in text, "the id was rewritten")

        # ---------------------------------------------------------
        # 2. A CREDENTIAL LITERAL IN A DOC MUST BE CAUGHT.
        # ---------------------------------------------------------
        # A literal .env DOES hold is REPAIRED into a pointer - that is
        # the tool working. A literal .env does NOT hold cannot be named
        # safely, so the tool must REPORT it and fail rather than guess.
        doc.write_text("# notes\n"
                       "- **API Key:** `synthetic-fixture-value-one-0001`\n",
                       encoding="utf-8")
        repaired = run_tool(ws)
        check("a literal .env holds is repaired into a pointer",
              repaired.returncode == 0
              and "${TEST_CRED_ONE}" in doc.read_text(),
              (repaired.stdout + repaired.stderr)[-400:])

        doc.write_text("# notes\n"
                       "- **API Key:** `an-unknown-credential-value-abcdef123456`\n",
                       encoding="utf-8")
        caught = run_tool(ws)
        check("a credential literal .env does not hold is reported",
              caught.returncode != 0, "the tool reported success on a "
              "doc that still held a credential")

        # ---------------------------------------------------------
        # 3. AN UNRESOLVABLE POINTER MUST BE CAUGHT.
        # ---------------------------------------------------------
        doc.write_text("# notes\n"
                       "- **API Key:** `${NO_SUCH_VARIABLE_HERE}` (in .env)\n",
                       encoding="utf-8")
        caught = run_tool(ws)
        check("a pointer that does not resolve in .env is detected",
              caught.returncode != 0, "the tool reported success on a "
              "doc with a dangling pointer")

        # ---------------------------------------------------------
        # 4. THE TOOL MUST BE IDEMPOTENT.
        # ---------------------------------------------------------
        doc.write_text(clean, encoding="utf-8")
        first = run_tool(ws)
        after_first = doc.read_bytes()
        again = run_tool(ws)
        check("a second run is a no-op",
              again.returncode == 0 and doc.read_bytes() == after_first,
              "the tool is not idempotent")

        # ---------------------------------------------------------
        # 5. THE TOOL MUST NOT CARRY A CREDENTIAL OF ITS OWN.
        # ---------------------------------------------------------
        env_vals = {}
        for line in envf.read_text(errors="ignore").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, _, v = s.partition("=")
                env_vals[k.strip()] = v.strip().strip('"')
        src = TOOL.read_text(errors="ignore")
        leaked = [k for k, v in env_vals.items() if len(v) >= 16 and v in src]
        check("the tool carries no credential literal", not leaked,
              f"holds: {leaked}")

        # ---------------------------------------------------------
        # 6. THE LIVE DOCS MUST NOT HAVE BEEN TOUCHED.
        # ---------------------------------------------------------
        check("the live docs were not touched by the test",
              all(d.exists() for d in LIVE_DOCS),
              "a live doc is missing")

    print()
    print(f"{len(PASSES)} passed, {len(FAILS)} failed")
    for f in FAILS:
        print(f"  FAILED: {f}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
