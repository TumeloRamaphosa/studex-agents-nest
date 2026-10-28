#!/usr/bin/env python3
"""Consolidated heartbeat check: health probes, drift, cron fleet state."""
import json, subprocess, datetime, os

print("=== TIME ===", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))

# --- health probes ---
print("=== HEALTH PROBES ===")
for name, cmd in [
    ("hub gitea :3000", "curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://100.95.66.29:3000/api/health"),
    ("registry :3778",  "curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://100.95.66.29:3778/health"),
    ("alibaba ssh",     "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o PasswordAuthentication=no root@47.236.124.79 'echo ALI_OK' 2>&1 | tail -1"),
]:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    out = (r.stdout or r.stderr).strip().replace("\n", " ")[:60]
    ok = out not in ("", "000")
    print(f"  {name:22} {'OK ' if ok else 'FAIL'} {out}")

# --- drift ---
print("=== DRIFT ===")
r = subprocess.run(["python3", "/workspace/ops/drift-check.py"], capture_output=True, text=True, timeout=600)
for ln in r.stdout.splitlines():
    if any(k in ln for k in ("asset copy", "pages:", "DRIFT", "NO ASSERTIONS")):
        print("  " + ln)
print("  DRIFT_EXIT=", r.returncode)

# --- cron fleet ---
print("=== CRON FLEET ===")
jf = "/root/.openclaw/cron/jobs.json"
jobs = json.load(open(jf))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
bad_channel, toosmall = [], []
for b in jobs:
    if not b.get("enabled"):
        continue
    d = b.get("delivery") or {}
    p = b.get("payload", {})
    if d.get("mode") == "announce" and not d.get("channel"):
        bad_channel.append(b.get("name"))
    to = p.get("timeoutSeconds")
    if to is not None and to < 300:
        toosmall.append((b.get("name"), to))
print("  announce jobs missing channel:", bad_channel or "NONE")
print("  jobs with timeout < 300s:", toosmall or "NONE")

# recent run status per enabled job
runs = "/root/.openclaw/cron/runs"
for b in jobs:
    if not b.get("enabled"):
        continue
    p = os.path.join(runs, b["id"] + ".jsonl")
    if not os.path.exists(p):
        continue
    rows = []
    for line in open(p):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    if not rows:
        continue
    rows.sort(key=lambda x: x.get("ts", 0))
    last = rows[-1]
    st = b.get("state", {}) or {}
    ce = st.get("consecutiveErrors", 0)
    ts = datetime.datetime.utcfromtimestamp(last.get("ts", 0) / 1000).strftime("%m-%d %H:%M")
    flag = ""
    if last.get("status") == "ok":
        flag = "GREEN"
    elif ce:
        flag = f"err x{ce}"
    print("  %-38s %s %-5s %-6s %s" % (
        b.get("name", "?")[:38], ts, last.get("status"),
        str(last.get("durationMs"))[:6], flag))
