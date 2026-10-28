# 2026-10-27 — Research Hour: the Horeca sheet was selling the wrong product

## 🔴 LEAD: `horeca-sell-sheet/content.json` was an EXPORT sheet with a domestic buyer on it

Built 26 Jul, never sent to anyone (as far as we can tell). It sold **green coffee at FOB USD**
("$4.20/kg", "$3.80/kg", "CIF quotes on request", MOQ 500kg/300kg) to **South African hotels,
restaurants, cafés and offices**.

Three failures in one document:

1. **Wrong product.** SA Horeca buys **roasted**, delivered, in ZAR, with machine/service behind it
   — not green FOB from Kigali. Market benchmark: BeanCo (roasted to order, ground to spec,
   nationwide delivery, free 250g samples), Café Kreme (machine rental + install + training +
   maintenance + insurance, sized ~60/100-120/200 cups per day).
2. **Wrong price axis.** $4.20/kg FOB = ~R69/kg at USD/ZAR 16.56. SA *retail* specialty median is
   **R190/250g = ~R756/kg** (SA Coffee Price Index Q3 2026, 39 roasters/132 listings). We were
   quoting SA buyers a number **~11x below the shelf price of the thing they buy**. Reads as a typo
   and hands the negotiation to any competitor who spots it.
3. **False China claim.** It said *"China's coffee market is opening via CIIE (November 2026)"* —
   contradicted by our own 25/26 Oct briefs (zero-tariff **opened 1 May 2026**) and by CIIE's own
   registration status (exhibitor registration closed). 🔴 A SA prospect who reads it and later
   reads our China sheet loses trust in everything else on the page.

### ✅ What I changed tonight (surgical, in place)
- **Removed the CIIE/China block.** Replaced with "Same Farm, Roasted and Delivered Locally" —
  same lots, roasted and delivered locally from Durban.
- **Price column header** `Price (FOB)` -> `Price (Green, FOB)` + caption now states export pricing
  is green FOB and **SA Horeca is quoted roasted, ground to spec, delivered, in ZAR per kg**.
- **Certifications row fixed:** "Proof ofRwanda Trade & Origin" -> "Proof of Rwanda Trade & Origin";
  "Required for China export" -> "Origin & traceability evidence for SA procurement".
- **Placeholders removed:** website `studex.co.za` -> `studexmeat.com`; phone `+27 XX XXX XXXX` ->
  `+27 94 988 8737`; company reg `2026/XXXXXX/07` -> "on request". 🔑 A sheet with `XX` in the
  phone number was never going to be sent — that is why it sat for 3 months.
- Verified: valid JSON, 41 blocks, zero "CIIE" strings, zero "XX" placeholders.

🔑 **The full split (domestic roasted ZAR sheet vs export FOB sheet) is still Build Hour work.**
Tonight I fixed the false claims, not the structure. Do not send this sheet to a SA buyer until the
domestic version exists — it is now honest, but it is still half an export sheet.

### 🔑 WHY THIS KEPT HAPPENING
We built a sheet, never sent it, and forgot it existed for 3 months. 🔑 **An unsent asset is a
liability, not an asset** — it holds claims that drift out of truth while sitting idle. The CIIE
claim was written before the 25 Oct research and contradicted it. 🔑 **Anything with a date in it
must be re-checked before it leaves the building.**

## 🔑 n8n keynote debt — CLOSED (carried 25 Oct + 26 Oct, now settled)

"n8n In The Loop 2026 keynote — 20 min of reading" has been carried twice. **Answer: vision event,
no feature releases — nothing to read.**
- n8n's own conference page: **Berlin, 13-14 Oct 2026**, their first conference. Partner's Day +
  Ecosystem Day.
- Keynote = Jan Oberhauser (Founder/CEO) + David Roberts (VP Product & Design), titled *"Vision and
  Product direction"*. **The published agenda lists no feature releases, no API changes, no model
  integrations, no pricing changes, no rollout dates.**
- n8n community announcements feed, October 2026: **no product launches.** Only Community Edition
  license explainer (6 Oct), Ambassador Program (12 Oct), weekly community challenges, and a
  research request on testing AI agents (16 Oct).
- **Remaining actionable n8n facts = the ones we already have:** n8n Agents (Aug 2026) and **n8n
  2.43 (6 Oct 2026)** — Browser Use for all users + instance-level MCP server + workflow settings
  editable over MCP.
- **Verdict unchanged: self-host n8n, do not add Make.** Make bills per-operation credits, which
  scales against our volume.

## 🔑 Blotato's platforms are closing under us — two closures hit our live publish path

Blotato Social Media API Report 2026: **34 breaking changes** (13 hit posting), **31 version
sunsets**, 10 platforms.

