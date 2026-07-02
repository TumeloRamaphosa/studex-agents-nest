# Shopify Webhook Spec — Studex Meat Delivery OS

**Spec version:** 1.0.0  
**Date:** 2026-06-29  
**Author:** Robusca (Delivery B@ye integrations layer)

---

## Overview

Charlie (orchestrator, port 3001 on Orgo VM) receives Shopify webhook events
at `POST /webhooks/shopify`. It verifies HMAC-SHA256, then routes each topic
to the appropriate handler. The Delivery Agent is notified via the Charlie→Delivery
message protocol (see `charlie-delivery-node.md`).

---

## Webhook Endpoint

```
POST /webhooks/shopify
Headers:
  X-Shopify-Topic: <topic>
  X-Shopify-Shop-Domain: studexmeat.myshopify.com
  X-Shopify-Webhook-Signature: <HMAC-SHA256 of body using SHOPIFY_WEBHOOK_SECRET>
  X-Shopify-API-Version: 2024-01
Content-Type: application/json
```

**HMAC verification (Node.js):**
```js
const crypto = require('crypto');
function verifyShopifyWebhook(rawBody, secret, signature) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(rawBody, 'utf8');
  const digest = 'sha256=' + hmac.digest('base64');
  return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(signature));
}
```

---

## Topics to Register in Shopify Admin

| Topic | Admin path | Purpose |
|---|---|---|
| `orders/create` | Settings → Notifications → Webhooks | New order intake |
| `orders/paid` | Settings → Notifications → Webhooks | Payment confirmed |
| `orders/fulfilled` | Settings → Notifications → Webhooks | Dispatched |
| `orders/cancelled` | Settings → Notifications → Webhooks | Cancelled / refunded |

Webhook URL to register:  
`https://<CHARLIE_PUBLIC_HOST>/webhooks/shopify`

---

## 1. `orders/create`

Fires when any new order is created (regardless of payment status).

### Trigger
Customer completes checkout → order record created in Shopify.

### Payload shape
```json
{
  "id": 1234567890,
  "order_number": 1001,
  "name": "#1001",
  "email": "customer@example.com",
  "created_at": "2026-06-29T10:00:00+02:00",
  "updated_at": "2026-06-29T10:00:00+02:00",
  "total_price": "459.00",
  "currency": "ZAR",
  "financial_status": "pending",
  "fulfillment_status": null,
  "note": null,
  "customer": {
    "id": 9876543210,
    "first_name": "Tshepo",
    "last_name": "Mokoena",
    "email": "customer@example.com",
    "phone": "+2712345678",
    "default_address": {
      "address1": "14 Kingsway Ave",
      "address2": "Sandton",
      "city": "Johannesburg",
      "province": "Gauteng",
      "zip": "2196",
      "country": "South Africa",
      "phone": "+2712345678"
    }
  },
  "line_items": [
    {
      "id": 111111,
      "title": "Wagyu Beef Ribeye 500g",
      "quantity": 2,
      "sku": "WAG-RBE-500",
      "price": "229.50",
      "vendor": "Moutloe Farm"
    },
    {
      "id": 222222,
      "title": "Lamb Chops 1kg",
      "quantity": 1,
      "sku": "LAMB-CHP-1K",
      "price": "0.00",
      "vendor": "Silent Valley"
    }
  ],
  "shipping_address": {
    "first_name": "Tshepo",
    "last_name": "Mokoena",
    "address1": "14 Kingsway Ave",
    "address2": "Sandton",
    "city": "Johannesburg",
    "province": "Gauteng",
    "zip": "2196",
    "country": "South Africa",
    "phone": "+2712345678"
  },
  "shipping_lines": [
    {
      "title": "Standard Delivery",
      "price": "0.00"
    }
  ]
}
```

### What Charlie does
1. **Verify HMAC** — reject if signature invalid.
2. **Upsert delivery state** — add order to `delivery-state.json` with
   `status: ORDER_INTAKE`, populate all customer/item fields.
3. **Run assignment rules** — determine delivery company (Dinkoko vs MyCourier)
   based on zone and order value.
4. **Notify Delivery Agent** — send `ORDER_NEW` message via Charlie→Delivery
   protocol (see `charlie-delivery-node.md`).
5. **Log** — append to `memory_log` with actor `Charlie`, action `New order received from Shopify`.

### Delivery Agent response
- Receives `ORDER_NEW` message from Charlie.
- Geocodes shipping address.
- Calculates ETA via Google Maps Routes API.
- Creates Kanban card in `[📥 New Order]`.
- Sends WhatsApp to driver (via OpenWA relay group).
- Sends confirmation WhatsApp to customer.

---

## 2. `orders/paid`

Fires when payment is successfully captured (financial_status → `paid`).

### Trigger
Payment captured via Shopify Payments / PayFast / card.

### Payload shape
Same as `orders/create` with updated fields:
```json
{
  "id": 1234567890,
  "financial_status": "paid",
  "total_price": "459.00",
  "currency": "ZAR",
  "created_at": "...",
  "updated_at": "2026-06-29T10:02:00+02:00"
}
```

