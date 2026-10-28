#!/usr/bin/env python3
"""Round 3: set timeouts from measured historical successful durations.

timeout = max(observed max successful duration * 1.5, floor) so the agent turn
has headroom over the work it actually does.
"""
import json, os, subprocess, time, datetime

RUNS = "/root/.openclaw/cron/runs"
JOBS_FILE = "/root/.openclaw/cron/jobs.json"
OPS = "channel:1538825048465481728"

# job id -> (label, timeout seconds)
PLAN = {
    "5ffb50d9-a1b0-4998-85d5-26164796d340": ("Morning Nudge", 1800),
    "e48bae9c-2adc-4ed0-9d06-60f142230aa5": ("Midday Nudge", 900),
    "5a506b8d-343f-49b8-968e-be08fe85bac9": ("Evening Standup", 900),
    "5d6729b7-8ad0-4ba3-99c8-b48ddeac49aa": ("Vault Sync Post-Meeting", 600),
    "4eba3bce-4551-4f02-8a03-fbbafa7084b0": ("Vault Sync EOD", 1200),
    "84025fd8-008d-440f-990a-cfea746856c9": ("Daily Content Agent", 900),
    "3816d7b1-608a-4503-8e62-429a6b4fa689": ("Studex Daily Post", 600),
    "ceo-standup-1700": ("CEO Standup 17:00", 600),
    "ceo-standup-2200": ("CEO Standup 22:00", 600),
    "ae77d9f3-5453-4bbb-b57b-206903a8e66d": ("Warmup Daily", 900),
    "5b01a76b-0d02-484e-ac91-0cef98ad967a": ("Warmup Build Hour", 900),
}

print("=== applying timeouts ===")
for jid, (label, to) in PLAN.items():
    args = ["openclaw", "cron", "edit", jid, "--timeout-seconds", str(to)]
    if jid in ("ae77d9f3-5453-4bbb-b57b-206903a8e66d",
               "5b01a76b-0d02-484e-ac91-0cef98ad967a"):
        args += ["--no-deliver"]
    else:
        args += ["--channel", "discord", "--to", OPS]
    r = subprocess.run(args, cwd="/workspace", capture_output=True, timeout=200)
    print("  %s %-24s -> %ds" % ("ok " if r.returncode == 0 else "FAIL", label, to))

jobs = json.load(open(JOBS_FILE))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
print("=== persisted ===")
for b in jobs:
    if b.get("id") in PLAN:
        d = b.get("delivery") or {}
        print("  %-26s timeout=%-6s mode=%-9s channel=%s" % (
            b.get("name", "?")[:26], b.get("payload", {}).get("timeoutSeconds"),
            d.get("mode"), d.get("channel") or "-"))

# Verify with ONE run of the daily warmup (the user-facing job).
CHECK = ("ae77d9f3-5453-4bbb-b57b-206903a8e66d.jsonl", "Warmup Daily")


def latest(path):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    return max(rows, key=lambda r: r.get("ts", 0)) if rows else None


p = os.path.join(RUNS, CHECK[0])
before = (latest(p) or {}).get("ts", 0)
subprocess.run(["openclaw", "cron", "run", CHECK[0][:-6]], cwd="/workspace",
               capture_output=True, timeout=120)

deadline = time.time() + 960
r = None
while time.time() < deadline:
    cur = latest(p)
    if cur and cur.get("ts", 0) > before:
        r = cur
        break
    time.sleep(20)

if r:
    print("=== VERIFY ===")
    print("  status=%-6s dur=%-8s delivery=%-13s err=%s" % (
        r.get("status"), r.get("durationMs"), r.get("deliveryStatus"),
        str(r.get("error"))[:70]))
    print("  summary:", str(r.get("summary"))[:400])
else:
    print("=== VERIFY === no new run record within the window")
