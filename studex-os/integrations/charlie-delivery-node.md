# Charlie → Delivery Agent Integration Node

**Spec version:** 1.0.0  
**Date:** 2026-06-29  
**Author:** Robusca (Delivery B@ye integrations layer)

---

## Overview

Charlie is the orchestrator running at **port 3001** on the Orgo VM
(`67.213.119.157`). It owns the Shopify webhook handlers and is the single
bridge between Shopify events and the Delivery Agent. The Delivery Agent
runs as a sub-agent inside OpenClaw (this MaxClaw instance). The two
communicate via **HTTP POST to a local Delivery Agent webhook endpoint**
exposed by OpenClaw's internal routing.

---

## Protocol: Charlie → Delivery Agent

### Transport
HTTP POST from Charlie (Orgo VM) → OpenClaw Gateway internal routing.

**Delivery Agent listens on:**  
`POST /internal/delivery-agent/webhook` (OpenClaw gateway route)

Charlie sends the message as JSON in the request body with:
```
Content-Type: application/json
Authorization: Bearer ${INTERNAL_DELIVERY_AGENT_TOKEN}
```

### Message Envelope

Every message from Charlie wraps its payload in this envelope:

```json
{
  "message_id": "msg_<uuid4>",
  "type": "ORDER_NEW | ORDER_PAID | ORDER_DISPATCHED | ORDER_CANCELLED | HEARTBEAT",
  "source": "charlie",
  "timestamp": "2026-06-29T10:00:00+02:00",
  "payload": { ... }
}
```

---

## Message Types

### `ORDER_NEW`
Triggered by Shopify `orders/create` webhook.

```json
{
  "message_id": "msg_a1b2c3d4",
  "type": "ORDER_NEW",
  "source": "charlie",
  "timestamp": "2026-06-29T10:00:00+02:00",
  "payload": {
    "order_id": "ord_internal_<shopify_id>",
    "shopify_order_id": "1234567890",
    "order_number": "1001",
    "status": "ORDER_INTAKE",
    "customer": {
      "name": "Tshepo Mokoena",
      "phone": "+2712345678",
      "whatsapp": "+2712345678",
      "address": "14 Kingsway Ave, Sandton, Johannesburg, Gauteng, 2196, South Africa",
      "address_raw": {
        "address1": "14 Kingsway Ave",
        "address2": "Sandton",
        "city": "Johannesburg",
        "province": "Gauteng",
        "zip": "2196",
        "country": "South Africa"
      }
    },
    "items": [
      { "title": "Wagyu Beef Ribeye 500g", "quantity": 2, "sku": "WAG-RBE-500" },
      { "title": "Lamb Chops 1kg", "quantity": 1, "sku": "LAMB-CHP-1K" }
    ],
    "order_value": 459.00,
    "currency": "ZAR",
    "fulfilment_status": "pending",
    "assigned_driver_company": "dinkoko",
    "eta_promised": null,
    "delivery_state_path": "/workspace/studex-os/delivery-state.json"
  }
}
```

### `ORDER_PAID`
Triggered by Shopify `orders/paid` webhook.

```json
{
  "message_id": "msg_e5f6g7h8",
  "type": "ORDER_PAID",
  "source": "charlie",
  "timestamp": "2026-06-29T10:02:00+02:00",
  "payload": {
    "order_id": "ord_internal_<shopify_id>",
    "shopify_order_id": "1234567890",
    "order_number": "1001",
    "order_value": 459.00,
    "payment_method": "shopify_payments"
  }
}
```

### `ORDER_DISPATCHED`
Triggered by Shopify `orders/fulfilled` webhook.

```json
{
  "message_id": "msg_i9j0k1l2",
  "type": "ORDER_DISPATCHED",
  "source": "charlie",
  "timestamp": "2026-06-29T12:00:00+02:00",
  "payload": {
    "order_id": "ord_internal_<shopify_id>",
    "shopify_order_id": "1234567890",
    "order_number": "1001",
    "status": "DISPATCHED",
    "driver_name": "Derrick Selepe",
    "driver_phone": "+27676813076",
    "delivery_company": "dinkoko",
    "tracking_number": "DK-20260629-001",
    "tracking_url": "https://dinkoko.co.za/track/DK-20260629-001",
    "dispatched_at": "2026-06-29T12:00:00+02:00"
  }
}
```

### `ORDER_CANCELLED`
Triggered by Shopify `orders/cancelled` webhook.

```json
{
  "message_id": "msg_m3n4o5p6",
  "type": "ORDER_CANCELLED",
  "source": "charlie",
  "timestamp": "2026-06-29T11:00:00+02:00",
  "payload": {
    "order_id": "ord_internal_<shopify_id>",
    "shopify_order_id": "1234567890",
    "order_number": "1001",
    "cancel_reason": "customer",
    "cancelled_at": "2026-06-29T11:00:00+02:00"
  }
}
```

### `HEARTBEAT` (optional keep-alive)
Charlie sends a heartbeat every 5 minutes to the Delivery Agent.

```json
{
  "message_id": "msg_hb001",
  "type": "HEARTBEAT",
  "source": "charlie",
  "timestamp": "2026-06-29T10:05:00+02:00",
  "payload": {
    "charlie_version": "1.0.0",
    "orders_processed": 47,
    "last_webhook_received": "2026-06-29T10:04:55+02:00"
  }
}
```

---

## Delivery Agent → Charlie (Response channel)

The Delivery Agent acknowledges each message with:

```
POST <charles_internal_callback_url>/delivery-agent/ack
```