### What Charlie does
1. **Verify HMAC.**
2. **Update delivery state** — set `status: ORDER_INTAKE` (if not already) and
   `last_updated_by: Charlie`; update `updated_at`.
3. **Notify Delivery Agent** — send `ORDER_PAID` message with `order_id`
   and `order_value`.
4. **Log** — append to `memory_log`.

### Delivery Agent response
- Confirms payment in Kanban card.
- Sends "Payment confirmed — preparing your order" WhatsApp to customer
  (if confirmation not yet sent).

---

## 3. `orders/fulfilled`

Fires when the order is marked fulfilled in Shopify (packing → driver collected).

### Trigger
Packer manually marks fulfilled in Shopify admin, OR fulfillment service
calls `POST /admin/api/2024-01/orders/{id}/fulfillments.json`.

### Payload shape
```json
{
  "id": 1234567890,
  "order_number": 1001,
  "name": "#1001",
  "fulfillment_status": "fulfilled",
  "financial_status": "paid",
  "updated_at": "2026-06-29T12:00:00+02:00",
  "fulfillments": [
    {
      "id": 555555,
      "status": "success",
      "tracking_company": "Dinkoko",
      "tracking_number": "DK-20260629-001",
      "tracking_url": "https://dinkoko.co.za/track/DK-20260629-001",
      "line_items": [
        {
          "id": 111111,
          "title": "Wagyu Beef Ribeye 500g",
          "quantity": 2
        }
      ]
    }
  ],
  "line_items": [ ... ],
  "shipping_address": { ... }
}
```

### What Charlie does
1. **Verify HMAC.**
2. **Update delivery state** — set `status: DISPATCHED`, record
   `driver_name`, `driver_phone`, `tracking_number` from the fulfillment payload.
3. **Notify Delivery Agent** — send `ORDER_DISPATCHED` message.
4. **Log** — append to `memory_log`.

### Delivery Agent response
- Updates Kanban card to `[🚚 Dispatched]`.
- Sends "Your order is on its way!" WhatsApp to customer with ETA.
- Starts ETA monitoring loop (15-min check cycle).

---

## 4. `orders/cancelled`

Fires when an order is cancelled by customer or admin.

### Trigger
Customer or admin cancels order in Shopify.

### Payload shape
```json
{
  "id": 1234567890,
  "order_number": 1001,
  "name": "#1001",
  "cancelled_at": "2026-06-29T11:00:00+02:00",
  "cancel_reason": "customer",
  "financial_status": "refunded",
  "fulfillment_status": null,
  "updated_at": "2026-06-29T11:00:00+02:00",
  "note": "Customer requested cancellation — items out of stock"
}
```

### What Charlie does
1. **Verify HMAC.**
2. **Update delivery state** — set `status: CANCELLED`, `last_updated_by: Charlie`.
3. **Notify Delivery Agent** — send `ORDER_CANCELLED` message.
4. **Remove from driver active list** — if order was already dispatched,
   remove `order_id` from driver's `active_orders` in delivery state.
5. **Log** — append to `memory_log`.

### Delivery Agent response
- Moves Kanban card to `[🔴 Cancelled]`.
- Sends cancellation confirmation WhatsApp to customer.
- If driver already collected: alerts Robusca immediately.

---

## Delivery Agent Notification Summary

| Shopify Event | Charlie Message Type | Delivery Agent Action |
|---|---|---|
| `orders/create` | `ORDER_NEW` | Create Kanban card, notify driver + customer |
| `orders/paid` | `ORDER_PAID` | Confirm payment, send payment confirmation |
| `orders/fulfilled` | `ORDER_DISPATCHED` | Update Kanban, send "on the way" WhatsApp, start ETA monitoring |
| `orders/cancelled` | `ORDER_CANCELLED` | Cancel Kanban card, notify customer |

---

## Error Handling

| Scenario | Charlie Behaviour |
|---|---|
| HMAC verification fails | Return `401`, log attempt, alert Robusca |
| Duplicate `orders/create` (idempotency) | Check if order_id exists in state — skip if yes, log duplicate |
| Missing shipping address | Set `status: NEEDS_REVIEW`, alert Robusca via Matrix |
| Delivery state file corrupt | Load backup `delivery-state.json.bak`, alert Robusca |
| Google Maps API unreachable | Use straight-line fallback estimate, flag order |
| Charlie→Delivery Agent message fails | Retry 3x with exponential backoff (1s, 2s, 4s), then alert Robusca |

---

## Environment Variables

```
SHOPIFY_ACCESS_TOKEN=       # Shopify Admin API access token
SHOPIFY_WEBHOOK_SECRET=     # Per-app webhook signing secret
SHOPIFY_STORE_DOMAIN=       # studexmeat.myshopify.com
CHARLIE_PUBLIC_HOST=         # Public URL of Charlie (Orgo VM)
```

---

## Implementation Checklist

- [ ] Register 4 webhook topics in Shopify Admin
- [ ] Implement HMAC verification middleware
- [ ] Write handlers for each topic in Charlie
- [ ] Test with ngrok tunnel to local Charlie dev instance
- [ ] Wire Charlie→Delivery Agent message protocol
- [ ] Add idempotency checks (dedupe on `order.id`)
