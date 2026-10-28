#!/usr/bin/env python3
import os, glob, json, time, subprocess

now = time.time()
cutoff = now - 3*24*3600

print("=== content-queue-ish files modified in last 3 days ===")
pats = ["/workspace/memory/**/*", "/workspace/outbound-drafts/**/*", "/workspace/drafts/**/*",
        "/workspace/content/**/*", "/workspace/studex-naledi-content/**/*",
        "/workspace/studex-content-pipeline/**/*", "/workspace/studex-content-os/**/*"]
for pat in pats:
    for p in glob.glob(pat, recursive=True):
        if os.path.isdir(p): continue
        try: m = os.path.getmtime(p)
        except: continue
        if m > cutoff:
            print(time.strftime("%Y-%m-%d %H:%M", time.gmtime(m)), p)

print("\n=== approval-ish files anywhere (names) ===")
for p in glob.glob("/workspace/**/*", recursive=True):
    if "/node_modules/" in p or "/.git/" in p: continue
    b = os.path.basename(p).lower()
    if any(k in b for k in ["approv","pending-","queue","awaiting","draft"]) and os.path.isfile(p):
        try: m = os.path.getmtime(p)
        except: continue
        if m > cutoff:
            print(time.strftime("%Y-%m-%d %H:%M", time.gmtime(m)), p)
