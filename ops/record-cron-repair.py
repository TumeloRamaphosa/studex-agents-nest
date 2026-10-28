#!/usr/bin/env python3
"""Record the cron fleet repair in memory/2026-10-22.md and HEARTBEAT.md."""
import subprocess

MEM = "/workspace/memory/2026-10-22.md"
HB = "/workspace/HEARTBEAT.md"

MEM_ADD = """
## 08:39-09:05 SAST — 🔴 THE WHOLE CRON FLEET HAD A 100% FAILURE RATE
Reading the run history of *every* job (not just the warmup ones) found the root
cause of the warmup failures was fleet-wide:
- **"Channel is required when multiple channels are configured: telegram, discord"** —
  two channels are configured, and every job with `delivery.mode: announce` but no
  explicit `delivery.channel` cannot resolve where to deliver. The error is raised
  *after* the agent turn completes, so **the work still ran** — but the job was
  recorded as an error every single time. Invisible unless you read the run log.
- Affected enabled jobs and their consecutive-error counts:
  Morning Nudge 54 · Daily Content Agent 70 · Vault Sync x2 14+2 ·
  Warmup Daily 30 · Warmup Build Hour 323 · Evening Standup 2 · Studex Daily Post 1.
- A second, independent cause: **`timeoutSeconds` too low for the agent turn.**
  The daily warmup script sends 30 emails with a 3-8s gap = ~165s of sleeping plus
  30 round-trips, so 300s was genuinely too tight.

**Fixed via `openclaw cron edit` (supported CLI — not by editing jobs.json):**
- All 6 enabled announce jobs that were missing a channel now have
  `--channel discord --to channel:1538825048465481728` (#ops).
  → **"announce jobs still missing a channel: NONE"**
- Timeouts set from **measured** historical successful durations (max × 1.5):
  Morning Nudge 1800 · Vault Sync EOD 1200 · Midday/Evening/Daily Content 900 ·
  Vault Sync PM + Daily Post 600 · CEO Standups 600 · **both warmup jobs 3600**
  (matching Build/Research Hour, whose measured max success is 2.9M ms).
- Both warmup jobs set to `--no-deliver` (they report by email, not Discord).

**Verified working:** the Build Hour engine is now actually sending —
`Cycle complete. Sent 2 emails (0 failed). Total today: 4/5`, then `5/5` (daily cap).
It had sent **nothing** for 19 days.

**Lesson: a job can do its work perfectly and still be failing 100% of the time.**
The failure was in delivery, and the scheduler records delivery failures as job
failures. Check `consecutiveErrors` and the run history, not just the job list.
"""

HB_ANCHOR = "### ⏰ BOTH WARMUP CRONS HAD A 100% FAILURE RATE — FIXED 2026-10-22"
HB_NEW = """### ⏰ THE CRON FLEET HAD A 100% FAILURE RATE — FIXED 2026-10-22
**Root cause (fleet-wide, not job-specific):** two channels are configured
(telegram, discord), and every job with `delivery.mode: announce` but **no explicit
`delivery.channel`** cannot resolve where to deliver. The error is raised *after* the
agent turn finishes, so **the work still ran** — but the job was recorded as an error
every single time. Invisible unless you read the run history.
Affected enabled jobs: Warmup Build Hour **323** · Daily Content Agent **70** ·
Morning Nudge **54** · Warmup Daily **30** · Vault Sync x2 **14+2** ·
Evening Standup / Daily Post **2+1**.
**Second cause:** `timeoutSeconds` too low — the daily warmup script sends 30 emails
with a 3-8s gap, so 300s was genuinely too tight.
**Fixed via `openclaw cron edit`** (not by editing `jobs.json`):
- All announce jobs now carry `--channel discord --to channel:1538825048465481728` (#ops)
  → *"announce jobs still missing a channel: NONE"*.
- Timeouts set from **measured** historical successes (max × 1.5): Morning Nudge 1800 ·
  Vault Sync EOD 1200 · Midday/Evening/Daily Content 900 · Daily Post 600 · warmup jobs 3600.
- Both warmup jobs → `--no-deliver` (they report by email).
**Verified:** the Build Hour engine now actually sends — `Sent 2 emails (0 failed)`,
then `5/5` at its daily cap. It had sent **nothing** for 19 days.
⚠️ **A job can do its work perfectly and still be failing 100% of the time.** The
failure was in *delivery*, and the scheduler records delivery failures as job failures.
Check `consecutiveErrors` and the run history — not just the job list.

"""

with open(MEM, "a") as fh:
    fh.write(MEM_ADD)

txt = open(HB).read()
if "THE CRON FLEET HAD A 100% FAILURE RATE" not in txt:
    assert txt.count(HB_ANCHOR) == 1
    txt = txt.replace(HB_ANCHOR, HB_NEW)
    open(HB, "w").write(txt)
    print("HEARTBEAT.md updated")
else:
    print("HEARTBEAT.md already has the section")

print(subprocess.run(["git", "-C", "/workspace", "add", "-A", "ops/", "memory/",
                      "HEARTBEAT.md"], capture_output=True, text=True).stderr)
print(subprocess.run(["git", "-C", "/workspace", "commit", "-q", "-m",
                      "fix(cron): repair fleet-wide 100% failure rate — missing delivery "
                      "channel + too-low timeouts",
                      "All 6 enabled announce jobs missing delivery.channel now set to "
                      "discord/#ops; timeouts raised from measured historical durations; "
                      "both warmup jobs set to no-deliver with 3600s ceiling. "
                      "Verified: Build Hour engine now actually sends."],
                     capture_output=True, text=True).stdout)
print(subprocess.run(["git", "-C", "/workspace", "log", "--oneline", "-1"],
                     capture_output=True, text=True).stdout)
