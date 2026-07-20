# Bot Integration Spec — Rocket.Chat War Room
**Studex Meat OS — Connecting Agents to War Room Channels**

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          STUDENT MEAT OS                               │
│                                                                       │
│  Shopify ──► Charlie ──► Rocket.Chat #orders ──► Robusca (pinged)     │
│              Naledi ──► Rocket.Chat #marketing                        │
│         Delivery ──► Rocket.Chat #delivery                             │
│           Robusca ──► Rocket.Chat #ceo ──► Tumelo (push)             │
│                                                                       │
│  MaxClaw ──► OpenClaw Gateway ──► Rocket.Chat (webhook) ──► War Room │
│                                                                       │
│  Rocket.Chat runs on: 67.213.119.157:3000 (VM)                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Agent API Setup

### Step 1: Get Personal Access Tokens

1. Login to Rocket.Chat as each bot user
2. Go to: **Profile** → **Tokens** → **Create Personal Access Token**
3. Name: `studex-war-room`
4. Copy **Token** and **User ID**
5. Store in VM environment:

```bash
# Add to /root/.bashrc or /root/studex-os/war-room/.env on the VM

# Charlie
export ROCKET_CHARLIE_TOKEN="your_token_here"
export ROCKET_CHARLIE_USER_ID="your_user_id_here"

# Naledi
export ROCKET_NALEDI_TOKEN="your_token_here"
export ROCKET_NALEDI_USER_ID="your_user_id_here"

# Delivery Agent
export ROCKET_DELIVERY_TOKEN="your_token_here"
export ROCKET_DELIVERY_USER_ID="your_user_id_here"

# Robusca
export ROCKET_ROBUSCA_TOKEN="your_token_here"
export ROCKET_ROBUSCA_USER_ID="your_user_id_here"

# Rocket.Chat server
export ROCKET_URL="http://67.213.119.157:3000"
```

---

## Universal Rocket.Chat Client (`rc-client.js`)

All agents use this shared client. Deploy once on the VM or include in each agent's codebase.

```javascript
// /root/studex-os/war-room/rc-client.js
// Shared Rocket.Chat API client for all Studex Meat agents

class RocketChatClient {
  constructor({ token, userId, serverUrl = 'http://67.213.119.157:3000' }) {
    this.token = token;
    this.userId = userId;
    this.serverUrl = serverUrl;
    this.apiBase = `${serverUrl}/api/v1`;
  }

  async request(method, endpoint, body = null) {
    const headers = {
      'Content-Type': 'application/json',
      'X-Auth-Token': this.token,
      'X-User-Id': this.userId,
    };
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${this.apiBase}${endpoint}`, opts);
    const json = await res.json();
    if (!json.success) throw new Error(json.error || JSON.stringify(json));
    return json;
  }

  /** Post a message to a channel or DM */
  async postMessage({ channel, text, alias, emoji, attachments = [] }) {
    return this.request('POST', '/chat.postMessage', {
      channel,
      text,
      alias: alias || undefined,
      emoji: emoji || undefined,
      attachments,
    });
  }

  /** Post a message AND pin it (for important alerts) */
  async postAlert({ channel, text, alias = 'Robusca', emoji = ':warning:' }) {
    const result = await this.postMessage({ channel, text, alias, emoji });
    if (result.message?._id) {
      await this.pinMessage(result.message._id);
    }
    return result;
  }

  /** Pin a message (for alerts) */
  async pinMessage(messageId) {
    return this.request('POST', `/chat.pinMessage`, { messageId });
  }

  /** React to a message */
  async react({ messageId, emoji }) {
    return this.request('POST', '/chat.react', {
      messageId,
      emoji,
    });
  }

  /** Get recent messages in a channel */
  async getMessages(channel, { limit = 20 } = {}) {
    return this.request('GET', `/channels.history?roomName=${channel}&count=${limit}`);
  }

  /** Create a new channel */
  async createChannel({ name, members = [], private: isPrivate = true }) {
    return this.request('POST', isPrivate ? '/channels.create' : '/groups.create', {
      name,
      members,
    });
  }

  /** Get user info */
  async me() {
    return this.request('GET', '/me');
  }
}