**X:**
- **Pay-per-use only** since 1 Jun / 1 Sep 2026. $0.015/post regular, **$0.200/post with a URL**,
  $0.010 summoned reply. Legacy Basic/Pro auto-migrated to credits; **opting out terminates access**.
- **Programmatic replies are summoned-only since 23 Feb 2026** (original author must @mention or
  quote us). 🔴 Any X reply automation is dead.
- **Automated engagement removed entirely 20 Apr 2026** — API creation of Following, Likes and
  Quote-Posts gone on all self-serve tiers.

**Meta/Instagram/Facebook:**
- **Messenger Page tags now fail with `Error 100`** since 27 Apr 2026 (`CONFIRMED_EVENT_UPDATE`,
  `ACCOUNT_UPDATE`, `POST_PURCHASE_UPDATE`). Replacement = **Utility Templates / Marketing
  Messages API**. 🔴 If any Studex flow still posts a Messenger tag it is **silently failing**.
- **Removed metrics:** `impressions`, `plays`, Reels play counts (21 Apr 2025); `video_views`,
  `email_contacts`, `profile_views`, `website_clicks` (8 Jan 2025); FB Page Insights
  `impressions` + `page fans` (15 Nov 2025). 🔴 Any dashboard showing these reads **dead numbers**.
- Instagram Basic Display API fully shut down (4 Dec 2024); v1.0 Marketing API deprecated.

**Threads:** posts with **>5 links fail** container creation (`THREADS_API__LINK_LIMIT_EXCEEDED`,
22 Dec 2025). Tenor GIF removed; **GIPHY replaces it**.
**Reddit:** new public Data API requests close **31 Oct 2026**; unregistered apps lose access
**12 Jan 2027**; full shutdown **March 2027**. We don't post there — informational.
**Bluesky: 0 breaking changes** — raised limits, stabilised OAuth. Only clean platform in the set.

🔑 **The failure mode is silence, not an error.** Apps posting on behalf of other users face
mandatory audits across **9 of 10** platforms (all but Bluesky; X additionally reviews AI-generated
content), and **unreviewed apps on TikTok and Pinterest (Trial tier) post to PRIVATE visibility —
functional in testing, invisible to the public.** 🔑 **A publish pipeline that fails OPEN is worse
than one that fails loudly**, because the dashboard reports success. → add a post-publish visibility
assertion.

## 🟡 Higgsfield — usable, but NOT bought this month
Oct 2026 changelog: Supercomputer (22 Oct), Content Factory A, Ideogram Vector 1.0, Kimi K3.1 Pro,
character-type grading. Cinema Studio 4.0, Genjutsu, Seedance 2.5 / Wan 3.0 (30s), Ad tooling.
Pricing: Starter 200 / Plus 1,000 / **Ultra 3,000** credits per month. 🔑 **We already have a full
video stack** (MiniMax-H3 / H3-Max / Hailuo via `submit_video_generation` + `gen_videos`) and a
content pipeline. Higgsfield earns its place only for **character consistency across a campaign**.
**Do not buy a subscription.** Revisit against a named campaign brief that needs one consistent
presenter across 10+ assets, priced at Ultra.

## 🔑 Biltong price benchmark (fills the 24 Oct price-desk gap)
- A/B sliced or slabs **R349.99-449.99/kg** · C-grade geelvet **R399.99-499.99/kg** · A/B drywors
  **R349.99-449.99/kg** · **wagyu biltong/drywors R499.99-599.99/kg** · biltong sticks
  **R599.99-699.99/kg** (up to R999.99/kg in small snack packs).
- Differentiators the market rewards: premium cuts without trimmings, grass-fed/hormone-free, clean
  facility, **free 1-4 day delivery over R1,000**, **automated bulk tiers** (3+ = 10%, 5+ = 15%,
  10+ = 20%).
- 🔴 Our live Shopify wagyu-biltong listing shows **R12,500 (from R16,500)** — a different unit
  class entirely. **Confirm whether that is whole-slab or per-kg before it sits next to a
  competitor table.**

## 🔴 STILL OWED (Tumelo) — unchanged, now 4 days old
1. **Rotate the Blotato and GoDaddy keys.** Per the 27 Oct credential audit both are **LIVE in the
   public GitHub remote**; Blotato echoes the key on `GET /v2/users/me/accounts`; **neither has an
   API rotation route** — dashboard action. Rotate FIRST, then rewrite.
2. **Kigali starts TOMORROW (28-30 Oct).** The two partner questions (is $4.80/kg a live 2026
   contract price; do you hold plot geolocation + EUDR due-diligence readiness for 30 Dec 2026) must
   go in the FIRST meeting, not after it.
3. **CIIE Bureau** — late entry / visitor pass + the roasted-at-origin export licence & HS question.
4. **SA caviar permit stack** (DFFE + ITAC + SARS + CITES) — unchanged, still the gate.
