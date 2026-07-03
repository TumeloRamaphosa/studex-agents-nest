# Coffee Subscription + Global Bridge — Planning
**Created:** 2026-07-02
**Status:** Active Planning

---

## 1. RUKUNDO COFFEE — Supplier Analysis

**Supplier:** Jacky Rukundo C. — RUKUNDO COFFEE (Rwanda)
**Product Range:**

| Product | Weight | Price (ZAR) | Cost per kg |
|---------|--------|-------------|-------------|
| Robusta Medium Beans | 250g | R120 | R480/kg |
| Robusta Dark Roast Beans | 250g | R130 | R520/kg |
| Arabica Beans | 250g | R135 | R540/kg |
| Bazzukulu Beans | 250g | R140 | R560/kg |
| Arabica Beans | 1kg | R520 | R520/kg |
| Bazzukulu Beans | 1kg | R520 | R520/kg |
| Dark Roast Beans | 1kg | R480 | R480/kg |
| Gift Bag (Blend) | 1kg | R620 | R620/kg |
| Dark Roast Gift Bag | 1kg | R580 | R580/kg |
| Honey | 350g | R160 | R457/kg |
| Gift Bag | — | R350 | — |

**Assessment:** These are wholesale/markup prices. RUKUNDO is likely the supplier; their prices suggest they are a mid-stream aggregator, not the farm. The "Bazzukulu" and "Arabica" branding suggests smallholder sourcing.

---

## 2. How to Price the Subscription

**Cost Build (示例 — 250g Arabica):**
- Bean cost from RUKUNDO: R135 (250g)
- Packaging (branded bag + label): ~R15
- Shipping allowance: ~R20
- Total cost: ~R170

**Recommended Retail Pricing:**
| Plan | Weight/week | Cost | Sell Price | Margin |
|------|-------------|------|------------|--------|
| Starter | 250g | R135 | R249 | 46% |
| Daily Drinker | 500g | R270 | R449 | 40% |
| Office/Family | 1kg | R520 | R799 | 35% |
| Premium Single-Origin | 250g | R140 | R289 | 52% |

**Note:** These are ex-JHB. Add delivery to other provinces.

---

## 3. The 5 Deals — Positioning Strategy

The goal: **Get suppliers to WANT to be on the platform, not just listed.**

### Deal Types:

**Deal 1 — Guaranteed Offtake**
- We commit to buying a fixed volume per month
- Farmer guarantees supply quality + delivery
- Our value: predictable income for them = lower risk

**Deal 2 — Co-Branded Origins**
- Label the coffee with the farmer/co-op name AND our brand
- Farmers get recognition; we get provenance story
- Shared marketing asset = they promote it too

**Deal 3 — Early Payment (Micro-Credit)**
- We pay farmers 30 days early for a small premium
- Unlocks working capital for smallholders
- Cost: ~3–5% discount; value to farmer: huge

**Deal 4 — Data Dividend**
- We share market intelligence with farmers (global prices)
- They understand where they sit relative to global markets
- They become smarter sellers = better margins for us too

**Deal 5 — Exclusive Regional Rights**
- We get first refusal on new harvests from a region
- Suppliers list on our exchange first before going elsewhere
- Creates platform exclusivity over time

---

## 4. Buyer Personas

**Primary Buyers:**
1. **African Diaspora** — South Africans, Nigerians, Kenyans abroad who want quality African coffee shipped globally
2. **Specialty Coffee Drinkers (Urban AU/NZ/UK/EU)** — Climate-conscious, provenance-aware, willing to pay premium for story
3. **Corporate Gifters** — Businesses buying African coffee for client hampers
4. **Wholesalers/Roasters (International)** — Sourcing African origins for their own roasting
5. **Subscription Box Curators** — Other subscription services looking for African supplier base

**Launch Target (July Africa):**
- Urban professionals in JHB, Cape Town, Lagos, Nairobi
- Age 25–45
- Already buying Checkers/Spar premium coffee
- Willing to pay R400–800/month for quality + story

---

## 5. Online Coffee Exchange — Global Bridge Vision

**What it is:** A B2B coffee trading platform layered over the subscription

### How We're Unique:
1. **Provenance-First Trading** — Every lot linked to farmer/co-op. Not just "Grade 1" but WHO grew it.
2. **African Price Benchmark** — We publish the only daily African specialty coffee price index (vs. NY ICE which is commodity Arabica)
3. **Subscription = Market Validation** — Consumer demand signals inform futures pricing for B2B
4. **Smallholder-First** — Built for farmers with <5 hectares, not corporate plantations
5. **Cross-Border Simplified** — We handle FX, logistics, compliance in one platform

### Revenue Model:
- Subscription revenue (B2C)
- Trading fees on exchange (B2B) — 2–5% per transaction
- Data subscriptions (price index reports sold to roasters)
- Logistics + fulfillment fees

---

## 6. Coffee Agents — Architecture

### Agent 1: COFFEE JARVIS (Buyer Intelligence Agent)
**Purpose:** Price intelligence + buyer profiling + supplier matching