// ── Factory functions for each agent ──────────────────────────────────
function createCharlieBot() {
  return new RocketChatClient({
    token: process.env.ROCKET_CHARLIE_TOKEN,
    userId: process.env.ROCKET_CHARLIE_USER_ID,
  });
}

function createNalediBot() {
  return new RocketChatClient({
    token: process.env.ROCKET_NALEDI_TOKEN,
    userId: process.env.ROCKET_NALEDI_USER_ID,
  });
}

function createDeliveryBot() {
  return new RocketChatClient({
    token: process.env.ROCKET_DELIVERY_TOKEN,
    userId: process.env.ROCKET_DELIVERY_USER_ID,
  });
}

function createRobuscaBot() {
  return new RocketChatClient({
    token: process.env.ROCKET_ROBUSCA_TOKEN,
    userId: process.env.ROCKET_ROBUSCA_USER_ID,
  });
}

module.exports = { RocketChatClient, createCharlieBot, createNalediBot, createDeliveryBot, createRobuscaBot };
```

---

## Charlie → `#orders` (Shopify Order Webhook)

Charlie runs at port 3001 (on MaxClaw) or can be deployed on the VM.

### `charlie-rocket.js` — Shopify → Rocket.Chat

```javascript
// /root/studex-os/agents/charlie/charlie-rocket.js
// Charlie orchestrator — Shopify webhook → Rocket.Chat #orders

const { createCharlieBot } = require('/root/studex-os/war-room/rc-client');
const fetch = require('node-fetch');

const rc = createCharlieBot();

// Route Shopify webhook to Rocket.Chat
async function handleShopifyWebhook(order) {
  const channel = '#orders';
  const isUrgent = order.fulfillment_status === 'urgent' || 
                   order.total_price > 10000 ||
                   order.tags?.includes('RUSH');

  const emoji = isUrgent ? ':red_circle:' : ':package:';
  const targetChannel = isUrgent ? '#alerts' : '#orders';

  // Format customer name
  const customer = order.customer 
    ? `${order.customer.first_name} ${order.customer.last_name}`
    : 'Guest';

  // Format line items
  const items = order.line_items
    ?.map(item => `  • ${item.title} × ${item.quantity} — R${parseFloat(item.price).toFixed(2)}`)
    ?.join('\n') || 'No items';

  const message = `${emoji} *New Shopify Order*
━━━━━━━━━━━━━━━━━━━━
📋 Order: #${order.id}
👤 Customer: ${customer}
💰 Total: *R${parseFloat(order.total_price).toFixed(2)}*
🚦 Status: \`${order.fulfillment_status || 'unfulfilled'}\`
📦 Items:
${items}
🔗 ${order.order_status_url || ''}
━━━━━━━━━━━━━━━━━━━━
${isUrgent ? '@robusca @tummebox — *URGENT ORDER*' : '@robusca @tummebox'}`;

  try {
    const result = await rc.postMessage({
      channel: targetChannel,
      text: message,
      alias: 'Charlie',
      emoji: ':robot_face:',
    });
    console.log(`[Charlie] ✅ Posted order #${order.id} to ${targetChannel}`);
    return result;
  } catch (err) {
    console.error(`[Charlie] ❌ Failed to post to Rocket.Chat:`, err.message);
    throw err;
  }
}

// Example: Express webhook endpoint (add to Charlie's Express server)
// app.post('/webhooks/shopify', async (req, res) => {
//   const order = req.body;
//   await handleShopifyWebhook(order);
//   res.status(200).send('OK');
// });

// ── Test: post a sample order ──────────────────────────────────────────
async function testOrder() {
  await handleShopifyWebhook({
    id: 12345,
    customer: { first_name: 'Tumelo', last_name: 'Mokoena' },
    total_price: '1599.99',
    fulfillment_status: 'unfulfilled',
    line_items: [
      { title: 'Premium Lamb Chops', quantity: 2, price: '499.99' },
      { title: 'Beef Short Ribs', quantity: 1, price: '599.99' },
    ],
    order_status_url: 'https://studexmeat.myshopify.com/admin/orders/12345',
  });
}

// testOrder();
module.exports = { handleShopifyWebhook };
```

### Naledi → `#marketing` (Content Published Alert)

