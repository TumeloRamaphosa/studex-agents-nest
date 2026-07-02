# Studex Meat — Delivery WhatsApp Message Templates
**Version:** 1.0 | **Date:** 2026-06-29 | **Author:** Naledi CMO (Studex Meat)
**Channel:** WhatsApp (client-facing + driver-facing + internal alerts)

> All messages are formatted for WhatsApp. No markdown headers. Bold via `*text*`. Variables in `{{double braces}}`. Emoji used sparingly but purposefully. Tone: professional but warm — Studex is premium, not cold.

---

## Client-Facing Messages

---

### 1. Order Confirmed → Client

**When sent:** Immediately on Shopify order capture, before packing begins.
**Trigger:** Shopify `order/create` webhook → Delivery Agent.

```
*✅ Order Confirmed — Studex Meat*

Hi {{customer_first_name}}!

Your order *#{{order_number}}* is confirmed and we're getting it ready. 🔪

*What to expect:*
📦 Your order will be packed within 2 hours
🚚 Delivery window: {{eta_window}} (approx.)
📍 Delivering to: {{delivery_address}}

You'll receive updates on WhatsApp as your order moves.

Questions? Reply here or call us any time.

— The Studex Team 🐄
```

---

### 2. Order Packed → Client

**When sent:** When team marks order as `📦 Packed` in Kanban.
**Trigger:** Kanban card moved to PACKED column.

```
📦 *Order Packed — #{{order_number}}*

Hi {{customer_first_name}}, your order is packed and ready for collection!

🚚 A driver will collect from our warehouse today and bring it straight to you.

We'll let you know the moment it's on its way.

Stay tuned! — Studex Meat 🐄
```

---

### 3. Driver Collected Order → Client

**When sent:** When Kanban card moves to `🚚 Dispatched`.
**Trigger:** Team marks card as dispatched → Delivery Agent fires WhatsApp.

```
🚚 *On Its Way — #{{order_number}}*

Hi {{customer_first_name}}! Your order is now with our driver.

👤 Driver: {{driver_name}}
📱 Contact: {{driver_phone}}
⏰ ETA: approximately *{{eta_time}} SAST*

Track live updates below (ETA updates as driver moves):
{{google_maps_live_link}}

See you soon! — Studex Meat 🐄
```

---

### 4. Driver En Route → Client (ETA Update)

**When sent:** Every 30 min for active deliveries, or when ETA changes by >10 min.
**Trigger:** Google Maps Routes API ETA update → Delivery Agent.

```
🔔 *Delivery Update — #{{order_number}}*

Hi {{customer_first_name}}, quick update:

🚚 Driver is en route to your address
⏰ Updated ETA: *{{eta_time}} SAST* ({{eta_minutes}} min away)

Almost there! 🐄
```

---

### 5. Driver Arrived at Address → Client

**When sent:** When driver enters 500m radius of delivery address (Google Maps geofence trigger).
**Trigger:** Geofence event or driver marks arrived.

```
🏁 *Driver Has Arrived — #{{order_number}}*

Your driver is *at your address now*!

Please come collect your order:
{{delivery_address}}

If you need to reschedule or redirect, reply here urgently.

— Studex Meat 🐄
```

---

### 6. Order Delivered → Client + Review Request

**When sent:** When team marks card as `🏁 Delivered` in Kanban. Review request follows 30 min later.
**Trigger:** Kanban `DELIVERED` column move.

**Immediate delivery confirmation:**
```
🏁 *Delivered! — #{{order_number}}*

Your order has been delivered. ✅

We hope you enjoy your premium Studex meat! 🥩

Questions or issues? Reply here within 24 hours.

— The Studex Team 🐄
```

**Follow-up (30 min later):**
```
Hey {{customer_first_name}}! Hope you're happy with your order 🥩

We'd love your feedback — it only takes 30 seconds:
⭐ {{review_link}}

Leave a review and get *10% off your next order.* 🐄
```

---

### 7. Order Delayed (Minor) → Client

