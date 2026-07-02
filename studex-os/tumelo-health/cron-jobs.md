# Tumelo Wellness OS — Cron Jobs

## Overview

All cron jobs run on the VM at `67.213.119.157`.
Cron daemon: `cron` on Ubuntu.

Jobs are managed via a single cron file: `/etc/cron.d/studex-wellness`

```
# Studex Wellness OS — Tumelo Ramaphosa
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=""
```

---

## Job Definitions

### 1. Water Reminder
**Purpose:** Prompt Tumelo to log water every hour during waking hours.

```
0 5-16 * * *  root  curl -s -X POST http://localhost:3000/internal/remind/water >> /var/log/studex-cron.log 2>&1
```
**SAST:** Every hour from 7am to 6pm  
**UTC:** `0 5-16 * * *` = 5am to 4pm UTC

**Script action (`/usr/local/bin/studex-water-remind`):**
```bash
#!/bin/bash
# Sends Telegram message via bot to Tumelo
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="💧 Tumelo — time to log your water! How much did you drink in the last hour?" \
  -d reply_markup='{"inline_keyboard":[[{"text":"250ml","callback_data":"/water 250"},{"text":"500ml","callback_data":"/water 500"},{"text":"750ml","callback_data":"/water 750"}]]}'
```

---

### 2. Meal Reminder
**Purpose:** Check in every 3 hours during meal windows.

```
0 4/3 * * *  root  curl -s -X POST http://localhost:3000/internal/remind/meal >> /var/log/studex-cron.log 2>&1
```
**SAST:** Every 3 hours starting 7am → 7am, 10am, 1pm, 4pm  
**UTC:** `0 4/3 * * *` = 4am, 7am, 10am, 1pm, 4pm UTC

**Script action:**
```bash
#!/bin/bash
# Determines meal slot from hour and sends appropriate reminder
HOUR_UTC=$(date +%H)
if [ "$HOUR_UTC" = "04" ]; then
  MSG="🍳 Breakfast time! Have you logged your breakfast yet?"
elif [ "$HOUR_UTC" = "07" ]; then
  MSG="🥗 Lunch time! What are you having for lunch?"
elif [ "$HOUR_UTC" = "10" ]; then
  MSG="🍖 Supper time! Log your evening meal."
elif [ "$HOUR_UTC" = "13" ]; then
  MSG="🍎 Snack check — any food or drinks since supper?"
fi

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="${MSG}"
```

---

### 3. Morning Health Advisor Briefing
**Purpose:** Generate and deliver the AI health advisor report at 6am SAST.

```
0 4 * * *  root  /usr/local/bin/studex-morning-briefing >> /var/log/studex-briefing.log 2>&1
```
**SAST:** 6am  
**UTC:** `0 4 * * *` = 4am UTC

**Script (`/usr/local/bin/studex-morning-briefing`):**
```bash
#!/bin/bash
set -euo pipefail

# 1. Call backend to generate briefing
RESPONSE=$(curl -s -X GET http://localhost:3000/api/health/advisor \
  -H "X-Internal-Secret: ${INTERNAL_SECRET}")

# 2. Extract markdown briefing
BRIEFING=$(echo "$RESPONSE" | jq -r '.briefing_md // empty')

# 3. Send via Telegram
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="🦁 GOOD MORNING, TUMELO — $(date +'%A %d %B %Y')

${BRIEFING}

---
🤖 Wellness Advisor | Studex OS" \
  -d parse_mode="Markdown"

# 4. Optionally generate voice audio via ElevenLabs and send as voice message
curl -s -X POST "http://localhost:3000/api/tts/speak" \
  -H "X-Internal-Secret: ${INTERNAL_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"text": "Good morning Tumelo. Your daily health briefing is ready.", "voice": "wellness"}' \
  -o /tmp/briefing_audio.mp3

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendAudio" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d audio=@/tmp/briefing_audio.mp3
```

---

### 4. Daily Plan Ritual (9am SAST)
**Purpose:** Prompt Tumelo to do his morning planning ritual.

```
0 5 * * *  root  /usr/local/bin/studex-daily-plan >> /var/log/studex-cron.log 2>&1
```
**SAST:** 7am (shown as 9am SAST = 7am SAST offset by 2h convention)  
**UTC:** `0 5 * * *` = 5am UTC

> **Note:** SAST is UTC+2. 9am SAST = 7am UTC.  
> Cron `0 7 * * *` would be 9am SAST. Using `0 7 * * *` for the actual 9am SAST intent.

**Revised (recommended):**
```
0 7 * * *  root  /usr/local/bin/studex-daily-plan >> /var/log/studex-cron.log 2>&1
```

**Script:**
```bash
#!/bin/bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="📋 Tumelo — good morning! Time for your daily planning ritual.

What are your top priorities for today?
• Business goals
• Agent tasks
• Personal

Open your dashboard: http://67.213.119.157:3001/plan

Or just reply here with your plan and I'll log it for you." \
  -d reply_markup='{"inline_keyboard":[[{"text":"📋 Open Dashboard","url":"http://67.213.119.157:3001/plan"}]]}'
```

---

### 5. Agent Board Meeting (10pm SAST)
**Purpose:** Signal the start of the daily agent stand-up.

