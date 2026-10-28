# 🎯 Tumelo Ramaphosa — Obsidian Vault System Overview

> **Kanan Band Dark Theme:** `#0a0505` background · `#8B1A1A` red · `#d4a017` gold
> Managed by: **Robusca** (CEO Agent)
> Last updated by: Robusca on 2026-06-29

---

## 📁 Vault Folder Structure

```
studex-obsidian-vault/
│
├── daily/                     # All daily notes — one per day (YYYY-MM-DD.md)
│
├── templates/                 # Reusable note templates
│   ├── daily-note-template.md
│   ├── agent-report-template.md
│   └── weekly-review-template.md
│
├── business/                  # Business operations, metrics, client notes
│   ├── DAILY-BUSINESS-LOG.md
│   ├── client-notes/
│   └── proposals/
│
├── agents/                   # Agent memory index + individual logs
│   ├── AGENT-MEMORY-INDEX.md
│   ├── charlie/
│   ├── naledi/
│   ├── delivery-agent/
│   └── robusca/
│
├── wellness/                  # Health, fitness, nutrition tracking
│
├── journal/                   # Psychological & personal journal entries
│
├── projects/                  # Active projects (product launches, campaigns)
│
├── proposals/                 # Client pitches & formal business proposals
│
├── knowledge/                 # Market intel, competitor research, industry info
│
└── TUMELO-SYSTEM-OVERVIEW.md  # This file
```

---

## 📅 Daily Note Convention

**File naming:** `daily/YYYY-MM-DD.md`  
**Example:** `daily/2026-06-29.md`

Every daily note MUST follow the [[daily-note-template]] and contain:

| Section | Description |
|---|---|
| Morning State | Energy, sleep, mood, gratitude, blockers |
| Business Goals | 3 key things to accomplish today |
| Agent Tasks | Assigned tasks for Charlie, Naledi, Delivery Agent, Robusca |
| Nutrition Log | All meals, KEFIs, water, protein total |
| Supplements | Timestamp + what was taken |
| Sleep | Bed time, wake time, quality rating |
| Fitness | Workout type + duration |
| Journal Dump | Voice or written reflections (type + timestamp) |
| Business Metrics | Orders, revenue, delivery, issues |
| Agent Board Report | 10pm stand-up — each agent reports |
| End of Day Review | Wins, improvements, next-day priority |

> ⚠️ **Rule:** Every daily note MUST end with:  
> `Last updated: HH:MM by Robusca`

---

## 🔗 How to Link Notes

Use Obsidian wiki-links to connect related notes:

```markdown
# Basic link
[[daily/2026-06-29]]          # Links to a daily note
[[Charlie]]                  # Links to an agent note
[[DAILY-BUSINESS-LOG]]       # Links to business tracker

# Section anchor
[[daily/2026-06-29#Agent Board Report]]   # Jump to specific section

# Alias (display different text)
[[agents/AGENT-MEMORY-INDEX|Agent Index]]  # Shows "Agent Index" as text
```

### Examples in daily notes:
```markdown
- Reviewed [[Charlie]]'s report on the new workflow → see [[projects/q3-product-launch]]
- Client feedback from [[proposals/BigBuy-Catering-Pitch]]
- Wellness check: [[wellness/nutrition-log-2026]] 📊
```

---

## 🏷️ Tags Convention

All tags are **lowercase, hyphenated or single-word**.

| Tag | Use When |
|---|---|
| `#daily` | Every daily note entry |
| `#charlie` | Anything related to Charlie agent |
| `#naledi` | Anything related to Naledi agent |
| `#delivery` | Delivery Agent or logistics |
| `#robusca` | Robusca CEO agent activity |
| `#business` | Business, orders, revenue |
| `#wellness` | Health, nutrition, fitness |
| `#idea` | Ideas and brainstorms |
| `#journal` | Journal entries |
| `#decision` | Key decisions made |
| `#blocker` | Blocker or challenge |
| `#win` | Wins and celebrations |
| `#proposal` | Client proposals |
| `#project` | Active projects |
| `#knowledge` | Market intel / research |

**Example usage:**
```markdown
#daily #charlie #business
```

---

## 🤖 How Agents Contribute

Each agent has a section in the daily note's **Agent Board Report (10pm stand-up)**. Agents file their own [[agent-report-template]] daily.

### Agent Sections in Daily Notes:

```markdown
## 🤖 Agent Board Report (10pm)
### Charlie:
[Charlie fills this in — what she did today, blockers, tomorrow's plan]

### Naledi:
[Naledi fills this in — content posted, engagement metrics, new leads]

### Delivery Agent:
[Delivery Agent fills this in — orders dispatched, delays, client feedback]

### Robusca (CEO Report):
[Robusca fills this in — decisions made, agent coordination, midnight build]

### Decisions Made:
[List of all decisions Tumelo made today]

### Midnight Build:
[What Robusca worked on building/fixing while Tumelo sleeps]
```

### Agent Naming in Notes:
- Charlie → `#charlie`
- Naledi → `#naledi`
- Delivery Agent → `#delivery`
- Robusca → `#robusca`

### Agent Memory Index:
Each agent updates [[agents/AGENT-MEMORY-INDEX]] at the end of every week with their current projects, blockers, and voice info.

---

## 🎨 Kanan Band Visual Style

**Theme colors:**
- Background: `#0a0505` (near-black)
- Red accent: `#8B1A1A` (deep red)
- Gold accent: `#d4a017` (rich gold)

**Obsidian Appearance Settings (for mobile/desktop):**
```css
/* Suggested CSS snippet for Obsidian's Appearance → CSS snippet */
body {
  --background-primary: #0a0505;
  --background-secondary: #120808;
  --text-accent: #d4a017;
  --text-accent-hover: #f0b829;
  --interactive-accent: #8B1A1A;
  --interactive-accent-hover: #a52a2a;
}
```

---

## 🔄 Daily Sync to VM

The vault syncs to the Orgo VM at `/root/obsidian-vault/` every night via `sync-to-vm.sh`.

To run manually:
```bash
cd /workspace/studex-obsidian-vault
./sync-to-vm.sh
```

The script commits changes with a dated message and pushes to git.

---

## 🗓️ Weekly Rhythm

| Day | What Happens |
|---|---|
| Monday | Weekly Review from last week created in [[weekly-review-template]] |
| Daily (morning) | Daily note created from [[daily-note-template]] |
| Daily (10pm) | Agent Board Report filled in |
| Daily (11:59pm) | Robusca does Midnight Build |
| Sunday | Week archived, new week folder created |

---

**Last updated: 22:21 by Robusca**  
_This vault is the single source of truth for Tumelo's life, business, and agent team._
