#!/usr/bin/env python3
"""Final cron pass: give the two warmup jobs a 3600s ceiling (matching the
Build Hour / Research Hour jobs, whose measured max successful duration is
2.9M ms) and confirm the persisted config for every enabled job."""
import json, subprocess

JOBS_FILE = "/root/.openclaw/cron/jobs.json"
OPS = "channel:1538825048465481728"

WARMUP = {
    "ae77d9f3-5453-4bbb-b57b-206903a8e66d": "Studex Email Warmup — Daily",
    "5b01a76b-0d02-484e-ac91-0cef98ad967a": "Studex Email Warmup — Build Hour Cycle",
}

print("=== set 3600s ceiling on the warmup jobs ===")
for jid, name in WARMUP.items():
    r = subprocess.run(["openclaw", "cron", "edit", jid, "--timeout-seconds",
                        "3600", "--no-deliver"],
                       cwd="/workspace", capture_output=True, timeout=240)
    print(f"  {'ok ' if r.returncode == 0 else 'FAIL'} {name}")

jobs = json.load(open(JOBS_FILE))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
print("=== final persisted state (enabled jobs) ===")
problems = []
for b in jobs:
    if not b.get("enabled"):
        continue
    d = b.get("delivery") or {}
    p = b.get("payload", {})
    mode = d.get("mode")
    ch = d.get("channel")
    to = p.get("timeoutSeconds")
    if mode == "announce" and not ch:
        problems.append(b.get("name"))
    print("  %-38s timeout=%-6s mode=%-9s channel=%s" % (
        b.get("name", "?")[:38], to, mode, ch or "-"))
print("=== announce jobs still missing a channel:", problems or "NONE")
