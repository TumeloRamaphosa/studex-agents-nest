#!/usr/bin/env python3
"""Inspect the two content-related cron jobs and any other Facebook poster."""
import json, os, re

jobs = json.load(open("/root/.openclaw/cron/jobs.json"))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
print("=== content-related cron payloads ===")
for b in jobs:
    jid = b.get("id", "")
    if jid.startswith(("84025fd8", "3816d7b1")):
        p = b.get("payload", {})
        print(f"\n--- {b.get('name')} [{jid}]")
        print("  sched:", b.get("schedule", {}).get("expr"), b.get("schedule", {}).get("tz"))
        print("  timeout:", p.get("timeoutSeconds"))
        print("  message:", repr(p.get("message"))[:900])

print("\n=== other facebook posters in /workspace ===")
for root, dirs, files in os.walk("/workspace"):
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "dist", ".next",
                                            "build", "OBLITERATUS", "Decepticon",
                                            ".matrix-chat-history")]
    for f in files:
        if not f.endswith((".js", ".ts", ".mjs", ".cjs", ".py")):
            continue
        p = os.path.join(root, f)
        try:
            t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if "graph.facebook.com" in t:
            print("  ", p.replace("/workspace/", ""))

print("\n=== image_prompt usage ===")
for root, dirs, files in os.walk("/workspace/studex-content-automation"):
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
    for f in files:
        if f.endswith((".js", ".ts")):
            p = os.path.join(root, f)
            t = open(p, encoding="utf-8", errors="ignore").read()
            if "image_prompt" in t:
                print("  ", p.replace("/workspace/", ""))
