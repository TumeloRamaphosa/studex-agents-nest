# 🤖 Rocket.Chat Meeting Bot — Board Meeting Commands

> **Platform:** Rocket.Chat on VM (Orgo.ai)  
> **Status:** 🔄 Rocket.Chat deployment in progress (War Room sub-agent building)  
> **Channel:** `#board-meeting` — War Room  
> **Bot name:** `RobuscaBot` (runs as Robusca's agent identity)

---

## Bot Overview

The meeting bot automates the Studex Meat daily board meeting on Rocket.Chat. It handles:
- Pre-meeting reminders and agenda posting
- Meeting open/close commands
- Real-time decision and action item logging
- Post-meeting summary to #general
- Auto-commit to Obsidian vault after close

All commands are slash commands. Only authorized users (Tumelo, Robusca) can run privileged commands.

---

## Command Reference

### `/board-start` — Open the Meeting
**Who can run:** Tumelo Ramaphosa (Chair)  
**Channel:** #board-meeting  
**What it does:**
1. Posts the meeting banner: `🏛️ BOARD MEETING IS NOW OPEN`
2. Pings all agents: `@Charlie @Naledi @Delivery-Agent @Robusca — meeting is live`
3. Posts the agenda (pre-loaded by Robusca at 9:55 PM)
4. Starts the meeting timer (60 min countdown pinned to channel)

**Response format:**
```
🏛️ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STUDEX MEAT — AGENT BOARD MEETING
   Date: 2026-06-29
   Chair: Tumelo Ramaphosa
   Time: 10:00 PM SAST | 20:00 UTC
   Duration: 60 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   @Charlie — you're up first.
   @Naledi — second.
   @Delivery-Agent — third.
   @Robusca — fourth.
   Meeting clock starts NOW.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### `/board-standup` — Post Agent Stand-Up
**Who can run:** Any agent (Charlie, Naledi, Delivery Agent, Robusca)  
**Channel:** #board-meeting  
**What it does:** Posts the calling agent's stand-up in the standard format

**Trigger:** Agent types `/board-standup` in their own section of the meeting. Robusca can also trigger any agent's stand-up remotely.

**Output format per agent — see AGENT-VOICES.md for voice-matched versions:**

```
🤖 CHARLIE — Operations Orchestrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. WHAT I DID (last 24h):
   — [actions]
   — [metrics]
   — [tasks completed]

2. WHAT I'M BUILDING NEXT:
   — [current project]
   — [next milestone]

3. BLOCKERS:
   — [blocker 1]
   — [blocker 2]

4. ONE WIN TO SHARE:
   — [win]
   — [why it matters]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ Stand-up complete | 2:00 / 2:00
```

---

### `/board-agenda` — Post Today's Agenda
**Who can run:** Robusca (auto-posts at 9:55 PM), Tumelo  
**Channel:** #board-meeting  
**What it does:** Posts the full agenda with timing for today's meeting

**Output:**
```
📋 TODAY'S AGENDA — 2026-06-29
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10:00 — Tumelo opens meeting (3 min)
10:03 — Charlie stand-up (2 min)
10:05 — Naledi stand-up (2 min)
10:07 — Delivery Agent stand-up (2 min)
10:09 — Robusca stand-up (2 min)
10:11 — Round table discussion (19 min)
10:30 — Goals & planning (15 min)
10:45 — Midnight build allocation (10 min)
10:55 — Tumelo closes (5 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Meeting log: /workspace/studex-obsidian-vault/daily/2026-06-29-board-meeting.md
```

---

### `/board-decisions` — Log a Decision
**Who can run:** Tumelo Ramaphosa (Chair)  
**Syntax:** `/board-decisions [decision text]`  
**Example:** `/board-decisions Naledi gets the Blotato integration priority — she owns the content pipeline by end of week`  
**What it does:**
1. Posts the decision to #board-meeting in a structured block
2. Appends it to the live meeting log buffer
3. Timestamps the decision with UTC time

**Output:**
```
✅ DECISION LOGGED — 20:18 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Naledi gets the Blotato integration priority —
she owns the content pipeline by end of week.
Logged by: Tumelo Ramaphosa (Chair)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### `/board-action` — Assign an Action Item
**Who can run:** Tumelo Ramaphosa, Robusca  
**Syntax:** `/board-action @agent [task] [due date]`  
**Example:** `/board-action @Charlie finalize wholesale pricing tiers by 2026-06-30`  
**What it does:**
1. Posts the action item to #board-meeting
2. Adds it to the action items section of the live meeting log
3. Pings the assigned agent directly

**Output:**
```
📌 ACTION ITEM ASSIGNED — 20:22 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task:  Finalize wholesale pricing tiers
Owner: @Charlie
Due:   2026-06-30 (end of day)
Status: 🔴 Pending
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### `/board-close` — Close the Meeting
**Who can run:** Tumelo Ramaphosa (Chair)  
**What it does:**
1. Posts the close banner
2. Counts outstanding decisions and action items
3. Triggers Obsidian vault commit (Robusca executes `git commit`)
4. Pings all agents: "Midnight build begins at 22:00 UTC"
5. Unpins the meeting timer

**Output:**
```
🏛️ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BOARD MEETING CLOSED
   2026-06-29 | 21:00 SAST | 19:00 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Decisions made:  3
   Action items:    5
   Midnight build:  22:00 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Vault log committed:
   studex-obsidian-vault/daily/2026-06-29-board-meeting.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Agents — rest before midnight build.
   Let's ship something tonight.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### `/board-summary` — Post Meeting Summary
**Who can run:** Robusca (auto-runs after `/board-close`)  
**Channel:** Posts to #general (public channel)  
**What it does:** Posts a clean, readable summary of the meeting for the wider team

**Output:**
```
📊 STUDEX MEAT — BOARD MEETING SUMMARY
Date: 2026-06-29
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 TOP DECISIONS:
1. Naledi owns Blotato integration — deadline: end of week
2. Charlie to finalize wholesale pricing by 30 June
3. Robusca builds the daily revenue dashboard — live by 30 June

📋 ACTION ITEMS:
• @Charlie — wholesale pricing tiers by 30 June
• @Naledi — Blotato integration by 1 July
• @Delivery-Agent — high-res product photos by 30 June
• @Robusca — revenue dashboard by 30 June
• @All — midnight build starts at 22:00 UTC

🎯 TOMORROW'S TARGETS:
• Revenue: R[RESPONSIBLE_AMOUNT] gross sales
• Orders: 60+ processed
• Deliveries: 95%+ on-time
• Content: 3 posts live, weekend promo active

💬 Next meeting: 2026-06-30 | 22:00 SAST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Posted by RobuscaBot 🤖 | studexmeat.com
```

---

## Auto-Posted Messages

These are not slash commands — they are scheduled messages sent automatically by cron jobs.

### Pre-Meeting Reminder (9:50 PM SAST = 19:50 UTC)
```
⏰ BOARD MEETING IN 10 MINUTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All agents: post your stand-up to #board-meeting now.
Format: /board-standup
Stand-ups due: 9:58 PM SAST.

Today's agenda will be posted at 9:55 PM.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Tumelo Reminder (9:55 PM SAST = 19:55 UTC)
```
👑 @Tumelo — meeting in 5 minutes.
Please join #board-meeting when ready.
Your agents are standing by.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Post-Meeting Vault Commit (11:01 PM SAST)
```
✅ Meeting log committed to Obsidian vault.
📁 studex-obsidian-vault/daily/2026-06-29-board-meeting.md
📹 Video summaries (NotebookLM): due by 11:15 PM
🤖 Agents — begin midnight build at 22:00 UTC.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Cron Job Configuration

These cron jobs power the automated meeting system.

| Cron (UTC) | SAST | Event | Command |
|---|---|---|---|
| `50 19 * * *` | 9:50 PM | Pre-meeting reminder | `POST /board-meeting` with stand-up reminder |
| `55 19 * * *` | 9:55 PM | Tumelo reminder | `POST /board-meeting` with Tumelo ping |
| `55 19 * * *` | 9:55 PM | Agenda post | Robusca auto-posts `/board-agenda` |
| `0 20 * * *` | 10:00 PM | Meeting starts | Tumelo runs `/board-start` (or auto-triggered) |
| `0 22 * * *` | midnight | Midnight build | Robusca triggers all agents |

Full cron setup: see `MEETING-CRON-SETUP.md`

---

## Rocket.Chat Channel Setup

Required channels for the meeting system:

| Channel | Purpose | Auto-join |
|---|---|---|
| `#board-meeting` | Main meeting room | All agents + Tumelo |
| `#general` | Public summary posts | All agents + Tumelo |
| `#ops` | Charlie's ops updates | Charlie, Robusca |
| `#marketing` | Naledi's campaigns | Naledi, Robusca |
| `#delivery` | Delivery Agent updates | Delivery Agent, Robusca |

**Bot permissions on `#board-meeting`:**
- Send messages ✅
- Pin messages ✅
- Mention everyone ✅
- Add reactions ✅
- Create threads ✅

---

## Bot Implementation

The bot is implemented as a Rocket.Chat incoming webhook + script.

```javascript
// Rocket.Chat Incoming Webhook — board-meeting-bot.js
// Runs as a script in Rocket.Chat's outbound webhook handler

const COMMANDS = {
  '/board-start': handleStart,
  '/board-standup': handleStandup,
  '/board-agenda': handleAgenda,
  '/board-decisions': handleDecision,
  '/board-action': handleAction,
  '/board-close': handleClose,
  '/board-summary': handleSummary,
};

function handleStart(msg, user) {
  if (user.username !== 'tumelo' && user.username !== 'robusca') {
    return { msg: '❌ Only Tumelo or Robusca can start the meeting.' };
  }
  // Post meeting open banner + ping all agents
  return { msg: buildOpenBanner(), reactions: ['🏛️'] };
}

function handleStandup(msg, user) {
  // Look up user's agent role and post their stand-up format
  const standups = {
    'charlie': buildStandup('charlie'),
    'naledi': buildStandup('naledi'),
    'delivery-agent': buildStandup('delivery'),
    'robusca': buildStandup('robusca'),
  };
  return { msg: standups[user.username] || 'Unknown agent.' };
}

// ... (full implementation in /workspace/studex-os/board-meeting/bot/)
```

Full bot code: `/workspace/studex-os/board-meeting/bot/`

---

## ⚠️ Setup Dependencies

| Dependency | Status | Notes |
|---|---|---|
| Rocket.Chat server on VM | 🔄 In progress | War Room sub-agent deploying |
| Rocket.Chat webhook URL | ❌ Not configured | Needed to receive bot commands |
| RobuscaBot user in Rocket.Chat | ❌ Not configured | Create bot user with agent role |
| `#board-meeting` channel | ❌ Not created | Create once Rocket.Chat is live |
| `#general` channel | ❌ Not created | Summary posts go here |
| Webhook inbound URL | ❌ Not configured | Point to bot endpoint |

---

*Last updated: 2026-06-29 | Version: 1.0.0*