**When sent:** When ETA slips by 15–29 minutes. Non-critical.
**Trigger:** Google Maps ETA update exceeds original by 15+ min → Delivery Agent.

```
⏱️ *Slight Delay — #{{order_number}}*

Hi {{customer_first_name}}, just letting you know:

Your delivery is running *slightly behind* schedule due to traffic/load.

New ETA: *{{new_eta_time}} SAST* (approx. {{delay_minutes}} min delay)

We apologise for the wait — your order is still fresh and on its way. 🐄
```

---

### 8. Order Delayed (Major / Escalation) → Client + Robusca Alert

**When sent:** When ETA slips by 30+ minutes, or order hits any SLA breach.
**Trigger:** SLA breach detected by Delivery Agent → Robusca alert simultaneously.

**To client:**
```
⚠️ *Delivery Delay — #{{order_number}}*

Hi {{customer_first_name}}, we owe you an honest update:

Your delivery has hit a delay. We're actively sorting it.

*Current status:* {{delay_reason}}
*New ETA:* {{new_eta_time}} SAST

We take full responsibility and will follow up shortly. You can reply here anytime.

— Robusca, Studex Meat 🐄
```

**To Robusca (via agent):** (see Internal Alert #9 below)

---

### 9. Order Cancelled → Client

**When sent:** When client or team cancels order. Must be before dispatch.
**Trigger:** Cancellation in Shopify or Kanban → Delivery Agent.

```
🚫 *Order Cancelled — #{{order_number}}*

Hi {{customer_first_name}},

Your order *#{{order_number}}* has been cancelled.

{{#if refund_applicable}}
💰 Refund will be processed within 5–7 business days to your original payment method.
{{else}}
No payment was taken for this order.
{{/if}}

We'd love to serve you again soon. Browse our range:
{{shopify_store_link}}

— Studex Meat 🐄
```

---

## Driver-Facing Messages

---

### 10. New Job — Driver (via WhatsApp Group)

**When sent:** On new order assignment to delivery company. Posted to the shared WhatsApp group with Derrick/Willy.
**Trigger:** Kanban card created → Delivery Agent identifies company → posts to group.

```
🚨 *NEW JOB — STUDEX MEAT*

📥 Order: *#{{order_number}}*
👤 Client: {{customer_name}}
📍 Collect: *{{warehouse_address}}*
📍 Deliver: *{{delivery_address}}*
📦 Items: {{item_summary}} ({{total_weight}}kg)
💰 Pay: R{{driver_rate}}

⚡ Collect by: *{{collect_by_time}} SAST*

Reply *YES* or *NO* within 15 min to accept.

— Delivery B@ye 🤖
```

---

### 11. Job Reminder — Driver (30 min before collect deadline)

**When sent:** 30 minutes before `collect_by_time`.
**Trigger:** Scheduled timer in Delivery Agent.

```
⏰ *REMINDER — #{{order_number}}*

Driver, please collect from warehouse by *{{collect_by_time}} SAST*.

📍 Warehouse: {{warehouse_address}}
📦 Order summary: {{item_summary}}

Reply here when collected. — Delivery B@ye 🤖
```

---

### 12. Driver Declined Job → Robusca Alert

**When sent:** When driver replies "NO" or fails to respond within 15 minutes.
**Trigger:** WhatsApp group message → OpenWA → Delivery Agent → Robusca alert.

**To Robusca (internal — via Delivery Agent):**
```
🚨 *DRIVER DECLINED — URGENT*

Company: *{{delivery_company}}*
Order: *#{{order_number}}*
Client: {{customer_name}}

{{delivery_company}} has declined or not responded.

⚡ Action needed: Re-assign to other provider or contact client.

— Delivery B@ye 🤖
```

---

## Internal / Agent Alert Messages

---

### 13. Driver Unreachable → Robusca Alert

**When sent:** Driver not contactable via phone/WhatsApp for 20+ minutes after dispatch.
**Trigger:** Delivery Agent fails to reach driver on 2 attempts.

```
🚨 *DRIVER UNREACHABLE — ESCALATION*

Company: *{{delivery_company}}*
Driver: {{driver_name}} ({{driver_phone}})
Order: *#{{order_number}}*

Attempts to reach driver: 2 (failed)

⚡ Immediate action:
1. Try alternate contact number
2. Switch to backup provider ({{backup_company}})
3. Notify client of delay

— Delivery B@ye 🤖
```

---

### 14. Daily Delivery Report → Robusca (17:00 SAST)

**When sent:** Daily at 17:00 SAST.
**Trigger:** Cron job on Delivery Agent (runs Mon–Sat).

```
📊 *STUDIX DELIVERY REPORT — {{date}}*

*Today's Summary*
Total orders: {{total_orders}}
Delivered: ✅ {{delivered_count}}
In transit: 🚚 {{in_transit_count}}
Delayed: ⚠️ {{delayed_count}}
Cancelled: 🚫 {{cancelled_count}}
Failed: ❌ {{failed_count}}

*Provider Performance*
Dinkoko: {{dinkoko_today}} orders — {{dinkoko_on_time_pct}}% on time
My Courier: {{my_courier_today}} orders — {{my_courier_on_time_pct}}% on time

*Flags for Review*
{{#if delayed_orders}}
⚠️ Delayed orders: {{delayed_order_list}}
{{/if}}
{{#if client_complaints}}
💬 Client complaints: {{complaint_summary}}
{{/if}}
{{#if none}}
✅ All clear — no issues today.
{{/if}}

Full board: {{kanban_link}}

— Delivery B@ye 🤖 | Report sent 17:00 SAST
```

---

### 15. Morning Briefing → Robusca (07:00 SAST)

**When sent:** Daily at 07:00 SAST (Mon–Fri).
**Trigger:** Cron job on Delivery Agent.

```
🌅 *STUDIX MORNING BRIEF — {{date}}*

Good morning Robusca! Here's what to expect today.

*Active Deliveries Overnight*
{{#if overnight_orders}}
{{overnight_order_list}}
{{else}}
None — clean slate.
{{/if}}

*Today's Orders (Shopify)*
{{today_order_count}} orders received so far
{{pending_dispatch_count}} awaiting dispatch

*Priority Jobs Today*
{{priority_job_list}}

*Weather Check (JHB/SA Metro)*
{{weather_summary}} — {{weather_impact_note}}

*Today's Team*
👥 Packing team: {{packing_team}}
🚚 Drivers confirmed: {{drivers_confirmed}}

Ready when you are. 🐄

— Delivery B@ye 🤖 | Brief sent 07:00 SAST
```

---

## Appendix: Message Variables Reference

| Variable | Source | Format |
|----------|--------|--------|
| `{{customer_first_name}}` | Shopify order | First name only |
| `{{customer_name}}` | Shopify order | Full name |
| `{{order_number}}` | Shopify order | e.g. `#STUD-1084` |
| `{{delivery_address}}` | Shopify order | Full address line |
| `{{eta_time}}` | Google Maps Routes API | `14:30 SAST` |
| `{{eta_window}}` | Zone lookup | `2–4 hours` |
| `{{delay_reason}}` | Delivery Agent | Free text |
| `{{driver_name}}` | Delivery company | Name string |
| `{{driver_phone}}` | Delivery company | `+27 XX XXX XXXX` |
| `{{item_summary}}` | Shopify order | Short item list |
| `{{total_weight}}` | Shopify order | e.g. `4.5 kg` |
| `{{warehouse_address}}` | Config | Fixed address |
| `{{collect_by_time}}` | SLA calc | `HH:MM SAST` |
| `{{google_maps_live_link}}` | Google Maps embed | URL |
| `{{review_link}}` | Shopify review app | URL |
| `{{shopify_store_link}}` | Config | `studexmeat.com` |
| `{{kanban_link}}` | Studex OS | URL |

---

*Compiled by Naledi CMO — Studex Meat Delivery OS — 2026-06-29*