```
0 20 * * *  root  /usr/local/bin/studex-board-meeting >> /var/log/studex-cron.log 2>&1
```
**SAST:** 10pm (UTC+2)  
**UTC:** `0 20 * * *` = 8pm UTC

**Script:**
```bash
#!/bin/bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="🦁 BOARD MEETING TIME — 10pm SAST

All agents — prepare your stand-up:
• Robusca
• Charlie
• Naledi
• Delivery Agent

Agenda:
1. Yesterday's work
2. Today's goals
3. Blockers
4. Midnight build plan

Open: http://67.213.119.157:3001/board

Agents — start speaking. 🗣️" \
  -d reply_markup='{"inline_keyboard":[[{"text":"🏛️ Open Board Room","url":"http://67.213.119.157:3001/board"}]]}'
```

---

### 6. Midnight Build Log
**Purpose:** Archive what was built/implemented today and notify Tumelo.

```
0 22 * * *  root  /usr/local/bin/studex-midnight-log >> /var/log/studex-midnight.log 2>&1
```
**SAST:** Midnight (12am SAST)  
**UTC:** `0 22 * * *` = 10pm UTC

> **Note:** There are two interpretations here. If 10pm SAST is "midnight build time" (when the agents do their build), use `0 22 * * *`. If it's truly midnight SAST, use `0 22 * * *` UTC+2 = 10pm UTC → midnight SAST. Correct.

**Script:**
```bash
#!/bin/bash
TODAY=$(date +%Y-%m-%d)

# Collect agent midnight build reports from DB
REPORTS=$(curl -s -X GET "http://localhost:3000/api/agents/board-meeting" \
  -H "X-Internal-Secret: ${INTERNAL_SECRET}" \
  | jq -r '.reports[] | "🤖 \(.agent_name): \(.midnight_build // "Nothing built today")"')

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="🌙 MIDNIGHT BUILD — ${TODAY}

What was shipped today?

${REPORTS}

---
Good night, Tumelo. Sleep well. 🦁" \
  -d parse_mode="HTML"
```

---

## Cron File: `/etc/cron.d/studex-wellness`

```cron
# Studex Wellness OS — Tumelo Ramaphosa
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=""

# Water reminder: every hour 7am–6pm SAST (5am–4pm UTC)
0 5-16 * * *  root  /usr/local/bin/studex-water-remind >> /var/log/studex-cron.log 2>&1

# Meal reminder: every 3 hours starting 7am SAST (4am UTC)
0 4/3 * * *   root  /usr/local/bin/studex-meal-remind >> /var/log/studex-cron.log 2>&1

# Morning briefing: 6am SAST (4am UTC)
0 4 * * *      root  /usr/local/bin/studex-morning-briefing >> /var/log/studex-briefing.log 2>&1

# Daily plan ritual: 9am SAST (7am UTC)
0 7 * * *      root  /usr/local/bin/studex-daily-plan >> /var/log/studex-cron.log 2>&1

# Agent board meeting: 10pm SAST (8pm UTC)
0 20 * * *     root  /usr/local/bin/studex-board-meeting >> /var/log/studex-cron.log 2>&1

# Midnight build log: midnight SAST (10pm UTC)
0 22 * * *     root  /usr/local/bin/studex-midnight-log >> /var/log/studex-midnight.log 2>&1
```

---

## Environment Variables

Set these in `/etc/environment` or `/etc/profile.d/studex.sh`:

```bash
# /etc/profile.d/studex.sh
export TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
export TELEGRAM_CHAT_ID="NEED_TELEGRAM_CHAT_ID"
export INTERNAL_SECRET="random-secure-string-for-internal-calls"
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export OBSIDIAN_VAULT_PATH="/workspace/studex-obsidian-vault"
export DB_PATH="/var/data/studex-wellness.db"
export JWT_SECRET="random-jwt-secret-32chars"
```

---

## Telegram Setup

1. Create bot via @BotFather → get `BOT_TOKEN`
2. Get Tumelo's `CHAT_ID`:
   - Start chat with bot
   - Send `/start`
   - `curl https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` → extract `chat.id`
3. Configure webhook or long-polling in backend

---

## Cron Validation

After installing, verify:
```bash
# Check cron is running
sudo systemctl status cron

# List installed crons
sudo crontab -l

# Check cron logs
sudo tail -f /var/log/syslog | grep CRON

# Test a job manually
/usr/local/bin/studex-water-remind
```

---

## SAST ↔ UTC Conversion Reference

| SAST Time | UTC Time | Cron Expression |
|-----------|----------|----------------|
| 6am | 4am | `0 4 * * *` |
| 7am | 5am | `0 5 * * *` |
| 9am | 7am | `0 7 * * *` |
| 7pm–6pm (hourly) | 5am–4pm (hourly) | `0 5-16 * * *` |
| 7am, 10am, 1pm, 4pm | 5am, 8am, 11am, 2pm | `0 4/3 * * *` |
| 10pm | 8pm | `0 20 * * *` |
| 12am (midnight) | 10pm | `0 22 * * *` |

> **Formula:** SAST = UTC + 2  
> To run at X SAST → run at (X-2) UTC
