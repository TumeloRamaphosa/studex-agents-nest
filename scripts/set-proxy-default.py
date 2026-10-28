#!/usr/bin/env python3
"""Set the lead-proxy URL as a source-level default in every landing page.

The proxy URL is PUBLIC - it is a public endpoint on workers.dev. It is not a
secret, so it belongs in source where it cannot be lost by a missing env file.
The credential stays in the Worker secret, server-side.
"""
import io

PROXY = "https://studex-lead-proxy.tumelor001.workers.dev"

FILES = [
    "ciie-coffee-landing/src/App.tsx",
    "china-coffee-lead-capture/src/App.tsx",
    "studex-caviar/src/App.tsx",
    "studex-corporate-gifting/src/App.tsx",
    "coffee-noir-landing/src/App.tsx",
]

ROOT = "/workspace/"

for rel in FILES:
    p = ROOT + rel
    s = io.open(p, encoding="utf-8").read()
    if "VITE_LEAD_PROXY_URL" not in s:
        print("  SKIP (no proxy ref):", rel)
        continue
    old = "'/api/lead'"
    new = "'" + PROXY + "'"
    if old in s:
        s = s.replace(old, new)
        io.open(p, "w", encoding="utf-8").write(s)
        print("  set (single quotes):", rel)
        continue
    old = '"/api/lead"'
    new = '"' + PROXY + '"'
    if old in s:
        s = s.replace(old, new)
        io.open(p, "w", encoding="utf-8").write(s)
        print("  set (double quotes):", rel)
        continue
    print("  ANCHOR MISS:", rel)
