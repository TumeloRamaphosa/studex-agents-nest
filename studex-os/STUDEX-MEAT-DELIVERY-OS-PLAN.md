# Studex Meat — Delivery OS Upgrade Plan
**CEO: Meat B@ye | Planner: Robusca | Date: 2026-06-29**

---

## 1. WHAT WE'RE BUILDING

A unified **Delivery OS** layered on top of the existing Studex OS:

```
Shopify Order (studexmeat.com)
    ↓ webhook
Charlie (orchestrator @ port 3001)
    ↓
[NEW] Delivery Agent (sub-agent, 15-min cycles)
    ↓
Delivery Pipeline (Kanban board in OS)
    ↓
WhatsApp to client + driver
    ↓
Memory log (who/what/when — agent or human)
```

---

## 2. CONTACTS & PROVIDERS (Source of Truth)

### Delivery Companies
| Company | Contact | Phone | WhatsApp Group |
|---------|---------|-------|---------------|
| **Dinkoko Pty** | Derrick Selepe | +27 67 681 3076 | ✅ Yes — existing |
| **My Courier** | Willy | +27 61 362 3448 | ❌ |

### Suppliers
| Supplier | Phone | Address |
|----------|-------|---------|
| **Silent Valley** | +27 71 346 5083 | 190 Rooiberg St, N4 Gateway Park, The Willows |
| **Noags Butchery** | — | 19 Pomona Rd, Pomona AH, Kempton Park, 1623 |

### Moutloe Farm (existing provenance)
- Farm shown on product pages (traceability)
- Keep as trust signal

---

## 3. DELIVERY KANBAN — BOARD DESIGN

### Columns
```
[📥 New Order] → [📦 Packed] → [🚚 Dispatched] → [🏁 Delivered] → [✅ Done]
[🔴 Cancelled]
```

### Per-Card Fields
- Order number (from Shopify)
- Customer name + address
- Items
- Delivery company assigned
- Driver name + phone
- **ETA** (Google Maps Routes API)
- **Status** (colour-coded)
- **Memory log** (collapsed by default, expands on click)
- **Assigned by** (team member or agent)
- **Last updated by** + timestamp

### Memory Log (per card)
```
[2026-06-29 08:42] 🤖 Charlie: Order assigned to Dinkoko — Derrick notified
[2026-06-29 08:45] 👤 Tumelo: Updated driver phone number
[2026-06-29 09:10] 🤖 Delivery Agent: Client notified via WhatsApp
[2026-06-29 09:30] 🤖 Charlie: Marked as dispatched
```

### Team Access
- Read/write via web UI (studex-os)
- Role-based: Viewer / Operator / Admin
- All team edits logged automatically

---

## 4. GOOGLE MAPS INTEGRATION

### What we use
- **Google Maps Routes API** — ETAs for delivery
- **Google Geocoding API** — convert addresses to lat/long
- Free tier: 28,000 calls/month (generous for SA meat delivery)

### What it does
- On order receive: geocode customer address
- Assign to nearest routing point
- Calculate delivery ETA (traffic-aware)
- Show on Kanban card: "ETA: 14:30 SAST"
- Colour-coded urgency: 🟢 >2hr | 🟡 1-2hr | 🔴 <1hr

### Setup (Tumelo does this)
1. Go to https://console.cloud.google.com
2. Create project "Studex Meat"
3. Enable Maps JavaScript API + Routes API
4. Create API key with HTTP restrictions
5. Give key to Robusca

---

## 5. WHATSAPP INTEGRATION (WhatApp Business)

### Goal: Two-way client comms via WhatApp group

**Option A — WhatApp Business API (official, scalable)**
- Connect to existing Meta Business account
- Use OpenWA or WhatsApp's API
- Issues: phone number may be blocked (per earlier session notes)

**Option B — WhatApp group relay (workaround)**
- Add a relay WhatsApp number to the WhatApp group
- OpenWA reads group messages → triggers agent actions
- Agent posts updates to group as "Studex Meat Bot"
- ✅ Preferred — faster to implement

**Option C — WhatApp click-to-chat links**
- Generate `https://wa.me/27XXXXXXXXX?text=...` links
- No API needed — just link in delivery card
- Client taps → opens WhatsApp with pre-filled message

### Implementation (this week — Option B first)
1. Install OpenWA on VM (Docker, port 2785)
2. Add relay number to WhatApp group with Derrick
3. OpenWA MCP tool reads group → forwards to Delivery Agent
4. Delivery Agent posts status updates to group

### Client notifications (automated)
- "Hi [Name], your order #[XXXX] is confirmed! ETA: [TIME]"
- "Your order is packed and being collected by [Driver] at [TIME]"
- "Your order is on its way! Track: [link]"
- "Delivered! Enjoy your [product]. Review us: [link]"

---

## 6. DELIVERY AGENT — Sub-Agent Spec

### Role
**Name:** `delivery-agent` | **AKA:** Delivery B@ye  
**Personality:** Hyper-organized, SMS-style short updates, proactive  
**Reports to:** Charlie (orchestrator) + Robusca CEO  

