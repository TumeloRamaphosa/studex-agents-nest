# WWE Hub — OpenClaw Agent Integration Guide
*How to connect each OpenClaw agent to ClickClack*

---

## Architecture Overview

```
Tumelo (Human) ←——— ClickClack ←———→ Charlie (OpenClaw — Studex Ops)
     ↑                                    ↓
     ←—— Naledi (OpenClaw — Content) ———↓
     ←—— Franchisee Agent A (OpenClaw — Their VM)
     ←—— Franchisee Agent B (OpenClaw — Their VM)
     ←—— Coffee Jarvis (OpenClaw — Coffee unit)
```

Each OpenClaw agent connects to ClickClack via:
1. **Webhook** (OpenClaw → ClickClack push messages)
2. **REST API polling** (agent reads channel periodically)
3. **Agent-to-agent direct** (agents communicate via shared memory)

---

## 1. Install ClickClack Bot SDK on Each VM

```bash
# On the VM running OpenClaw
cd ~/robusca/robusca-brain
npm install @clickclack/sdk   # or the published package name
```

Or use the agent-friendly CLI built into ClickClack:

```bash
# Read last N messages from a channel
CLICKCLACK_URL=https://hub.studexmeat.com \
CLICKCLACK_TOKEN=ccb_xxx \
  clickclack messages list --channel franchisee-tumelo --limit 10

# Post a message
CLICKCLACK_URL=https://hub.studexmeat.com \
CLICKCLACK_TOKEN=ccb_xxx \
  clickclack send --channel ops-studex-meat "Charlie: Order #STUD-0042 dispatched ✅"
```

---

## 2. OpenClaw Agent Configuration

In your OpenClaw config (via gateway tool):

```json
{
  "agents": {
    "charlie": {
      "clickclack": {
        "url": "https://hub.studexmeat.com",
        "token": "ccb_xxx",        // Bot token from ClickClack admin
        "channel": "ops-studex-meat",
        "mention_channel": "ops-studex-meat"
      }
    },
    "naledi": {
      "clickclack": {
        "url": "https://hub.studexmeat.com",
        "token": "ccb_yyy",
        "channel": "ops-content",
        "mention_channel": "ops-content"
      }
    }
  }
}
```

---

## 3. What Each Agent Does on ClickClack

### Charlie — Studex Ops Agent
```
On new Shopify order → post to #ops-studex-meat
On approval needed   → post to #ops-studex-meat with @tumelo mention
On dispatch          → post to #ops-studex-meat + update #ops-orders
On error             → post to #alerts
Daily morning report → post to #ops-studex-meat (7:00 SAST Mon-Fri)
```

### Naledi — Content & Social Agent
```
On content scheduled → post to #ops-content (what's queued)
On post published    → post to #ops-content (confirmation)
On Meta blocked      → post to #ops-content + #alerts (flag Tumelo)
Weekly content plan  → post to #ops-content every Monday
```

### Franchisee Agent (per VM)
```
On new lead         → post to #franchisee-{name} + @franchisee-owner mention
On order complete    → post to #franchisee-{name}
Daily summary       → post to #franchisee-{name} (end of day)
Weekly metrics      → post to #franchisee-{name} Friday
On VM error         → post to #alerts
```

---

## 4. Tumelo's Human Interactions

### Via ClickClack web/app:
- Browse `#ops-*` channels for business updates
- React with ✅/❌ to approve or reject agent requests
- Jump into any thread to give instructions
- Friday: join `#coaching` for wrap-up

### Via OpenClaw main session:
- Talk directly to Charlie/Naledi as normal
- Commands like "post a message to ClickClack about X"
- Review agent session logs and history

---

## 5. Webhook — Shopify → ClickClack (Order Alerts)

```javascript
// n8n workflow or serverless function
// Trigger: Shopify new order webhook
// Action: POST to ClickClack

const webhookPayload = {
  channel: "ops-studex-meat",
  text: `🛒 New Order #${order.id}\n` +
        `Customer: ${order.customer.first_name} ${order.customer.last_name}\n` +
        `Total: R ${order.total_price}\n` +
        `Items: ${order.line_items.map(i => i.title).join(", ")}\n` +
        `→ Charlie: awaiting processing`
};

await fetch(`https://hub.studexmeat.com/api/messages`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${process.env.CLICKCLACK_BOT_TOKEN}`
  },
  body: JSON.stringify(webhookPayload)
});
```

---

## 6. Cross-Franchisee Visibility (Tumelo-only)

Tumelo can see all channels (as workspace admin). Franchisees only see their own franchisee channel.

```
Tumelo sees: all #franchisee-* + all #ops-* + #hub-hq
Franchisee A sees: #franchisee-a + #hub-hq (read-only for others)
Charlie sees: #ops-studex-meat + #ops-orders + #alerts
Naledi sees: #ops-content + #ops-studex-meat + #alerts
```

---

## 7. Franchisee Onboarding Flow

```
1. New franchisee joins WWE Hub
2. Robusca provisions their VM on Orgo.ai (or they self-host)
3. OpenClaw installed on their VM
4. ClickClack bot token created by Tumelo (admin)
5. OpenClaw configured with franchisee name + ClickClack credentials
6. Franchisee channel created in ClickClack
7. Welcome message sent automatically from Tumelo's agent
8. Franchisee gets onboarding doc + channel tour
```

---

*Built: 2026-07-12 · WWE Hub OS*
