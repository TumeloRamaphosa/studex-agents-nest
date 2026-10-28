#!/usr/bin/env python3
"""
check-client-secret-exposure.py — FAIL if a browser bundle can hold a secret.

THE RULE
    A tracked-or-untracked client source file must not read
    `import.meta.env.VITE_<NAME>` where <NAME> looks like a credential.

WHY A NEW CHECKER IS NEEDED
    `credential-resolution-check.py` looks for LITERAL credential values in files.
    A secret read through `import.meta.env` never appears as a literal — Vite
    resolves it at BUILD time from `.env` and inlines the value into the
    bundle. So the literal scanner sees nothing and reports CLEAN while the
    secret is one `npm run build` away from being public.

    This is the same blind spot this repo keeps hitting: a checker that covers a
    different surface than the rule it enforces. The rule is "no credential in a
    browser bundle". The enforcement surface is the CLIENT SOURCE, because that
    is where the bundler makes the decision.

    It is also the same lesson as the Blotato browser-header removal: removing
    the exposure from the source is not enough — the guard has to make it
    impossible to put it back.

GRAMMAR
    A client file is a .ts/.tsx/.js/.jsx/.mjs/.vue/.svelte/.html file.
    A "secret-looking" VITE_ name contains any of:
        TOKEN SECRET KEY PASSWORD CREDENTIAL ACCESS PRIVATE AUTH BEARER SIGNATURE
    (case-insensitive), matched on the whole variable name.

ALLOWLIST
    Exact names only, never a pattern — a loose pattern false-positives on
    variable names and teaches people to ignore the checker.
      VITE_SUPABASE_ANON_KEY        Supabase publishable/anon key, public by design
      VITE_APP_FIREBASE_CONFIG      Firebase web config, public by design
      VITE_APP_PLUS_EXPORT_PUBLIC_KEY  Excalidraw public key, public by design

EXIT CODES
    0 = CLEAN    no client file can read a secret-named VITE_ var
    1 = DRIFT    at least one can - this is a credential exposure
    2 = UNCHECKED no client source files were found; nothing was asserted

    UNCHECKED is deliberately not CLEAN. A green tick that asserted nothing is
    worse than no checker.

TESTING
    CLIENT_SECRET_CHECK_ROOT=<dir> points the checker at a sandbox instead of
    /workspace, so the rule-proving test NEVER writes into the live tree.
"""
import os
import re
import sys
from pathlib import Path

CLIENT_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue", ".svelte", ".html"}

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".archive", ".next", ".turbo",
    ".matrix-session-memory", "__pycache__", ".venv", "venv",
    # third-party vendored trees - not ours to police
    "OpenJarvis", "gstack", "headroom", "OBLITERATUS", "Decepticon", "core",
    "OpenClawHomeAssistant", "odysseus", "Agent-Reach",
}

SECRETISH = re.compile(
    r"(TOKEN|SECRET|KEY|PASSWORD|CREDENTIAL|ACCESS|PRIVATE|AUTH|BEARER|SIGNATURE)",
    re.I,
)

# exact names only - see ALLOWLIST in the docstring
ALLOWED = {
    "VITE_SUPABASE_ANON_KEY",
    "VITE_APP_FIREBASE_CONFIG",
    "VITE_APP_PLUS_EXPORT_PUBLIC_KEY",
}

# import.meta.env.VITE_FOO  |  import.meta.env['VITE_FOO']  |  import.meta.env["VITE_FOO"]
READ_PATTERNS = [
    re.compile(r"import\.meta\.env\.(VITE_[A-Za-z0-9_]+)"),
    re.compile(r"import\.meta\.env\[['\"](VITE_[A-Za-z0-9_]+)['\"]\]"),
]

REMEDIATION = (
    "  fix: the value must not reach the browser. Either\n"
    "        (a) move the call behind a server route that holds the secret\n"
    "            (same shape as VITE_LEAD_PROXY_URL + the server-side proxy), or\n"
    "        (b) rename the variable so it does NOT start with VITE_ - Vite only\n"
    "            inlines VITE_-prefixed vars, so a non-VITE_ name can never be\n"
    "            shipped, and the panel degrades to its existing mock/error path."
)


def client_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".matrix-")]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix in CLIENT_EXTS:
                yield p


def scan(root: Path):
    findings = []
    scanned = 0
    for p in client_files(root):
        try:
            text = p.read_text(encoding="utf8", errors="ignore")
        except OSError:
            continue
        scanned += 1
        for lineno, line in enumerate(text.split("\n"), 1):
            for rx in READ_PATTERNS:
                for name in rx.findall(line):
                    if name in ALLOWED:
                        continue
                    if SECRETISH.search(name):
                        findings.append((p, lineno, name))
    return scanned, findings


def main() -> int:
    root = Path(os.environ.get("CLIENT_SECRET_CHECK_ROOT", "/workspace")).resolve()
    if not root.exists():
        print(f"UNCHECKED - root does not exist: {root}")
        return 2

    scanned, findings = scan(root)

    if scanned == 0:
        print(f"UNCHECKED - no client source files found under {root}; nothing was asserted")
        return 2

    if findings:
        print(f"DRIFT - {len(findings)} client-side secret read(s) in {scanned} client file(s)")
        for p, lineno, name in findings:
            try:
                shown = p.relative_to(root)
            except ValueError:
                shown = p
            print(f"  {shown}:{lineno}  {name}")
        print(REMEDIATION)
        return 1

    print(f"CLEAN - {scanned} client file(s) scanned - no secret-named VITE_ variable is reachable from the browser")
    return 0


if __name__ == "__main__":
    sys.exit(main())
