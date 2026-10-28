#!/usr/bin/env python3
"""Read-only: is any PRICE going out on a public feed?

THE RULE
--------
`skills/studex-daily-posting/SKILL.md` validation rule [10]:
    "No price on a public feed"  (scope note: "trade pricing stays on the China page")

This is a house rule, not an invention. `memory/2026-10-25-content-package.md`
records a reviewer returning *PACKAGE: REWORK* for exactly this breach.

WHY A CHECKER IS NEEDED
-----------------------
The two publishing paths have OPPOSITE price policies and only one is enforced:

  Path A  scripts/daily-post.py              -> enforces it
           `FAIL: Price published on public feed`
  Path B  studex-content-automation/scripts/
          daily-content-agent.js              -> DOES NOT ENFORCE IT
           the prompt says "Quote the price EXACTLY as given in the product
           record above", and validateCaption() only checks the price is
           *registry-owned*, never whether a price should be there at all.

Live consequence (verified 2026-10-26): the 2026-10-22 caption published
`R1,450` publicly to Instagram `8383092` + Threads `8383081` while every
status stayed green. Nothing flagged it.

    And `studex-content-automation/scripts/blotato-fallback.js` performs NO
    price re-validation at all -- it never reads the catalog or the registry.
    A staged caption ships whatever price was baked in at generation time.

A TRADE price is materially worse than a retail price: the registry's trade
table holds wholesale per-kg figures (e.g. Oscietra `R34,000/kg`), and
publishing one to a retail feed pitches wholesale pricing at retail buyers.

    NOTE ON FLOORS -- do NOT add a below-floor table to this checker.
    `studex-meat/CAVIAR-PRICING-FLOOR-FINDING-2026-10-24.md` says the caviar
    trade prices sit below a 30% floor (Oscietra R34,000 vs floor R37,661).
    **That model is superseded.** `research/2026-10-24-price-reality-check.md`
    §4 and `studex-meat/PRICE-SOURCE-REGISTRY.md` §4j recompute the floors at
    LIVE FX (16.578, not the stale 18.5) with import VAT treated as
    recoverable: Oscietra landed R20,674 / floor R29,535 -> R34,000 **clears
    by R4,465 (39.2%)**; Kaluga R22,000 vs R21,009 clears; Sevtruga R12,500
    vs R12,483 clears by R17 (AT floor, not above it). Both remaining caveats
    are the broker's to answer, not ours: the 20% duty rate is unverified, and
    if import VAT is NOT recoverable then Kaluga and Sevtruga fall below.
    A checker that asserts a stale floor manufactures a false margin crisis.
    This checker reports PRICE ON A PUBLIC FEED, which is a house-rule
    question with an unambiguous answer; it does not opine on margin.

TRADE vs RETAIL is decided by CONTEXT, not by the number. The registry's trade
table lists `R12,500` as the Sevtruga trade/kg price, but `R12,500` is ALSO
the retail price of the Wagyu Biltong Gold 7kg case -- so a numeric set alone
misclassifies. A qualifier modifies what FOLLOWS it, so we look for a
trade/wholesale qualifier before the amount, bounded by the sentence:
    "Trade buyers, we see you too -- R34,000/kg"   -> TRADE
    "at R400/kg for home brewers, with trade orders welcome from 50kg"
                                                 -> RETAIL (qualifier is later,
                                                    and describes a different
                                                    thing)

USAGE
    python3 ops/check-price-on-feed.py              # staged + LIVE (default)
    python3 ops/check-price-on-feed.py --no-live    # staged only (offline)
    python3 ops/check-price-on-feed.py --json       # machine-readable

    The live scan is the DEFAULT. It was opt-in (`--live`) until 2026-10-26,
    which let the default run report a clean live feed it had never checked.
    Use --no-live only for a deliberate offline staged-only run; it says so in
    its output and never claims a whole-feed clean bill.

EXIT CODES
    0 = clean
    1 = FINDING (a price on a public feed)
    2 = could not prove the answer (never a silent pass)

Reads BLOTATO_API_KEY from /workspace/.env IN-PROCESS -- never on a command
line (a literal key in argv is written to the gateway log by the probe itself).
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = "/workspace"
PENDING_DIR = os.path.join(ROOT, "studex-content-automation/posts/pending")
REGISTRY = os.path.join(ROOT, "studex-meat/PRICE-SOURCE-REGISTRY.md")
SKILL = os.path.join(ROOT, "skills/studex-daily-posting/SKILL.md")
ENV = os.path.join(ROOT, ".env")
BASE = "https://backend.blotato.com/v2"

# ZAR amounts as they appear in a caption. "R4,200", "R 4 200", "R34,000".
# A price with a comma or a space separator counts; a bare "R650" counts too.
AMOUNT_RE = re.compile(r"R\s?(\d{1,3}(?:[,\s]\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)")


def _digits(raw):
    """Normalise '4,200' / '4 200' / '4200' -> '4200'."""
    return re.sub(r"\D", "", raw)


# A qualifier modifies what FOLLOWS it.
TRADE_CONTEXT = re.compile(
    r"\b(trade|wholesale|distributor|bulk|ex[ -]?vat)\b", re.I
)
TRADE_WINDOW = 100


def trade_context_near(text, start):
    """True if a trade/wholesale qualifier PRECEDES this amount.

    Bounded by the sentence: a qualifier belongs to the sentence it is in, so
    a full stop between the qualifier and the amount ends its reach. This is
    what separates "Trade buyers -- R34,000/kg" (TRADE) from
    "R400/kg for home brewers, with trade orders welcome from 50kg" (RETAIL).
    """
    if not text:
        return False
    before = text[max(0, start - TRADE_WINDOW):start]
    if "." in before:
        before = before[before.rfind(".") + 1:]
    return bool(TRADE_CONTEXT.search(before))


def registry_trade_prices():
    """Wholesale per-kg prices from the registry's trade table.

    Parsed from the 'Trade, per kg' table so the checker follows the registry
    instead of hardcoding a private allowlist of figures. Used only to
    ANNOTATE a price as trade-listed; the trade/retail verdict comes from
    context (see trade_context_near), because a registry trade price can also
    be a retail price for a different product.
    """
    found = set()
    try:
        with open(REGISTRY, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return found
    in_trade_table = False
    for line in lines:
        low = line.lower()
        if low.startswith("**trade, per kg") or low.startswith("| product | trade /kg"):
            in_trade_table = True
            continue
        if in_trade_table:
            if not line.strip().startswith("|"):
                if found:
                    break
                continue
            if set(line.replace("|", "").strip()) <= set("- :"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or cells[0].lower() in ("product",):
                continue
            for cell in cells[1:2]:
                for m in AMOUNT_RE.finditer(cell):
                    found.add(_digits(m.group(1)))
    return found


def skill_rule_10():
    """Confirm the rule this checker enforces is still in the skill."""
    try:
        with open(SKILL, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    m = re.search(r"^\s*\[?10\]?[^\n]*no price on a public feed", text, re.I | re.M)
    if m:
        return m.group(0).strip()
    if re.search(r"no price on a public feed", text, re.I):
        return "no price on a public feed"
    return None


def scan_caption(text, trade_prices):
    """Return the list of price findings in one caption.

    Each finding carries:
      amount   - the raw text as it appeared
      digits   - normalised digits
      kind     - 'TRADE' | 'RETAIL', decided by CONTEXT (qualifier before the
                 amount, sentence-bounded), not by the number
      listed   - True if the amount is also a price in the registry trade table
                 (annotation only; R12,500 is both a trade/kg price and the
                 retail 7kg-case price, so this cannot decide the kind)
    """
    out = []
    for m in AMOUNT_RE.finditer(text or ""):
        raw = m.group(0).strip()
        digits = _digits(m.group(1))
        if not digits:
            continue
        is_trade = trade_context_near(text or "", m.start())
        out.append(
            {
                "amount": raw,
                "digits": digits,
                "kind": "TRADE" if is_trade else "RETAIL",
                "listed": digits in trade_prices,
            }
        )
    return out


def staged_captions(trade_prices):
    """Every staged (not-yet-published) caption on disk."""
    rows = []
    if not os.path.isdir(PENDING_DIR):
        return rows
    for name in sorted(os.listdir(PENDING_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(PENDING_DIR, name)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        caption = data.get("caption") or ""
        status = data.get("status") or ""
        if not caption:
            continue
        hits = scan_caption(caption, trade_prices)
        rows.append(
            {
                "date": name[: -len(".json")],
                "status": status,
                "published": bool(data.get("fallback", {}).get("posted")),
                "product": data.get("productName") or data.get("product") or "",
                "prices": hits,
                "caption": caption,
            }
        )
    return rows


def _env_key(name):
    try:
        with open(ENV, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == name:
                    return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def live_posts(trade_prices):
    """Live Blotato posts. Returns (rows, error)."""
    key = _env_key("BLOTATO_API_KEY")
    if not key:
        return [], "BLOTATO_API_KEY not set"

    def get(path):
        req = urllib.request.Request(
            BASE + path,
            headers={"blotato-api-key": key, "accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.load(resp)

    try:
        d = get("/posts?limit=50")
    except urllib.error.HTTPError as e:
        return [], "posts HTTP %s (wrong header or expired key)" % e.code
    except Exception as e:  # noqa: BLE001
        return [], "posts request failed: %s" % e
    items = d if isinstance(d, list) else (d.get("items") or d.get("posts") or [])
    if not items:
        # An empty list must never read as "nothing published".
        return [], "post list came back empty - cannot prove what published"

    rows = []
    for it in items:
        acct = it.get("account")
        acc = acct if isinstance(acct, dict) else {}
        text = it.get("text") or it.get("content") or ""
        rows.append(
            {
                "id": str(it.get("id") or ""),
                "platform": acc.get("platform") or it.get("platform") or "",
                "account": str(acc.get("id") or it.get("accountId") or ""),
                "postTime": str(it.get("postTime") or it.get("publishedAt") or "")[:19],
                "prices": scan_caption(text, trade_prices),
            }
        )
    return rows, None


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    # Live is the DEFAULT, not an opt-in.
    #
    # On 2026-10-26 the default run printed "live posts : 0" and its CLEAN
    # verdict claimed "no price on any public feed (staged or live)" -- while
    # posts 8383092 / 8383081 still carried R1,450 live, and the live scan had
    # never run. A checker that can report CLEAN without looking at the live
    # feed is a false all-clear, which is worse than no checker at all.
    # --no-live is the explicit opt-out, and it must not claim live coverage.
    want_live = "--no-live" not in args

    trade_prices = registry_trade_prices()
    rule = skill_rule_10()

    if not rule:
        print("ERROR: rule [10] 'no price on a public feed' not found in %s" % SKILL)
        print("       cannot prove the policy this checker enforces. Refusing to pass.")
        return 2

    staged = staged_captions(trade_prices)
    live, live_err = ([], None)
    if want_live:
        live, live_err = live_posts(trade_prices)
        if live_err:
            print("ERROR: %s" % live_err)
            print("       refusing to report a clean feed without live evidence.")
            return 2

    staged_bad = [r for r in staged if r["prices"] and not r["published"]]
    live_bad = [r for r in live if r["prices"]]

    if as_json:
        print(
            json.dumps(
                {
                    "rule": rule,
                    "trade_prices": sorted(trade_prices),
                    "staged_with_prices": staged_bad,
                    "live_with_prices": live_bad,
                    "staged_total": len(staged),
                    "live_total": len(live),
                },
                indent=2,
            )
        )
        return 1 if (staged_bad or live_bad) else 0

    print("price-on-feed check")
    print("  rule            : %s" % rule)
    print("  trade prices    : %s" % (", ".join(sorted(trade_prices)) or "none parsed"))
    print("  staged captions : %d" % len(staged))
    if want_live:
        print("  live posts      : %d" % len(live))
    else:
        print("  live posts      : SKIPPED (--no-live; live feed NOT checked)")

    for r in staged_bad:
        print(
            "  [STAGED] %s  %s  %s"
            % (r["date"], r["status"], r["product"][:40])
        )
        for p in r["prices"]:
            print("           %-8s %s" % (p["kind"], p["amount"]))
    for r in live_bad:
        print(
            "  [LIVE]   %s %s acct=%s"
            % (r["postTime"], r["platform"], r["account"])
        )
        for p in r["prices"]:
            print("           %-8s %s" % (p["kind"], p["amount"]))

    if staged_bad or live_bad:
        n_stage = len(staged_bad)
        n_live = len(live_bad)
        print(
            "VERDICT: FINDING - %d staged caption(s) and %d live post(s) carry a price on a public feed."
            % (n_stage, n_live)
        )
        print("         Rule [10]: no price on a public feed. Strip the price, or get an")
        print("         explicit approval for that specific caption before publishing it.")
        return 1

    if want_live:
        print("VERDICT: CLEAN - no price on any public feed (staged or live).")
    else:
        print("VERDICT: CLEAN (staged only) - live feed NOT checked (--no-live).")
        print("         This is NOT a whole-feed clean bill of health.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
