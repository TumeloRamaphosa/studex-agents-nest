# Cursor prompts — studexmeat.com

Two ready-to-paste prompts. The first uses Cursor's new **Computer Use** capability (agents can
drive desktop apps and the browser, not just edit files). The second is for repo work.

Before either prompt is useful, the agent must be grounded — `.cursor/rules/studexmeat.mdc` in
this repo carries the prices, contacts, canonical URLs and the banned claims, and applies
automatically to any Cursor session opened here.

---

## 1. Catalogue audit — verify the LIVE storefront (primary)

**Why this prompt exists:** the storefront at `studexmeat.com` is live and selling, but the
**Shopify Admin API is unauthenticated**, so orders and inventory cannot be read
programmatically. The catalogue can still be read through Shopify's **public** catalogue API —
`https://studexmeat.com/products.json?limit=250` — which is the authoritative source for what
exists, and it does **not** need a browser.

⚠️ **This host has no browser.** Cursor's `@Computer Use` cannot drive anything here: there is no
Chromium, and Cursor has **no MCP servers configured**, so its browser tool calls are routed to
the host's tool registry and auto-rejected (nothing can answer the approval prompt in headless
mode). `--approve-mcps` does not help — there is nothing local to approve. Variant B below is the
same audit for a host that *does* have a browser.

```
Audit the live Studex Meat storefront for defects. Read .cursor/rules/studexmeat.mdc first —
it is ground truth, and it records findings from the 2026-10-24 baseline audit you are about to
re-run. Your job is to find what has changed since, and anything the baseline missed.

STEP 1 — the catalogue, from the API (this is authoritative for what EXISTS):
  GET https://studexmeat.com/products.json?limit=250
  For every product record: title, product_type, the first variant's price, compare_at_price,
  and available (sold-out or not).

STEP 2 — the rendered page (this is authoritative for what a CUSTOMER SEES):
  Fetch https://studexmeat.com/ and https://studexmeat.com/collections/all and record the
  displayed titles, displayed sale and regular prices, and any banner text.

STEP 3 — reconcile the two, and report:
  (a) any product that exists in the API but is missing from the rendered grid (pagination
      hides products — the grid shows 24 of 48; that is normal, not a defect)
  (b) any product in the API whose price differs from what the page shows
  (c) any product in the API that is a placeholder or default title
  (d) any product whose title contains hashtags, a leading numeral, emoji, or a typo
  (e) any non-meat product sitting in the meat catalogue — agent subscriptions, event tickets —
      and whether its title currency matches the price currency
  (f) any sold-out product, and any seasonal product out of season
  (g) whether caviar is present. As of the baseline it is NOT — zero caviar SKUs across all 48
      products. If that has changed, say so loudly.
  (h) the published contact details, and whether a customer-facing WhatsApp link is present

RULES:
- Do not report the "Product title" R19.99 theme placeholder as a product. It is not in
  products.json and is not purchasable.
- Do not report a product as missing because it is past the fold of the 24-item grid.
- Never describe the store as dark, closed or not selling. It is selling.
- Do not modify anything, and do not deploy. Report only.

Finish with one table: check | expected | found | pass/fail, then a short prioritised list of
defects with the exact SKU or page and the exact wrong text. Findings only — I will decide what
gets changed on a live selling page.
```

### Variant B — browser-driven (needs a host with Chromium; **will not work here**)

