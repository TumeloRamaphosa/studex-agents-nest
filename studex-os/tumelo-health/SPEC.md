# Tumelo Wellness OS — Specification

> Personal performance operating system for Tumelo Ramaphosa, CEO of Studex Meat.
> Built for peak physical + mental performance. Voice-first. Dark Kanan Band aesthetic.

---

## 🎨 Design System — Kanan Band

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-void` | `#0a0505` | Page background |
| `--bg-surface` | `#120808` | Card backgrounds |
| `--bg-raised` | `#1e0f0f` | Elevated surfaces, modals |
| `--red` | `#8B1A1A` | Primary actions, accents |
| `--red-glow` | `#c0392b` | Hover states, highlights |
| `--gold` | `#d4a017` | Secondary accents, icons |
| `--gold-light` | `#f0c040` | Active states, badges |
| `--cream` | `#f5f0e8` | Primary text |
| `--cream-dim` | `#b8a89a` | Secondary text |
| `--border` | `#2a1515` | Dividers, card borders |

**Typography:**
- Headings: `Cormorant Garamond` (serif, authoritative)
- Body: `Inter` (clean, readable)
- Mono/data: `JetBrains Mono` (logs, metrics)

**Motion:**
- Entrance: fade-up, 200ms ease-out
- Hover: scale 1.02, 150ms
- Voice active: pulsing gold ring
- Section transitions: slide + fade

---

## A. Daily Wellness Dashboard

**URL:** `http://67.213.119.157:3001`

### Layout
```
┌─────────────────────────────────────────┐
│  🦁 TUMELO WELLNESS OS    [≡] [🎤] [📷] │
│  Mon 29 June 2026 · Day Streak: 14 🔥  │
├─────────────────────────────────────────┤
│  [Health Advisor Morning Briefing Card] │
├─────────────────────────────────────────┤
│  SLEEP │ NUTRITION │ SUPPLEMENTS        │
│  FITNESS │ JOURNAL  │ DAILY PLAN        │
│  AGENT BOARD MEETING                    │
├─────────────────────────────────────────┤
│  TODAY'S NUMBERS                        │
│  Protein: 142g / 180g ████████░░       │
│  Carbs:   89g  / 120g ██████░░░░       │
│  Water:   1.8L / 3.0L ██████░░░░       │
│  KEFI:    ✓✓✗                           │
└─────────────────────────────────────────┘
```

### Global Controls
- **🎤 Voice Button:** Fixed bottom-right. Press to activate Web Speech API. Shows listening indicator. Transcribes → auto-routes to correct logger.
- **📷 Camera Button:** Opens camera for food photos. Captures → sends to backend AI vision endpoint → parses into structured meal data.
- **≡ Menu:** Navigation drawer with all sections.

### Section Cards (Expandable)
Each section is a collapsible card with:
- Header: icon + title + today's summary
- Body: detailed logging interface
- Footer: quick-add buttons, voice trigger

---

## B. Nutrition Tracking System

### Voice Food Logging
User says: *"I just had eggs and toast for breakfast"*

1. Web Speech API transcribes → text
2. Frontend sends to `POST /api/log/meal`
3. Backend uses AI to parse: `{ meal_slot: "breakfast", items: [...], protein_g: N, carbs_g: N }`
4. User confirms/edits before saving

### Meal Slots
| Slot | Time Window | Icon |
|------|------------|------|
| Breakfast | 7–9am SAST | 🍳 |
| Lunch | 12–2pm SAST | 🥗 |
| Supper | 6–8pm SAST | 🍖 |
| Snacks | Any | 🍎 |

### Food Photo Pipeline
```
Camera → POST /api/vision/analyze → AI vision returns structured nutrition data → User confirms → Saved to meals table
```

### Daily Nutrition Summary
- Protein bar (g, % of target)
- Carbs bar (g, % of limit)
- Estimated calories
- Water intake tracker (glasses or mL)
- Visual timeline of meals

### Goals (configurable)
- Protein: **180g/day** (default)
- Carbs: **120g/day** (default)
- Water: **3L/day**
- Calories: **2,400 kcal/day** (estimated)

