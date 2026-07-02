# studex-auto-meat

> 🤖 Auto-fulfilment agent for [studexmeat.com](https://studexmeat.com) — Shopify store automation.

## Overview

This repository powers the automated order fulfilment pipeline for the Studex Meat Shopify store. It listens for Shopify webhook events (new orders, payments, shipping updates) and orchestrates the full fulfilment lifecycle — from order confirmation to dispatch notification — without manual intervention.

## What It Does

- **Webhook Receiver**: Receives and validates Shopify `orders/create`, `orders/paid`, and `fulfillment/create` events
- **Inventory Check**: Validates stock availability before committing to fulfilment
- **Packer Dispatch**: Assigns orders to packer/fulfilment staff via WhatsApp or internal channel
- **Tracking Upload**: Pushes tracking numbers back to Shopify automatically
- **Customer Notifications**: Sends dispatch SMS/WhatsApp alerts to customers
- **Error Handling**: Flags failed fulfilments and escalates to human review

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Runtime | OpenClaw (Node.js) |
| Webhooks | Express.js receiver |
| Shop Integration | Shopify Admin API |
| Notifications | WhatsApp Business API |
| Database | Supabase |
| Hosting | Vercel / Railway |

## Quick Start

```bash
git clone https://github.com/TumeloRamaphosa/studex-auto-meat.git
cd studex-auto-meat
npm install
cp .env.example .env
# Fill in SHOPIFY_API_KEY, SHOPIFY_STORE_DOMAIN, SUPABASE_URL, etc.
npm run dev
```

## Project Structure

```
studex-auto-meat/
├── agents/
│   └── fulfiller/
│       └── fulfiller-agent.md   # Core fulfilment decision agent
├── scripts/
│   └── setup-webhooks.js        # One-time Shopify webhook registration
├── src/
│   ├── routes/
│   │   └── webhook.js           # Webhook endpoint handler
│   ├── services/
│   │   ├── shopify.js           # Shopify Admin API client
│   │   ├── supabase.js          # Supabase DB client
│   │   └── notifier.js          # WhatsApp/SMS notification service
│   └── utils/
│       └── signature-verify.js  # HMAC signature verification
├── configs/
│   └── .env.example             # Environment variables template
├── protocols/
│   └── fulfilment-protocol.md   # Standard operating procedure
├── tests/
│   └── webhook.test.js          # Webhook handler unit tests
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SHOPIFY_STORE_DOMAIN` | Your store domain (e.g. `studexmeat.myshopify.com`) |
| `SHOPIFY_ACCESS_TOKEN` | Admin API access token |
| `SHOPIFY_WEBHOOK_SECRET` | Webhook HMAC signing secret |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `WHATSAPP_BUSINESS_TOKEN` | WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | Your WhatsApp Business phone ID |

## Fulfilment Protocol

See [protocols/fulfilment-protocol.md](protocols/fulfilment-protocol.md) for the full SOP.

## Status

🟡 **In Development** — Webhook receiver deployed; full pipeline in progress.

---

Built with 🤖 by the **Studex CTO Department**.
