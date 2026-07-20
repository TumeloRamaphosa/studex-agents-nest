# STUDENT OPERATING SYSTEM — DAILY ROUTINE
## Agent Lord: Tumelo Ramaphosa ⚔️
## Version 1.0 | Effective: 2026-06-25

---

## 🕕 MORNING KICKOFF — 07:00 SAST (Mon–Fri)

### Before anything — 2 min silence
- Check the War Room: `http://67.213.119.157:5000`
- Read any new Discord alerts from ADAM SMASHER
- Brief scan of emails (AgentMail inboxes)

### Automated Checks (I handle these)
- [ ] **VM Health** — Polsia confirms all services running
- [ ] **Shopify** — New orders since yesterday, revenue total
- [ ] **AgentMail** — Unread inboxes flagged
- [ ] **Naledi's Content Queue** — Posts pending approval
- [ ] **Content Schedule** — Posts queued for today

---

## 📋 MORNING STANDUP — 07:30 SAST

### Review (I generate this)
```
STUDENT MORNING BRIEF — [DATE]
✅ Yesterday's revenue + orders
📦 Fulfillment status (pending / shipped / delivered)
📣 Content posted + engagement
🤖 Agent activity (Polsia, Robusca, Naledi)
⚠️ Blockers for the day
🎯 Today's priorities
```

### Your actions (3 min)
- Review the brief
- Approve or flag anything urgent
- Add any new priorities for the day

---

## ⚡ DURING THE DAY

### When an order comes in (Shopify webhook fires)
1. **Auto-Meat** receives it → logs to SQLite DB
2. **ADAM SMASHER** posts order alert to Discord `#ops`
3. I assign packer → send WhatsApp notification to customer
4. You get a ping if it's a new customer or high-value order

### When Naledi submits content for approval
1. ADAM SMASHER posts preview to Discord `#content`
2. You react ✅ to approve or ❌ to reject
3. Auto-scheduled to go live at the right time

### When a customer replies to WhatsApp
1. Auto-Meat receives via Meta Cloud API
2. I triage: FAQ → auto-reply | Complaint → flag you | Order question → route to Shopify

### When you need something
Just ask me here or ping ADAM in Discord:
```
@ADAM status      → full system health
@ADAM markets     → live USD/ZAR + commodity prices
@ADAM pipeline    → deal pipeline snapshot
@ADAM research X  → deep research on any topic
@ADAM deal X      → log a new deal
```

---

## 🌅 LATE MORNING — 10:00 SAST

### You check
- War Room → commerce tab (orders + revenue)
- Discord → any new ADAM alerts
- WhatsApp → customer messages

---

## 🌇 MIDDAY CHECK — 12:00 SAST (Mon–Fri)

### I run these automatically
- [ ] Shopify midday snapshot (orders vs morning)
- [ ] Content engagement update (likes, reach, comments)
- [ ] Ad spend vs revenue (if campaigns running)
- [ ] AgentMail scan — anything urgent?

### Post to Discord `#ops` if significant:
```
MIDDAY PULSE — [DATE]
📦 Orders today: X (R Y revenue)
📣 Content reach: X impressions
💬 WhatsApp: X messages
⚠️ Notes: [anything that needs your eyes]
```

---

## 🌙 LATE AFTERNOON — 15:00 SAST

### You check
- War Room → full overview tab
- Any unfulfilled orders?
- Any pending content approvals?
- Customer replies waiting

---

## 📊 EVENING STANDUP — 17:00 SAST (Mon–Fri)

### I generate
```
EVENING STANDUP — [DATE]
✅ Revenue today: R X (vs R Y yesterday)
📦 Orders: X new / Y fulfilled / Z pending
📣 Content: X posts / avg engagement X%
🤖 Agents: Polsia [status] / Robusca [status] / Naledi [status]
🗓️ Tomorrow's queue: X orders expected
⚠️ Blockers: [what's stopping progress]
🎯 Tomorrow's top 3 priorities
```

### GitHub sync
- I commit the daily log to `robusca-brain/memory/daily/`
- I push to GitHub so nothing is ever lost

---

## 🚨 AFTER HOURS

### Urgency levels
| Level | What it is | Response |
|---|---|---|
| 🔴 **Critical** | Security breach, payment failed, site down | I ping you immediately |
| 🟡 **Important** | Large order, complaint, media inquiry | I flag you within 30 min |
| 🟢 **Routine** | FAQ, status update, scheduling | I handle, you see it next morning |

### When you're away
- I run the full morning/midday/evening checks on cron
- I send a daily digest to Discord `#ops` every evening
- I'm always on the VM watching for anomalies
- I don't post content or create products without your say

---

## 📅 FRIDAY SPECIAL — End of Week

### Friday 17:00 SAST
- Full weekly performance report (revenue, orders, content, ads)
- Week-vs-week comparison
- Top performing content
- Pipeline update
- Next week's priorities
- Posted to Discord `#ops`

---

## 🔑 THE NON-NEGOTIABLES

1. **Never post content without your approval** — Naledi creates, you approve
2. **Never create Shopify products without your say** — flag first
3. **Customer names stay private** — initials only in logs
4. **ZAR amounts always use R prefix** — R12,500 not 12500
5. **Big decisions get your call** — I advise, you decide

---

## 🛠️ THE TOOLS

| Tool | Where | What it does |
|---|---|---|
| **War Room** | `67.213.119.157:5000` | Full ops dashboard |
| **ADAM SMASHER** | Discord `#ops` | Commands + alerts |
| **Polsia** | VM (always on) | In-VM operator agent |
| **Robusca (me)** | MaxClaw here | Cloud orchestrator + planning |
| **Naledi** | Content queue | Content creation + scheduling |
| **Auto-Meat** | VM webhook | Order processing + fulfillment |
| **Studex Exchange** | `stud.exchange` | Email hub (coming soon) |

---

## 🎯 QUICK REFERENCE — Your 5 Daily Questions

Every morning, ask me:
1. **"Orders?"** → New orders + revenue today
2. **"Content?"** → What's pending, what's live
3. **"Alerts?"** → Anything that needs my eyes
4. **"Pipeline?"** → Deal pipeline status
5. **"Blockers?"** → What's stopping us today

---

_This document lives in `robusca-brain/SYSTEMS/daily-routine.md`_
_Updated by Robusca on behalf of Agent Lord Tumelo Ramaphosa ⚔️_