**Capabilities:**
- Scrapes global coffee futures (NY ICE, London LIFFE) daily
- Tracks RUKUNDO + competitor pricing weekly
- Monitors FX (USD/ZAR, EUR/ZAR) impact on landed costs
- Identifies arbitrage opportunities between African origins
- Alerts when margin drops below threshold

**Tools:** Web scraping, yfinance, FX API, Discord alerts

**Output:** Daily price brief → posted to Discord #coffee-ops

---

### Agent 2: SUPPLIER MATCHMAKER
**Purpose:** Onboard + manage farmer suppliers

**Capabilities:**
- Walks new farmers through onboarding (what we need: SCA lot ID, farm GPS, harvest date, processing method)
- Verifies Halaal/organic certifications
- Calculates fair farmgate price vs. market
- Flags at-risk suppliers (late delivery, quality drops)

**Output:** Supplier dashboard in Obsidian + alert if supply gap

---

### Agent 3: SUBSCRIPTION ORCHESTRATOR
**Purpose:** Run the subscription loop autonomously

**Capabilities:**
- Tracks active subscriptions, renewal dates, delivery status
- Alerts when customer is approaching renewal
- Flags churn risk (no engagement in 30 days)
- Posts weekly subscription report to Discord

**Trigger:** New order → validates payment → triggers dispatch → confirms delivery

---

### Agent 4: GLOBAL BRIDGE AGENT
**Purpose:** Manage cross-border B2B inquiries

**Capabilities:**
- Qualifies international buyer inquiries (what origin? what volume? what frequency?)
- Matches buyers to verified suppliers
- Manages LOI (Letter of Intent) workflow
- Tracks shipment status across borders

---

## 7. RileyJarvis — Desktop Control via TailScale

**What it is:** Local Electron AI companion with voice, screen control, and browser automation. Built by rileybrown — macOS native.

**How it works for us:**
```
Your Mac Mini (TailScale VPN)
    ↓ SSH + screen share
Orgo VM (Our Server)
    ↓
OpenClaw (Our Brain)
```

**What we can do with it:**
1. Open Chrome on your desktop → navigate to Shopify admin → extract the API key
2. Paste the key into our config automatically
3. Monitor orders live via your Shopify session
4. Access any browser-based service you have open

**Setup path:**
1. Install TailScale on your Mac Mini + on Orgo VM
2. Authenticate both under same account
3. Access your desktop via VNC or SSH tunnel from Orgo
4. RileyJarvis runs on your Mac Mini, we interact with it via API

**RISK NOTE:** Computer-use mode on macOS requires Accessibility permissions. Only enable when we need it. Disable after key extraction.

---

## 8. Dench + Cashclaw OS Pages

### DENCH — CRM Page (embeddable)
**URL:** dench.com (owned by Dench Design — needs dench.com/api key)
**What it shows:**
- All customer contacts (from Shopify + AgentMail)
- Deal pipeline (open orders, pending wholesale, hot leads)
- Message history per customer
- Next action items

**Our integration:** We create a `/dench` page in the OS that embeds the Dench CRM via iframe or pulls data via their API

**Status:** `dench.com/api` key MISSING — need to get this from dench.com

---

### CASHCLAW — Freelance Work Page
**Platform:** moltlaunch.com marketplace
**What it shows:**
- Active gigs on Moltlaunch
- Earnings to date
- Available tasks/clients
- CashClaw's own agent dashboard (if it has a web UI)

**Our integration:** Create a `/cashclaw` page that:
- Pulls Moltlaunch public gigs via web scraping
- Shows what CashClaw is working on
- Displays earnings tracker

**Status:** No public API for Moltlaunch — web scraping or manual entry required

---

## 9. July Launch — Subscription Checklist

- [ ] Confirm Shopify store is live with coffee products
- [ ] Get Shopify API token → connect to OpenClaw
- [ ] Finalise RUKUNDO supply agreement (price list locked)
- [ ] Design branded packaging (from RUKUNDO plain → Studex branded)
- [ ] Set up payment gateway (Shopify Payments or PayGenius SA)
- [ ] Write product descriptions (copy from this doc)
- [ ] Configure delivery (local: CourierGuy? Pudo? | National: Aramex?)
- [ ] COFFEE JARVIS agent live — price monitoring active
- [ ] Draft launch post (Naledi + Freekpik)
- [ ] Soft launch to existing Studex Meat customers first

---

## 10. Immediate Next Steps (This Week)

1. **Get Shopify key** — Via RileyJarvis + TailScale access (coordinate with Tumelo)
2. **Clone RUKUNDO pricing** into our product pages
3. **Launch COFFEE JARVIS** — daily price brief to Discord
4. **Build `/coffee` page** on the OS — live pricing dashboard
5. **Build `/dench` page** — CRM embed (pending API key)
6. **Build `/cashclaw` page** — Moltlaunch scraper (manual for now)

---

*Last updated: 2026-07-02 21:15 UTC*
