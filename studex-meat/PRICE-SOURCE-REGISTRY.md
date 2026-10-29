# Studex — Price & Contact Source Registry
**Purpose:** one row per price and per contact, naming the file that OWNS it and every page that must show it.
**Created:** 2026-10-21 · **Last verified:** 2026-10-21 21:40 UTC (Build Hour — trade-terms panel + caviar permit lead time)
**Why this exists:** on 2026-10-21 four customer-facing pages shipped wrong numbers (caviar units, coffee "June 2026" pricing, gifting quoting per-kg meat prices, Biltong product-offer stale prices) and one dead contact (`agent.studexmeat.com`) was found in 3 email signatures and 6 operative agent docs. Every one of those was a page or doc that had drifted from its source. This file is the drift alarm.

---

## 1. THE RULE
> **A price belongs to a product, not a page.** If a price changes, the owning source is changed **first**, then every page listed against it is re-checked. A page must never be edited to hold a price that exists nowhere else.

---

## 2. PRICE REGISTRY

### 2.1 Retail biltong & bundles — owner: `studex-biltong/dist/index.html` (mirrored to live Shopify `studexmeat.com`)
| Product | Price | Must appear on |
|---|---|---|
| Luxury Wagyu Biltong, 500g | From **R325** (500g pack) | `t56b7vkncytt` |
| Wagyu Biltong Gold, 1kg | **R1,250** (per kg) | `t56b7vkncytt` · `i09hd71cvt06` |
| Wagyu Biltong Gold, 7kg case | **R8,400** (1,200/kg — beats seven 1kg bags) | `t56b7vkncytt` |
| Subscription — Starter (200g/mo) | **R295** | `t56b7vkncytt` |
| Subscription — Connoisseur (500g + 100g Ox Tail/mo) | **R495** | `t56b7vkncytt` |
| Subscription — Bulk / Corporate (per mo) | **R850** | `t56b7vkncytt` |
| Fire & Feast Box | **R999** | `t56b7vkncytt` |
| StudBot Rise Bundle | **R4,599** | `t56b7vkncytt` |
| Biltong Gold 200g (gift box) | included in hamper | `oi28dhtke3yk` |
| Premium Beef Biltong 300g (gift box) | included in hamper | `oi28dhtke3yk` |

### 2.2 Roasted coffee (SA) — owner: live Shopify `studexmeat.com`
| Process | Price /kg | Must appear on |
|---|---|---|
| Washed | **R400** | `t56b7vkncytt` · `i09hd71cvt06` |
| Honey | **R350** | `t56b7vkncytt` · `i09hd71cvt06` |
| Aerobic | **R380** | `t56b7vkncytt` · `i09hd71cvt06` |
| Natural | **R270** | `t56b7vkncytt` · `i09hd71cvt06` |
| Trade MOQ (roasted) | **50 kg** | `i09hd71cvt06` |

### 2.3 Caviar — owner: `deploy-caviar/index.html` (AUTHORITATIVE — units are per 100g)
**Retail, per 100g — caviar page only (caviar came off the retail sale path on 2026-10-28):**
| Product | Retail /100g | Must appear on |
|---|---|---|
| Oscietra Imperial | **R4,200** | `ess0ocgcd9f0` |
| Kaluga Prestige | **R2,800** | `ess0ocgcd9f0` |
| Sevtruga Medium | **R1,600** | `ess0ocgcd9f0` |

**Trade, per kg — caviar page only:**
| Product | Trade /kg | Must appear on |
|---|---|---|
| Oscietra Imperial | **R34,000** | `ess0ocgcd9f0` ·  |
| Kaluga Prestige | **R22,000** | `ess0ocgcd9f0` ·  |
| Sevtruga Medium | **R12,500** | `ess0ocgcd9f0` ·  |

**Caviar page only:**
| Item | Detail | Must appear on |
|---|---|---|
| Private-label tins | from **5 kg MOQ** | `ess0ocgcd9f0` |
| Import lead (commercial handling) | 7–14 days — **counted from the date the DAFF veterinary import permit is issued**, not from order confirmation | `ess0ocgcd9f0` |
| DAFF veterinary import permit | applied for **at least 4 weeks before shipment**; **5–10 working days** to issue once approved — so a first shipment is roughly two months end to end | `ess0ocgcd9f0` |

> ⚠️ **Never** use the retired names "Sevruga Premium" / "Siberian Reserve" or the unit "per 250g". Both were wrong and are gone.

### 2.4 Institutional meat — owner: `studex-meat/institutional-sales-onepager.md` (ex VAT, as at Oct 2026, subject to confirmation)
| Product | Price | Must appear on |
|---|---|---|
| Wagyu ribeye (A5 cross) | **R1,050/kg** | `hhsmhunf1xci` |
| Wagyu fillet | **R1,150/kg** | `hhsmhunf1xci` |
| Craft biltong (original) | **R380/kg** | `hhsmhunf1xci` |
| Craft biltong (peri-peri) | **R410/kg** | `hhsmhunf1xci` |
| Dry-aged beef (30-day) | **R850/kg** | `hhsmhunf1xci` |
| Custom hamper (12-pack) | **R2,200/hamper** | `hhsmhunf1xci` |

### 2.5 Corporate gifting — owner: `studex-meat/CORPORATE-GIFTING-OCT2026.md`
| Box | Price | Minimum | Delivery | Must appear on |
|---|---|---|---|---|
| The Classic | **R1,299/box** | 5 boxes | 5 days | `oi28dhtke3yk` · `hhsmhunf1xci` |
| The Executive | **R2,499/box** | 3 boxes | 3 days | `oi28dhtke3yk` · `hhsmhunf1xci` |
| The Boardroom | **R4,999/box** | 2 boxes | 2 days | `oi28dhtke3yk` · `hhsmhunf1xci` |
| Custom branding | — | 20+ boxes | 4-week lead | `oi28dhtke3yk` |
| Early bird | **10% off** Executive + Boardroom | order before **28 Nov** | code `STUDEXGIFT10` | `oi28dhtke3yk` |
| Final order date | **20 Dec 2026** | — | — | `oi28dhtke3yk` |

> ⚠️ The old `studex-corporate-gifting/` page quoted **R850 / R1,450 / R2,200** — those are institutional per-kg meat prices and were WRONG in a gifting context. That file has been overwritten with the corrected page.

