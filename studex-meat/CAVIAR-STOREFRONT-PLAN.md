# Caviar on the storefront — collection + enquiry-to-checkout plan

**Status:** proposal, nothing built, nothing published. Implements `studex-meat/CAVIAR-SOURCING-RISK-MEMO.md`
decision **#5** — *"Caviar is not in the Shopify store — it sells via the trade page only. A quote
with no purchase path is a quote that dies. Needs a collection + enquiry-to-checkout path."*

**Why this is a gap and not a feature request:** the 2026-10-24 storefront audit found **zero
caviar SKUs across all 48 live products** (`https://studexmeat.com/products.json?limit=250`).
The product, the pricing, the lead-time copy and three canonical pages all exist. The SKU does
not. The static retail site has an enquiry form; the store has nothing to check out into.

---

## 1. Shape

**A collection, not a nav item.** Memo decision #1: the premium tier must be *"a clearly-labelled
optional SKU, not the spine of the line."* The same logic applies to the storefront — caviar
belongs in a **Caviar collection** reachable from the product grid, not in the top nav and not
in the meat grid beside the R125,000 agent tier.

**Three purchasable retail SKUs (100g tins) + one enquiry-only private-label product.**

🔑 **Trade prices do NOT go on the storefront.** They are per-kg wholesale prices for hospitality
buyers, they are quote-based, and as of 2026-10-24 they are **below our own 30% floor**
(see `CAVIAR-PRICING-FLOOR-FINDING-2026-10-24.md`). A consumer storefront selling below-floor
wholesale prices would be the worst possible place to expose them. Trade stays on the caviar
page, behind an enquiry.

## 2. The SKUs

Prices are **retail per 100g, taken verbatim from `PRICE-SOURCE-REGISTRY.md` §2.3**. No price is
invented here.

| # | Title | Handle | Price | Compare-at | Type |
|---|---|---|---|---|---|
| 1 | Oscietra Imperial Caviar — 100g Tin | `oscietra-imperial-caviar-100g` | **R4,200.00** | — | `caviar` |
| 2 | Kaluga Prestige Caviar — 100g Tin | `kaluga-prestige-caviar-100g` | **R2,800.00** | — | `caviar` |
| 3 | Sevtruga Medium Caviar — 100g Tin | `sevtruga-medium-caviar-100g` | **R1,600.00** | — | `caviar` |
| 4 | Caviar Private Label — Your Logo, from 5kg | `caviar-private-label-5kg-moq` | *(enquiry)* | — | `caviar` |

SKU 4 has **no price** — it routes to the server-side lead proxy (`studex-lead-proxy/`, which
delivers to `sales@studex-group.com`) with a quote request, per the existing *"Private-label tins
from 5kg MOQ"* line on the retail page. It is the **volume tier** memo decision #4 says the
segment should lead with.

**Options, if wanted:** a single 100g unit only. 🔑 **Do not add a 250g option** — *"per 250g"* is a
retired claim (registry §banned) and *"500g per tin"* is retired too. One unit, per 100g, exactly
as the caviar page and the registry state.

**Inventory:** do **not** track stock with invented quantities. Caviar is imported to order and
the first shipment runs ≈2 months end-to-end. Either leave stock untracked, or track with 0 and
allow backorder. 🔑 **Never publish a stock level we do not have.**

## 3. Copy — what each description must and must not contain

**Must:**
- **Origin, explicitly** — Russia · Caspian Sea (Oscietra) · Amur River (Kaluga) · Black Sea
  (Sevtruga), and *"Moscow → SA cold-chain"*. This is already the published position on the
  caviar page and it is correct.
- **"Certificate of origin from Russian supplier"** — already published wording; keep it.
- **Lead time, in the published form** — *"7–14 days' commercial handling from order confirmation,
  counted from the date the DAFF veterinary import permit is issued. For a first shipment the
  permit must be applied for at least 4 weeks ahead and takes 5–10 working days to issue once
  approved — allow roughly two months end to end."*
- **Unit** — 100g, and the per-kg equivalence where useful.
- **"Prices in ZAR"** and the landed-cost framing.