---

## C. Sleep & Recovery Tracking

### Voice Input
*"I slept 7 hours and it was pretty good"*
→ Parses: `{ hours: 7, quality: 4 }`

*"Went to bed at 11, woke up at 6:30"*
→ Parses: `{ bed_time: "23:00", wake_time: "06:30", hours: 7.5 }`

### Manual Entry
- Bed time picker (time wheel)
- Wake time picker
- Quality: 1–5 star rating
- Notes: free text
- Resting HR (optional)

### Weekly Sleep Chart
- Bar chart: hours per night (7 days)
- Color: red = <6h, gold = 6-8h, green = 8+h
- Quality trend line overlay

---

## D. Medicine & Supplement Tracking

### KEFI Supplement
- One-tap "I took my KEFI" button
- Timestamps automatically
- Checkmark grid: AM dose ✓, PM dose ✓
- Streak counter for KEFI adherence

### Medicine Log
- Add medicine: name + dosage + time
- Schedule: daily, weekly, as-needed
- Reminder toggle (triggers Telegram notification)
- Adherence %: taken / scheduled

### Adherence Dashboard
```
KEFI:    ████████░░ 80%  (8/10 days this week)
Vitamin D: ██████████ 100% (7/7)
Iron:    █████░░░░░ 50%  (3/6 doses)
```

---

## E. Fitness Tracking

### Voice Input
*"Did a 45 minute run this morning"*
*"Hit chest and tris, 80kg bench 5x5"*
*"30 min mobility work"*

### Fitness Types
- **Cardio:** Run, Walk, Cycle, Swim — duration + distance + avg HR
- **Strength:** Muscle group + exercises + sets/reps/weight
- **Mobility:** Stretching, Yoga, Foam rolling — duration

### Quick Log Buttons
- 🏃 Quick Run
- 🏋️ Quick Gym
- 🚶 Quick Walk
- 🧘 Quick Mobility

### Weekly Summary
- Total training days
- Total volume (kg lifted)
- Cardio minutes
- Rest day indicator

---

## F. Psychological Journal

### Morning Voice Dump
Prompt: *"How are you feeling this morning? What's on your mind?"*
- Opens voice recorder (30-second minimum, up to 3 min)
- Transcribes → saves as journal entry type=`morning`
- Emotion tags auto-detected: 😤 stressed, 😴 tired, 🔥 energized, 😤 frustrated, 🙏 grateful

### Evening Reflection
Prompt: *"How did today go? What went well? What could be better?"*
- Same interface, type=`evening`

### Journal Entry Format
```markdown
## Morning Journal — Mon 29 June 2026

[Transcribed text...]

**Emotion Tags:** 🔥 Energized, 🙏 Grateful
**Wellbeing Score:** 8/10
**Action Items:**
- [ ] Follow up with supplier on Tuesday order
- [ ] 20 min stretching after gym

**Backlinks:** ← Sunday 28 June | → Tuesday 30 June
```

### Wellbeing Score
- Self-rated 1–10 slider
- Based on sleep quality + energy + mood
- Tracked over time with trend line

---

## G. Daily Planning Ritual

### Trigger: 7am SAST (shown as "9am SAST" = 7am SAST in cron doc)
*"My plan for today is..."*

### Structure
```
## TODAY'S PLAN — Mon 29 June 2026

### 🏢 Business Goals
- [ ]

### 🤖 Agent Tasks
- Charlie:
- Naledi:
- Delivery Agent:
- Robusca:

### 💪 Personal
- [ ]

### 🎯 Top 3 Priorities
1.
2.
3.
```

### Synced to Obsidian
- On save, pushes to `/YYYY-MM-DD.md` in Obsidian vault
- Section: `## Morning Plan`
- Previous day auto-linked as backlink

---

## H. Agent Board Meeting

### Trigger: 10pm SAST (8pm UTC)