### Skills (from ravila4/claude-adhd-skills)
```
- task check-everything: runs every 15 min
- daily digest: sends Robusca morning briefing
- flag-and-forward: escalate delays immediately
```

### Tasks (loop, 15-min interval)
```
1. Poll Shopify API (new orders since last check)
2. For each new order:
   a. Validate address (geocode check)
   b. Determine routing zone
   c. Assign delivery company (rules: zone-based)
   d. Post to Delivery Kanban (Charlie updates board)
   e. Send WhatsApp to Derrick/Willy via WhatApp group
   f. Send client confirmation WhatsApp
3. Check in-transit orders — update ETAs
4. Flag delayed orders to Charlie + Robusca
5. Daily 17:00 SAST: send delivery report to Robusca
```

### Assignment Rules
```
Customer in JHB metro + < 15km from warehouse → My Courier (cheaper)
Customer outside JHB / rural → Dinkoko (full-service)
Large orders (>R2000) → Dinkoko Priority
```

### Escalation Rules
```
Order not dispatched within 2hrs of packing → Flag to Charlie
ETA missed by >30 min → WhatsApp Robusca immediately
Driver unreachable → Switch provider + notify client
```

---

## 7. NEW ORDER FLOW (Full Chain)

```
Customer places order (studexmeat.com)
    ↓ Shopify webhook (order/create)
Charlie receives
    ↓
Delivery Agent activated (sub-agent)
    ↓ checks every 15 min
Assign delivery company (rules above)
    ↓
Kanban card created in [📥 New Order]
    ↓
WhatsApp sent to Derrick/Willy (WhatApp group relay)
    ↓
Client receives WhatsApp confirmation + ETA
    ↓
Team packs order + marks [📦 Packed]
    ↓
Driver collects + team marks [🚚 Dispatched]
    ↓
Delivery Agent sends tracking WhatsApp to client
    ↓
Driver delivers + team marks [🏁 Delivered]
    ↓
24hr later: Delivery Agent sends review request
    ↓
Kanban card moves to [✅ Done]
```

---

## 8. EXISTING ASSETS TO BUILD ON

| Asset | What It Does | Use For Delivery OS |
|-------|-------------|-------------------|
| `studex-kanban/` | Kanban board (TypeScript/React) | Delivery pipeline UI |
| `studex-auto-meat/` | Shopify webhook → fulfiller agent | Order intake base |
| `studex-os/control-plane/` | Agent registry | Register Delivery Agent |
| `orchestrix/` | Matrix/agent messaging | Charlie ↔ Delivery Agent comms |
| OpenWA (needs install) | WhatsApp gateway | Client notifications |

---

## 9. WHAT I CAN BUILD THIS WEEK

### Phase 1 — Foundation (Robusca builds now)
- [ ] Update `studex-kanban/` — add delivery columns, ETA field, memory log
- [ ] Write Delivery Agent prompt (sub-agent spec)
- [ ] Write delivery assignment rules engine
- [ ] Design WhatsApp message templates
- [ ] Write Shopify → Charlie webhook handler spec

### Phase 2 — Integration (Requires Tumelo input)
- [ ] Google Maps API key → add to VM env
- [ ] Shopify Access Token → activate shopify-agent
- [ ] OpenWA setup on VM (or WhatApp relay)
- [ ] WhatApp group relay number

### Phase 3 — Activation
- [ ] Spawn Delivery Agent (sub-agent on MaxClaw)
- [ ] Connect to Charlie on Orgo VM
- [ ] Test full order flow end-to-end
- [ ] Train team on Kanban

---

## 10. WHAT I NEED FROM TUMELO

| Item | Who | How | Urgency |
|------|-----|-----|---------|
| Shopify Admin API token | Tumelo | Shopify Admin → Apps → Dev app | 🔴 Now |
| Google Maps API key | Tumelo | Cloud Console (free tier) | 🔴 Now |
| WhatApp relay number (SIM/number) | Tumelo | Any SA number not on WhatsApp Business | 🟡 Soon |
| OpenWA hosting decision | Tumelo | Use existing VM or new? | 🟡 Soon |
| Meta Business verify | Tumelo | For WhatApp Business API | 🟡 When ready |

---

## 11. IDENTITY — CEO of Studex Meat

> **Name:** Meat B@ye  
> **Role:** CEO of Studex Meat  
> **Vibe:** No nonsense, moves fast, cares about the steak  
> **Persona:** You're the one in charge. Delivery Agent is your operative. Charlie is your right hand. You see everything.  

This is me — I'll update my SOUL.md to reflect this.

---

## 12. MEMORY LOG — Agent/Team Audit Trail

Every Kanban card gets a timestamped log. Every action has an actor tag:
- `🤖 [Agent name]` — automated action
- `👤 [Human name]` — manual edit
- `🔄 [System]` — Shopify webhook triggered

Format:
```
[TIMESTAMP] [ACTOR] Action description
```

Stored in: per-card JSON + daily aggregate in `studex-os/memory/delivery/`

---

*Plan by Robusca for Meat B@ye — 2026-06-29*