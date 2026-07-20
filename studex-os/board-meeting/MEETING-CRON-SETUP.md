# ⏰ Meeting Cron Setup — Studex Meat Agent Board Meeting

> **Time zone:** SAST (South African Standard Time) = UTC + 2  
> **Meeting time:** 10:00 PM SAST daily  
> **All times below are UTC** (SAST = UTC + 2)

---

## Time Zone Reference

| SAST | UTC | Event |
|---|---|---|
| 9:50 PM | 19:50 | Pre-meeting reminder |
| 9:55 PM | 19:55 | Tumelo reminder + agenda post |
| 9:57 PM | 19:57 | Agents confirm readiness |
| 9:59 PM | 19:59 | Tumelo joins |
| **10:00 PM** | **20:00** | **Meeting starts — `/board-start`** |
| 10:03 PM | 20:03 | Charlie stand-up |
| 10:05 PM | 20:05 | Naledi stand-up |
| 10:07 PM | 20:07 | Delivery Agent stand-up |
| 10:09 PM | 20:09 | Robusca stand-up |
| 10:11 PM | 20:11 | Round table begins |
| 10:30 PM | 20:30 | Goals & planning |
| 10:45 PM | 20:45 | Midnight build allocation |
| 10:55 PM | 20:55 | Tumelo closes |
| 11:00 PM | 21:00 | Meeting ends |
| 11:01 PM | 21:01 | Vault commit + summary |
| 11:10 PM | 21:10 | Video links posted |
| **Midnight** | **22:00** | **Midnight build triggers** |
| 6:00 AM | 04:00 | Morning build review |

---

## Cron Jobs — Full Setup

All cron jobs should be configured in OpenClaw using the `cron-mastery` skill.

### 1. Pre-Meeting Reminder (9:50 PM SAST)

```cron
50 19 * * *
```

**Description:** 10 minutes before the meeting, remind all agents to prepare their stand-ups.

**Action:** Robusca bot posts to #board-meeting:

```
⏰ BOARD MEETING IN 10 MINUTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All agents: prepare your stand-up for #board-meeting.

/board-standup — your format when the meeting opens.
Stand-ups due: 9:58 PM SAST.

Chair: @Tumelo — see you at 10:00 PM.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Command to set up (OpenClaw cron):**
```
/cron add pre-meeting-reminder "50 19 * * *" "Board meeting reminder — 10 min" channel=board-meeting
```

---

### 2. Tumelo Reminder + Agenda Post (9:55 PM SAST)

```cron
55 19 * * *
```

**Description:** 5 minutes before. Post Tumelo-specific reminder AND trigger Robusca's agenda post.

**Actions:**
1. Robusca bot pings Tumelo: `@Tumelo — meeting in 5 minutes. Your agents are standing by.`
2. Robusca auto-posts `/board-agenda`

**Command to set up (OpenClaw cron):**
```
/cron add tumelo-reminder "55 19 * * *" "Tumelo reminder + agenda post" channel=board-meeting
/cron add agenda-post "55 19 * * *" "Robusca posts agenda" channel=board-meeting
```

---

### 3. Meeting Start (10:00 PM SAST)

```cron
0 20 * * *
```

**Description:** The meeting begins. This cron fires the meeting open signal.

**Action:** Either:
- **Option A (Tumelo runs manually):** `/board-start` typed by Tumelo in #board-meeting
- **Option B (auto-trigger):** Robusca auto-posts the open banner + pings all agents

> **Recommendation:** Keep this as a reminder, not auto-start. Tumelo should explicitly open the meeting. This ensures the chair is present before it begins.

**Reminder message:**
```
🏛️ STUDEX MEAT — BOARD MEETING STARTING NOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Charlie @Naledi @Delivery-Agent @Robusca — meeting is live.
Chair @Tumelo has opened the floor.
60 minutes. Let's go.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Command to set up (OpenClaw cron):**
```
/cron add meeting-start "0 20 * * *" "Meeting starting now" channel=board-meeting
```

---

### 4. Post-Meeting Vault Commit (11:01 PM SAST)

```cron
1 21 * * *
```

**Description:** 1 minute after the meeting closes, Robusca commits the meeting log to Obsidian vault and posts the summary to #general.

**Actions:**
1. Commit meeting log to `/workspace/studex-obsidian-vault/daily/{{DATE}}-board-meeting.md`
2. Run `/board-summary` to post to #general

**Command to set up (OpenClaw cron):**
```
/cron add vault-commit "1 21 * * *" "Commit meeting log to Obsidian + post summary"
```

---

### 5. Midnight Build Trigger (Midnight SAST = 22:00 UTC)

```cron
0 22 * * *
```

**Description:** The midnight build begins. All agents start their overnight builds.

**Action:** Robusca posts to #board-meeting:

