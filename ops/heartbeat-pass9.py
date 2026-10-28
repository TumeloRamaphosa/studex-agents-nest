#!/usr/bin/env python3
"""Heartbeat pass 9 (02:17 UTC) — consolidated, single pass, no polling.

The big thing due: the Friday 09:00 SAST Daily Post fires ~07:00 UTC (~4.7 h).
Per the HEARTBEAT lesson, a publish path must be PRE-FLIGHTED BEFORE its cron
runs, not after - a post that goes wrong at 09:00 is live on the internet.

Checks:
  1. git state + concurrent commits since pass 8
  2. drift
  3. cron fleet
  4. Friday publish pre-flight: queue file, media, validate_brand, per-platform
     skip markers, markdown residue, char limits
  5. what the Friday cron will actually do
  6. badge clock

Usage: python3 ops/heartbeat-pass9.py
"""
import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
os.chdir(ROOT)

print("=" * 76)
print("HEARTBEAT PASS 9 —", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
print("=" * 76)

# ---------------------------------------------------------------- 1. git
print("\n[1] git")
print(subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True).stdout.rstrip())
st = subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout.strip()
print(f"   working tree: {st if st else 'clean'}")

# ---------------------------------------------------------------- 2. drift
print("\n[2] drift")
r = subprocess.run(["python3", "ops/drift-check.py"], capture_output=True, text=True, timeout=300)
for l in r.stdout.splitlines():
    if l.startswith("pages:") or "DRIFT]" in l:
        print("   " + l)

# ---------------------------------------------------------------- 3. cron
print("\n[3] cron fleet")
cj = subprocess.run(["openclaw", "cron", "list", "--json"], capture_output=True, text=True, timeout=120)
jobs = []
try:
    d = json.loads(cj.stdout)
    jobs = d.get("jobs", d if isinstance(d, list) else [])
except Exception:
    pass
en = [j for j in jobs if j.get("enabled")]
fail = [j for j in en if ((j.get("state") or {}).get("consecutiveErrors") or 0) > 0
        or (j.get("state") or {}).get("lastStatus") == "error"]
print(f"   ENABLED JOBS: {len(en)} | FAILING: {len(fail)}")
for j in fail:
    print(f"     !! {j.get('id')} {j.get('name')}")
ciie_on = [j for j in jobs if "ciie" in (j.get("name") or "").lower() and j.get("enabled")]
print(f"   CIIE crons enabled: {len(ciie_on)} (must be 0)")
for j in jobs:
    if j.get("id", "").startswith(("84025fd8", "3816d7b1", "ceo-standup")) or "Daily Post" in (j.get("name") or ""):
        print(f"   * {j.get('id')[:10]} {j.get('name')[:52]}  schedule={j.get('schedule')} enabled={j.get('enabled')}")

# ---------------------------------------------------------------- 4. Friday pre-flight
print("\n[4] FRIDAY 09:00 SAST PUBLISH PRE-FLIGHT")
sys.path.insert(0, "scripts")
import importlib.util
spec = importlib.util.spec_from_file_location("dp", "scripts/daily-post.py")
dp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dp)

DATE = "2026-10-23"
PILLAR = "Agents"
qf = dp.queue_file_for(DATE, PILLAR)
print(f"   queue file: {qf}")
if not qf:
    print("   !! NO QUEUE FILE — the 09:00 cron would have nothing to publish")
else:
    md = pathlib.Path(qf).read_text(encoding="utf8")
    content = dp.extract_content(qf)
    media_url = dp.extract_media_url(qf)
    img = dp.find_image(DATE)
    print(f"   content len: {len(content) if content else 0}")
    print(f"   media url  : {media_url or '(none)'}")
    print(f"   local image: {img}")
    if img and not media_url:
        print("   !! local image exists but no media URL in the queue file")
    if not img:
        print("   !! no local image for the Agents pillar")

    checks = dp.validate_brand(content or "", PILLAR, image_exists=bool(img))
    print(f"   validate_brand(): {checks if checks else 'CLEAN'}")

    texts = dp.build_platform_texts(content or "")
    RES = re.compile(r"\*\*|__|`|^\s*>", re.M)
    for plat, t in texts.items():
        bad = RES.search(t)
        print(f"   {plat:9} len={len(t):5} residue={(bad.group(0) if bad else 'none')!r}"
              f"{'  <-- OVER 500' if plat == 'threads' and len(t) > 500 else ''}")
        if plat == "threads" and len(t) > 500:
            print(f"      !! threads over limit by {len(t)-500} chars")

# ---------------------------------------------------------------- 5. what the Friday cron will do
print("\n[5] Daily Post cron payload + published markers")
for j in jobs:
    nm = (j.get("name") or "")
    if "Daily Post" in nm or j.get("id", "").startswith("3816d7b1"):
        pay = j.get("payload") or {}
        print(f"   job {j.get('id')}  schedule={j.get('schedule')}  tz={j.get('scheduleTz') or j.get('timezone')}")
        msg = pay.get("message") or pay.get("text") or str(pay)[:400]
        print("   payload:")
        for line in str(msg).splitlines()[:22]:
            print(f"     {line[:150]}")

print("\n   published-state marker files:")
for f in sorted(pathlib.Path("memory").glob("published-2026-10-2*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf8"))
        print(f"     {f.name}: {json.dumps(d)[:300]}")
    except Exception as e:
        print(f"     {f.name}: unreadable ({e})")

print("\n   pending/ dir:")
for f in sorted(pathlib.Path("studex-content-automation/posts/pending").glob("*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf8"))
        print(f"     {f.name}: status={d.get('status')} fallback={json.dumps(d.get('fallback', {}))[:200]}")
    except Exception as e:
        print(f"     {f.name}: unreadable ({e})")

# ---------------------------------------------------------------- 6. badge clock
print("\n[6] badge clock")
now = datetime.now(timezone.utc)
dl = datetime(2026, 10, 23, 16, 0, tzinfo=timezone.utc)
h = (dl - now).total_seconds() / 3600
print(f"   CNY 200 · due {dl:%Y-%m-%d %H:%M} UTC (18:00 SAST) · {h:.1f} h left")

print("\n" + "=" * 76)
print("SUMMARY: drift", "OK" if r.returncode == 0 else "DRIFT",
      f"| cron {len(en)}/{len(fail)}",
      "| CIIE crons disabled" if not ciie_on else "| !! CIIE CRON ENABLED")
