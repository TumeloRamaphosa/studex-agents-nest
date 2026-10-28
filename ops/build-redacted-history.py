#!/usr/bin/env python3
"""Build a REDACTED history of the Studex public repo in an ISOLATED clone.

Why this exists
---------------
`ops/credential-resolution-check.py` says the tracked source is clean, and it is
- in the LOCAL tree. But the PUBLIC remote (`origin/master`) is 636 commits
behind and still serves live credential values across ~42 files, reachable
unauthenticated via raw.githubusercontent.com. Removing a secret from the working
tree does NOT remove it from Git history.

This script:
  1. clones the repo into /tmp (the live /workspace tree is never touched),
  2. rewrites history with git-filter-repo, replacing every credential-shaped
     value with a labelled redaction marker,
  3. RE-VERIFIES the rewritten history: a single batch scan over EVERY object
     in the repo must find zero credential values,
  4. writes a report and leaves the redacted clone ready to push.

It does NOT push. Pushing a rewritten public history needs the owner's
decision (it rewrites every commit id) and a working GitHub PAT.

No credential value is ever printed - only counts, hashes and file names.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

SRC = "/workspace"
WORK = "/tmp/studex-scrub"
REPORT = "/tmp/studex-scrub-report.json"
EXPR = "/tmp/filter-expressions.txt"

# Credential shapes. These are the same families the checker enforces.
PATTERNS = [
    ("AgentMail", r"am_us_[A-Za-z0-9]{30,}"),
    ("Orgo", r"sk_live_[A-Za-z0-9]{20,}"),
    ("ClickUp", r"pk_[0-9]{9}_[A-Za-z0-9]{20,}"),
    ("Blotato", r"blt_[A-Za-z0-9]{20,}"),
    ("Meta", r"EAAS[A-Za-z0-9]{40,}"),
    ("Kimi", r"sk-r[A-Za-z0-9]{30,}"),
    ("FeedHive", r"fh_[0-9a-f]{40,}"),
    ("Tailscale", r"tskey-auth-[A-Za-z0-9-]{20,}"),
    ("Google", r"AIza[A-Za-z0-9_-]{30,}"),
    ("Alibaba", r"LTAI[A-Za-z0-9]{16,}"),
    ("Composio", r"ak_[A-Za-z0-9]{20,}"),
    ("Relace", r"rl_sk_[A-Za-z0-9_]{20,}"),
    ("DashScope", r"sk-ws-[A-Za-z0-9.]+"),
    ("Cloudflare", r"cfat_[A-Za-z0-9]{30,}"),
    ("Pinecone", r"pcsk_[A-Za-z0-9]{30,}"),
    ("Shopify", r"prtapi_[A-Za-z0-9]{20,}"),
    ("NVIDIA", r"nvapi-[A-Za-z0-9]{20,}"),
    ("Hyvare", r"hyrve_ak_[A-Za-z0-9]{30,}"),
    ("Perplexity", r"pplx-[A-Za-z0-9]{20,}"),
    ("ElevenLabs", r"sk_93f8[A-Za-z0-9]{20,}"),
    ("OpenAI", r"sk-proj-[A-Za-z0-9_-]{20,}"),
    ("GitHub", r"gh[pousr]_[A-Za-z0-9]{20,}"),
    ("GitHubFine", r"github_pat_[A-Za-z0-9_]{20,}"),
]
COMBINED = "|".join(p for _, p in PATTERNS)


def run(args, cwd=None, check=True, binary=False):
    r = subprocess.run(args, cwd=cwd, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{args} -> {r.returncode}\n"
                           f"{r.stdout[-2000:].decode('utf-8', 'replace')}\n"
                           f"{r.stderr[-2000:].decode('utf-8', 'replace')}")
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def scan_all_values(cwd):
    """One pass over EVERY object in the repo. Returns {value: {provider,...}}.

    Uses `git cat-file --batch-all-objects --batch` so the whole repo is read
    through a single process. An earlier version spawned one `git cat-file`
    per blob and never finished - a per-object subprocess does not scale to a
    600-commit repo with thousands of blobs.
    """
    p = subprocess.Popen(
        ["git", "cat-file", "--batch-all-objects", "--batch"],
        cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    found = {}
    scanned = 0
    rx = re.compile(COMBINED.encode())
    name_by_pat = {p: n for n, p in PATTERNS}
    pat_order = sorted(PATTERNS, key=lambda kv: -len(kv[1]))

    def classify(raw):
        hits = set()
        for name, pat in pat_order:
            if re.search(pat.encode(), raw.encode("utf-8", "replace")):
                hits.add(name)
        return hits

    while True:
        header = p.stdout.readline()
        if not header:
            break
        parts = header.split()
        if len(parts) < 3:
            continue
        sha1, otype, size = parts[0].decode(), parts[1].decode(), int(parts[2])
        data = p.stdout.read(size)
        p.stdout.read(1)          # trailing newline
        if otype != "blob" or size > 5_000_000:
            continue
        if b"\x00" in data[:2048]:
            continue
        scanned += 1
        for m in rx.finditer(data):
            val = m.group(0).decode("utf-8", "replace")
            names = classify(val)
            found.setdefault(val, set()).update(names or {"unknown"})
    p.stdout.close()
    p.wait()
    return found, scanned


def main():
    if os.path.exists(WORK):
        shutil.rmtree(WORK, ignore_errors=True)
    print("1) cloning into an isolated directory (the live tree is never touched)")
    run(["git", "clone", "--no-hardlinks", "--quiet", SRC, WORK])
    run(["git", "remote", "remove", "origin"], cwd=WORK)

    print("2) scanning EVERY object in the repo (single batch process)")
    found, scanned = scan_all_values(WORK)
    print(f"   text blobs scanned: {scanned}")
    print(f"   distinct credential values present: {len(found)}")
    by_prov = {}
    for v, names in found.items():
        for n in names:
            by_prov[n] = by_prov.get(n, 0) + 1
    if by_prov:
        print("   by provider: " + ", ".join(f"{k}={v}" for k, v in sorted(by_prov.items())))

    if not found:
        print("   nothing to redact - history is already clean")
        json.dump({"values": 0, "work_dir": WORK}, open(REPORT, "w"), indent=2)
        return 0

    # --- build the replace-text file: regex expressions, one per family
    with open(EXPR, "w") as f:
        for name, pat in PATTERNS:
            f.write(f"regex:{pat}==>[REDACTED_{name.upper()}_{sha(pat)}]\n")
    print(f"3) wrote {len(PATTERNS)} replacement expressions -> {EXPR}")

    print("4) rewriting history with git-filter-repo")
    run(["git-filter-repo", "--force", "--replace-text", EXPR,
         "--sensitive-data-removal", "--quiet"], cwd=WORK)

    print("5) RE-VERIFYING the rewritten history (full object scan again)")
    residual, scanned2 = scan_all_values(WORK)
    print(f"   text blobs scanned: {scanned2}")
    print(f"   credential values STILL present anywhere in rewritten history: {len(residual)}")
    for v in list(residual)[:10]:
        print(f"     RESIDUAL {sorted(found.get(v, {'unknown'}))} sha={sha(v)}")

    # also check the tip tree
    tip_hits = run(["git", "grep", "-lI", "-E", COMBINED, "--all"], cwd=WORK, check=False)
    tip_files = [l for l in tip_hits.splitlines() if l.strip()]

    report = {
        "values_redacted": len(found),
        "by_provider": by_prov,
        "value_hashes": {sha(v): sorted(found[v]) for v in found},
        "residual_after_rewrite": len(residual),
        "residual_shas": [sha(v) for v in list(residual)[:20]],
        "files_still_matching": tip_files[:20],
        "work_dir": WORK,
    }
    json.dump(report, open(REPORT, "w"), indent=2)
    print(f"   report -> {REPORT}")
    return 0 if not residual else 1


if __name__ == "__main__":
    sys.exit(main())