```json
{
  "message_id": "msg_a1b2c3d4",
  "status": "PROCESSED | FAILED | DEFERRED",
  "delivery_agent_action": "KANBAN_CREATED | WHATSAPP_SENT | ETA_CALCULATED | ERROR",
  "error": null,
  "timestamp": "2026-06-29T10:00:05+02:00"
}
```

---

## Retry Logic

### Charlie → Delivery Agent (outbound)

| Attempt | Delay | On failure |
|---|---|---|
| 1 | Immediate | — |
| 2 | 1 second | Log warning |
| 3 | 2 seconds | Log error |
| 4 | 4 seconds | Log critical, alert Robusca |

After 4 failed attempts, Charlie:
1. Writes the failed message to `/workspace/studex-os/failed-messages/<message_id>.json`
2. Sends a Matrix/email alert to Robusca with the message contents.
3. Continues processing other orders (does not block the queue).

### Delivery Agent → Charlie (ack)

| Attempt | Delay |
|---|---|
| 1 | Immediate |
| 2 | 3 seconds |
| 3 | 9 seconds |

After 3 failures, Delivery Agent logs to its own error file and continues.

---

## Error Handling

| Error | Charlie action | Delivery Agent action |
|---|---|---|
| HTTP 4xx from Delivery Agent | Retry (see retry table) | Log error, alert Robusca |
| HTTP 5xx from Delivery Agent | Retry with backoff | Log, alert Robusca |
| Connection refused | Retry 3x, then alert Robusca | Retry 3x, then alert Robusca |
| Malformed JSON response | Log raw response, retry | Log, retry |
| Delivery state file locked | Wait 500ms, retry (max 5x) | Same |
| Message ID already processed | Skip silently, return 200 | Idempotent — skip |

---

## Delivery Agent Incoming Endpoint (OpenClaw)

OpenClaw's gateway must expose an internal route for Charlie to POST to:

```
POST /internal/delivery-agent/webhook
Headers:
  Authorization: Bearer ${INTERNAL_DELIVERY_AGENT_TOKEN}
  Content-Type: application/json
  X-Charlie-Source: charlie-orchestrator
Body: <message envelope (see above)>
```

The OpenClaw skill/skill config for the Delivery Agent should register this
route and dispatch incoming messages to the Delivery Agent's message handler.

**Note for MaxClaw platform team:** If OpenClaw's routing does not support
incoming HTTP POST from Charlie directly, an alternative is for Charlie to
write a JSON file to a watched directory:

```
/workspace/studex-os/incoming-orders/<message_id>.json
```

The Delivery Agent's heartbeat loop checks this directory every cycle
and processes any new files. This is a simpler alternative that works
reliably without network routing.

---

## Internal Token

Both sides share a secret for mutual authentication:

```
INTERNAL_DELIVERY_AGENT_TOKEN=  # Shared secret — set in Charlie env and OpenClaw env
```

Store this in:
- Charlie: `.env` on Orgo VM
- OpenClaw: OpenClaw Gateway environment variables or skill config

---

## File-based Fallback (Recommended for Reliability)

**Primary:** HTTP POST to OpenClaw webhook endpoint.  
**Fallback:** Charlie writes JSON to `/workspace/studex-os/incoming-orders/`
directory. Delivery Agent polls this directory every 15-min cycle.

```js
// Charlie fallback — write to file instead of HTTP POST
const fs = require('fs');
const path = require('path');

function deliverToDeliveryAgent(message) {
  const dir = '/workspace/studex-os/incoming-orders';
  const file = path.join(dir, `${message.message_id}.json`);
  
  // Try HTTP first
  httpPostWithRetry(OPENCLAW_WEBHOOK_URL, message)
    .then(() => console.log(`Delivered ${message.message_id} via HTTP`))
    .catch(() => {
      // Fallback: write file
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(file, JSON.stringify(message, null, 2));
      console.warn(`HTTP failed — written to ${file} as fallback`);
    });
}
```

---

## Logging

All messages (sent, received, acknowledged, failed) are logged to:
```
/workspace/studex-os/logs/charlie-delivery-agent.log
```

Format:
```
[2026-06-29T10:00:01+02:00] OUT msg_a1b2c3d4 ORDER_NEW → delivery-agent [PROCESSING]
[2026-06-29T10:00:05+02:00] ACK msg_a1b2c3d4 ORDER_NEW ← delivery-agent [PROCESSED]
[2026-06-29T10:00:02+02:00] OUT msg_e5f6g7h8 ORDER_PAID → delivery-agent [PROCESSING]
[2026-06-29T10:00:06+02:00] ACK msg_e5f6g7h8 ORDER_PAID [FAILED] — retry 2/4
```

---

## Environment Variables

```
# Charlie side
SHOPIFY_ACCESS_TOKEN=         # Shopify Admin API
INTERNAL_DELIVERY_AGENT_TOKEN=# Shared secret with Delivery Agent
OPENCLAW_DELIVERY_AGENT_URL=  # http://<maxclaw-host>/internal/delivery-agent/webhook
DELIVERY_STATE_PATH=          # /workspace/studex-os/delivery-state.json
INCOMING_ORDERS_DIR=          # /workspace/studex-os/incoming-orders
FAILED_MESSAGES_DIR=          # /workspace/studex-os/failed-messages
```

```
# Delivery Agent side (OpenClaw env / skill config)
INTERNAL_DELIVERY_AGENT_TOKEN=# Must match Charlie's token
DELIVERY_STATE_PATH=          # /workspace/studex-os/delivery-state.json
INCOMING_ORDERS_DIR=          # /workspace/studex-os/incoming-orders
OPENWA_API_URL=               # http://<orgo-vm>:2785/api
```
