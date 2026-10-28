#!/usr/bin/env python3
"""Answer two questions about the FEEDHIVE leak, in-process, printing no values.

Q1: Does /tmp/TOOLS.bak still exist, and does it still hold credential-shaped
    values? (It was the source of the value that got logged on 2026-10-24.)
Q2: Does any WORKSPACE script still print a credential VALUE to stdout?

Scanning is done with python (not `grep` over the whole tree) so it completes
fast, and values are never printed - only names and counts.
"""
import os
import re
import sys

VALUE_SHAPES = [
    ("fh_[A-Za-z0-9]{16,}", "FeedHive"),
    ("am_us_[A-Za-z0-9]{16,}", "AgentMail"),
    ("sk_live_[A-Za-z0-9]{16,}", "Stripe/live"),
    ("sk-r[A-Za-z0-9]{24,}", "OpenAI-style"),
    ("EAAS[A-Za-z0-9]{40,}", "Meta/Facebook"),
    ("pk_[0-9]{6,}_[A-Za-z0-9]{20,}", "ClickUp"),
    ("blt_[A-Za-z0-9]{20,}", "Blotato"),
    ("sk-ws-[A-Za-z0-9._-]{20,}", "Alibaba MAAS"),
]


def scan_file(path):
    try:
        txt = open(path, errors="replace").read()
    except Exception:
        return []
    out = []
    for pat, name in VALUE_SHAPES:
        n = len(re.findall(pat, txt))
        if n:
            out.append((name, n))
    return out


def q1():
    print("=== Q1: /tmp/TOOLS.bak ===")
    for p in ("/tmp/TOOLS.bak", "/tmp/TOOLS.bak.txt"):
        if os.path.exists(p):
            st = os.stat(p)
            print("  EXISTS %s size=%d" % (p, st.st_size))
            hits = scan_file(p)
            print("  credential-shaped values found:", hits if hits else "none")
            if hits:
                print("  -> this file is still a live credential surface")
        else:
            print("  absent: %s" % p)


def q2():
    print()
    print("=== Q2: workspace scripts that could print a credential value ===")
    roots = ["/workspace/ops", "/workspace/scripts", "/workspace/studex-email-warmup",
             "/workspace/discord-ops-bot", "/workspace/studex-content-automation",
             "/workspace/skills"]
    pats = [re.compile(p) for p, _ in VALUE_SHAPES]
    risky = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "node_modules", "__pycache__", ".venv")]
            for fn in filenames:
                if not fn.endswith((".py", ".js", ".ts", ".sh")):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    txt = open(p, errors="replace").read()
                except Exception:
                    continue
                for pat, name in VALUE_SHAPES:
                    for m in re.finditer(pat, txt):
                        ln = txt.count("\n", 0, m.start()) + 1
                        src = txt.splitlines()[ln - 1].strip()
                        prints = bool(re.search(r"print\(|echo |console\.log", src))
                        risky.append((p, ln, name, prints))
    if not risky:
        print("  no hardcoded credential-shaped literal in these trees")
    for p, ln, name, prints in risky[:25]:
        print("  %s L%d [%s]%s" % (p, ln, name, "  <-- PRINTS A VALUE" if prints else ""))
    print("  total hardcoded literals:", len(risky))


if __name__ == "__main__":
    q1()
    q2()
    sys.exit(0)
