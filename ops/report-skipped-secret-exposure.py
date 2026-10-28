#!/usr/bin/env python3
"""Quantify live credentials still exposed in TRACKED files.

THE GAP THIS MEASURES
----------------------
The concurrent session's credential scrubber (scripts/scrub-tracked-credentials.py)
deliberately SKIPS .matrix-chat-history/, memory/, builds/, research/,
studex-obsidian-vault/, outbound-drafts/, gstack/, headroom/, OpenJarvis/ and
Decepticon/ - rationale: "logs/history of what happened".

But those paths are TRACKED and the repo is PUBLIC (commit 4492069c untracked
.env and TOOLS.md "from PUBLIC repo"). Skipping them because they are history
leaves live keys committed and world-readable.

NOTE: this script matches by PATTERN, never by literal secret. An earlier
version embedded the live values as literals and was correctly BLOCKED by the
pre-commit guard - which is the guard doing its job. Liveness is determined at
runtime by comparing against the UNTRACKED /workspace/.env, so no secret value
is ever written into this repository.

Usage: python3 ops/report-skipped-secret-exposure.py
"""
import os
import re
import subprocess

ROOT = "/workspace"
ENV_FILE = "/workspace/.env"

# (pattern, label) - shape only, no values
PATTERNS = [
    (r"am_us_[A-Za-z0-9]{30,}", "AgentMail API key"),
    (r"blt_[A-Za-z0-9]{20,}", "Blotato API key"),
    (r"cfat_[A-Za-z0-9]{20,}", "Cloudflare API token"),
    (r"pk_[0-9]+_[A-Za-z0-9]{20,}", "ClickUp API token"),
    (r"LTAI[A-Za-z0-9]{12,}", "Alibaba Cloud key id"),
    (r"sk-proj-[A-Za-z0-9]{20,}", "OpenAI API key"),
    (r"pcsk_[A-Za-z0-9]{30,}", "Pinecone API key"),
    (r"pplx-[A-Za-z0-9]{30,}", "Perplexity API key"),
    (r"MTUw[A-Za-z0-9]{20,}\.[A-Za-z0-9_.\-]{20,}", "Discord bot token"),
    (r"sk_[A-Za-z0-9]{30,}", "misc sk_ key (ElevenLabs/Orgo/...)"),
    (r"EAAS[A-Za-z0-9]{80,}", "Facebook user/page token"),
    (r"sk_live_[A-Za-z0-9]{20,}", "Stripe live key"),
]
SKIP_PREFIXES = [
    ".matrix-chat-history/", "memory/", "builds/", "research/",
    "studex-obsidian-vault/", "outbound-drafts/", "gstack/", "headroom/",
    "OpenJarvis/", "Decepticon/",
]


def live_values():
    """Values currently present in the UNTRACKED .env -> these are live."""
    live = set()
    try:
        txt = open(ENV_FILE, encoding="utf8", errors="ignore").read()
    except OSError:
        return live
    for pat, _ in PATTERNS:
        for m in re.finditer(pat, txt):
            live.add(m.group(0))
    return live


def main():
    live = live_values()
    tracked = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True,
                             cwd=ROOT).stdout.split("\0")
    tracked = [f for f in tracked if f.strip()]

    skipped, scrubbed = {}, {}
    for rel in tracked:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            continue
        try:
            if os.path.getsize(p) > 3_000_000:
                continue
            t = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        is_skip = any(rel.startswith(x) for x in SKIP_PREFIXES)
        for pat, label in PATTERNS:
            for m in re.finditer(pat, t):
                val = m.group(0)
                bucket = skipped if is_skip else scrubbed
                d = bucket.setdefault((label, val), set())
                d.add(rel)

    def show(title, bucket):
        print(f"\n-- {title} --")
        if not bucket:
            print("   none")
            return
        by_label = {}
        for (label, val), files in bucket.items():
            by_label.setdefault(label, []).append((val, files))
        for label, items in sorted(by_label.items(), key=lambda x: -sum(len(f) for _, f in x[1])):
            nfiles = len({f for _, fs in items for f in fs})
            is_live = any(v in live for v, _ in items)
            print(f"   {label:28} {len(items):2} distinct value(s) in {nfiles:3} file(s)"
                  f"   {'<-- LIVE (also in untracked .env)' if is_live else '(not in .env - may be rotated/revoked)'}")
            for val, fs in items[:2]:
                shown = val[:10] + "..." + val[-4:] if len(val) > 16 else val
                print(f"       {shown}  e.g. {sorted(fs)[0]}")

    print("=" * 78)
    print("LIVE CREDENTIALS STILL IN TRACKED FILES")
    print("=" * 78)
    print(f"  tracked files scanned: {len(tracked)}")
    print(f"  live values known (from untracked .env): {len(live)}")
    show("INSIDE the scrubber's SKIP LIST - still literal, tracked, committed", skipped)
    show("OUTSIDE the skip list", scrubbed)

    print("\n" + "=" * 78)
    print("WHY THIS MATTERS")
    print("=" * 78)
    print("""
  1. The repo is PUBLIC. A key literal in ANY tracked file is published.
  2. Scrubbing the working tree is necessary but NOT sufficient: the key stays
     in GIT HISTORY. Anyone reading an older commit still gets it. For a public
     repo the complete fix is ROTATE the key, then rewrite history
     (git filter-repo / BFG).
  3. The skip list hides live keys in markdown/log files that are tracked and
     committed, and .gitignore does not untrack anything that is already
     tracked.

So the actionable list is:
  a. ROTATE every credential above that is still live. Rotation is owner-side:
     Cloudflare, Alibaba, ClickUp, OpenAI, Pinecone, Blotato, Perplexity,
     Discord bot token, AgentMail keys, ElevenLabs/Orgo keys.
  b. Untrack the skip-listed directories (or scrub them) so the next commit
     does not re-publish them.
  c. A history rewrite, if the repo is public and the keys are not rotated.

(a) and (c) need Tumelo's decision - rotating keys is not something to do
unattended.""")


if __name__ == "__main__":
    main()