```
@Computer Use

Open https://studexmeat.com and run a full purchase-path audit of the live storefront, driving
the browser exactly as a customer would. Do not use the Shopify Admin API — it is
unauthenticated and cannot read orders or inventory.

For every product in the catalogue, open its page and record: title, price as displayed
(including any compare-at or sale price), the variant options offered, and the stock status
shown. Then add the cheapest in-stock biltong to the cart and walk cart → checkout → payment as
far as it goes WITHOUT completing a purchase. Screenshot the cart and the checkout summary.

Then verify, against .cursor/rules/studexmeat.mdc:

1. Every price on the page matches the retail list: Luxury Wagyu Biltong from R650, Biltong Gold
   1kg R1,450, 7kg case R12,500, Fire & Feast R999, StudBot Rise R4,599. Flag any mismatch and
   give both the displayed and the expected number.
2. The caviar block shows Sevtruga Medium R1,600/100g, Kaluga Prestige R2,800/100g and Oscietra
   Imperial R4,200/100g — and the string "Sevruga" appears nowhere.
3. The coffee block shows roasted SA prices per kg — Washed R400, Honey R350, Aerobic R380,
   Natural R270 — not green FOB USD/MT pricing.
4. The contact block shows info@studexmeat.com and +27 84 421 6035, and the WhatsApp button
   resolves to +27 94 988 8737. Flag any bare "Email Us" or "WhatsApp Order" label with no
   address or number next to it.
5. The retail order form's WhatsApp destination is +27 83 593 2577. This is deliberate — REPORT
   it, do not change it.
6. No street address is shown anywhere. If one appears, flag it: we have no verified address.

Then open each of these, confirm it loads and shows its expected page, and screenshot it:

  nudsduvyrc12.space.mcode.io   retail biltong store
  ess0ocgcd9f0.space.mcode.io   caviar trade & hospitality
  de6xdoikz95g.space.mcode.io   green coffee B2B export
  psq9xaisb9kf.space.mcode.io   specialty coffee, SA hospitality
  oi28dhtke3yk.space.mcode.io   corporate gifting, Christmas 2026
  fr7m7fzyailo.space.mcode.io   Rwanda coffee, export to China

Finish with one table: check | expected | found | pass/fail. Name every failure with the exact
page and the exact wrong text. DO NOT fix anything in this run — report only. I want the findings
before any edit lands on a live selling page.
```

---

## 2. Repo work (no browser)

```
Working in /workspace. Read .cursor/rules/studexmeat.mdc first and treat it as ground truth,
not suggestions. Then: <TASK>.

Before you change any price, URL or contact, check studex-meat/PRICE-SOURCE-REGISTRY.md §4 —
that is the authoritative index, and several pages under /workspace are retired duplicates that
still serve stale copy.

Keep every API key server-side. No credential may appear in a browser bundle, a client file, a
mailto link or a query string. Lead forms POST to the server-side lead proxy in
studex-lead-proxy/.

When you are done, run `bash ops/run-tests.sh` and `python3 ops/drift-check.py` and paste the
output. The drift check must read "pages: 17 clean: 17 drift: 0 unreachable: 0".

Do not push, deploy, or send anything externally.
```

---

## Connecting Cursor to this repo — DONE on this host

The Cursor CLI binary is **`agent`** (with `cursor-agent` kept as a legacy alias). It is installed
here at `/root/.local/bin/agent`, version `2026.10.22-27dcf5f`, and is **authenticated and
verified** — `agent -p --trust "…"` returned `CURSOR_CLI_OK`.

| Step | Command | Note |
|---|---|---|
| Install | `curl https://cursor.com/install -fsS \| bash` | installs to `~/.local/share/cursor-agent/versions/…`, symlinks `~/.local/bin/agent` |
| Path | `export PATH="$HOME/.local/bin:$PATH"` | add to `~/.bashrc` to persist |
| Authenticate | `export CURSOR_API_KEY=<key>` | **env var, not a login prompt** — the key lives in `TOOLS.md` / `.env` |
| Headless run | `agent -p --trust "<prompt>"` | `--trust` is required or it stops at a directory-trust prompt |
| Apply edits | `agent -p --trust --force "<prompt>"` | ⚠️ print mode **only proposes** changes by default — `--force`/`--yolo` applies them |
| Output | `--output-format text` (default) \| `json` \| `stream-json` | `stream-json` + `--stream-partial-output` for live progress |

🔑 **`--force` is deliberately omitted from prompt 1.** Print mode only *proposes* changes unless
forced, which is exactly the guarantee we want on a live selling page: the agent reports, we
decide. Use `--force` only on prompt 2, and only for repo work.

### ⚠️ The open question on this host
`@Computer Use` needs a **display and a browser** to drive. This is a headless Linux container,
so the browser-driving capability may not work here even though the CLI itself does. Verify before
promising the storefront audit: if it fails, the fallback is a headless browser we drive
ourselves (Playwright/Chromium) and hand the screenshots to `agent` for analysis.

### ⚠️ Do not `npm i -g cursor-agent`
That is a **different, unrelated package** — it installs three packages and exposes no `agent`
binary. The real CLI comes from the install script above. The wrong package was removed from
this host on 2026-10-24.

