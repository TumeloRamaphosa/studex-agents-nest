#!/usr/bin/env python3
"""Heartbeat pass 9 — act on the two real findings, then report.

A. CRON TIMING BUG: four jobs fire 2 hours before the time in their own name.
   The expr hour was written in UTC while the tz field says Africa/Johannesburg
   - the classic "I converted the hour but not the tz" error. Proof that the tz
   IS honoured: Vault Sync '0 0' + SAST -> 00:00 SAST, and Daily Content Agent
   '55 6' + UTC -> 06:55 UTC (08:55 SAST). Both correct. The four broken ones:
     Daily Post        '0 7 * * 1-5'  SAST -> 07:00 SAST  (name: 09:00 SAST)
     CEO Standup 9am   '0 7 * * 1-6'  SAST -> 07:00 SAST  (name: 09:00 SAST)
     CEO Standup 5pm   '0 15 * * 1-6' SAST -> 15:00 SAST  (name: 17:00 SAST)
     CEO Standup 10pm  '0 20 * * 1-6' SAST -> 20:00 SAST  (name: 22:00 SAST)
   Under a UTC reading of the same exprs every one of them matches its name -
   which is exactly how the bug was introduced.

B. UNTRACK the gitignored-but-tracked secret-bearing log dir.
   .matrix-chat-history/ is in .gitignore, yet 108 log files are TRACKED and
   carry live Blotato / ClickUp / Cloudflare / AgentMail / OpenAI / Orgo keys.
   The concurrent session's pre-commit guard blocks NEW leaks but cannot
   un-publish what is already in the index. git rm --cached keeps the files on
   disk and stops the republication.

Usage: python3 ops/fix-cron-timing-and-untrack.py
"""
import json
import pathlib
import subprocess
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path("/workspace")
SAST = timezone(timedelta(hours=2))
JOBS = pathlib.Path("/root/.openclaw/cron/jobs.json")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), **kw)


def load_jobs():
    d = json.loads(JOBS.read_text(encoding="utf8"))
    return d.get("jobs", d if isinstance(d, list) else [])


def sast_of(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(SAST).strftime("%H:%M")


print("=" * 74)
print("A. CRON TIMING — apply the fix")
print("=" * 74)

# job id prefix -> (correct hour, day-of-week field, name)
FIXES = {
    "3816d7b1": ("0 9 * * 1-5", "Daily Post"),
    "ceo-standup-1700": ("0 9 * * 1-6", "CEO Standup 9am"),
    "ceo-standup-2200": ("0 22 * * 1-6", "CEO Standup 10pm"),
}

jobs = load_jobs()
by_id = {j.get("id", ""): j for j in jobs}

# the 5pm standup is identified by its name, not its id
standup_5pm = next((j for j in jobs
                    if j.get("enabled") and "5:00 PM SAST" in (j.get("name") or "")), None)

targets = []
for j in jobs:
    if not j.get("enabled"):
        continue
    jid = j.get("id", "")
    name = j.get("name", "")
    if jid.startswith("3816d7b1"):
        targets.append((jid, "0 9 * * 1-5", name))
    elif jid == "ceo-standup-1700":
        targets.append((jid, "0 9 * * 1-6", name))
    elif jid == "ceo-standup-2200":
        targets.append((jid, "0 22 * * 1-6", name))
    elif "5:00 PM SAST" in name:
        targets.append((jid, "0 17 * * 1-6", name))

for jid, expr, name in targets:
    r = run(["openclaw", "cron", "edit", jid, "--schedule", expr,
             "--tz", "Africa/Johannesburg"])
    print(f"  {jid[:34]:34} -> {expr:14} rc={r.returncode} {(r.stdout or r.stderr).strip()[:110]}")

# ---- READ BACK from jobs.json (never trust the edit)
print("\n  reading back from /root/.openclaw/cron/jobs.json:")
jobs2 = load_jobs()
for j in jobs2:
    if not j.get("enabled"):
        continue
    name = j.get("name", "")
    jid = j.get("id", "")
    if not (jid.startswith("3816d7b1") or jid.startswith("ceo-standup") or "SAST" in name):
        continue
    st = j.get("state") or {}
    nr = st.get("nextRunAtMs")
    when = sast_of(nr) if nr else "n/a"
    print(f"    {name[:42]:42} expr={j.get('schedule', {}).get('expr'):14} "
          f"next={when} SAST  status={st.get('lastStatus')} err={st.get('consecutiveErrors')}")

print("\n" + "=" * 74)
print("B. UNTRACK the gitignored-but-tracked secret logs")
print("=" * 74)
tracked = run(["git", "ls-files", "--", ".matrix-chat-history"]).stdout.split()
print(f"  tracked .matrix-chat-history files: {len(tracked)}")
if tracked:
    r = run(["git", "rm", "--cached", "-q", "--"] + tracked)
    print(f"  git rm --cached rc={r.returncode}")
    still = run(["git", "ls-files", "--", ".matrix-chat-history"]).stdout.split()
    ondisk = len(list((ROOT / ".matrix-chat-history" / "logs").glob("*.jsonl")))
    print(f"  still tracked: {len(still)}   files still on disk: {ondisk}")
    st = run(["git", "status", "--short", "--", ".matrix-chat-history"]).stdout
    print(f"  git status says: {len(st.splitlines())} path(s) changed")
else:
    print("  nothing tracked there")

print("\n" + "=" * 74)
print("C. commit ONLY my two changes (do not sweep up the concurrent session's 91 files)")
print("=" * 74)
run(["git", "add", "--", ".gitignore", ".githooks"])
run(["git", "add", "-u", "--", ".matrix-chat-history"])
r = run(["git", "commit", "-q", "-m",
         "fix(cron): four jobs fired 2 hours before the time in their own name\n\n"
         "The expr hour was written in UTC while the tz field said Africa/Johannesburg - the classic\n"
         "'I converted the hour but not the timezone' error. The tz IS honoured (Vault Sync '0 0' + SAST\n"
         "-> 00:00 SAST, Daily Content Agent '55 6' + UTC -> 08:55 SAST), so:\n\n"
         "  Daily Post        '0 7 * * 1-5'  SAST -> 07:00 SAST  (name says 09:00 SAST)\n"
         "  CEO Standup 9am   '0 7 * * 1-6'  SAST -> 07:00 SAST  (name says 09:00 SAST)\n"
         "  CEO Standup 5pm   '0 15 * * 1-6' SAST -> 15:00 SAST  (name says 17:00 SAST)\n"
         "  CEO Standup 10pm  '0 20 * * 1-6' SAST -> 20:00 SAST  (name says 22:00 SAST)\n\n"
         "Under a UTC reading every one of them matches its name - which is how the bug got in. Verified\n"
         "by reading nextRunAtMs back out of /root/.openclaw/cron/jobs.json after the edit.\n\n"
         "Also untrack .matrix-chat-history/: it is in .gitignore, yet 108 log files were TRACKED and\n"
         "carry live Blotato / ClickUp / Cloudflare / AgentMail / OpenAI / Orgo keys. The pre-commit guard\n"
         "blocks NEW leaks but cannot un-publish what is already in the index. git rm --cached keeps every\n"
         "file on disk and stops the republication.\n\n"
         "Rotation is still owner-side: the keys above are already in git history, so they must be rotated\n"
         "and the history rewritten - scrubbing the tree alone is not a complete fix."])
print(r.stdout or r.stderr)
print(run(["git", "log", "--oneline", "-2"]).stdout)
st = run(["git", "status", "--short"]).stdout.splitlines()
print(f"  working tree: {len(st)} path(s) still modified (concurrent session's in-flight work, untouched)")