**Must not:**
- 🔴 **Any duty or VAT percentage.** The broker's HS classification answer is outstanding and the
  memo rule is *"do not publish the answer until it comes back."* Use the approved wording:
  *"exclude import duty and delivery"* / *"import duty and VAT quoted in the landed cost."*
- 🔴 **"certified Russian caviar houses"** or **"ethically sourced"** — both retired (registry §4).
- 🔴 **"Sevruga"** (retired) — it is **Sevtruga Medium**.
- 🔴 **A stock level, a lead-time number that is not the published one, or any certification
  claim we cannot cite.**
- 🔴 **Any trade price.**

## 4. Images — the real gap

Two caviar images exist in the repo:
`imgs/caviar-premium.png` · `studex-biltong/caviar_product_01.png`

🔑 **Neither is verified as a per-SKU image for a 100g tin**, and a storefront product with the
wrong tin photo is worse than no photo. **Three SKU images are required** before publishing —
one per tier, showing the 100g tin. If they don't exist, they need shooting; they must not be
cropped from a generic premium shot without checking what the tin actually looks like.

## 5. Collection

Create collection **`Caviar`** (handle `caviar`), put SKUs 1–4 in it, and **do not** add it to
the top-level nav. Add it to the **Caviar** collection on the caviar page and the retail site's
caviar block so the three surfaces agree.

## 6. Checkout mechanics

- Shopify Payments, currency **ZAR** (the store already prices in ZAR — `ShopifyStore.tsx`).
- The store's Admin API token is still missing, so inventory/orders cannot be read
  programmatically. **That is why this plan exists** — the caviar enquiry path today ends in a
  form on a static page, not a checkout.
- Do **not** put an AgentMail or Blotato key in any client bundle. The enquiry form posts to the
  existing server-side lead proxy.

## 7. How it gets built

`studex-meat/scripts/create-caviar-skus.py` — **dry-run by default**, `--confirm` required to write.

It needs two things that are not available yet:
- `SHOPIFY_ADMIN_TOKEN` (Admin API, `write_products` scope)
- the shop domain (`SHOPIFY_SHOP`)

Until those exist the script **prints the payloads and exits** — it never silently "succeeds"
with zero products created. 🔑 **Missing credentials must fail loudly; a script that reports
success while creating nothing is the exact failure class this repo keeps hitting.**

### The order of work

🔑 **This plan does NOT wait on the trade-price decision.** The trade prices (R34,000 / R22,000 /
R12,500 per kg) are below our modelled floor and under review. **The retail prices are not.**
Retail is +59.3% / +49.7% / +44.9% markup on landed cost — comfortably above the 30% floor —
so the three purchasable SKUs can be built on registry retail prices while the trade question
is resolved separately. The trade prices appear on **no** storefront SKU; they stay quote-only.

1. **Send the clearing-agent email** (HS line, 2026 duty rate, ITAC permit, Rebate 460.19) — it
   is the input that decides the floor, and therefore whether the trade prices move at all.
   *Blocked on a named recipient + Tumelo's approval.*
2. **Correct the landed-cost model** — remove recoverable import VAT, replace the assumed 20%
   duty with the broker's answer, move FX off a hardcoded 18.5, then recompute the floor.
3. **Decide the trade price** (floor vs accept) — *after* step 2, not before.
4. **Shoot or select three 100g tin images.** The two caviar images in the repo are generic —
   a wrong tin photo is worse than no photo.
5. **Get the Admin API token** (`SHOPIFY_ADMIN_TOKEN`). Until then nothing can be published.
6. **Build the collection + 3 SKUs + 1 enquiry product**; link from the caviar page and the
   retail page.
7. **Add the corrected floor to `PRICE-SOURCE-REGISTRY.md`** as a visible reference row —
   the research asked for this on 2026-10-23 and it never happened. (The *cost sheet* rebuild
   did land; the *registry* update did not.)

## 8. What this plan does **not** do

- ❌ It does not create the **R650–900 service entry tier** (memo decision #3 — *pending
  approval, no verified cost behind it*).
- ❌ It does not name a **farmed second source** (memo decision #2 — *no farm contacted*).
- ❌ It does not list **any tier as the spine** of the line.
- ❌ It does not publish a **duty number**.
- ❌ It does not change a published price.
