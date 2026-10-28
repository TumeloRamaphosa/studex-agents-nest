#!/usr/bin/env python3
"""Verify the cron fixes: run the warmup-daily job, then wait (internally) for
the three manual runs to land, and print their final status."""
import json, os, subprocess, time, datetime

RUNS = "/root/.openclaw/cron/runs"
JOBS = [
    ("ae77d9f3-5453-4bbb-b57b-206903a8e66d.jsonl", "Warmup Daily (30 errs)"),
    ("84025fd8-008d-440f-990a-cfea746856c9.jsonl", "Daily Content (70 errs)"),
    ("5a506b8d-343f-49b8-968e-be08fe85bac9.jsonl", "Evening Standup (2 errs)"),
    ("5b01a76b-0d02-484e-ac91-0cef98ad967a.jsonl", "Warmup Build Hour (323 errs)"),
]


def latest(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        return None
    return max(rows, key=lambda r: r.get("ts", 0))


def stamp(ms):
    return datetime.datetime.utcfromtimestamp(ms / 1000).strftime("%H:%M:%S")


# Baseline: record the newest ts we already have for each job.
before = {}
for f, _ in JOBS:
    p = os.path.join(RUNS, f)
    r = latest(p) if os.path.exists(p) else None
    before[f] = r.get("ts", 0) if r else 0

# Trigger the warmup-daily job (the one that had delivery.mode changed to none).
subprocess.run(["openclaw", "cron", "run",
                "ae77d9f3-5453-4bbb-b57b-206903a8e66d"],
               cwd="/workspace", capture_output=True, timeout=120)

# Wait internally for all four to produce a NEWER record. Single bounded wait.
deadline = time.time() + 540
done = set()
while time.time() < deadline and len(done) < len(JOBS):
    for f, _ in JOBS:
        if f in done:
            continue
        p = os.path.join(RUNS, f)
        if not os.path.exists(p):
            continue
        r = latest(p)
        if r and r.get("ts", 0) > before[f]:
            done.add(f)
    if len(done) < len(JOBS):
        time.sleep(15)

print("=== FINAL STATUS ===")
for f, label in JOBS:
    p = os.path.join(RUNS, f)
    r = latest(p) if os.path.exists(p) else None
    if not r:
        print(f"{label:32s} NO RUN RECORD")
        continue
    fresh = "NEW " if r.get("ts", 0) > before[f] else "old "
    print(f"{fresh}{label:28s} {stamp(r.get('ts', 0))} status={r.get('status')} "
          f"dur={r.get('durationMs')} delivery={r.get('deliveryStatus')} "
          f"err={str(r.get('error'))[:55]}")
