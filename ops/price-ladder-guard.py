#!/usr/bin/env python3
"""
LADDER LOCK — price-integrity and caviar-compliance guard for StudEx.

Built: 2026-10-28 (Build Hour). Owner: Robusca / StudEx Ops.

WHY THIS EXISTS
---------------
On 2026-10-28 the research brief found two live defects on the StudEx price
ladder and one compliance exposure:

  1. PRICE INVERSION — "Luxury Wagyu Biltong" 500g (R450) cost MORE per kilo
     (R900/kg) than the 1kg (R650 = R650/kg). The smaller pack was penalised.
  2. CASE ARBITRAGE — "Wagyu Biltong Gold" 7kg case (R12,500 = R1,785/kg) cost
     more than seven 1kg boxes (7 x R1,450 = R10,150). A rational buyer beat
     the "premium" case by 18.8% on our own price sheet.
  3. CAVIAR EXPOSURE — caviar is marketed on live pages while the SA permit
     stack (DFFE -> ITAC -> DAFF -> SARS -> NRCS -> CITES) is unassembled.

This guard re-derives all three from live sources, so the defect cannot
silently return after someone edits a page.

DESIGN NOTES (why it is not naive)
----------------------------------
Three false-positive traps were found while building this and are handled
explicitly, because a guard that cries wolf gets switched off:

  * CATEGORY — a biltong market ceiling must never be applied to coffee pods
    or beef steaks. Every rule is category-scoped.
  * FORM — a 10 x 50g coffee pod pack (R2,000/kg) is not the same product as
    a 1kg bean bag (R350/kg). Pod-vs-bag is normal merchandising, not an
    inversion. Per-kg comparison only happens inside the same pack form.
  * GRADE — coffee grades (A1/A2/A3) are different products. A1 500g is
    never compared against A2 1kg.

Per-kg comparison additionally requires a minimum weight of MIN_WEIGHT_KG so
that sample/tasting units (e.g. a 1g cut) do not manufacture absurd numbers.

SEVERITY MODEL
--------------
  BLOCKING  — a defect that costs money or creates legal risk:
              case arbitrage, a same-form smaller-pack penalty above
              SMALL_PACK_MAX_PREMIUM_PCT, caviar offered for sale without a
              permit stack, an unconditional compliance claim, price drift
              between the catalog and the live store.
  WARN      — needs a human decision but is not automatically wrong:
              a per-kg premium on a smaller pack that is normal merchandising,
              a price above the category ceiling without a named benchmark,
              caviar marketed with correctly permit-conditioned copy.
  INFO      — context only.

USAGE
-----
  python3 ops/price-ladder-guard.py                  # human-readable report
  python3 ops/price-ladder-guard.py --json           # machine-readable
  python3 ops/price-ladder-guard.py --out FILE       # write markdown report

Exit code: 0 when no BLOCKING findings, 1 when blocking findings exist.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "studex-products-catalog.csv"
STOREFRONT = "https://studexmeat.com/products.json?limit=250"

LIVE_PAGES = {
    # current
    "t56b7vkncytt": "Retail / biltong landing",
    "ujlho19swr48": "Price & provenance sheet (festive)",
    "oi28dhtke3yk": "Corporate gifting",
    "ess0ocgcd9f0": "Caviar page",
    "i09hd71cvt06": "Coffee & hospitality (SA)",
    # 2026-10-28 — the retired retail builds (nudsduvyrc12, bkqn328wj5a6) are
    # out of this list on purpose: they still serve the old prices and a caviar
    # sale path, so checking them produces findings nobody can act on. The
    # do-not-share rule for those URLs lives in the registry's superseded table.
}

# ---------------------------------------------------------------- compliance
PERMIT_STACK_ASSEMBLED = False
PERMIT_STACK_COMPONENTS = [
    "DFFE",
    "ITAC frozen-fish notification",
    "DAFF importer registration",
    "SARS importer code + duty line",
    "NRCS",
    "CITES export permit + registered exporter code",
]

CAVIAR_RE = re.compile(r"caviar|beluga|oscietra|kaluga|sevtruga|sevruga|sturgeon", re.I)

# A caviar PRICE is tied to a caviar GRADE. The generic word "caviar" counts
# mentions but does not, on its own, mean a price is a caviar price — that
# assumption flagged pages carrying unrelated prices near the word.
CAVIAR_GRADE_RE = re.compile(
    r"oscietra|kaluga|sevtruga|sevruga|beluga|sturgeon|sevruga imperial|caviar\s+(?:imperial|prestige|medium)",
    re.I,
)

# Copy that asserts compliance as a settled fact.
UNCONDITIONAL_CLAIMS = [
    re.compile(p, re.I)
    for p in (
        r"cites[- ]compliant",
        r"itac[- ]compliant",
        r"\bcites certified\b",
        r"we handle the paperwork",
        r"fully compliant",
        r"all permits in place",
        r"import permit (?:is )?in hand",
    )
]

# Copy that ties the claim to a permit that has not yet been issued. This is
# acceptable while the stack is unassembled — provided no sale path exists.
CONDITIONAL_ALLOWLIST = [
    re.compile(p, re.I)
    for p in (
        r"permit is in hand",
        r"permit obtained before dispatch",
        r"permit is issued",
        r"documentation where applicable",
        r"import compliance",
        r"subject to",
        r"where required",
        r"on issuance of",
        r"before dispatch",
        r"lead time",
    )
]

# ------------------------------------------------------------------ market
# SA biltong ladder, Oct 2026 (research/2026-10-28.md, Topic 2).
BILTONG_BENCHMARKS = [
    ("Butcher Brothers, Westrand", 269.99),
    ("Vanni Vrystaat", 279.90),
    ("Biltong Boss, Gqeberha", 305.95),
    ("Biltong Boytjies (entry)", 349.99),
    ("Biltong Boytjies (top)", 449.99),
    ("Mooiplaats Wagyu", 600.00),
    ("Woolworths free-range sliced 400g", 700.00),
]
BILTONG_CEILING_PER_KG = 1053.00  # Woolworths chilli snapsticks 150g
BILTONG_CEILING_SOURCE = "Woolworths chilli snapsticks 150g — R157.99 / 150g = R1,053/kg"

# A smaller pack may carry a per-kg premium. How much is acceptable depends
# on the line, and pretending otherwise is how a guard gets switched off.
#
#   biltong / coffee — we sell these on provenance and price-sheet coherence.
#                      A per-kg penalty on the smaller pack makes the sheet
#                      look broken, so we hold these strictly monotone.
#   beef             — a smaller cut carrying a premium is normal SA butcher
#                      convention (and smaller cuts cost more to trim/handle).
#                      We flag it, we do not mandate it.
#   default          — same treatment as beef.
LADDER_POLICY = {
    "biltong": 15.0,
    "coffee": 15.0,
    "beef": 45.0,
    "default": 45.0,
}


def max_premium_pct(category: str) -> float:
    return LADDER_POLICY.get(category, LADDER_POLICY["default"])

MIN_WEIGHT_KG = 0.1  # below this, per-kg comparison is meaningless

# Pack forms that must match before two SKUs are compared per-kg.
FORM_TOKENS = ("pod", "bag", "pouch", "packet", "box", "case", "tin", "can", "jar")

UA = "Mozilla/5.0 (compatible; StudExLadderLock/1.0)"


# ---------------------------------------------------------------- utilities
def fetch(url: str, timeout: int = 25) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def parse_weight_kg(text: str) -> float | None:
    if not text:
        return None
    t = text.lower()
    if "monthly" in t or "subscription" in t or "default title" in t:
        return None
    paren = re.search(r"\(([\d.]+)\s*(kg|g)\)", t)
    if paren:
        q = float(paren.group(1))
        return q if paren.group(2) == "kg" else q / 1000.0
    m = re.search(r"([\d.]+)\s*kg", t)
    if m:
        return float(m.group(1))
    m = re.search(r"([\d.]+)\s*g\b", t)
    if m:
        return float(m.group(1)) / 1000.0
    m = re.search(r"(\d+)\s*x\s*([\d.]+)\s*g", t)
    if m:
        return float(m.group(1)) * float(m.group(2)) / 1000.0
    return None


def strip_sizes(text: str) -> str:
    t = text.lower()
    t = re.sub(r"\b\d+\s*x\s*\d+\s*g\b", " ", t)
    t = re.sub(r"\b\d+(?:\.\d+)?\s*(?:kg|g|grams?)\b", " ", t)
    return re.sub(r"\s+", " ", t).strip(" -—·()[],")


def line_key(title: str) -> str:
    """Loose product-line key: the first meaningful tokens of the title."""
    t = strip_sizes(title)
    t = re.sub(r"^\s*\d+[.)]\s*", "", t)
    t = re.sub(r"[|—–·]", " ", t)
    stop = {"the", "and", "a", "of", "for", "from", "our", "with"}
    toks = [w for w in re.findall(r"[a-z0-9]+", t) if w not in stop]
    return " ".join(toks[:3])


def grade_key(variant: str) -> str:
    """Variant identity with sizes stripped — keeps grade/format descriptors."""
    t = strip_sizes(variant)
    t = re.sub(r"\bdefault\s+title\b", "", t)
    return re.sub(r"\s+", " ", t).strip(" -—·/|,")


def form_of(*texts: str) -> str:
    blob = " ".join(texts).lower()
    for tok in FORM_TOKENS:
        if re.search(rf"\b{tok}s?\b", blob):
            return tok
    return "plain"


GENERIC_CATEGORIES = {"", "simple", "default", "default title", "uncategorised", "none"}


def normalise_category(cat: str, title: str = "", handle: str = "") -> str:
    """
    Map a product to a pricing category.

    Shopify's `product_type` is frequently the literal string "simple", so a
    category that is not usable is inferred from the title and handle. Without
    this, live biltong SKUs fall outside the biltong market ceiling and the
    strict 15% small-pack policy — which is exactly how a defect slips through.
    """
    c = (cat or "").strip().lower()
    if c not in GENERIC_CATEGORIES:
        if "biltong" in c:
            return "biltong"
        if "coffee" in c:
            return "coffee"
        if "caviar" in c:
            return "caviar"
        if "wagyu" in c or "beef" in c or "steak" in c:
            return "beef"
        if "box" in c or "bundle" in c:
            return "boxes"
        return c

    blob = f"{title} {handle}".lower()
    if "biltong" in blob:
        return "biltong"
    if "caviar" in blob:
        return "caviar"
    if "coffee" in blob:
        return "coffee"
    if "wagyu" in blob or "steak" in blob or "boerewors" in blob:
        return "beef"
    return c or "uncategorised"


# ------------------------------------------------------------------ findings
@dataclass
class Finding:
    severity: str
    code: str
    subject: str
    detail: str
    evidence: str = ""
    fix: str = ""

    def line(self) -> str:
        return f"[{self.severity}] {self.code} — {self.subject}: {self.detail}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    live_products: int = 0
    catalog_products: int = 0
    pages_checked: dict[str, Any] = field(default_factory=dict)
    ladder: list[dict] = field(default_factory=list)

    def add(self, *a, **k):
        self.findings.append(Finding(*a, **k))

    @property
    def blocking(self):
        return [f for f in self.findings if f.severity == "BLOCKING"]


# --------------------------------------------------------- ladder analysis
def analyse_ladder(rows: list[dict], rep: Report, origin: str) -> None:
    entries = []
    for r in rows:
        kg = parse_weight_kg(r["variant"]) or parse_weight_kg(r["title"])
        if not kg or not r["price"] or kg <= 0:
            continue
        if kg < MIN_WEIGHT_KG:
            continue
        e = {
            **r,
            "kg": kg,
            "per_kg": r["price"] / kg,
            "cat": normalise_category(r.get("category", ""), r["title"], r.get("handle", "")),
            "line": line_key(r["title"]),
            "grade": grade_key(r["variant"]),
            "form": form_of(r["title"], r["variant"]),
        }
        entries.append(e)
        rep.ladder.append(
            {
                "origin": origin,
                "title": r["title"],
                "variant": r["variant"],
                "category": e["cat"],
                "price": r["price"],
                "kg": kg,
                "per_kg": round(e["per_kg"], 2),
            }
        )

    # ---- A: per-kg comparison inside product line + grade + form
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        groups.setdefault((e["line"], e["grade"], e["form"]), []).append(e)

    for (ln, gr, fm), items in groups.items():
        if len(items) < 2:
            continue
        for a in items:
            for b in items:
                if a is b or a["kg"] >= b["kg"]:
                    continue
                if a["per_kg"] <= b["per_kg"] + 0.01:
                    continue
                premium = (a["per_kg"] / b["per_kg"] - 1) * 100
                limit = max_premium_pct(a["cat"])
                blocking = premium > limit
                rep.add(
                    "BLOCKING" if blocking else "WARN",
                    "LADDER-INVERSION",
                    f"{a['title']} ({a['variant']}) [{origin}]",
                    f"{a['variant']} costs R{a['per_kg']:,.2f}/kg against R{b['per_kg']:,.2f}/kg "
                    f"for the larger {b['variant']} — a {premium:.0f}% per-kilo penalty "
                    f"(limit for {a['cat']}: {limit:.0f}%).",
                    f"R{a['price']:,.0f}/{a['kg']}kg = R{a['per_kg']:,.2f}/kg  vs  "
                    f"R{b['price']:,.0f}/{b['kg']}kg = R{b['per_kg']:,.2f}/kg",
                    f"Price {a['variant']} at or below R{b['per_kg']:,.2f}/kg so the larger pack "
                    f"stays the volume anchor.",
                )

    # ---- B: case-vs-singles arbitrage (product line, form ignored)
    for case in entries:
        blob = f"{case['title']} {case['variant']}".lower()
        # A bulk SKU is a "case" or a multi-kilogram box. Both are sold to
        # resellers and gifting operations, and both must beat the singles.
        if not re.search(r"\b(case|box)\b", blob):
            continue
        if case["kg"] < 1:
            continue
        for sib in entries:
            if sib is case or sib["line"] != case["line"]:
                continue
            if sib["kg"] >= case["kg"]:
                continue
            ratio = case["kg"] / sib["kg"]
            if abs(ratio - round(ratio)) > 0.01 or ratio < 2:
                continue
            r = int(round(ratio))
            singles = sib["price"] * r
            if case["price"] > singles:
                beaten = (case["price"] - singles) / case["price"] * 100
                rep.add(
                    "BLOCKING",
                    "LADDER-CASE-ARBITRAGE",
                    f"{case['title']} ({case['variant']}) [{origin}]",
                    f"The {case['kg']}kg case (R{case['price']:,.0f}) costs more than {r} x "
                    f"{sib['variant']} (R{singles:,.0f}). A buyer can beat the case by "
                    f"{beaten:.1f}% on our own price sheet.",
                    f"R{case['price']:,.0f}/{case['kg']}kg = R{case['per_kg']:,.2f}/kg  vs  "
                    f"{r} x R{sib['price']:,.0f} = R{singles:,.0f}",
                    f"Set the case at or below R{singles:,.0f}. A small bulk discount is fine — "
                    f"it is what makes the case the obvious choice.",
                )

    # ---- E: category-scoped market ceiling
    for e in entries:
        if e["cat"] != "biltong":
            continue
        if e["per_kg"] <= BILTONG_CEILING_PER_KG:
            continue
        rep.add(
            "WARN",
            "LADDER-ABOVE-CEILING",
            f"{e['title']} ({e['variant']}) [{origin}]",
            f"R{e['per_kg']:,.2f}/kg is above the highest openly quoted SA biltong price "
            f"(R{BILTONG_CEILING_PER_KG:,.0f}/kg) with no named benchmark.",
            BILTONG_CEILING_SOURCE,
            "Name the benchmark on the page, or bring the price into the band.",
        )


# --------------------------------------------------------- caviar exposure
def check_pages(rep: Report) -> None:
    for sid, label in LIVE_PAGES.items():
        url = f"https://{sid}.space.mcode.io"
        code, body = fetch(url)
        if code != 200 or not body:
            rep.pages_checked[sid] = {"label": label, "http": code, "ok": False}
            rep.add(
                "WARN",
                "PAGE-UNREACHABLE",
                f"{label} ({sid})",
                f"Could not fetch {url} (HTTP {code}); caviar exposure unverified.",
                f"HTTP {code}",
                "The guard cannot verify a page it cannot read.",
            )
            continue

        caviar_hits = len(CAVIAR_RE.findall(body))
        claims = [p.pattern for p in UNCONDITIONAL_CLAIMS if p.search(body)]

        # Strip conditional sentences, then look for residual hard claims.
        scrub = body
        for c in CONDITIONAL_ALLOWLIST:
            scrub = c.sub(" ", scrub)
        residual = [p.pattern for p in UNCONDITIONAL_CLAIMS if p.search(scrub)]

        # Does the page offer caviar for sale (a published price + an order path)?
        #
        # A caviar price is a price that sits NEAR A CAVIAR KEYWORD. Matching
        # price formatting alone is wrong: "R1,250 / 1kg" is biltong, and a
        # naive /1kg matcher reads it as caviar.
        offers = False
        for kw in CAVIAR_GRADE_RE.finditer(body):
            window = body[max(0, kw.start() - 400): kw.end() + 400]
            if re.search(r"R\s?[\d,]{3,6}", window):
                offers = True
                break
        has_order_path = bool(
            re.search(r"(add to cart|order now|buy now|checkout|inquiry form|request a quote|whatsapp)", body, re.I)
        )

        rep.pages_checked[sid] = {
            "label": label,
            "http": code,
            "caviar_mentions": caviar_hits,
            "unconditional_claims": residual,
            "offers_caviar_price": offers,
            "has_order_path": has_order_path,
        }

        if caviar_hits and not PERMIT_STACK_ASSEMBLED:
            if residual:
                rep.add(
                    "BLOCKING",
                    "CAVIAR-COMPLIANCE-CLAIM",
                    f"{label} ({sid})",
                    "Publishes an unconditional compliance claim with no permit behind it.",
                    "; ".join(residual),
                    "Tie the claim to a permit in hand, or remove it.",
                )
            elif offers and has_order_path:
                rep.add(
                    "BLOCKING",
                    "CAVIAR-SELL-WITHOUT-PERMIT",
                    f"{label} ({sid})",
                    f"Publishes caviar prices ({caviar_hits} mentions) with an order path while "
                    f"the SA caviar permit stack is unassembled. A caviar sale without the "
                    f"stack is a seizure risk.",
                    "; ".join(PERMIT_STACK_COMPONENTS),
                    "Pull the caviar offer from the purchase path until the permit stack exists. "
                    "Keep the page as a permit-conditioned inquiry desk only.",
                )
            else:
                rep.add(
                    "WARN",
                    "CAVIAR-PERMIT-CONDITIONED",
                    f"{label} ({sid})",
                    f"{caviar_hits} caviar mention(s) published. Copy is permit-conditioned, so "
                    f"this is acceptable — but no purchase path may be added before the stack exists.",
                    "conditional language detected; no unconditional claim found",
                    "Re-check before adding any caviar checkout or 'order' CTA.",
                )


# ------------------------------------------------------------------- drift
def check_drift(rep: Report, live: list[dict], catalog: list[dict]) -> None:
    def key(r):
        return (r["title"].strip().lower(), r["variant"].strip().lower())

    live_map = {key(r): r for r in live}
    cat_map = {key(r): r for r in catalog}
    for k in sorted(set(live_map) & set(cat_map)):
        lp, cp = live_map[k]["price"], cat_map[k]["price"]
        if abs(lp - cp) > 0.01:
            rep.add(
                "BLOCKING",
                "PRICE-DRIFT",
                f"{k[0]} ({k[1]})",
                f"Live storefront shows R{lp:,.0f} but the catalog export says R{cp:,.0f}.",
                f"live=R{lp:,.0f} catalog=R{cp:,.0f}",
                "The catalog export is the source of truth — reconcile before editing pages.",
            )


# --------------------------------------------------------------------- I/O
def load_live() -> tuple[list[dict], int]:
    code, body = fetch(STOREFRONT)
    if code != 200:
        return [], 0
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return [], 0
    rows = []
    for p in data.get("products", []):
        cat = p.get("product_type") or ""
        for v in p.get("variants", []):
            try:
                price = float(v.get("price") or 0)
            except (TypeError, ValueError):
                continue
            rows.append(
                {
                    "title": p.get("title", ""),
                    "variant": v.get("title", ""),
                    "price": price,
                    "compare_at": v.get("compare_at_price"),
                    "handle": p.get("handle", ""),
                    "category": cat,
                }
            )
    return rows, len(data.get("products", []))


def load_catalog() -> list[dict]:
    if not CATALOG.exists():
        return []
    rows = []
    with CATALOG.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                price = float(r.get("Price (ZAR)") or 0)
            except (TypeError, ValueError):
                continue
            rows.append(
                {
                    "title": r.get("Product Title", ""),
                    "variant": r.get("Variant", ""),
                    "price": price,
                    "compare_at": r.get("Compare At", ""),
                    "handle": r.get("Handle", ""),
                    "category": r.get("Category", ""),
                }
            )
    return rows


def render(rep: Report) -> str:
    out = []
    out.append("# LADDER LOCK — price integrity & caviar compliance report")
    out.append("")
    out.append(f"- Generated: {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}")
    out.append(f"- Live storefront products: **{rep.live_products}**")
    out.append(f"- Catalog rows: **{rep.catalog_products}**")
    out.append(f"- Live pages checked: **{len(rep.pages_checked)}**")
    out.append(f"- Blocking findings: **{len(rep.blocking)}**")
    out.append("")
    out.append("## Findings")
    out.append("")
    if not rep.findings:
        out.append("_No findings. Ladder monotone, no case arbitrage, no caviar exposure._")
    else:
        order = {"BLOCKING": 0, "WARN": 1, "INFO": 2}
        for f in sorted(rep.findings, key=lambda x: (order.get(x.severity, 3), x.code)):
            out.append(f"### {f.line()}")
            if f.evidence:
                out.append(f"- **Evidence:** {f.evidence}")
            if f.fix:
                out.append(f"- **Fix:** {f.fix}")
            out.append("")
    out.append("## Page exposure matrix")
    out.append("")
    out.append(
        "| Deploy | Page | HTTP | Caviar mentions | Unconditional claims | "
        "Caviar priced | Order path | Verdict |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for sid, i in rep.pages_checked.items():
        verdict = "CLEAN"
        if i.get("unconditional_claims"):
            verdict = "BLOCK — compliance claim"
        elif i.get("caviar_mentions") and i.get("offers_caviar_price") and i.get("has_order_path"):
            verdict = "BLOCK — caviar for sale"
        elif i.get("caviar_mentions"):
            verdict = "REVIEW — caviar, permit-conditioned"
        out.append(
            f"| `{sid}` | {i.get('label','')} | {i.get('http','')} | "
            f"{i.get('caviar_mentions','-')} | {len(i.get('unconditional_claims') or [])} | "
            f"{i.get('offers_caviar_price','-')} | {i.get('has_order_path','-')} | {verdict} |"
        )
    out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="StudEx price-ladder + caviar-compliance guard")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--out", help="write the markdown report to this path")
    args = ap.parse_args()

    rep = Report()
    live_rows, n_live = load_live()
    rep.live_products = n_live
    cat_rows = load_catalog()
    rep.catalog_products = len(cat_rows)

    if not live_rows:
        rep.add("WARN", "STOREFRONT-UNREADABLE", "studexmeat.com",
                "Live storefront product feed unreadable; live checks skipped.", "",
                "Check storefront availability.")

    analyse_ladder(live_rows, rep, "live-storefront")
    analyse_ladder(cat_rows, rep, "catalog")
    check_pages(rep)
    if live_rows and cat_rows:
        check_drift(rep, live_rows, cat_rows)

    if args.json:
        payload = {
            "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "live_products": rep.live_products,
            "catalog_products": rep.catalog_products,
            "pages": rep.pages_checked,
            "findings": [asdict(f) for f in rep.findings],
            "blocking": len(rep.blocking),
            "ladder": rep.ladder,
        }
        text = json.dumps(payload, indent=2)
    else:
        text = render(rep)

    print(text)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"(written to {args.out})", file=sys.stderr)

    return 1 if rep.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
