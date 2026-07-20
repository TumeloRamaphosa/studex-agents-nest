# WWE Hub — Master Plan
**Version:** 1.0 | **Date:** 2026-07-12 | **Author:** Robusca (COO)

---

## Vision

WWE Hub is a collaborative AI business platform where entrepreneurs join a shared operating system, receive their own VM with two AI agents, and build businesses — all coordinated through a central hub that runs and automates their operations.

The hub owner (Tumelo) orchestrates. Each franchisee focuses on their business. The agents do the work. Revenue is split 50/50.

> **"Our computers work for us."**

---

## The Model

### Weekly Rhythm
```
MONDAY        → Plan for the week (all franchisees + Tumelo)
DAILY         → 2h implement (together on ClickClack)
              → 1h learn (structured, coach-led)
              → 10min break
              → 2h implement
FRIDAY        → Founders Day (weekly wrap + coaching + community call)
```

### Franchisee Gets
- 1× VM (2 CPU, 8GB RAM) with their own branded AI
- 2× OpenClaw agents (e.g. "Operations Agent" + "Outreach Agent")
- Access to ClickClack hub — franchisee channel + hub-wide channels
- White-label of Eve AI Workforce model for their market
- GoHighLevel account (reseller relationship via SVHQ)
- Hub OS dashboard — see their business metrics + agent activity
- Weekly coaching sessions + community calls

### Hub Owner (Tumelo) Gets
- 50% of franchisee revenue
- Full visibility across all franchisee channels (ClickClack)
- Aggregate reporting — entire hub at a glance
- Franchisee onboarding + agent provisioning service

---

## Brand Alignment

| Brand | Role | Territory |
|-------|------|-----------|
| **Silicon Valley HQ** | Global partner / franchise parent | Worldwide |
| **Eve AI Workforce** | AI Operator product (GHL-based) | SA + regional |
| **WWE Hub** | The platform/franchise layer | SA + Africa |

Eve AI SA (or whatever SA-localized name) becomes the first franchisee under WWE Hub.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Hub OS / Coordination | OpenClaw | Multi-agent orchestration |
| Team Chat | ClickClack (self-hosted) | Self-hosted, agent-friendly |
| Agent VMs | Orgo.ai (or self-hosted VPS) | 2 CPU, 8GB per franchisee |
| CRM / Automation | GoHighLevel (reseller) | Via SVHQ partnership |
| AI Agents | OpenClaw + custom agents | Charlie, Naledi + per-franchisee |
| Voice / Phone | To be confirmed | TBD |
| Payments | Shopify + manual | Per-franchisee Shopify |

---

## ClickClack Hub — Channel Structure

```
WWE Hub Workspace
├── #announcements        — Tumelo broadcasts
├── #general              — Hub-wide chat
├── #help-desk            — Support questions
│
├── #ops-studex-meat      — Charlie + Naledi (Tumelo's business)
├── #ops-coffee           — Coffee unit agents
├── #ops-content          — Naledi content pipeline
├── #ops-orders           — Order alerts
│
├── #franchisee-tumelo    — Tumelo's personal ops (Charlie, etc.)
├── #franchisee-{name}    — Each franchisee's channel + their agents
│
├── #coaching             — Coach threads + Friday wrap-ups
├── #learn-sessions       — Learning notes + resources
├── #founders-lounge      — Founders Day weekly
│
└── #alerts               — Agent errors, VM health
```

---

## Franchisee Onboarding Checklist

### Week 1 — Setup
- [ ] VM provisioned on Orgo.ai (2 CPU, 8GB)
- [ ] Ubuntu 22.04 installed + Docker
- [ ] ClickClack deployed on VM (self-hosted)
- [ ] OpenClaw installed
- [ ] Two agents configured (Operations + Outreach)
- [ ] ClickClack bot tokens created (hub owner creates)
- [ ] Franchisee invited to ClickClack workspace
- [ ] GoHighLevel sub-account provisioned (via SVHQ reseller)
- [ ] Domain pointed to their VM
- [ ] Branding applied (logo, brand name, colours)

### Week 2 — Integration
- [ ] Agents connected to ClickClack channels
- [ ] Shopify connected (or setup for their product)
- [ ] WhatsApp Business configured
- [ ] First pipeline created in GHL
- [ ] First automation tested

### Week 3 — Launch
- [ ] First leads generated
- [ ] First order processed
- [ ] First payment received
- [ ] Franchisee introduces themselves in #founders-lounge

---

## Tumelo's Action Plan — Week of July 14

| Day | Focus | Actions |
|-----|-------|---------|
| **Mon** | Plan the week | 2h session — set 3 priorities for hub build |
| **Tue–Thu** | VM setup | Get Orgo credentials + provision first franchisee VM |
| **Tue–Thu** | ClickClack | Deploy ClickClack on hub VPS ($6–10/mo DigitalOcean) |
| **Tue–Thu** | Eve AI SA | Confirm SA localization — branding, pricing, GHL setup |
| **Fri** | Founders Day | First weekly wrap with franchisee(s) |
| **Aug 1** | eveaiworkforce.com | Localize for SA — pricing in ZAR, SA case studies |
| **Aug** | Outreach | Recruit first 3 franchisees — South African entrepreneurs |

---

## Revenue Model

### Per Franchisee (per month)
| Revenue Stream | Split | Tumelo | Franchisee |
|--------------|-------|--------|------------|
| Eve AI SA subscription (R 2,997/mo per operator) | 50/50 | R 1,498 | R 1,498 |
| Biltong / product sales (their business) | 0% | — | 100% |
| GoHighLevel reseller margin (10% of sub) | 50/50 | 5% | 5% |
| Coaching upsell (R 997/month coach access) | 60/40 | R 598 | R 399 |

### Hub-Level Revenue
| Stream | Rate |
|--------|------|
| Franchise fee (one-time) | R 4,997 per franchisee |
| Agent provisioning service | R 1,997 per agent setup |
| Training workshop (2-day) | R 9,997 per founder cohort |

---

## Immediate Next Step

**Deploy ClickClack** on a $10/month DigitalOcean VPS using the script in this repo. This is the single most impactful thing we can do right now to start connecting agents.

Once ClickClack is live:
1. Tumelo creates workspace "WWE Hub"
2. Charlie and Naledi connect via bot tokens
3. Tumelo sees the hub working in real time
4. We add franchisee VMs one by one

---

*Robusca — COO, WWE Hub / Studex Meat*
*Built: 2026-07-12*
