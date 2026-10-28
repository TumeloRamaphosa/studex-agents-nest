#!/usr/bin/env python3
"""Close the last open question: did the scanner print a LIVE credential into
the gateway log, and is the live Blotato key in any doc that feeds my context?

FACTS ESTABLISHED (do not re-derive):
  * ops/measure-cred-shapes.py scans ONLY `git ls-files` output.
  * It printed matched values verbatim, into stdout, which the gateway
    captures into /tmp/openclaw/openclaw-2026-10-23.log.
  * That log holds 39 runs of the scanner.
  * The live Blotato key (48 chars) WAS in tracked source until commit
    0aa93b09 removed it - i.e. DURING the window when the scanner ran.
    So the scanner very likely printed it into the log.

So this does two things:
  1. For every live credential in .env, search the gateway logs for its
     literal. If present, mask it IN PLACE with a same-length mask
     (byte offsets never shift, the inode is never replaced, so the
     gateway's fd and append position stay valid - the technique proven
     on the AgentMail keys earlier tonight).
  2. Redact the live Blotato literal out of the two DOC files that carry
     it. Both are untracked so they are not published, but TOOLS.md is
     injected into my own context every session - a literal there can be
     quoted onward by accident. The docs get a pointer to .env instead,
     which is where the value actually lives.

No credential value is ever printed.
"""
import pathlib
import re
import subprocess

# The canonical credential-name filter lives in ONE place so these tools
# cannot drift apart. See ops/cred_name_filter.py for why a copy-pasted
# regex in nine files was a real security bug.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_cred_name_filter", "/workspace/ops/cred_name_filter.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

WS = pathlib.Path("/workspace")
LOGS = [pathlib.Path("/tmp/openclaw/openclaw-2026-10-23.log"),
        pathlib.Path("/tmp/openclaw/openclaw-2026-10-24.log")]
DOCS = [WS / "TOOLS.md", WS / "TOOLS_SUPPLEMENT.md"]
MASK = b"REDACTED_CREDENTIAL"

CRED_NAME_RE = _mod.CRED_NAME_RE


def env_creds():
    out = {}
    env = WS / ".env"
    if not env.exists():
        return out
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= 16 and CRED_NAME_RE.match(k.strip()):
            out[k.strip()] = v
    return out


def mask_in_place(path, needle):
    """Overwrite every occurrence in place with a same-length mask."""
    data = path.read_bytes()
    occurrences = []
    start = 0
    while True:
        i = data.find(needle, start)
        if i < 0:
            break
        occurrences.append(i)
        start = i + 1
    if not occurrences:
        return 0
    size_before = path.stat().st_size
    ino_before = path.stat().st_ino
    with open(path, "r+b") as fh:
        for i in occurrences:
            fh.seek(i)
            fh.write((MASK + b"_" * len(needle))[:len(needle)])
        fh.flush()
    size_after = path.stat().st_size
    ino_after = path.stat().st_ino
    print(f"    {path.name}: masked {len(occurrences)} occurrence(s); "
          f"size {size_before}->{size_after} (same: {size_before == size_after}); "
          f"inode same: {ino_before == ino_after}")
    return len(occurrences)


def main():
    creds = env_creds()
    print(f"live credentials in .env: {len(creds)}")
    print()
    print("=== 1. LIVE CREDENTIALS IN THE GATEWAY LOG ===")
    total = 0
    for log in LOGS:
        if not log.exists():
            continue
        data = log.read_bytes()
        for name, val in sorted(creds.items()):
            n = data.count(val.encode())
            if n:
                print(f"  {log.name}: {name} present {n}x  -> MASKING")
                total += mask_in_place(log, val.encode())
    if total == 0:
        print("  no live credential literal found in the gateway logs")
    print()

    print("=== 2. LIVE CREDENTIALS IN THE DOC FILES ===")
    for doc in DOCS:
        if not doc.exists():
            continue
        data = doc.read_bytes()
        for name, val in sorted(creds.items()):
            n = data.count(val.encode())
            if n:
                print(f"  {doc.name}: {name} present {n}x  -> REDACTING")
                mask_in_place(doc, val.encode())
    print()

    print("=== 3. VERIFY ===")
    ok = True
    for log in LOGS:
        if not log.exists():
            continue
        data = log.read_bytes()
        for name, val in creds.items():
            if val.encode() in data:
                print(f"  !! {log.name} still contains {name}")
                ok = False
    for doc in DOCS:
        if not doc.exists():
            continue
        data = doc.read_bytes()
        for name, val in creds.items():
            if val.encode() in data:
                print(f"  !! {doc.name} still contains {name}")
                ok = False
    print("  no live credential literal remains in the logs or the docs"
          if ok else "  SOMETHING STILL REMAINS")

    print()
    print("=== 4. TRACKED-FILE SAFETY (the published surface) ===")
    files = subprocess.run(["git", "ls-files"], cwd=WS,
                           capture_output=True, text=True).stdout.splitlines()
    carriers = []
    for rel in files:
        p = WS / rel
        try:
            if p.stat().st_size > 5_000_000:
                continue
            t = p.read_text(errors="ignore")
        except OSError:
            continue
        for name, val in creds.items():
            if val in t:
                carriers.append((rel, name))
    if carriers:
        for rel, name in carriers:
            print(f"  !! {rel} contains the live {name}")
    else:
        print(f"  none of the {len(files)} tracked files contains a live credential")


if __name__ == "__main__":
    main()
