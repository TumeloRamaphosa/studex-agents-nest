# Storefront audit — studexmeat.com

**Date:** 2026-10-24 · **Source of truth:** `https://studexmeat.com/products.json?limit=250`
(Shopify's own public catalogue API — 48 products) cross-checked against the rendered homepage,
`/collections/all` and `/search?q=StudBot`.
**Why the API and not the page:** the rendered grid is paginated at 24 and hides products behind
"load more". Two findings in this audit were **false alarms** until the API was consulted — see
§5. Never conclude a product is absent from the rendered page alone.

## Verdict
The store is **live and selling** — "In Stock and ready to ship", sale pricing across the
catalogue, cart and checkout working. This is not a dark store and must never be reported as one.
But the catalogue has **three real problems** that a customer sees today.

---

## 1. ✅ The registry prices are all correct

Every price in `studex-meat/PRICE-SOURCE-REGISTRY.md` matches the live store exactly:

| Product | Registry | Live store |
|---|---|---|
| Luxury Wagyu Biltong | from R650 | R650.00 ✅ |
| Wagyu Biltong Gold 1kg | R1,450 | R1,450.00 ✅ |
| Wagyu Biltong Gold 7kg box | R12,500 | R12,500.00 ✅ |
| Fire & Feast Box | R999 | R999.00 ✅ |
| StudBot Rise | R4,599 | R4,599.00 ✅ (in stock) |
| Coffee — Washed | R400/kg | R400.00 ✅ |
| Coffee — Honey | R350/kg | R350.00 ✅ |
| Coffee — Aerobic | R380/kg | R380.00 ✅ |
| Coffee — Natural | R270/kg | R270.00 ✅ |

Contacts also correct: `info@studexmeat.com` and `+27 84 421 6035` are published; **no street
address** appears (correct — we have no verified one); and no "closed / paused / dark" statement
appears anywhere.

## 2. 🔴 THERE IS NO CAVIAR ON THE STORE — at all

`caviar-ish: []` against all 48 products. Not one caviar SKU. Yet caviar is a headline product
with three canonical pages and full trade pricing:

- Oscietra Imperial R4,200/100g (trade R34,000/kg)
- Kaluga Prestige R2,800/100g (trade R22,000/kg)
- Sevtruga Medium R1,600/100g (trade R12,500/kg)
- private-label tins from 5kg MOQ · lead 7–14 days commercial handling

The retail static site lists caviar, so **the pages and the store disagree**. A buyer who clicks
through from the caviar page to "buy" lands on a store with nothing to buy. This is the single
highest-value finding in this audit.
Also absent: **Ox Tail** (`ox tail: []`) — consistent with "on enquiry", but no enquiry form for
it was found on the storefront, so the path should be confirmed.

## 3. 🔴 AGENT SUBSCRIPTIONS AND EVENT TICKETS ARE SELLING IN THE MEAT CATALOGUE

Six non-meat SKUs sit in the same grid as the Wagyu:

| SKU | Price | product_type |
|---|---|---|
| StudBot Rise · 3 Agents + 1kg Wagyu Biltong Gold + Agentic Rise Membership | R4,599 | Agent Subscription |
| Tier 4 — Operator ($4,500 / month) | R75,000 | — |
| Tier 5 — Ghost (The Sovereign) ($7,500 / month and up) | R125,000 | — |
| Trade Week 2026 — In-Person Access (Private Working Group) | R8,500 | Event Ticket |
| Trade Week 2026 — Online Live Access | R2,500 | Event Ticket |

Two defects inside this:
- **Currency mismatch.** The titles say **$** while the store prices in **R**. "Tier 4 — Operator
  ($4,500 / month)" sells for R75,000. A customer reads a dollar figure and a rand figure and has
  to guess which governs.
- **Positioning.** The site title is *"the home of premium South African Halaal Wagyu beef"*, and
  the grid beneath it offers a R125,000 agent tier and trade-week tickets. Deliberate or not,
  this is what the brand's front door looks like to a first-time buyer.

`StudBot Rise` is the exception — it is a genuine hybrid (agents **+** 1kg biltong) and is
defensible. The four others are not meat and not agent-meat.

## 4. 🟡 PRODUCT TITLES ARE POLLUTED — customer-visible

From the rendered storefront (note: these prefixes are in the **displayed** heading, not the
`title` field of `products.json`):

- `#wagyu #wagyubeef Wagyu Ribeye Steak 5.0`
- `#wagyu #wagyubeef Studex Meat Wagyu Flat Iron Steak`
- `#wagyu Wagyu Braai BOSS Box`
- `1. AEROBIC FERMENTATION PROCESS` · `1. NATURAL (DRY) PROCESSING` — numbered lists as product names
- `Coffeee - FULLY WASHED (WET) PROCESS` — three e's
- `🎄✨ CHRISTMAS BRAAI SORTED IN ONE CLICK! ✨🎄` — pure emoji as a title

Hashtags and emoji in a product title on a premium-beef storefront read as a social-media shop,
not a butchery. It also pollutes the SEO title string that Google renders.

**Two stale seasonal SKUs** are also live: `Easter Family Feast` (R2,850 — Easter is ~6 months
away) and the Christmas braai set (R2,850). Both sit at the same price point as current stock.

**One sold-out SKU:** `Ankole Ribeye Steak 1kg` (R1,050 sale / R1,750). Every other product is
in stock — worth a look if that cut was meant to be available.

## 5. 🟢 TWO FINDINGS THAT WERE FALSE ALARMS — and why they matter

- **"Product title" at R19.99** — a placeholder rendered by the theme's modal template. It is
  **not in `products.json`** and is not purchasable. A page-scraping audit flagged it as a live
  SKU. It is not.
- **"StudBot Rise is missing from the store"** — it *is* there (R4,599, in stock). The catalogue
  grid paginates at 24 of 48; the product was simply past the fold.

🔑 **Both mistakes came from trusting the rendered page instead of the catalogue API.** A
paginated grid and a theme template both look exactly like "missing" and "broken" respectively.
**For catalogue truth, query `products.json`.** For what a customer *sees*, query the rendered
page. They answer different questions, and each one masquerades as the other.

## 6. Not product_type'd — there is no catalogue taxonomy

Most SKUs have an **empty `product_type`**; only a handful are set (`simple`, `coffee`,
`Event Ticket`, `Agent Subscription`, `variable`). The visible collections are *Speciality
Coffee · Carnivore Connoisseur · Shop All Cuts · Shop Categories* — **no caviar, no biltong,
no coffee-as-collection beyond one**. A flat, untaxonomised 48-SKU catalogue is why the grid
reads as a wall and why buyers cannot find a category.

## 7. 🔴 THERE IS NO WHATSAPP ON THE STOREFRONT — CONFIRMED

Checked against the **raw server-rendered HTML** (838 KB, `curl` of the homepage, not extracted
text):

- `wa.me/…` — **0 occurrences**
- the string `whatsapp` — **0 occurrences**
- email addresses — exactly **one**: `info@studexmeat.com` ✅ (no stale addresses)
- `+27…` numbers in the markup — none in that bare format; `+27 84 421 6035` *is* published, but
  formatted with separators, which is why a strict digit-run regex missed it. **Not a defect.**

🔑 **This is conclusive, not "unverified".** Shopify renders themes **server-side through
Liquid**, so a theme WhatsApp button *would* appear in the raw HTML. A JS-only element appended
after load would not — but Shopify sticky buttons are Liquid, and there is no trace of one.
**The storefront has no WhatsApp channel at all.** A customer can email or phone, and nothing else.

Consequence: our canonical store WhatsApp **`+27 94 988 8737`** is published on the static pages
but is **absent from the storefront**, and the retail order form on the static site routes to a
**different** number (`+27 83 593 2577`, deliberate). So the two surfaces a buyer meets first
offer them **three different phone numbers and one channel they cannot use**.
🔑 **The WhatsApp number is the fastest conversion path in this market and it is not wired to the
shop.**

## Owner decisions
1. **List caviar on the store** — 3 SKUs, prices already agreed. Highest value, lowest effort.
2. **Fix the "$" vs "R"** in the Tier 4 / Tier 5 titles, or move those SKUs off the meat store.
3. **Decide what belongs in the meat grid.** `StudBot Rise` yes; Tier 4, Tier 5 and the
   Trade Week tickets need a home of their own.
4. **Clean the 6 polluted titles** and remove the two stale seasonal SKUs.
5. **Set `product_type`** across the catalogue and add caviar + biltong collections.
6. Restore the **Shopify Admin API token** — without it, stock and orders cannot be read
   programmatically, which is why this audit had to be done over the public catalogue.
