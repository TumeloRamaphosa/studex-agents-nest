#!/usr/bin/env python3
"""Round 2: the delivery fix worked (channel error gone); what remains is the
300s agent-turn timeout. Raise the enabled announce jobs to 900s, trigger a
fresh run of the worst offender, and report the final status."""
import json, os, subprocess, time, datetime

RUNS = "/root/.openclaw/cron/runs"
JOBS_FILE = "/root/.openclaw/cron/jobs.json"
OPS_CHANNEL = "channel:1538825048465481728"

TARGETS = [
    ("5ffb50d9-a1b0-4998-85d5-26164796d340", "Morning Nudge"),
    ("e48bae9c-2adc-4ed0-9d06-60f142230aa5", "Midday Nudge"),
    ("5a506b8d-343f-49b8-968e-be08fe85bac9", "Evening Standup"),
    ("5d6729b7-8ad0-4ba3-99c8-b48ddeac49aa", "Vault Sync Post-Meeting"),
    ("4eba3bce-4551-4f02-8a03-fbbafa7084b0", "Vault Sync EOD"),
    ("84025fd8-008d-440f-990a-cfea746856c9", "Daily Content Agent"),
    ("3816d7b1-608a-4503-8e62-429a6b4fa689", "Studex Daily Post"),
    ("ceo-standup-1700", "CEO Standup 17:00"),
    ("ceo-standup-2200", "CEO Standup 22:00"),
    ("ae77d9f3-5453-4bbb-b57b-206903a8e66d", "Warmup Daily"),
]

print("=== raising timeouts to 900s ===")
for jid, name in TARGETS:
    args = ["openclaw", "cron", "edit", jid, "--timeout-seconds", "900"]
    if jid == "ae77d9f3-5453-4bbb-b57b-206903a8e66d":
        args += ["--no-deliver"]
    else:
        args += ["--channel", "discord", "--to", OPS_CHANNEL]
    r = subprocess.run(args, cwd="/workspace", capture_output=True, timeout=180)
    ok = r.returncode == 0
    print(f"  {'ok ' if ok else 'FAIL'} {name}")

# Confirm what actually landed on disk.
jobs = json.load(open(JOBS_FILE))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
print("=== persisted config ===")
for b in jobs:
    if b.get("id") in {j for j, _ in TARGETS}:
        d = b.get("delivery") or {}
        print("  %-24s timeout=%-5s channel=%-8s mode=%s" % (
            b.get("name", "?")[:24],
            b.get("payload", {}).get("timeoutSeconds"),
            d.get("channel") or "-", d.get("mode")))

CHECK = [
    ("ae77d9f3-5453-4bbb-b57b-206903a8e66d.jsonl", "Warmup Daily"),
    ("84025fd8-008d-440f-990a-cfea746856c9.jsonl", "Daily Content Agent"),
]


def latest(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return max(rows, key=lambda r: r.get("ts", 0)) if rows else None


before = {}
for f, _ in CHECK:
    p = os.path.join(RUNS, f)
    r = latest(p) if os.path.exists(p) else None
    before[f] = r.get("ts", 0) if r else 0

for jid, _ in CHECK:
    subprocess.run(["openclaw", "cron", "run", jid], cwd="/workspace",
                   capture_output=True, timeout=120)

deadline = time.time() + 900
done = set()
while time.time() < deadline and len(done) < len(CHECK):
    for f, _ in CHECK:
        if f in done:
            continue
        p = os.path.join(RUNS, f)
        if not os.path.exists(p):
            continue
        r = latest(p)
        if r and r.get("ts", 0) > before[f]:
            done.add(f)
    if len(done) < len(CHECK):
        time.sleep(20)

print("=== FINAL ===")
for f, label in CHECK:
    p = os.path.join(RUNS, f)
    r = latest(p) if os.path.exists(p) else None
    if not r:
        print(f"  {label}: no record")
        continue
    fresh = "NEW " if r.get("ts", 0) > before[f] else "old "
    print("  %s%-22s %s status=%-6s dur=%-7s delivery=%-13s err=%s" % (
        fresh, label,
        datetime.datetime.utcfromtimestamp(r.get("ts", 0) / 1000).strftime("%H:%M:%S"),
        r.get("status"), r.get("durationMs"), r.get("deliveryStatus"),
        str(r.get("error"))[:60]))
