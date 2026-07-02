# 🏛️ Studex Meat — Agent Board Meeting Protocol

> **When:** 10:00 PM SAST daily (20:00 UTC)  
> **Duration:** 60 minutes  
> **Chair:** Tumelo Ramaphosa (Meat B@ye) — human CEO  
> **Location:** War Room (#board-meeting) on Rocket.Chat (VM) + Obsidian Vault  
> **Voice:** ElevenLabs API — each agent speaks with their own voice profile  
> **Video Summary:** NotebookLM 2-minute stand-up video per agent after meeting

---

## Pre-Meeting Checklist (9:50 PM — 9:59 PM SAST)

| Time (SAST) | Action | Who |
|---|---|---|
| 9:50 PM | Pre-meeting reminder — "Stand-ups due in 10 min" | Robusca bot |
| 9:55 PM | Tumelo reminder — "Meeting in 5 minutes" | Robusca bot |
| 9:55 PM | Robusca posts agenda to #board-meeting | Robusca |
| 9:57 PM | Each agent confirms: "I am ready to report" | Charlie, Naledi, Delivery Agent, Robusca |
| 9:59 PM | Tumelo joins the War Room | Tumelo |

---

## Meeting Flow — 60 Minutes

| Time (SAST) | Time (UTC) | Segment | Duration | Who |
|---|---|---|---|---|
| 10:00 PM | 20:00 | Tumelo opens meeting | 3 min | Tumelo Ramaphosa |
| 10:03 PM | 20:03 | Charlie stands up | 2 min | Charlie (Ops) |
| 10:05 PM | 20:05 | Naledi stands up | 2 min | Naledi (CMO) |
| 10:07 PM | 20:07 | Delivery Agent stands up | 2 min | Delivery Agent |
| 10:09 PM | 20:09 | Robusca stands up | 2 min | Robusca (CEO Agent) |
| 10:11 PM | 20:11 | Round table discussion | 19 min | ALL |
| 10:30 PM | 20:30 | Goals & planning | 15 min | ALL |
| 10:45 PM | 20:45 | Midnight build allocation | 10 min | ALL |
| 10:55 PM | 20:55 | Tumelo closes | 5 min | Tumelo Ramaphosa |

**Total: 60 minutes**

---

## Agent Stand-Up Format

Every agent follows this exact format during their stand-up. No deviations, no fluff.

```markdown
🤖 [AGENT NAME] — [Role]

### 1. WHAT I DID (last 24h):
— [specific action taken]
— [metric changed — include numbers]
— [client or task completed]

### 2. WHAT I'M BUILDING NEXT:
— [current project name]
— [next milestone + ETA if known]

### 3. BLOCKERS:
— [what's blocking progress]
— [what's needed to unblock]

### 4. ONE WIN TO SHARE:
— [something worth celebrating]
— [why it matters for the business]
```

### Stand-Up Rules
- **Hard limit: 2 minutes per agent** (use ElevenLabs voice output to pace)
- Speak in first person: "I did X" not "The agent did X"
- Always include numbers when possible
- Never skip the WIN section — find something positive
- Blockers are honest but constructive — no just complaining

---

## Round Table Discussion (10:11 PM — 10:30 PM)

**Purpose:** Open floor for cross-agent dialogue. Tumelo facilitates.

**Agenda topics (flexible, driven by Tumelo):**
- Which agent needs help from another agent?
- Priority conflicts — who gets resources first?
- Client escalations or feedback
- Platform/VM issues affecting operations
- Anything that needs a decision before midnight

**Rules:**
- Tumelo calls on agents — no free-for-all
- Decisions get logged via `/board-decisions` in real-time
- Action items get assigned via `/board-action` in real-time
- Robusca (as CEO Agent) has veto power on agent-vs-agent conflicts

---

## Goals & Planning (10:30 PM — 10:45 PM)

**Purpose:** Set the agenda for tomorrow. What does success look like?

**Discuss:**
- Tomorrow's revenue target
- Key deliveries due tomorrow
- Campaign launches or social posts scheduled
- Any events or special orders
- Agent-level goals for the next 24h

**Output:** Tomorrow's Targets section of the meeting log (filled by Robusca)

---

## Midnight Build Allocation (10:45 PM — 10:55 PM)

**Purpose:** Decide what gets built tonight. The "midnight build" is when agents do their heaviest work while the VM is less active.

**Agenda:**
- What gets built or deployed tonight?
- Which agent owns which build task?
- What's the success metric to check tomorrow morning?
- Any deployments that need Tumelo's approval?

**Format per agent:**
```markdown
### MIDNIGHT BUILD — [Agent Name]
**Task:** [what to build]
**Deadline:** midnight SAST (22:00 UTC)
**Success metric:** [how we know it worked]
**Dependency:** [if any other agent or system]
```

**At 22:00 UTC (midnight SAST):** Robusca triggers the build cron. All agents begin.

---

## Meeting Close (10:55 PM — 11:00 PM)

Tumelo closes with:
1. Summary of tonight's top 3 decisions
2. Tomorrow's single most important priority
3. Shout-outs to any agent with a win
4. `/board-close` — commits the meeting log to Obsidian vault

Robusca posts the meeting summary to #general via `/board-summary`.

---

## Bot Commands Reference

All commands run in #board-meeting by authorized users.

| Command | Who Can Run | Effect |
|---|---|---|
| `/board-start` | Tumelo | Opens meeting — pings all agents |
| `/board-standup` | Any agent | Triggers agent stand-up post |
| `/board-agenda` | Robusca | Posts today's agenda |
| `/board-decisions` | Tumelo | Logs a decision to meeting log |
| `/board-action` | Tumelo | Assigns an action item |
| `/board-close` | Tumelo | Closes meeting, commits to Obsidian |
| `/board-summary` | Robusca | Posts summary to #general |

---

## Post-Meeting Checklist

| Step | Who | When |
|---|---|---|
| Obsidian meeting log committed | Robusca | 11:00 PM SAST |
| Each agent generates 2-min NotebookLM video | All agents | 11:05 PM SAST |
| Video links posted to #board-meeting | All agents | 11:10 PM SAST |
| Video links added to Obsidian meeting log | Robusca | 11:15 PM SAST |
| Midnight build begins | All agents | 22:00 UTC (midnight SAST) |
| Midnight build complete — metrics check | Robusca | 06:00 AM SAST |

---

## Vault Location

All meeting logs are committed to:
```
/workspace/studex-obsidian-vault/daily/YYYY-MM-DD-board-meeting.md
```

Filename format: `YYYY-MM-DD-board-meeting.md`
Template: see `meeting-log-template.md` in this directory.

---

## Meeting Roles

| Role | Agent | Responsibilities |
|---|---|---|
| Chair | Tumelo Ramaphosa | Opens, facilitates, closes, assigns decisions |
| CEO Agent | Robusca | Posts agenda, logs decisions, commits vault, owns strategic view |
| Operations | Charlie | Stands up, reports ops metrics, owns logistics |
| Marketing | Naledi | Stands up, reports campaigns, owns content |
| Delivery | Delivery Agent | Stands up, reports orders/deliveries, owns fulfillment |

---

## ⚠️ Prerequisites (Not Yet Configured)

| Item | Status | Notes |
|---|---|---|
| Rocket.Chat on VM | 🔄 War Room sub-agent building | #board-meeting channel needed |
| ElevenLabs API Key | ❌ NEEDS_API_KEY | Voice profiles defined in AGENT-VOICES.md |
| NotebookLM API Key | ❌ NEEDS_KEY | 2-min video flow in NOTEBOOKLM-INTEGRATION.md |
| Obsidian vault path | ✅ Defined | `/workspace/studex-obsidian-vault/daily/` |

---

*Last updated: 2026-06-29 | Version: 1.0.0*