```javascript
// /root/studex-os/agents/naledi/naledi-rocket.js
// Naledi CMO — content published → Rocket.Chat #marketing

const { createNalediBot } = require('/root/studex-os/war-room/rc-client');

const rc = createNalediBot();

async function notifyContentPublished({ platform, contentType, caption, postUrl, reach, engagement }) {
  const platformEmoji = {
    facebook: ':facebook:',
    instagram: ':instagram:',
    twitter: ':twitter:',
    all: ':globe_with_meridians:',
  }[platform] || ':mega:';

  const message = `${platformEmoji} *Content Published*
━━━━━━━━━━━━━━━━━━━━
📣 Platform: *${platform.toUpperCase()}*
📝 Type: ${contentType}
💬 Caption: "${caption?.substring(0, 100)}${caption?.length > 100 ? '...' : ''}"
🔗 ${postUrl || ''}
📊 Reach: ${reach || 'TBD'}
💬 Engagement: ${engagement || 'TBD'}
━━━━━━━━━━━━━━━━━━━━
@robusca @tummebox`;

  try {
    return await rc.postMessage({
      channel: '#marketing',
      text: message,
      alias: 'Naledi',
      emoji: ':star:',
    });
  } catch (err) {
    console.error(`[Naledi] ❌ Failed to post to Rocket.Chat:`, err.message);
  }
}

// Trigger when content goes live
// notifyContentPublished({ platform: 'facebook', contentType: 'Promo Video', caption: '...', postUrl: '...' });
module.exports = { notifyContentPublished };
```

### Delivery Agent → `#delivery` (Status Updates)

```javascript
// /root/studex-os/agents/delivery/delivery-rocket.js
// Delivery Agent — delivery status → Rocket.Chat #delivery

const { createDeliveryBot } = require('/root/studex-os/war-room/rc-client');

const rc = createDeliveryBot();

async function notifyDeliveryUpdate({ orderId, status, driverName, eta, notes = '' }) {
  const statusEmoji = {
    picked_up: ':package:',
    in_transit: ':truck:',
    delivered: ':white_check_mark:',
    delayed: ':warning:',
    failed: ':x:',
    returned: ':leftwards_arrow_with_hook:',
  }[status] || ':information_source:';

  const statusText = {
    picked_up: 'Picked Up',
    in_transit: 'In Transit',
    delivered: 'Delivered ✅',
    delayed: 'Delayed ⚠️',
    failed: 'Delivery Failed ❌',
    returned: 'Returned to Sender',
  }[status] || status;

  const message = `${statusEmoji} *Delivery Update*
━━━━━━━━━━━━━━━━━━━━
📋 Order: #${orderId}
🚚 Status: *${statusText}*
${driverName ? `👤 Driver: ${driverName}` : ''}
${eta ? `⏱️ ETA: ${eta}` : ''}
${notes ? `📝 Notes: ${notes}` : ''}
━━━━━━━━━━━━━━━━━━━━
${['delayed', 'failed'].includes(status) ? '@robusca @tummebox' : '@robusca'}`;

  try {
    return await rc.postMessage({
      channel: '#delivery',
      text: message,
      alias: 'Delivery Agent',
      emoji: ':truck:',
    });
  } catch (err) {
    console.error(`[Delivery Agent] ❌ Failed to post to Rocket.Chat:`, err.message);
  }
}

// Trigger on each delivery status change
// notifyDeliveryUpdate({ orderId: '12345', status: 'in_transit', driverName: 'John D.', eta: '2:30 PM' });
module.exports = { notifyDeliveryUpdate };
```

### Robusca → `#ceo` (Daily Briefing)

```javascript
// /root/studex-os/agents/robusca/robusca-rocket.js
// Robusca AI — daily CEO briefing → Rocket.Chat #ceo

const { createRobuscaBot } = require('/root/studex-os/war-room/rc-client');

const rc = createRobuscaBot();

async function postDailyBriefing({ date, ordersSummary, deliverySummary, marketingSummary, issues = [] }) {
  const issuesSection = issues.length > 0
    ? `\n⚠️ *Issues Requiring Attention*\n${issues.map(i => `  • ${i}`).join('\n')}`
    : '';

  const message = `🌅 *Good Morning, Meat B@ye!*
