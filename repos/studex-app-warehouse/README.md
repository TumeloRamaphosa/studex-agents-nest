# studex-app-warehouse

> 🏭 **The Client App Factory** — Templated app generation pipeline for Studex Group and its clients.

## Overview

The App Warehouse is a systematic, template-driven app factory. When a client submits a request (via Google Form intake), an automated pipeline launches — using the BMAD (Build More Architect Dreams) methodology — to scaffold, build, and deploy a production-ready app from a curated template library.

**Goal**: Reduce client app delivery from weeks to hours by combining:
- Templated architectures (React Native, Next.js, etc.)
- AI-powered coding agents (BMAD agents)
- Automated quality checks (CodeRabbit)
- One-click deployment (Vercel, Expo)

## How It Works

```
Client Intake (Google Form)
        ↓
N8n Workflow Trigger
        ↓
App Warehouse Agent (classifies + assigns template)
        ↓
BMAD Pipeline: PM → Architect → Dev → QA → Deploy
        ↓
CodeRabbit Auto-Review
        ↓
Vercel / Expo Deployment
        ↓
Client Notification (WhatsApp / Email)
```

## Template Library

| App Type | Stack | Deploy Time |
|----------|-------|-------------|
| Restaurant / Takeaway | React + Supabase | ~2 hrs |
| Booking / Appointments | Next.js + Cal.com | ~2 hrs |
| E-commerce Store | Shopify / Next.js | ~3 hrs |
| Delivery Tracking | React Native + Maps | ~4 hrs |
| Business Dashboard | Next.js + Supabase | ~2 hrs |
| Landing Page | Next.js + Vercel | ~30 min |
| Portfolio / Personal | Astro + Vercel | ~30 min |
| Loyalty / Rewards | React + Supabase | ~3 hrs |
| WhatsApp Business Bot | Node.js + WhatsApp API | ~1 hr |
| Food Delivery (Full) | React Native + Supabase | ~6 hrs |

## Client Intake Form Fields

The intake form captures:
- Business name & industry
- App type (from template list)
- Target platforms (Web / iOS / Android / All)
- Key features (checkboxes)
- Budget range
- Timeline
- Brand assets (logo upload / color preference)
- Contact details

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Intake | Google Forms + N8n |
| Agent Orchestration | BMAD (Multi-Agent) |
| Code Generation | Claude Code / Codex |
| Code Review | CodeRabbit |
| Backend DB | Supabase |
| Hosting | Vercel (web) / Expo (mobile) |
| Maps | Google Maps API |
| Payments (SA) | Yoco / Stripe |
| Notifications | OneSignal / WhatsApp Business |

## Quick Start

```bash
git clone https://github.com/TumeloRamaphosa/studex-app-warehouse.git
cd studex-app-warehouse
npm install
# Set N8N_WEBHOOK_URL, BMAD_API_KEY, SUPABASE_URL, etc.
npm run warehouse:status   # Check active builds
npm run templates:list      # List available templates
```

## Project Structure

```
studex-app-warehouse/
├── agents/
│   └── warehouse-agent/
│       └── warehouse-agent.md   # Main intake + routing agent
├── templates/
│   ├── restaurant-nextjs/       # Restaurant/takeaway template
│   ├── booking-nextjs/          # Booking/appointments template
│   ├── ecommerce-shopify/       # E-commerce template
│   ├── delivery-reactnative/   # Delivery app template
│   ├── dashboard-nextjs/       # Business dashboard template
│   ├── landing-nextjs/          # Landing page template
│   ├── portfolio-astro/         # Portfolio template
│   └── whatsapp-bot/            # WhatsApp bot template
├── client-apps/
│   └── [client-name]/            # Generated client projects (archived)
├── intake/
│   ├── google-forms-config/      # Form field mappings
│   └── n8n-workflows/           # N8n automation workflows
├── configs/
│   └── .env.example
├── protocols/
│   └── warehouse-protocol.md    # Delivery SLA + quality gates
├── scripts/
│   ├── launch-app.js            # Trigger new app build
│   └── deploy-template.js       # Deploy from template to Vercel
├── docs/
│   ├── template-guide.md        # How to create new templates
│   └── client-onboarding.md     # Client onboarding checklist
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## Adding a New Template

1. Create a new folder under `templates/`
2. Add `template-manifest.json` with metadata (name, stack, estimated hours)
3. Write a `README.md` inside the template folder
4. Add to BMAD pipeline config
5. Update `TEMPLATE_LIBRARY.md` in docs/

## Status

🔴 **Planning** — Intake form and N8n workflows in design; BMAD integration pending.

---

Built with 🏭 by the **Studex CTO Department**.