### 2.6 Green coffee, FOB — owner: `studex-wildlife-coffee-vite/dist/index.html` (indicative, as at Oct 2026)
| Origin | From | Cupping | Must appear on |
|---|---|---|---|
| Rwanda A1 Washed (Nyamasheke) | **USD 4,200/MT** FOB Djibouti | 84–87 | `de6xdoikz95g` · `i09hd71cvt06` |
| Ethiopia Yirgacheffe (Gedeo) | **USD 4,500/MT** FOB Djibouti | 86–90 | `de6xdoikz95g` · `i09hd71cvt06` |
| Kenya AA Nyeri | **USD 4,800/MT** FOB Mombasa | 87–89 | `de6xdoikz95g` · `i09hd71cvt06` |
| Uganda Bugisu AA (Elgon) | **USD 3,400/MT** FOB Djibouti | 83–86 | `de6xdoikz95g` · `i09hd71cvt06` |
| South Africa Bourbon (Mpumalanga) | **USD 5,200/MT** CIF Durban | 82–85 | `de6xdoikz95g` · `i09hd71cvt06` |
| Custom blend (MOQ 5 MT) | **USD 3,800/MT** FOB Djibouti | — | `de6xdoikz95g` · `i09hd71cvt06` |
| A1 Premium — 17+ screen, wet polished, 20 MT | **USD 4,200–4,800/MT** | — | `de6xdoikz95g` |
| A2 Commercial — 15–16 screen, 40 MT | **USD 3,600–4,000/MT** | — | `de6xdoikz95g` |
| Sample shipment (5–10 kg) | **USD 28–45/kg** | — | `de6xdoikz95g` |
| Hospitality | 50–200 kg/mo per client | — | `de6xdoikz95g` · `i09hd71cvt06` |
| Office | 20–100 kg/mo per office | — | `de6xdoikz95g` · `i09hd71cvt06` |
| Retail & specialty | 200–2,000 kg/mo | — | `de6xdoikz95g` · `i09hd71cvt06` |
| Commodity traders | 60–240 MT/container | — | `de6xdoikz95g` · `i09hd71cvt06` |

### 2.7 Green coffee, CIF Shanghai (China) — owner: `china-coffee-export/index.html`
| Lot | Price | MOQ | Must appear on |
|---|---|---|---|
| Rwanda A1 — Washed | **$4,800 – $5,400/MT** CIF Shanghai | 1 MT | `fr7m7fzyailo` |
| Rwanda A2 — Washed | **$4,200 – $4,700/MT** CIF Shanghai | 1 MT | `fr7m7fzyailo` |
| Rwanda Premium — Natural (87+) | **Enquire** — quoted per lot, no published price | 500 kg | `fr7m7fzyailo` |
| Lead time | **5–7 weeks** (Kigali→Djibouti 5–7d + ~21d sea) | — | `fr7m7fzyailo` |
| Tariff | **0%, and NO expiry for our Rwandan LDC origin** — China's 100% zero-tariff treatment for African LDCs has been in force since **1 Dec 2024**, and from **1 May 2026** the zero-tariff framework covers all 53 African countries with diplomatic relations (all but Eswatini). The **30 Apr 2028** window applies to the 20 African countries that are **not** LDCs — it is THEIR expiry, never ours. African coffee under unified phytosanitary system **from 20 July 2026** | — | `fr7m7fzyailo` |

### 2.8 Stud-Bot / Studex Computer — owner: `studex-computer/index.html`
| Tier | Price | Must appear on |
|---|---|---|
| Starter | **R4,999 once + R499/mo** | `3zryumjeuemk` |
| Growth | **R8,999 once + R999/mo** | `3zryumjeuemk` |
| Scale | **R18,999 once + R1,999/mo** | `3zryumjeuemk` |

> ❗ **UNRESOLVED CONFLICT.** MEMORY.md's "Stud-Bot Super Agents" product spec says **R500 / R1,500 / R4,000 per month** (per-agent tiers, no setup fee). The live page says the above. These are two different products/pricings. **Owner must confirm which is correct; nothing was changed.**

### 2.9 Retail steaks (live Shopify product pages) — owner: live Shopify `studexmeat.com`
| Product | Price | Must appear on |
|---|---|---|
| Wagyu Ribeye Steak — 500g | **R950** (was R1,569) | `studexmeat.com/products/ribeye-steak` |
| Wagyu Ribeye Steak — 1kg | **R1,950** (was R2,939) | `studexmeat.com/products/ribeye-steak` |

> 🔑 **ADDED 2026-10-27.** The content agent's product catalog carried a "Wagyu Ribeye
> Steak", but this registry had **no** row for a retail ribeye at all — so the price was
> **unowned**: nothing owned it, nothing checked it, and nothing would have seen it change.
> `ops/check-catalog.py` now compares the **numeric** price (not the price string) and
> flags any catalog product whose price is absent from this registry.
>
> 🔑 **"From" means the CHEAPEST variant, and the cheapest is R950** (the 500g). The catalog
> said **"From R1,950"**, which is the 1kg price — on a Facebook post that overstates the
> entry price by **R1,000 (105%)**. The convention already set on 21 Oct (see §2.1) is to
> quote **live Shopify sale pricing**.
>
> ⚠️ **The canonical static retail site (`t56b7vkncytt`) does not carry the steak range at
> all**, though the live store sells it. The store's `Steaks` collection includes ribeye,
> chuckeye, sirloin, t-bone, tri-tip, tomahawk, rump, fillet, picanha and the Ankole cuts.
> **Tumelo to confirm** whether the static sales surface should carry that range.
> (`Ankole Ribeye Steak 1kg` at **R1,050** is already owned by §2.4.)

---

## 3. CONTACT REGISTRY
| Contact | Status | Use for |
|---|---|---|
| `info@studexmeat.com` | ✅ verified live (on the Shopify storefront) | default public contact on every page |
| `info@studex-group.com` | ✅ live AgentMail inbox | corporate gifting, group enquiries |
| `sales@studex-group.com` | ✅ live AgentMail inbox | trade / platform enquiries |
| `t-ramaphosa-ceo@studex-group.com` | ✅ live AgentMail inbox | CEO / Super Agents enquiries |
| `naledi-cmo@studex-group.com` | ✅ live AgentMail inbox | CMO / content |
| `support.superagents@studex-group.com` | ✅ live AgentMail inbox | Super Agents support |
| `robusca.romanov@studex-group.com` | ✅ live AgentMail inbox | Chief of Staff |
| `+27 94 988 8737` | ✅ store WhatsApp | **default WhatsApp CTA on every page** |
| `+27 84 421 6035` | ✅ store phone | public phone on every page |
| `+27 83 593 2577` | ✅ Tumelo personal | named contact only — **not** the default CTA |
| `https://studexmeat.com` | ✅ live storefront | retail |
| `agent.studexmeat.com` | ❌ **NO DNS — never use** | removed from all pages, posts, signatures, agent docs |
| `studexwildlife.com` | ⚠️ parked (AWS parking IPs), no verifiable mail route | `t.ramaphosa@studexwildlife.com` removed from coffee page |