### Format
```
## Agent Board Meeting — Mon 29 June 2026
### Chair: Tumelo | Time: 22:00 SAST

---

### 🤖 Robusca (CEO Agent)
**Yesterday:** [...]
**Today:** [...]
**Blockers:** [...]
**Midnight Build:** [...]

---

### ⚡ Charlie (Operations)
**Yesterday:** [...]
**Today:** [...]
**Blockers:** [...]
**Midnight Build:** [...]

---

### 🎨 Naledi (Marketing)
**Yesterday:** [...]
**Today:** [...]
**Blockers:** [...]
**Midnight Build:** [...]

---

### 🚚 Delivery Agent
**Yesterday:** [...]
**Today:** [...]
**Blockers:** [...]

---

### 🦁 Tumelo — Chair Notes
[Notes during meeting]

---
**Meeting ended:** 23:00 SAST
```

### Agent Voice Lines
Each agent reads their stand-up aloud via ElevenLabs before Tumelo reviews. Text-based entries also accepted.

---

## I. Agent Voices (ElevenLabs)

| Agent | Character | ElevenLabs Voice ID | Use Case |
|-------|-----------|---------------------|---------|
| Robusca | CEO, authoritative, deep male | `PLACEHOLDER_DEEP_MALE` | Morning briefing intro, board meeting chair |
| Charlie | Fast, efficient, ops | `PLACEHOLDER_EFFICIENT_MALE` | Ops updates, reminder notifications |
| Naledi | Warm, creative, marketing | `PLACEHOLDER_WARM_FEMALE` | Marketing reports, encouragement |
| Delivery Agent | No-nonsense, logistics | `PLACEHOLDER_STRAIGHT_MALE` | Delivery updates, ETA notifications |
| Wellness Advisor | Clinical, sports science | `PLACEHOLDER_CLINICAL_MALE` | Health reports, morning briefing |

> **Note:** Replace `PLACEHOLDER_*` with actual ElevenLabs voice IDs. Configure in `backend/.env` as `ELEVENLABS_API_KEY`.

---

## J. Obsidian Vault Integration

**Vault path:** `/workspace/studex-obsidian-vault/`

### Daily Note Template
```
---
date: 2026-06-29
day: Monday
tags: [daily, 2026-W27]
---

## 🌅 Morning Plan
[migrated from Daily Planning Ritual]

## 🍽️ Nutrition Log
| Meal | Time | Protein | Carbs | Calories |
|------|------|---------|-------|----------|
|      |      |         |       |          |

**Totals:** P: __g | C: __g | kcal: ___

## 😴 Sleep
Bed: __ | Wake: __ | Duration: __h | Quality: ⭐⭐⭐⭐☆

## 💪 Training
[type] — [duration] — [notes]

## 🧠 Journal
**Wellbeing Score:** /10
[morning entry]
[evening reflection]

## 🤖 Agent Updates
[Board meeting notes]

## 📊 Business Metrics
- Revenue:
- Orders:
- Agents active:

## 🔗 Backlinks
← [[2026-06-28]] | [[2026-W25]] | → [[2026-06-30]]
```

### Sync Mechanism
- Backend writes to local vault path via Node.js `fs`
- Telegram bot reads vault for daily briefing
- Board meeting notes auto-append to daily note

---

## K. AI Wellness Advisor

### Morning Briefing (6am SAST)

**Inputs:** Yesterday's full log (sleep, meals, supplements, training, journal)