```
🌙 MIDNIGHT BUILD — INITIATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
It's midnight SAST. The build begins.

Agents — execute your assigned builds.
Success metrics are in the meeting log.

Tomorrow morning check: 06:00 AM SAST.
Robusca will review all build results.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Command to set up (OpenClaw cron):**
```
/cron add midnight-build "0 22 * * *" "Midnight build triggers — agents begin builds"
```

---

### 6. Morning Build Review (6:00 AM SAST = 04:00 UTC)

```cron
0 4 * * *
```

**Description:** Robusca reviews midnight build results and posts a morning status report.

**Action:** Robusca posts to #board-meeting:

```
☀️ MORNING BUILD REVIEW — {{DATE}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reviewing midnight build results...

Robusca: [STATUS] — [result]
Charlie: [STATUS] — [result]
Naledi: [STATUS] — [result]
Delivery Agent: [STATUS] — [result]

Business check:
• Orders pending: [count]
• Today's deliveries: [count]
• Content scheduled: [yes/no]

Next meeting: Tonight, 10:00 PM SAST.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Command to set up (OpenClaw cron):**
```
/cron add morning-review "0 4 * * *" "Morning build review" channel=board-meeting
```

---

## Complete Cron Table

| # | Cron (UTC) | SAST | Name | Action |
|---|---|---|---|---|
| 1 | `50 19 * * *` | 9:50 PM | Pre-meeting reminder | All agents prepare stand-ups |
| 2 | `55 19 * * *` | 9:55 PM | Tumelo reminder | @Tumelo ping + agenda post |
| 3 | `0 20 * * *` | 10:00 PM | Meeting start | Meeting banner + all agents pinged |
| 4 | `1 21 * * *` | 11:01 PM | Vault commit | Commit log + post summary to #general |
| 5 | `0 22 * * *` | Midnight | Midnight build | Build trigger — all agents begin |
| 6 | `0 4 * * *` | 6:00 AM | Morning review | Robusca reviews build results |

---

## OpenClaw Cron Configuration

Use the `cron-mastery` skill to set up all jobs. Example setup:

```bash
# Via OpenClaw CLI (non-interactive)
openclaw cron create \
  --name "pre-meeting-reminder" \
  --cron "50 19 * * *" \
  --message "⏰ Board meeting in 10 minutes. Post stand-up to #board-meeting." \
  --channel board-meeting \
  --label studex-daily

openclaw cron create \
  --name "tumelo-reminder" \
  --cron "55 19 * * *" \
  --message "👑 @Tumelo — meeting in 5 minutes. Join #board-meeting." \
  --channel board-meeting \
  --label studex-daily

openclaw cron create \
  --name "meeting-start" \
  --cron "0 20 * * *" \
  --message "🏛️ STUDEX MEAT — BOARD MEETING STARTING NOW" \
  --channel board-meeting \
  --label studex-daily

openclaw cron create \
  --name "vault-commit" \
  --cron "1 21 * * *" \
  --command "robusca-vault-commit.sh" \
  --label studex-daily

openclaw cron create \
  --name "midnight-build" \
  --cron "0 22 * * *" \
  --message "🌙 Midnight build begins. Agents — execute your builds." \
  --channel board-meeting \
  --label studex-daily

openclaw cron create \
  --name "morning-review" \
  --cron "0 4 * * *" \
  --message "☀️ Morning build review" \
  --channel board-meeting \
  --label studex-daily
```

---

## Cron Job Scripts

### robusca-vault-commit.sh

```bash
#!/bin/bash
# /workspace/studex-os/board-meeting/scripts/robusca-vault-commit.sh
# Called by cron at 21:01 UTC (11:01 PM SAST)

DATE=$(date +%Y-%m-%d)
VAULT_PATH="/workspace/studex-obsidian-vault/daily"
WORKSPACE="/workspace/studex-os/board-meeting"

# Copy meeting log from workspace to vault
if [ -f "$WORKSPACE/logs/${DATE}-meeting-log-draft.md" ]; then
    cp "$WORKSPACE/logs/${DATE}-meeting-log-draft.md" \
       "$VAULT_PATH/${DATE}-board-meeting.md"
    echo "Meeting log committed: $VAULT_PATH/${DATE}-board-meeting.md"
else
    echo "ERROR: Meeting log draft not found for $DATE"
    exit 1
fi

# Git commit (if vault is a git repo)
cd "$VAULT_PATH" || exit
git add "${DATE}-board-meeting.md"
git commit -m "docs: board meeting $DATE — committed by RobuscaBot"

# Post summary to #general
echo "Summary ready for #general posting"
exit 0
```

---

## Weekend Override

Saturday and Sunday meetings follow the same schedule but with adjusted focus:

**Saturday (optional meeting — if needed):**
- Skip if no significant business events
- Robusca posts a written update instead

**Sunday:**
- Pre-meeting prep for the week ahead
- Agenda focuses on week planning, not daily stand-ups

**Cron override for weekends:**
```cron
# Skip automated posts on Saturday
0 20 * * 6
# Skip on Sunday unless Tumelo opts in
# Manual trigger only on Sunday
```

---

## Testing the Cron Jobs

Before going live, test each cron job:

```bash
# Manually trigger each cron job to verify output
# Use the OpenClaw cron test command:

openclaw cron test pre-meeting-reminder
openclaw cron test tumelo-reminder
openclaw cron test meeting-start
openclaw cron test vault-commit
openclaw cron test midnight-build
openclaw cron test morning-review
```

Check #board-meeting in Rocket.Chat after each test to confirm the message posts correctly.

---

## ⚠️ Prerequisites Before Activating

| Item | Status | Notes |
|---|---|---|
| OpenClaw cron access | ✅ Available | Use `cron-mastery` skill |
| Rocket.Chat channel #board-meeting | 🔄 Pending | War Room sub-agent creating |
| Obsidian vault path | ✅ Defined | `/workspace/studex-obsidian-vault/daily/` |
| robusca-vault-commit.sh | ✅ Written above | Make executable before activating |
| Weekend override | 🔄 Optional | Set up after weekday schedule is stable |

---

*Last updated: 2026-06-29 | Version: 1.0.0*