> ⚠️ The **retail order form** (`t56b7vkncytt`) routes to `wa.me/27835932577` = **Tumelo's personal line**. Every other page uses the store line. Left deliberately — do not change without owner approval.

---

## 4. PAGE → SOURCE → URL
| Page | Source dir | Live URL |
|---|---|---|
| Retail store | `studex-biltong/dist/` | `t56b7vkncytt.space.mcode.io` |
| Institutional & corporate sales | `studex-sales-static/` | `hhsmhunf1xci.space.mcode.io` |
| Corporate gifting | `corporate-gifting/` | `oi28dhtke3yk.space.mcode.io` |
| Caviar trade | `deploy-caviar/` | `ess0ocgcd9f0.space.mcode.io` |
| Coffee B2B green | `studex-wildlife-coffee-vite/dist/` | `de6xdoikz95g.space.mcode.io` |
| Coffee SA hospitality | `sa-hospitality-coffee/` | `i09hd71cvt06.space.mcode.io` |
| Coffee China / CIIE | `china-coffee-export/` | `fr7m7fzyailo.space.mcode.io` |
| B2B narrative | `studex-meat-static/` | `4mak476g6rmo.space.mcode.io` |
| Stud-Bot | `studex-computer/` | `3zryumjeuemk.space.mcode.io` |
| CIIE coffee landing (React) | `ciie-coffee-landing/dist/` | `9yk65ajlg1s9.space.mcode.io` |
| Coffee noir B2B landing (React) | `coffee-noir-landing/dist/` | `qefqcvvpd8al.space.mcode.io` |
| China coffee lead capture (React) | `china-coffee-lead-capture/dist/` | `jqbgl8pu0uyh.space.mcode.io` |
| Caviar trade (React) | `studex-caviar/dist/` | `jgk62vzamgtk.space.mcode.io` |
| Price reference (React) | `studex-price-desk/dist/` | `jisom3k4i126.space.mcode.io` |

> **⛔ SUPERSEDED URLS — still live, do not share (2026-10-21).** Each redeploy creates a new URL and the old one keeps serving the **old** copy.
> | Superseded URL | What it still says | Replaced by |
> |---|---|---|
> | `hrji88f70666.space.mcode.io` | *"Every product we produce is certified Halaal… No exceptions"* | `t56b7vkncytt.space.mcode.io` |
> | `x2tvaieb5qgz.space.mcode.io` | *"Rainforest Alliance certified"* + *"Full RA certification across all supply chain stages"* | `fr7m7fzyailo.space.mcode.io` |
> | `z7p9urw22jwb.space.mcode.io` | *"All products Halaal certified"* | `hhsmhunf1xci.space.mcode.io` |
> | `lyf0l7cahlbd.space.mcode.io` | badge spelled *MJC Halal Trust* | `t56b7vkncytt.space.mcode.io` |
> | `j439h3l2g94g.space.mcode.io` | linked the old sales sheet | `4mak476g6rmo.space.mcode.io` |
> | `lqzo3q09yntr.space.mcode.io` | *"The 0% tariff window closes on 30 April 2028"* — **wrong for a Rwandan LDC origin** (our zero-tariff has no expiry) | `fr7m7fzyailo.space.mcode.io` |
> | `eukr32nxiptw.space.mcode.io` | *"0% for all 53 African countries, 1 May 2026 – 30 April 2028"* — the expiry was **theirs, not ours** | `de6xdoikz95g.space.mcode.io` |
> | `o1xo4h5m6u9u.space.mcode.io` | *"0% — and no expiry for our Rwandan LDC origin"* — correct for Rwanda, but the non-Rwandan origins’ 30 April 2028 window was missing | `de6xdoikz95g.space.mcode.io` |
| `llox95u1dtfg.space.mcode.io` | marquee + footer said *100% Halaal Certified* | `t56b7vkncytt.space.mcode.io` |
| `klre58fvhmdc.space.mcode.io` | said *certified farms* | `de6xdoikz95g.space.mcode.io` |
| `tex91uns0obh.space.mcode.io` | craft block said *100% Halaal Certified*; order CTA said *Halaal guaranteed* | `t56b7vkncytt.space.mcode.io` |
| `8fk34ak7bp5o.space.mcode.io` | no visible contact block (the source file had drifted) | `t56b7vkncytt.space.mcode.io` |
| `fa4xt0vnu67u.space.mcode.io` | caviar page published **"7–14 days from order confirmation"** as the total lead time (the DAFF veterinary permit needs 4 weeks + 5–10 working days) and **"duty (±20%)"** — an unsourced duty estimate | `ess0ocgcd9f0.space.mcode.io` |
| `anvkfflansa9.space.mcode.io` | coffee B2B page had no Origin/Compliance/Trade Terms panel, said *"ethically sourced"*, published the caviar lead time as **7–14 days**, and linked the old caviar page | `de6xdoikz95g.space.mcode.io` |
| `hketvigqcs2f.space.mcode.io` | China page showed the 0% tariff **with no expiry date**, carried an unsourced *"Direct Trade Origin"* badge, and had no Origin/Compliance/Trade Terms panel | `fr7m7fzyailo.space.mcode.io` |
| `yuq0txpfa4nq.space.mcode.io` | coffee SA hospitality page linked the old caviar page | `i09hd71cvt06.space.mcode.io` |
| `nzj87hus15vc.space.mcode.io` | retail store linked the old caviar page | `t56b7vkncytt.space.mcode.io` |
> **🔑 RETIRED 2026-10-23 — these served a LEAKED API KEY. Do not share, do not reuse.**
> | Retired URL | What it served | Replaced by |
> |---|---|---|
> | `y0r9ilfj96mj.space.mcode.io` | CIIE coffee landing whose JS bundle contained a live AgentMail API key | `9yk65ajlg1s9.space.mcode.io` |
> | `q3afz51say2o.space.mcode.io` | coffee noir B2B landing whose JS bundle contained a live AgentMail API key | `qefqcvvpd8al.space.mcode.io` |
> | `bx003kfuml66.space.mcode.io` | CIIE landing, first clean rebuild | `9yk65ajlg1s9.space.mcode.io` |
> | `uq2ic93nd5as.space.mcode.io` | coffee noir, first clean rebuild | `qefqcvvpd8al.space.mcode.io` |
> | `a7rv94lqmzxj.space.mcode.io` | China lead capture, first clean rebuild | `1bl06cgsu643.space.mcode.io` |
> | `naq1ucjwxw49.space.mcode.io` | caviar trade, first clean rebuild | `2hkb7k7q2gni.space.mcode.io` |
| `1bl06cgsu643.space.mcode.io` | China lead capture — published **"Rainforest Alliance certified"** and linked `ceo@agent.studexmeat.com` (no DNS) while no assertion watched it | `jqbgl8pu0uyh.space.mcode.io` |
| `2hkb7k7q2gni.space.mcode.io` | caviar trade — published **"certified Russian caviar houses"** and "ethically sourced" while no assertion watched it | `jgk62vzamgtk.space.mcode.io` |
> The key in those two bundles was **revoked and verified dead (HTTP 401)**. Every React landing page
> now posts to the **server-side lead proxy** (`studex-lead-proxy/`, Cloudflare Worker) which holds
> the credential as a secret — **no key may ever be built into a browser bundle.**
> `ops/secret_leak_scan.py` enforces this on every drift check (negative-tested: it fails on an injected key).

