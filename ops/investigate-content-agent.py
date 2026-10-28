#!/usr/bin/env python3
"""Investigate the content agent's blockers:
1. Does a Facebook Page token work (TOOLS.md lists one)?
2. What are the EXACT product names/prices on the retail source page?
3. Has this agent ever posted?
"""
import json, os, subprocess, re

print("=== 1. FB_PAGE_TOKEN availability ===")
for f in ("/root/.env", "/workspace/.env", "/workspace/studex-content-automation/.env"):
    if os.path.exists(f):
        keys = []
        for line in open(f):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                keys.append(line.split("=", 1)[0].strip())
        print(f"  {f}: {keys}")
    else:
        print(f"  {f}: (missing)")

PAGE_TOKEN = os.environ.get("META_PAGE_TOKEN", "")
PAGE_ID = "108934711902801"
print("=== test TOOLS.md Facebook Page token ===")
r = subprocess.run(["curl", "-s", "--max-time", "30",
                    f"https://graph.facebook.com/v18.0/{PAGE_ID}?fields=id,name,fan_count&access_token={PAGE_TOKEN}"],
                   capture_output=True, text=True, timeout=45)
print("  ", r.stdout[:300].replace("\n", " "))

print("=== 2. exact retail product names + prices from the source of truth ===")
src = open("/workspace/studex-biltong/index.html").read()
print("  file len", len(src))
for pat in ("Wagyu Biltong Gold", "Luxury Wagyu", "Fire & Feast", "StudBot Rise",
            "Oscietra", "Kaluga", "Sevtruga", "Coffee", "Experience Box", "Game"):
    hits = sorted(set(re.findall(r"[^<>\"\n]{0,60}" + re.escape(pat) + r"[^<>\"\n]{0,80}", src)))
    for h in hits[:3]:
        print(f"  [{pat}] {h.strip()[:150]}")
    if not hits:
        print(f"  [{pat}] -- NOT FOUND")

print("=== 3. has the content agent ever posted? ===")
p = "/workspace/studex-content-automation/posts/log.json"
if os.path.exists(p):
    print("  ", open(p).read()[:500])
else:
    print("   no posts/log.json")