━━━━━━━━━━━━━━━━━━━━
📅 Date: ${date || new Date().toLocaleDateString('en-ZA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
━━━━━━━━━━━━━━━━━━━━
${ordersSummary ? `📦 *Orders Today*\n${ordersSummary}\n` : ''}
${deliverySummary ? `🚚 *Deliveries*\n${deliverySummary}\n` : ''}
${marketingSummary ? `📣 *Marketing*\n${marketingSummary}\n` : ''}
${issuesSection}
━━━━━━━━━━━━━━━━━━━━
@here — War Room is open. Let's crush it today! 💪
*Your Robusca AI*`;

  try {
    return await rc.postMessage({
      channel: '#ceo',
      text: message,
      alias: 'Robusca',
      emoji: ':sun_with_face:',
    });
  } catch (err) {
    console.error(`[Robusca] ❌ Failed to post daily briefing:`, err.message);
  }
}

async function postUrgentAlert({ title, description, action = 'Review immediately' }) {
  return rc.postAlert({
    channel: '#alerts',
    text: `🚨 *URGENT — ${title}*
━━━━━━━━━━━━━━━━━━━━
${description}
━━━━━━━━━━━━━━━━━━━━
Action required: ${action}
@robusca @tummebox`,
    alias: 'Robusca',
    emoji: ':rotating_light:',
  });
}

async function postWeeklyReport({ weekOf, totalOrders, revenue, topItems, topLocations, cta }) {
  const message = `📊 *Weekly Performance Report*
━━━━━━━━━━━━━━━━━━━━
📅 Week of: ${weekOf}
🛒 Total Orders: *${totalOrders}*
💰 Revenue: *R${revenue}*
🥩 Top Items: ${topItems?.join(', ') || 'TBD'}
📍 Top Locations: ${topLocations?.join(', ') || 'TBD'}
━━━━━━━━━━━━━━━━━━━━
${cta ? `💡 ${cta}` : ''}
*Report by Robusca AI — Studex Meat War Room*`;

  try {
    return await rc.postMessage({
      channel: '#ceo',
      text: message,
      alias: 'Robusca',
      emoji: ':chart_with_upwards_trend:',
    });
  } catch (err) {
    console.error(`[Robusca] ❌ Failed to post weekly report:`, err.message);
  }
}

// Schedule daily briefing: 06:00 UTC = 08:00 SAST
// Add to Robusca's cron setup
// cron.schedule('0 6 * * *', () => postDailyBriefing({ ... }));
module.exports = { postDailyBriefing, postUrgentAlert, postWeeklyReport };
```

---

## OpenClaw → Rocket.Chat (Webhook Integration)

### Option A: Incoming Webhook (Rocket.Chat → OpenClaw)

Create webhook in Rocket.Chat: `Admin → Integrations → Incoming Webhook`

- **Channel:** `#war-room`
- **Bot name:** `Robusca`
- **URL:** Your OpenClaw webhook URL (from MaxClaw settings)

Rocket.Chat will POST messages to this URL.

### Option B: OpenClaw Notification to Rocket.Chat

Add this to OpenClaw's config (`openclaw.json`) or as a notification script:

```javascript
// /root/studex-os/war-room/openclaw-notify.js
// OpenClaw → Rocket.Chat notification

async function notifyRocketChat({ message, channel = '#war-room', alias = 'Robusca', emoji = ':bell:' }) {
  const token = process.env.ROCKET_ROBUSCA_TOKEN;
  const userId = process.env.ROCKET_ROBUSCA_USER_ID;
  const serverUrl = 'http://67.213.119.157:3000';

  const res = await fetch(`${serverUrl}/api/v1/chat.postMessage`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': token,
      'X-User-Id': userId,
    },
    body: JSON.stringify({ channel, text: message, alias, emoji }),
  });
  return res.json();
}

// Example: Notify war room when a critical event happens
// await notifyRocketChat({ 
//   message: '@tummebox Critical alert from OpenClaw: System check failed',
//   channel: '#alerts',
//   alias: 'Robusca',
//   emoji: ':rotating_light:'
// });
module.exports = { notifyRocketChat };
```

### Option C: Rocket.Chat App (Custom Plugin)

Rocket.Chat 6+ supports Apps Framework — build a custom app for deeper integration:

```javascript
// /root/studex-os/war-room/apps/studex-app/app.json
{
  "name": "Studex Meat Integration",
  "version": "1.0.0",
  "id": "studex-meat-app",
  "description": "Shopify + Delivery + Marketing integration for Studex Meat War Room",
  "author": "Studex Meat OS",
  "permissions": [
    "room:read",
    "message:write",
    "room:write",
    "webhook:write"
  ],
  "extends": {
    "IPostMessageSent": {
      "executable": "./src/handlers/postMessage.ts"
    }
  }
}
```

---

## Notification Routing Rules

| Event | Agent | Channel | Ping | Priority |
|---|---|---|---|---|
| New Shopify order | Charlie | `#orders` | `@robusca @tummebox` | Normal |
| Urgent/priority order | Charlie | `#alerts` | `@robusca @tummebox` | HIGH |
| Content published | Naledi | `#marketing` | `@robusca @tummebox` | Normal |
| Delivery picked up | Delivery | `#delivery` | `@robusca` | Normal |
| Delivery in transit | Delivery | `#delivery` | `@robusca` | Normal |
| Delivery delayed | Delivery | `#alerts` | `@robusca @tummebox` | HIGH |
| Delivery failed | Delivery | `#alerts` | `@robusca @tummebox` | CRITICAL |
| Daily briefing | Robusca | `#ceo` | `@tummebox` | Normal |
| Weekly report | Robusca | `#ceo` | `@tummebox` | Normal |
| System alert | Robusca | `#alerts` | `@tummebox` | CRITICAL |
| Marketing campaign launched | Naledi | `#ceo` | `@tummebox` | Normal |

---

## Testing All Integrations

```bash
# SSH into VM and run integration tests
curl -X POST "https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105/bash" \
  -H "Authorization: Bearer sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2" \
  -H "Content-Type: application/json" \
  -d '{"command":"cd /root/studex-os/war-room && \
    export ROCKET_CHARLIE_TOKEN=$(docker exec rocketchat_server env | grep TOKEN | head -1) && \
    node -e \"const rc = require(\"./rc-client\"); \
    rc.createRobuscaBot().postMessage({channel:\"#war-room\", text:\"🟢 Robusca connected to War Room!\", alias:\"Robusca\", emoji:\":checkered_flag:\"}).then(r => console.log(\"OK\", r)).catch(e => console.error(e))\" \
  "}'
```

---

## Error Handling & Retry Logic

```javascript
// Robust posting with retry
async function postWithRetry(rc, params, maxRetries = 3, delayMs = 2000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await rc.postMessage(params);
    } catch (err) {
      if (i < maxRetries - 1) {
        await new Promise(r => setTimeout(r, delayMs * (i + 1)));
        console.warn(`[Retry ${i + 1}/${maxRetries}]`, err.message);
      } else {
        // Log to external monitoring
        console.error(`[FATAL] All retries exhausted for message to ${params.channel}`);
        throw err;
      }
    }
  }
}
```

---

## Monitoring

### Health Check Endpoint

```javascript
// GET /health on VM
// curl http://67.213.119.157:3000/api/v1/info
// Expected: { version: "7.x.x", status: "Running" }

app.get('/war-room/health', async (req, res) => {
  try {
    const { createRobuscaBot } = require('./rc-client');
    const rc = createRobuscaBot();
    const info = await rc.me();
    res.json({ status: 'ok', connected: true, user: info.data?.username });
  } catch (err) {
    res.status(503).json({ status: 'error', message: err.message });
  }
});
```

### Alert if Rocket.Chat Goes Down

```bash
# Add to VM crontab — check every 5 minutes
*/5 * * * * curl -sf http://localhost:3000/api/v1/info > /dev/null || \
  curl -X POST "https://api.agentmail.to/v0/message" \
    -H "Authorization: Bearer am_us_..." \
    -d '{"to":"ceo@studexmeat.com","subject":"War Room DOWN","body":"Rocket.Chat is not responding!"}'
```