> The old China URL was already circulated to China/CIIE buyers, so the **correction note to those buyers must also correct the Rainforest Alliance claim** if it is sent.

> **⚠️ CLIENT-RENDERED PAGES (React SPAs) — asserted against the BUILT BUNDLE, not the HTML.**
> A React page returns ~150 characters of HTML shell, so a text assertion against the fetched page
> proves nothing. These four were therefore UNCHECKED — and while nothing watched them,
> `china-coffee-lead-capture` published **"Rainforest Alliance certified"** (the unsourced claim
> we removed from the static China page on 2026-10-21) plus a link to `ceo@agent.studexmeat.com`,
> and `studex-caviar` published **"certified Russian caviar houses"** and "ethically sourced".
> All of it was live. The checker now asserts the built bundle for any page whose source dir
> ships a hashed `assets/` bundle, and it verifies that the live site is serving THAT build —
> a fixed source with no redeploy is reported as **STALE BUILD**, not as a pass.

> **Price format rule (2026-10-21):** prices are written with a **comma thousands separator and no space** — `R4,999`, `R12,500`, `R1,450` — matching the live Shopify storefront. The Stud-Bot page previously wrote `R 4 999` (space separator) and was normalised; **values were not changed**. The drift checker enforces this.

---



## 4c. CHINA / CIIE — verified facts (owner: `china-coffee-export/`)
> Added 2026-10-21: the China page carried **zero price assertions** because the prices are written `$4,800` and the generator only matched `USD 4,800`. Same class of miss as `<sup>R</sup>295`. The page a CIIE/China buyer sees was the one page whose prices nothing owned.

| Fact | Value | Must appear on |
|---|---|---|

| `nudsduvyrc12.space.mcode.io` | legacy retail build — pre-ladder-lock prices, caviar sold at retail | `t56b7vkncytt.space.mcode.io` |
| `bkqn328wj5a6.space.mcode.io` | retail build with the Katia nav but the pre-ladder-lock prices | `t56b7vkncytt.space.mcode.io` |
| Rwanda A1 Washed, CIF Shanghai | **$4,800 – $5,400/MT** | `fr7m7fzyailo` |
| Rwanda A2 Washed, CIF Shanghai | **$4,200 – $4,700/MT** | `fr7m7fzyailo` |
| China import tariff start | `1 May 2026` | `fr7m7fzyailo` |
| China import tariff expiry — **ours (Rwanda, an LDC)** | **none — no expiry** (100% zero-tariff for African LDCs since 1 Dec 2024) | `fr7m7fzyailo` |
| China import tariff expiry — **THEIRS (20 African non-LDC countries)** | `30 April 2028` | — |
| Rwanda Premium Natural (no price published — quote on request) | `500 kg` | `fr7m7fzyailo` |

