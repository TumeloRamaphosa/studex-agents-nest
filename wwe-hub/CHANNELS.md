# WWE Hub — ClickClack Channel Setup
*Studex Hub OS — Multi-Agent Operations Layer*

---

## Workspace Structure

**Workspace name:** `WWE Hub`
**Owner:** Tumelo Ramaphosa
**Access:** Invite-only (no public guest access)

---

## Channels to Create

### 🏠 Hub HQ — All Franchisees + Tumelo
| Channel | Purpose |
|---------|---------|
| `#announcements` | Tumelo broadcasts — weekly plans, new features, milestones |
| `#general` | General chat for all hub members and agents |
| `#help-desk` | Franchisees ask questions — agents and Tumelo respond |

### 📣 Per-Franchisee Channels (create one per franchisee)
| Channel | Purpose |
|---------|---------|
| `#franchisee-tumelo` | Tumelo's personal ops — Charlie + his agents |
| `#franchisee-{name}` | Each franchisee's dedicated channel + their agents |
| `#tiger-ai-ops` | Tiger's franchise — their agents + Tumelo |
| `#melrose-ai-ops` | Melrose franchise — etc. |

### ☕ Business Units (Tumelo's own ops)
| Channel | Purpose |
|---------|---------|
| `#ops-studex-meat` | Charlie + Naledi — biltong orders, dispatch, content |
| `#ops-coffee` | Coffee buyer outreach, supplier comms |
| `#ops-content` | Naledi — content planning, posting queue |
| `#ops-orders` | Charlie — order processing, fulfilment alerts |

### 🧠 Learning & Coaching
| Channel | Purpose |
|---------|---------|
| `#coaching` | Coach threads — Friday wrap-ups, guest coach sessions |
| `#learn-sessions` | Shared learning resources, notes from sessions |
| `#founders-lounge` | Founders Day Friday — wins, challenges, community |

### 🔧 Technical / DevOps
| Channel | Purpose |
|---------|---------|
| `#alerts` | Agent error alerts, VM health pings |
| `#deployments` | New agent deployments, VM provisioning |

---

## Bot Token Setup (per agent)

Each OpenClaw agent needs a bot token to connect to ClickClack.

### Create a bot token (CLI on ClickClack server):
```bash
docker exec clickclack clickclack admin bot create \
  --name "Charlie — Studex Ops" \
  --description "Studex Meat operations agent"
```

### Agent environment variables:
```bash
CLICKCLACK_URL=https://hub.studexmeat.com   # Your ClickClack instance
CLICKCLACK_TOKEN=ccb_...                    # Bot token from above
CLICKCLACK_CHANNEL_ID=chn_...               # Default channel ID
```

---

## Agent-to-Agent Communication Protocol

### Standard message formats:

**Agent reports to channel:**
```
[STUDEX-MEAT|Charlie] New order received: #STUD-0042
Customer: Lwandile M.
Items: 1× Wagyu Biltong 500g + 1× Droëwors
Total: R 895
Status: PENDING → PACKING
```

**Agent requests approval:**
```
[STUDEX-MEAT|Charlie] ⚠️ Approval needed:
Order #STUD-0041 — bulk request R 4,200
Customer: Nkosinathi M. (new client)
Request: 10× Wagyu Biltong + 2× Caviar tins
Buffer: 20% above standard margin
→ @tumelo approve or reject?
```

**Franchisee agent reports:**
```
[TIGER-AI|FranchiseeBot] 📊 Weekly Summary — Tiger AI
New leads: 3 (via website form)
Orders: 1 completed (R 2,400)
Open tasks: 7
Agent status: ✅ All systems operational
```

---

## Human ↔ Agent Interaction

### Humans mention agents to get their attention:
```
@tumelo can you check if Charlie has processed order #STUD-0041?
@coaching-bot what's the learning topic for this Friday?
```

### Agents wake on:
- Direct mention: `@agentname`
- Keyword triggers in any channel
- Scheduled time (cron)
- Webhook from external services (Shopify order, email received)

### Reply format:
```
[STUDEX-MEAT|Charlie] @nkosinathi — order #STUD-0041
is confirmed and will be dispatched tomorrow by 10am.
Tracking will be sent via WhatsApp once collected.
```

---

## Setting Up Per-Franchisee Agents

Each franchisee VM runs OpenClaw connected to ClickClack:

```bash
# On each franchisee VM:
# 1. Install OpenClaw
# 2. Set env vars:
export CLICKCLACK_URL=https://hub.studexmeat.com
export CLICKCLACK_TOKEN=ccb_franchisee_bot_token
export CLICKCLACK_CHANNEL_ID=chn_franchisee_channel_id
export FRANCHISEE_NAME="Tiger AI"
export FRANCHISEE_OWNER="Your Name"

# 3. Configure OpenClaw to send daily summaries to ClickClack
# 4. Configure OpenClaw to read franchisee channel for instructions
```

---

## Tumelo's Hub OS Dashboard

The War Room or a dedicated page shows:
- All franchisee channels + last activity
- Agent health (up/down)
- Open approvals waiting for Tumelo
- Daily summary across all businesses

This becomes your single pane of glass for the entire hub.

---

*Built: 2026-07-12 · WWE Hub OS*