**Output format:**
```
🦁 GOOD MORNING, TUMELO — MON 29 JUNE 2026

📊 YESTERDAY'S SCORE: 8.2/10
Sleep: 7.5h ⭐⭐⭐⭐ | Protein: 142g | KEFI: ✓
Training: 45min run | Wellbeing: 8/10

🎯 TODAY'S 5-POINT BRIEFING

1. RECOVERY STATUS
   You're recovered. Energy score high. No red flags.
   → Proceed with planned training.

2. PROTEIN OPTIMIZATION
   You hit 142g yesterday — solid. Today's target: 180g.
   Tip: Front-load protein at breakfast (30g+).
   Meal suggestion: 3 eggs + 150g beef mince + toast.

3. SUPPLEMENT TIMING
   KEFI AM: Take WITH breakfast (not empty stomach).
   Vitamin D: Morning with KEFI for best absorption.
   Magnesium: Evening only — aids sleep onset.

4. TRAINING RECOMMENDATION
   Yesterday: Run (cardio)
   Today: Strength — legs + shoulders
   Focus: Compound lifts, 4-6 rep range for strength.
   Pre-workout: 30g protein + carbs 90min before gym.

5. PRIORITY ACTIONS
   1. Take KEFI with breakfast (not before)
   2. Eat 30g+ protein at breakfast within 1hr of waking
   3. Evening mobility: 15 min hip + spine stretch

⚠️ WATCH: Cortisol is slightly elevated (journal noted stress).
   → Add 10 min box breathing before bed.
   → Avoid intense training on low-sleep days (<6h).

---
Prepared by Wellness Advisor · Sports Science + Orthopaedics + Hormone Health
```

### Advisor Knowledge Base
- Sports science: protein timing, meal distribution, pre/post-workout nutrition
- Orthopaedics: mobility, injury prevention, recovery protocols
- Hormone health: cortisol management, testosterone support via sleep/nutrition/training
- Supplements: KEFI formulation, Vitamin D, Magnesium, Iron interactions

---

## Technical Architecture

```
┌──────────────────────────────────────────────────┐
│  FRONTEND (React SPA)                            │
│  http://67.213.119.157:3001                     │
│  - Dashboard, voice input, camera, all UI      │
│  - Web Speech API for voice                     │
│  - Axios → backend REST API                     │
└──────────────────┬──────────────────────────────┘
                   │ HTTP REST
┌──────────────────▼──────────────────────────────┐
│  BACKEND (Express.js / Node.js)                 │
│  http://67.213.119.157:3000                     │
│  - REST API (see backend-api.md)                │
│  - SQLite via better-sqlite3                    │
│  - AI vision: /api/vision/analyze (LLM call)   │
│  - AI parse: /api/parse/meal (LLM call)        │
│  - ElevenLabs TTS for agent voices             │
│  - Obsidian vault sync via fs                   │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  DATA LAYER (SQLite)                            │
│  /var/data/studex-wellness.db                  │
│  - All tables (see database-schema.sql)        │
└──────────────────────────────────────────────────┘
```

---

## Security

- **PIN Auth:** 4-digit PIN stored as bcrypt hash in `users` table
- **Session:** JWT token issued on PIN login, stored in localStorage
- **VM-only:** No external health data leaves the VM
- **Telegram:** Bot token for notifications only

---

## Cron Jobs Summary

| Job | Cron (SAST) | UTC Cron | Action |
|-----|------------|----------|--------|
| Water reminder | Every hour 7am–6pm | `0 5-16 * * *` | Telegram: log water |
| Meal reminder | Every 3h from 7am | `0 4/3 * * *` | Telegram: meal check |
| Morning briefing | 6am | `0 4 * * *` | Health advisor AI report |
| Daily plan ritual | 7am | `0 5 * * *` | Telegram + dashboard prompt |
| Agent board meeting | 10pm | `0 20 * * *` | Telegram: start stand-up |
| Midnight build log | Midnight | `0 22 * * *` | Archive day's work |

---

## File Structure

```
/workspace/studex-os/tumelo-health/
├── SPEC.md                  ← This file
├── database-schema.sql      ← All SQLite tables
├── backend-api.md           ← Express REST API spec
├── frontend-spec.md         ← React component specs
├── cron-jobs.md             ← Cron setup documentation
└── health-advisor-prompt.md ← LLM wellness advisor prompt
```

**To be built (Phase 2):**
```
backend/
├── server.js
├── routes/api.js
├── routes/auth.js
├── services/vision.js
├── services/parser.js
├── services/elevenlabs.js
├── services/obsidian.js
├── services/wellness-advisor.js
├── db/database.js
├── db/schema.sql
└── .env.example
frontend/
├── package.json
├── vite.config.js
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── components/
│   ├── pages/
│   └── styles/
└── index.html
```