## 4b. CONTACT FACTS — every page that must show them
> Added 2026-10-21 after the retail page shipped with **no visible contact at all** (buttons labelled 'Email Us' / 'WhatsApp Order', no address or number rendered anywhere). The price tables could not catch that, so contacts are now asserted facts in their own right. **A page that loses its contact block will now fail the drift check.**
> ⚠️ Two deliberate inconsistencies are recorded as-is pending an owner decision: the **order line +27 83 593 2577** (Tumelo's personal mobile) on the retail + coffee B2B pages, and **`info@studex-group.com`** on the gifting page while every other page uses `info@studexmeat.com`. Both are asserted at their current values so the pages cannot drift silently; changing them is a one-line registry edit plus a redeploy.

| Contact fact | Value | Must appear on |
|---|---|---|
| Support email | `info@studexmeat.com` | `t56b7vkncytt` · `ess0ocgcd9f0` · `de6xdoikz95g` · `i09hd71cvt06` · `fr7m7fzyailo` · `4mak476g6rmo` · `3zryumjeuemk` · `hhsmhunf1xci` |
| Gifting enquiry email | `info@studex-group.com` | `oi28dhtke3yk` |
| Store phone | +27 84 421 6035 | `t56b7vkncytt` · `ess0ocgcd9f0` · `de6xdoikz95g` · `4mak476g6rmo` · `hhsmhunf1xci` |
| Store WhatsApp | +27 94 988 8737 | `t56b7vkncytt` · `ess0ocgcd9f0` · `i09hd71cvt06` · `fr7m7fzyailo` · `4mak476g6rmo` · `oi28dhtke3yk` · `3zryumjeuemk` · `hhsmhunf1xci` |
| Order line (personal mobile) | +27 83 593 2577 | `t56b7vkncytt` · `de6xdoikz95g` |
| Trading entity | `Studex Meat (Pty) Ltd` | `t56b7vkncytt` |
| Locations | `Cape Town, South Africa & Kigali, Rwanda` | `t56b7vkncytt` · `hhsmhunf1xci` |

## 4d. COPY CLAIMS — headline / product strings that must appear
| Claim | Value | Must appear on |
|---|---|---|
| Caviar tier — Oscietra | `Oscietra Imperial` | `ess0ocgcd9f0` · `t56b7vkncytt` |
| Caviar tier — Kaluga | `Kaluga Prestige` | `ess0ocgcd9f0` · `t56b7vkncytt` |
| Caviar tier — Sevtruga | `Sevtruga Medium` | `ess0ocgcd9f0` · `t56b7vkncytt` |
| Caviar retail unit | `per 100g` | `ess0ocgcd9f0` |
| Coffee origin — Rwanda | `Rwanda` | `de6xdoikz95g` |
| Coffee origin — Ethiopia | `Ethiopia` | `de6xdoikz95g` |
| Coffee origin — Kenya | `Kenya` | `de6xdoikz95g` |
| Coffee origin — Uganda | `Uganda` | `de6xdoikz95g` |
| Gift box — The Classic | `The Classic` | `oi28dhtke3yk` · `hhsmhunf1xci` |
| Gift box — The Executive | `The Executive` | `oi28dhtke3yk` · `hhsmhunf1xci` |
| Gift box — The Boardroom | `The Boardroom` | `oi28dhtke3yk` · `hhsmhunf1xci` |
| Gifting discount code | `STUDEXGIFT10` | `oi28dhtke3yk` · `hhsmhunf1xci` |
| Gifting final order date | `20 December 2026` | `oi28dhtke3yk` |
| Halaal scope — retail page | `Our Wagyu range is certified Halaal` | `t56b7vkncytt` |
| Halaal scope — sales sheet | `Our Wagyu range is Halaal certified` | `hhsmhunf1xci` |

## 4e. REQUIRED LINKS — hrefs that must exist on the page
| Link | Reason | Must appear on |
|---|---|---|
| Institutional sell sheet | `https://hhsmhunf1xci.space.mcode.io` | `4mak476g6rmo` |
| Gifting WhatsApp | `https://wa.me/27794988737` | `oi28dhtke3yk` |

## 4f. FORBIDDEN STRINGS — must NOT appear on the page
| Forbidden string | Reason | Must not appear on |
|---|---|---|
| `agent.studexmeat.com` | dead domain, no DNS | `3zryumjeuemk` · `ess0ocgcd9f0` · `t56b7vkncytt` · `4mak476g6rmo` · `de6xdoikz95g` · `oi28dhtke3yk` · `fr7m7fzyailo` · `i09hd71cvt06` · `hhsmhunf1xci` · `9yk65ajlg1s9` · `qefqcvvpd8al` · `jqbgl8pu0uyh` · `jgk62vzamgtk` |
| `charlie@agent.studexmeat.com` | dead domain | `ess0ocgcd9f0` |
| `27 82 555 0194` | unverified phone, replaced | `ess0ocgcd9f0` |
| `Sevruga Premium` | retired caviar name | `ess0ocgcd9f0` · `t56b7vkncytt` |
| `Siberian Reserve` | retired caviar name | `ess0ocgcd9f0` · `t56b7vkncytt` |
| `per 250g` | wrong caviar unit | `ess0ocgcd9f0` · `t56b7vkncytt` |
| `R 4 999` | spaced price format | `3zryumjeuemk` |
| `R 8 999` | spaced price format | `3zryumjeuemk` |
| `R 18 999` | spaced price format | `3zryumjeuemk` |
| `R 1 999` | spaced price format | `3zryumjeuemk` |
| `R500/mo` | retired spec price | `3zryumjeuemk` |
| `0% window runs to 30 April 2028` | the 30 Apr 2028 expiry was THEIRS, not ours - a Rwandan LDC origin has no expiry | `fr7m7fzyailo` · `9yk65ajlg1s9` · `jqbgl8pu0uyh` · `qefqcvvpd8al` · `4mak476g6rmo` |
| `Zero Tariff — to 30 Apr 2028` | the 30 Apr 2028 expiry was THEIRS, not ours - a Rwandan LDC origin has no expiry | `fr7m7fzyailo` · `9yk65ajlg1s9` · `jqbgl8pu0uyh` · `qefqcvvpd8al` · `4mak476g6rmo` |
| `tariff window closes on 30 April 2028` | the 30 Apr 2028 expiry was THEIRS, not ours - a Rwandan LDC origin has no expiry | `fr7m7fzyailo` · `9yk65ajlg1s9` · `jqbgl8pu0uyh` · `qefqcvvpd8al` · `4mak476g6rmo` |
| `0% for all 53 African countries, 1 May 2026 – 30 April 2028` | the 30 Apr 2028 expiry was THEIRS, not ours - a Rwandan LDC origin has no expiry | `fr7m7fzyailo` · `9yk65ajlg1s9` · `jqbgl8pu0uyh` · `qefqcvvpd8al` · `4mak476g6rmo` |
| `R1,500/mo` | retired spec price | `3zryumjeuemk` |
| `R4,000/mo` | retired spec price | `3zryumjeuemk` |
| `R2,600` | retired caviar price | `oi28dhtke3yk` · `hhsmhunf1xci` |
| `R3,400` | retired caviar price | `oi28dhtke3yk` · `hhsmhunf1xci` |
| `R2,200` | per-kg meat price, wrong in a gifting context | `oi28dhtke3yk` |
| `R1,450` | per-kg meat price, wrong in a gifting context | `oi28dhtke3yk` |
| `R850` | per-kg meat price, wrong in a gifting context | `oi28dhtke3yk` |
| `STUDESGIFT10` | wrong code (missing the X) | `oi28dhtke3yk` · `hhsmhunf1xci` |
| `June 2026` | stale date | `de6xdoikz95g` · `i09hd71cvt06` |
| `Coming Soon` | stale, caviar now ships | `de6xdoikz95g` · `i09hd71cvt06` |
| `500+ MT` | unverified volume claim | `de6xdoikz95g` · `i09hd71cvt06` |
| `svetlana@prowtc.com` | a real prospect, not our contact | `de6xdoikz95g` · `i09hd71cvt06` · `fr7m7fzyailo` |
| `PROWTC` | a prospect's brand, not ours | `de6xdoikz95g` · `i09hd71cvt06` · `fr7m7fzyailo` |
| `Rainforest Alliance` | no source document exists for any Studex coffee — claim removed 2026-10-21 | `fr7m7fzyailo` · `de6xdoikz95g` · `i09hd71cvt06` · `9yk65ajlg1s9` · `qefqcvvpd8al` · `jqbgl8pu0uyh` · `jgk62vzamgtk` |
| `Every product we produce` | MJC certificate covers 4 Wagyu products only — not caviar, coffee or game | `t56b7vkncytt` |
| `All products Halaal certified` | same overclaim — scoped to the Wagyu range | `hhsmhunf1xci` |
| `MJC Halal Trust` | wrong spelling of the certifier name (MJC Halaal Trust) | `t56b7vkncytt` · `hhsmhunf1xci` |
| `100% Halaal Certified` | the certificate covers 4 Wagyu products, not caviar, coffee or game | `t56b7vkncytt` |
| `certified farms` | certification claim with no document behind it | `de6xdoikz95g` |
| `Halaal guaranteed` | page-level absolute — the certificate covers the Wagyu range only | `t56b7vkncytt` |
| `certified Russian caviar houses` | the caviar source page makes no such claim | `t56b7vkncytt` |
| `certified Russian caviar houses` | the React caviar page made this claim while UNCHECKED — live 2026-10-23 | `jgk62vzamgtk` |
| `ethically sourced` | retired unsourced claim (removed from the coffee pages 2026-10-21) | `jgk62vzamgtk` |
| `Direct Trade` | retired unsourced badge — "single washing station" is the honest line | `jqbgl8pu0uyh` · `9yk65ajlg1s9` · `qefqcvvpd8al` |
| `Tariff-free entry into China from July 20, 2026` | wrong tariff date — the tariff started 1 May 2026; 20 July is the unified phytosanitary system | `jqbgl8pu0uyh` |

| `booth confirmed` | unverified CIIE booth claim — the email warmup engines sent it from real Studex inboxes until 2026-10-22 | warmup engines (`studex-email-warmup/*.js`) |
| `African Nations Pavilion` | unverified pavilion claim | warmup engines (`studex-email-warmup/*.js`) |
| `PROWTC` | a prospect's brand, not ours — it was in the warmup email copy | warmup engines (`studex-email-warmup/*.js`) |
| `Sevruga` | retired caviar name | warmup engines (`studex-email-warmup/*.js`) |
| `14-21 days` | wrong caviar lead time — the DAFF permit must be applied for 4 weeks ahead | warmup engines (`studex-email-warmup/*.js`) |
| `R380/tin` | retired caviar price | warmup engines (`studex-email-warmup/*.js`) |

> **The manifest is now generated purely from this file** — nothing is carried over from the previous manifest. If an assertion disappears from here, it stops being checked, and the generator prints `LOST ASSERTIONS` so that is never silent.

## 4g. OUTREACH EMAIL COPY RULES — the rendered bodies of the CIIE nurture emails
> Checked against the **rendered** email (what a buyer would actually receive), not the source file. On 2026-10-21 the source scan passed a sequence whose first line was *"Thank you for meeting the Studex Meat Co. team at CIIE 2026 in Shanghai"* — the show had not happened yet, and 21 emails had already gone out. Scanning the source is useless here: every email body is a template literal. Plain case-insensitive substring match.

| Rule | Kind |
|---|---|
| `Thank you for meeting` | forbidden |
| `studexmeat.com/catalogue` | forbidden |
| `HACCP` | forbidden |
| `ISO 22000` | forbidden |
| `registered exporter` | forbidden |
| `cold-chain certified` | forbidden |
| `Experience supplying` | forbidden |
| `meeting point to be confirmed` | forbidden |
| `CIIE Special` | forbidden |
| `R180` | forbidden |
| `R950` | forbidden |
| `R280` | forbidden |
| `R9,000` | forbidden |
| `R19,000` | forbidden |
| `R8,400` | forbidden |
| `R36,400` | forbidden |
| `Springbok` | forbidden |
| `Eland` | forbidden |
| `Kudu` | forbidden |
| `agent.studexmeat.com` | forbidden |
| `info@studexmeat.com` | required |
| `de6xdoikz95g.space.mcode.io` | required |
| `fr7m7fzyailo.space.mcode.io` | required |
| `ess0ocgcd9f0.space.mcode.io` | required |
| `0% since 1 May 2026` | required |
| `certificate of analysis` | required |
| `R1,450` | required |
| `4,800` | required |
| `PROWTC` | forbidden |
| `expressed interest` | forbidden |
| `4.60/kg` | forbidden |
| `5.50/kg` | forbidden |
| `69,000` | forbidden |
| `USD 18/tin` | forbidden |
| `15% YoY` | forbidden |
| `halal` | forbidden |
| `6–8 weeks` | forbidden |
| `DAP your port` | forbidden |
| `I will be attending` | forbidden |
| `I will be at CIIE` | forbidden |
| `book a 30-minute` | forbidden |
| `meeting request` | forbidden |
| `bilateral agricultural protocol` | forbidden |
| `Rainforest Alliance` | forbidden |
| `MJC Halal Trust` | forbidden |

> **The China page's Rainforest Alliance claim was REMOVED on 2026-10-21** — not merely flagged. The only documentary source in our material (`studex-os/proposals/rwanda-offer-PROWTC-2026-07.pdf`) mentions Rainforest Alliance **nowhere**, and no certificate file exists in the workspace. The claim traced back to our own fabricated email copy. It is now a **forbidden string** on the coffee pages. If a valid RA certificate exists, send it and the claim can be put back with a number and expiry.

## 4h. TRADE-TERMS PANEL ASSERTIONS — added 2026-10-21 (Build Hour)
> The "Origin, Compliance & Trade Terms" panel is generated from **one** file — `studex-trade-terms/trade-terms.json`, built by `node studex-trade-terms/build.mjs`. Both coffee pages render from it, so they cannot say different things. The panel is the honest state of the compliance file: **no third-party certification is held**, and **EUDR farm-level geolocation is in progress**. These are asserted so the truth cannot silently regress into a claim.

| Fact | Value | Must appear on |
|---|---|---|
| Panel — certification status | `None held by Studex` | `de6xdoikz95g` · `fr7m7fzyailo` |
| Panel — EUDR / traceability status | `EUDR` | `de6xdoikz95g` · `fr7m7fzyailo` |
| Panel — China tariff statement (ours) | `no expiry` + `LDC` | `de6xdoikz95g` · `fr7m7fzyailo` |
| Panel — traceability status | `Lot Traceability` | `fr7m7fzyailo` |
| Caviar — regulatory lead time | `DAFF veterinary import permit` | `ess0ocgcd9f0` · `de6xdoikz95g` |
| Caviar — duty quoted, not guessed | `duty and VAT quoted in the landed cost` | `ess0ocgcd9f0` |
| Caviar — origin stated | `Russia` | `ess0ocgcd9f0` · `de6xdoikz95g` |

> **Newly retired claims (2026-10-21, Build Hour).** Removed because they were unsourced, not because they were wrong in spirit: *"Direct Trade Origin"* / *"Direct Trade"* (a badge we cannot evidence — the page now says *single washing station*), *"ethically sourced"* (an ethical claim on a page that states no certification is held), and *"duty (±20%)"* (SA duty on prepared caviar is HS 1604.14.10 = 25% or 200c/kg, and our roe-vs-caviar classification is still an open question for the broker — so the page quotes no number at all).

## 4i. OUTBOUND TRADE-ENQUIRY FIGURES — ASSUMPTIONS, NOT PUBLISHED PRICES (added 2026-10-23)
> The clearing-agent enquiry draft (`outbound-drafts/clearing-agent-caviar-duty-rebate.md`) quotes landed-cost figures so the broker can size the duty saving. Those figures are **internal assumptions carried from 2026-08-14 / 2026-09-21 research and are not verified.** They are registered here for one reason only: so the drift checker can see that a number leaving the building is a *known* number rather than an unsourced one. **None of these is a published price. None may appear on a page, be quoted to a customer, or be booked as savings.**
>
> 🔒 **Rebate 460.19 must not be booked as savings in any model until the clearing agent confirms in writing** — a pure reseller who sells the product as received may not qualify; the rebate is described for further processing.
>
> ⚠️ The caviar page still quotes **no duty number at all** (`duty and VAT quoted in the landed cost`). That stays true until a broker confirms the HS classification and rate. Do not let these enquiry figures leak back onto a page as if they were the duty rate.

- Oscietra Imperial — farm gate, modelled: **USD 1,000/kg** (assumption; unverified)
- Duty assumed in the enquiry, not published: **20%** (assumption; unverified — see §4h, SA duty on prepared caviar may be 25% or 200c/kg)
- Model FX used in the enquiry: **18.5** (assumption; unverified) — 🔴 **SUPERSEDED 2026-10-24.** The live rate is **16.578** (exchangerate-api.com, 24 Oct 2026 00:02 UTC; ECB reference frankfurter.dev = 16.5976, agreeing within 0.12%). The 18.5 assumption was **10.39% high**, making every USD-denominated landed cost in this enquiry **R1,922/kg too high per $1,000 of cost**. Any figure in the clearing-agent enquiry built on 18.5 must be recomputed before it is sent. Source: `research/2026-10-24-price-reality-check.md`.
- Live FX now used in all recomputed models: **USD/ZAR 16.578102** (live, refreshable). Landed-cost floors recomputed at live FX (VAT recoverable, duty on CIF, margin on price): Oscietra R20,674 landed / R29,535 floor; Kaluga R14,706 / R21,009; Sevtruga R8,738 / R12,483 — **all three clear the 30% floor.** The 23 Oct "selling below cost" verdict was a stale-FX + VAT artefact, not a pricing defect. Source of truth: `studex-price-desk/`, live desk https://jisom3k4i126.space.mcode.io
- Rebate 460.19 relief assumed in the enquiry: **up to 20% of duty** (assumption; a pure reseller may not qualify)

## 4j. PRICE REFERENCE DESK — live market & published prices (added 2026-10-24, Build Hour)
> Source: `studex-price-desk/` · Live URL: `jisom3k4i126.space.mcode.io` · Built from `research/2026-10-24-price-reality-check.md`.
>
> 🔒 **This page is public, so it publishes MARKET DATA and ALREADY-PUBLISHED prices only.** It does **not** publish our cost model, landed cost, margin floor, wholesale trade price, or recommended quote band. The internal build (`studex-price-desk/dist-internal/`) carries those and is **not deployed** — it needs auth and a decision. See `studex-meat/CAVIAR-TRADE-DESK-EXPOSURE-FINDING-2026-10-24.md`.
>
> 🔑 A permanent gate now exists: `studex-price-desk/scripts/audit-bundle.mjs` greps the public bundle for 29 internal identifiers and the old internal numbers (18.5, 23042, 32917, 34000, …) and **fails the build** if any is present. It also asserts the internal bundle still carries the cost model.

### Must appear on the price reference desk

| Published reference | Value | Must appear on |
|---|---|---|
| Best of Rwanda 2026 top lot, micro-lot Geisha (K-Organics, Huye) | `Best of Rwanda` | `jisom3k4i126` |
| SA Coffee Price Index Q3 2026 | `SA Coffee Price Index` | `jisom3k4i126` |
| ICE Arabica C live benchmark | `ICE Arabica` | `jisom3k4i126` |
| Published caviar SKU — Oscietra Imperial | `Oscietra` | `jisom3k4i126` |
| Published caviar SKU — Kaluga Prestige | `Kaluga` | `jisom3k4i126` |
| Published caviar SKU — Sevtruga Medium | `Sevtruga` | `jisom3k4i126` |
| CNY rate, for CIIE quoting | `USD/CNY` | `jisom3k4i126` |

### Must NOT appear on the price reference desk

| Forbidden internal string | Why | Must not appear on |
|---|---|---|
| `farmGateUsdPerKg` | farm-gate cost — hands a buyer our cost | `jisom3k4i126` |
| `landedZarPerKg` | landed cost | `jisom3k4i126` |
| `floorZarPerKg` | our minimum viable price — the buyer negotiates to exactly this | `jisom3k4i126` |
| `belowFloor` | margin verdict | `jisom3k4i126` |
| `marginPct` | our margin | `jisom3k4i126` |
| `SPECIALTY_DISCOUNT` | our quote band | `jisom3k4i126` |
| `fxImpact` | FX model | `jisom3k4i126` |
| `18.5` | the old hardcoded FX assumption — internal cost model | `jisom3k4i126` |
| `23042` | Oscietra landed cost at the old FX | `jisom3k4i126` |
| `32917` | Oscietra floor at the old FX | `jisom3k4i126` |
| `34000` | Oscietra wholesale trade price | `jisom3k4i126` |
| `22000` | Kaluga wholesale trade price | `jisom3k4i126` |
| `12500` | Sevtruga wholesale trade price | `jisom3k4i126` |
| `R29,535` | Oscietra floor at live FX | `jisom3k4i126` |
| `R20,674` | Oscietra landed cost at live FX | `jisom3k4i126` |
| `R34,000` | Oscietra wholesale trade price | `jisom3k4i126` |
| `farm gate` | farm-gate cost in prose | `jisom3k4i126` |
| `landed cost` | landed cost in prose | `jisom3k4i126` |
| `margin floor` | our minimum viable price in prose | `jisom3k4i126` |

> 🔒 The "must not" list is the durable half of this registration. If a future build puts any of
> these on the public page, the drift checker reports it as DRIFT — the same mechanism that caught
> the unsourced Rainforest Alliance claim on the China page.

### Open items this page is waiting on

- **Kigali partner:** is $4.80/kg still current, and does the A1 lot carry a premium over the ICE composite? Decides whether the sheet price is a genuine discount or a stale number.
- **Clearing agent:** HS classification (1604.31 vs 1604.14.10) and whether import VAT is claimable. Decides every caviar floor.

---

## 5. OPEN ITEMS FOR OWNER CONFIRMATION
> **Updated 2026-10-21 16:05 UTC — the live storefront was read directly (web extraction of `studexmeat.com`) and it CLOSED four of these. Evidence, not assumption.**

1. **Stud-Bot pricing** — R499/999/1999 per month + setup fee (live page `3zryumjeuemk`), or R500/1500/4000 per month (spec)? ⏳ **STILL OPEN.** Not a Shopify product, so the storefront cannot arbitrate. The **page is currently the customer-facing truth** — if the spec is right, the page is wrong and must be corrected. *The only pricing question that still needs an answer.*
2. ~~7kg case vs 1kg~~ — ✅ **CLOSED — NOT AN ERROR.** The storefront carries **both** live products: `Wagyu Biltong Gold 7kg Box of 100 x 70g packets` at **R12,500** (100 × 70g = exactly 7kg) and `Wagyu Biltong Gold — 1kg (14 × 70g Packets)` at **R1,450**. R1,786/kg vs R1,450/kg is a **~19% volume discount**, which is normal wholesale behaviour. Our pages already match the store exactly. **No change needed.**
3. ~~"14 resealable 70g pouches" = 980g~~ — ✅ **CLOSED — IT IS THE STORE'S OWN TITLE, NOT OURS.** The Shopify product title literally reads `Wagyu Biltong Gold — 1kg (14 × 70g Packets)` (14 × 70g = 980g). Our pages copy the storefront verbatim, so **no page change is warranted.** If he wants the 20g discrepancy fixed, the fix belongs in the **Shopify product title** (admin access required) — and only if 980g is not deliberate.
4. **Subscription tiers R295 / R495 / R850 — ⚠️ CORRECTION: THEY *DO* APPEAR ON THE RETAIL PAGE. My earlier note ("nothing publishes them") was WRONG.**
   - I had grepped the raw HTML for `R295` and found nothing — **false negative**: the page writes the currency symbol in a separate tag (`<sup>R</sup>295`), so the literal string `R295` never appears in the source. The rendered text **does** show R295 / R495 / R850. Lesson recorded: **check rendered text, not raw markup.**
   - **What is true:** the storefront has **no subscription product of any kind** — so these three tiers are sold **outside Shopify**, fulfilled manually. The page says exactly that ("Subscriptions are fulfilled directly by our team. Plan pricing is confirmed on enquiry") but it *also* prints the prices, which contradicts "confirmed on enquiry".
   - **Open:** (a) the "Start Starter / Connoisseur / Bulk" CTAs link to the generic `#order` form, which has **no subscription field** — a subscription request arrives as an ordinary order; (b) the Connoisseur tier includes **100g Ox Tail Biltong, which is not a product in the storefront catalogue**; (c) R295/month for 200g sits above the per-kg equivalent of the store's 500g biltong at "From R650". **Are these three tiers live, and do they need a Shopify product + a subscription-aware form?**
   - **Now registered in the price table above**, so the drift checker asserts them on the retail page and will flag any change.
5. ~~`orders@studexmeat.com`~~ — ✅ **CLOSED — DON'T PUBLISH.** The storefront's only contact email is **`info@studexmeat.com`**; `orders@` appears nowhere on the store. Unless he creates and confirms that mailbox, it stays unpublished.
6. **Sales-sheet testimonials** — two unattributed quotes, deliberately not published. ⏳ OPEN.
7. **Platform-enquiry inbox** — which address should the Super Agents posts use? ⏳ OPEN.
8. **CIIE booth** — has StudEx received an actual booking confirmation or invoice? ⏳ OPEN (see MEMORY.md — both CIIE crons are disabled until this is answered).

### 5c. CERTIFICATION / CLAIMS ON LIVE PAGES — owner confirmation (added 2026-10-21)
- **Retail page Halaal claim — SCOPED 2026-10-21 from the certificate image we publish.** Read from `studex-biltong/imgs/halal-cert.png` (the file on the live page): issuer **MJC Halaal Trust** (Muslim Judicial Council), certificate number **HT 4606** in the body but a **placeholder "HT 0000" in the emblem**, **certificate holder = Cape Deli, 34 Shiraz Road, Saxenburg Park 1, Blackheath**, **brand = STUDEX**, products = **Wagyu Droewors, Wagyu Biltong original, Wagyu Snapsticks Chilli, Wagyu Snapsticks Original**, and **no issue date and no expiry date are legible**. The page said *"Every product we produce is certified Halaal… No exceptions"* — provably false against the document beside it (caviar, coffee and game biltong are not covered). It now says: *"Our Wagyu range is certified Halaal by the MJC Halaal Trust — Wagyu biltong, droewors and snapsticks, certified under the STUDEX brand… Our caviar, coffee and game biltong are not covered by it."* **Still open:** the certificate's issue/expiry dates, and whether **Cape Deli is our producer** (its address is the only street address we have seen — it is *not* published as ours).
- **Nurture email (disarmed):** "SA Revenue Services registered exporter" · "Cold-chain certified (HACCP, ISO 22000)" · "Experience supplying to China, Middle East, Europe". Unchanged pending approval.
- **Institutional sheet / B2B:** "Cold-chain certified", "SA Revenue Services registered exporter" — same two claims, now on public pages.

### 5b. STOREFRONT HYGIENE — needs Shopify admin (Tumelo) — found 2026-10-21
Read from the live store, not inferred:
- **A placeholder product is on sale.** Title literally `Product title`, price **R19.99** — a leftover theme default, publicly buyable. **Delete or hide it.**
- **Public product-title typo:** `Coffeee - FULLY WASHED (WET) PROCESS` (three e's).
- **Stray numbering in two product titles:** `1. AEROBIC FERMENTATION PROCESS`, `1. NATURAL (DRY) PROCESSING`.
- **Awkward title:** `Wagyu Biltong Gold 7kg Box of 100 x 70g packets of Biltong Gold !` (trailing " !", and "of Biltong Gold" twice).
- **No physical address anywhere on the storefront.** For a food business — and for institutional/corporate procurement, which routinely requires a registered physical address — this is a credibility gap. The inst. sell sheet carries one; the store does not.
- **No "Wholesale" or "Bulk" collection.** Collections are only `Coffee`, `Ankole`, `Steaks`, `Biltong`. But our own pages advertise **trade** pricing (coffee MOQ 50kg, caviar per-kg trade rates, institutional per-kg meat). A buyer who lands on the store has **no visible route to wholesale.** A `Trade` collection, or a "Wholesale & Trade — enquire" block on the store, would close it.
- **No institutional/bulk enquiry address on the store** — `info@studexmeat.com` is the only route.

## 4k. 🔴 EXPOSED — LIVE PAGES THAT MUST BE DELETED (added 2026-10-24 21:53 UTC)

A live, public URL that serves content we must not publish. It is deliberately **not** in the §4
checked page map: a source-vs-live diff gives the wrong remedy here ("redeploy this app"), and
redeploying would re-publish the cost model. The correct remedy is **deletion**.

  minimum viable price, the superseded hardcoded FX rate and our trade prices, and flags our own
  published prices as a "pricing defect". We publish landed cost and our minimum viable price;
  competitors publish retail. **Replace by: the price reference desk (§4j). Remedy: DELETE the
  deploy** from the mcode.io dashboard — that dashboard is not reachable from this host, so this is
  an owner action.

> Machine-readable list and the checker: **`ops/exposed-pages.txt`** + `ops/check-cost-model-exposure.py`
> (exit `1` = exposed, `2` = unchecked). 🔑 **It is deliberately NOT a blocking gate in
> `ops/run-tests.sh`**: the state cannot be fixed from this host, and a veto that fires on a
> scheduled job is a self-inflicted outage. The check is run on every heartbeat, reported here and
> escalated to `#ops`, and its own correctness is proven by positive and negative controls in
> `ops/test-cost-model-exposure.py`.

⛔ **Never publish landed cost, farm-gate cost, duty/VAT/FX assumptions or a margin-floor on a
public surface.** Retail only; trade is quote-only.
