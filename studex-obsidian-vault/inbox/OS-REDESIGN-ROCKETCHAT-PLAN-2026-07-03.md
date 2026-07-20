# OS Redesign + RocketChat Mission Control — Plan
**Created:** 2026-07-03
**Status:** Active Build

---

## 1. Devin Design Language — What We're Taking

**Colors:**
- Background: `#0A0A0A` (charcoal black, not pure)
- Surface: `#111111`
- Primary text: `#FFFFFF`
- Muted text: `#666666`
- Accent: `#3AFF9F` (neon green — Devin's terminal accent)
- Gold accent: `#C9A84C` (keep from Studex brand)
- Danger: `#FF4444`

**Typography:**
- Headlines: Inter or Geist Sans (clean, modern)
- Code/mono: JetBrains Mono or Fira Code
- Body: Inter

**Visual Motifs:**
- Dot-grid background pattern (hexagonal molecular nodes)
- Thin vertical alignment lines (like code editor rulers)
- Corner registration marks (small dot clusters)
- Monospace type-writer effect for subheadlines
- Terminal cursor blink (`█`)
- No rounded corners, no gradients, no drop shadows — flat geometric

---

## 2. Bloomberg Terminal — Page Structure

### Header
- Logo (Studex gold) left
- Nav: STUDEX OS / MISSION CONTROL / COFFEE EXCHANGE / AGENTS
- Status bar: current time, system status, active agents online

### Section 1 — LIVE COMMAND TERMINAL
```
STUDEX_OS > _
> agents status
> Charlie ........... ACTIVE
> Naledi ............ IDLE
> Coffee Jarvis ...... STANDBY
> RileyJarvis ........ CONNECTED
> orders today ....... 0
> revenue today ...... R0
```
Monospace, green cursor, typewriter effect

### Section 2 — KPI STRIP (Bloomberg-style horizontal scroll)
| STUDEX MEAT | COFFEE EXCHANGE | AGENTS | REVENUE |
|-------------|-----------------|--------|---------|
| Orders: 0 | Coffee Orders: — | Active: 3 | Today: R0 |
| Revenue: R0 | Active Subs: — | Idle: 1 | MTD: R0 |
| Stock: OK | New Farmers: 1 | Total: 4 | Target: R__ |

### Section 3 — AGENT FEED (Real-time activity)
```
[14:32] Charlie ████████████████████ 100%
  → New order loop running. Shopify API pending...
  
[14:31] Naledi ████████░░░░░░░░░░░░░░░  40%
  → Posting Youth Day follow-up to Facebook...
  
[14:30] Coffee Jarvis ████████████████░░░░  85%
  → RUKUNDO price check complete. Arabica: $3.42/lb
  
[14:28] RileyJarvis ████████████████░░░░  82%
  → Connected. Awaiting command...
```

### Section 4 — MARKET DATA (Coffee futures + FX)
```
ARABICA (NY ICE)    $3.42/lb    +0.02 (+0.6%)
ROBUSTA (London)    $4.18/lb    -0.01 (-0.2%)
USD/ZAR              R18.34      +0.12 (+0.7%)
EUR/ZAR              R19.87      -0.08 (-0.4%)
```

### Section 5 — SUPPLY CHAIN (Coffee pipeline)
```
RUKUNDO COFFEE ──────────────────────────────────────
  Lot #12 Arabica    500kg    IN TRANSIT    ETA: Jul 15
  Lot #13 Robusta    300kg    CONFIRMED    Ship: Jul 20
  Lot #14 Bazzukulu  200kg    NEGOTIATING  Price: R520/kg
```

### Section 6 — CONTENT HUB (Naledi's queue)
```
Scheduled Posts:
  📅 Jul 03 09:00  Instagram  "Wagyu Biltong — Heritage Pack"  [APPROVED]
  📅 Jul 04 12:00  Facebook   "Behind the Craft: How Biltong is Made" [PENDING]
  📅 Jul 05 18:00  TikTok     @freekpik "Why Supporting Black Business is Strategy" [DRAFT]
```

### Section 7 — MISSION CONTROL (RocketChat embed)
- Live RocketChat channels: #ops, #coffee, #agents, #alerts
- Agent activity mirrored from RocketChat
- Full chat UI embedded in OS

### Section 8 — ORGO VM STATUS
```
NODE: Orgo.ai VM
STATUS: ● ONLINE
UPTIME: 99.9%
RAM: 6.2GB / 8GB
CPU: 12% avg
DISK: 22GB / 30GB
WARRROOM: https://2bhlkngegvb9.space.minimax.io
AGENTS: Charlie | Naledi | Coffee Jarvis | RileyJarvis
```

---

## 3. RocketChat — Deployment on Orgo VM

### Why RocketChat
- Self-hosted, full ownership
- Agents can have their own channels (charlie, naledi, coffee-jarvis)
- API for embedding chat widgets
- Real-time messaging + threads
- Matrix federation support
- Apps-Engine for custom integrations

### Docker Deploy (Orgo VM)
```bash
# On Orgo VM:
cd /root/rocket.chat
docker-compose up -d

# Config:
# - MongoDB + RocketChat in one compose
# - Port 3000 internally, reverse proxy via nginx
# - Domain: chat.studexmeat.com
```

### RocketChat Agent Channels
| Channel | Purpose | Agents |
|---------|---------|--------|
| #ops | Daily operations | Charlie, Naledi |
| #coffee | Coffee exchange | Coffee Jarvis, Tumelo |
| #alerts | System alerts | All agents |
| #content | Naledi's queue | Naledi, Charlie |
| #orders | Order pipeline | Charlie |
| #dev | Dev/engineering | RileyJarvis, Charlie |

### Embed in OS
```html
<!-- RocketChat chat widget embedded -->
<iframe 
  src="https://chat.studexmeat.com/channel/ops"
  style="width:100%; height:600px; border:none;">
</iframe>
```

---

## 4. Agent → RocketChat Connection

### Charlie → RocketChat
```
Charlie monitors #orders
  → New Shopify order → post to #orders
  → Confirm dispatch → update #ops
  → Low stock alert → post to #alerts
```

### Naledi → RocketChat
```
Naledi monitors #content-queue
  → New content approved → post to #content
  → Post live → update #content
  → Engagement drop → alert in #alerts
```

### Coffee Jarvis → RocketChat
```
Coffee Jarvis monitors #coffee
  → Daily price brief → posted to #coffee
  → Arbitrage opportunity → alert to #alerts
  → New RUKUNDO lot → post to #coffee
```

### RileyJarvis → RocketChat
```
RileyJarvis connects via RocketChat API
  → Receives commands from Tumelo via voice
  → Posts responses to #ops
  → Triggers other agents via channel mentions
```

---

## 5. Architecture — How It All Connects

```
                    ┌─────────────────────────────────┐
                    │   STUDEX OS  (War Room / OS)   │
                    │                                 │
  Tumelo ──────────│  ┌─────────────────────────────┐ │
  (Voice/Chat)     │  │  ROCKETCHAT EMBED / WIDGET │ │
                    │  │  #ops #coffee #alerts ... │ │
                    │  └──────────┬────────────────┘ │
                    │             │                  │
                    │  ┌──────────▼────────────────┐  │
                    │  │   AGENT LAYER (OpenClaw) │  │
                    │  │ Charlie │ Naledi │ Jarvis │  │
                    │  └──────────┬────────────────┘  │
                    │             │                  │
                    │  ┌──────────▼────────────────┐  │
                    │  │   ROCKETCHAT SERVER        │  │
                    │  │   (Orgo VM :3000)         │  │
                    │  └───────────────────────────┘  │
                    └─────────────────────────────────┘
```

---

## 6. Build Phases

### Phase 1 — OS Redesign (This Week)
- [ ] New dark theme CSS (Devin aesthetic)
- [ ] Bloomberg terminal header with live clock
- [ ] KPI strip component
- [ ] Agent activity feed component
- [ ] Market data component (coffee futures + FX)
- [ ] Deploy as new OS tab: MISSION CONTROL

### Phase 2 — RocketChat Deploy (This Week)
- [ ] Docker Compose on Orgo VM
- [ ] Nginx reverse proxy + SSL
- [ ] Agent accounts (charlie, naledi, coffee, rileyjarvis)
- [ ] Channel setup (ops, coffee, alerts, content, orders)
- [ ] API token for bot access

### Phase 3 — Agent → RocketChat Integration (Next Week)
- [ ] Charlie posts order updates to #orders via RocketChat API
- [ ] Naledi posts content status to #content
- [ ] Coffee Jarvis posts daily price brief to #coffee
- [ ] All agents post to #alerts for escalations

### Phase 4 — Embed Mission Control (Next Week)
- [ ] RocketChat iframe widget in OS
- [ ] Channel switcher (ops / coffee / alerts / content)
- [ ] Unread count badges per channel
- [ ] Agent status indicators in OS header

---

## 7. Tech Stack

| Layer | Technology |
|-------|------------|
| OS Frontend | React + Vite + TypeScript (existing War Room) |
| 3D Globe | Three.js + React Three Fiber |
| Charts | Recharts |
| Design | Custom CSS (Devin aesthetic) |
| Chat Server | RocketChat 6.x (Docker on Orgo VM) |
| Chat Embed | RocketChat iframe widget + API |
| Real-time | RocketChat WebSocket API |
| Agents | OpenClaw (Charlie, Naledi, Coffee Jarvis) |
| Agent → Chat | RocketChat REST + WebSocket API |
| Voice | RileyJarvis (Mac Mini M4) |
| VM | Orgo.ai (Ubuntu, existing) |

---

*Last updated: 2026-07-03 00:50 UTC*
