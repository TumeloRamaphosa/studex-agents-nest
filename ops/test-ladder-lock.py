#!/usr/bin/env python3
"""Regression test for the 2026-10-28 LADDER LOCK (retail biltong price ladder).

Asserts, deterministically:
  1. the hand-edited source and the deployable copy are byte-identical;
  2. the registry page map points at the CURRENT retail + SA-hospitality pages
     and names no retired slug;
  3. each live page carries the prices the registry says it must carry;
  4. the retired prices / copy claims are GONE from the pages that dropped them;
  5. the price-ladder guard's own page list names the current pages.

Exit 0 = every assertion passed. Exit 1 = at least one failed (each is printed).
Read-only: it fetches pages, it never writes or deploys anything.
"""
import os, re, sys, html, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "studex-meat/PRICE-SOURCE-REGISTRY.md")
SRC = os.path.join(ROOT, "studex-biltong/index.html")
DIST = os.path.join(ROOT, "studex-biltong/dist/index.html")
GUARD = os.path.join(ROOT, "ops/price-ladder-guard.py")

RETAIL = "t56b7vkncytt"      # retail / biltong store (ladder-locked build)
SA_HOSP = "i09hd71cvt06"    # coffee SA hospitality (rebuilt 2026-10-28)
CAVIAR = "ess0ocgcd9f0"     # caviar trade page (still the caviar home)
INSTIT = "hhsmhunf1xci"     # institutional sell sheet
RETIRED = ("nudsduvyrc12", "bkqn328wj5a6", "psq9xaisb9kf")

fails, checks = [], 0


def check(cond, label):
    global checks
    checks += 1
    if not cond:
        fails.append(label)


def visible(html_body):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_body, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(re.sub(r"\s+", " ", t))


def money(text, amount):
    """True when the amount appears as a Rand price (R1,250 / R 1 250 / R1250)."""
    digits = amount.lstrip("Rr").replace(",", "")
    return re.search(r"R\s*" + digits + r"(?![0-9])", re.sub(r"[,\s]+", "", text)) is not None


def fetch(slug):
    url = f"https://{slug}.space.mcode.io/"
    try:
        rq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(rq, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, visible(raw), raw
    except Exception as e:
        return None, str(e), ""


# 1 ---------------------------------------------------------------- source == dist
check(os.path.exists(SRC) and os.path.exists(DIST), "source and dist both exist")
if os.path.exists(SRC) and os.path.exists(DIST):
    check(open(SRC, "rb").read() == open(DIST, "rb").read(),
          "studex-biltong/index.html is byte-identical to studex-biltong/dist/index.html")

reg = open(REG, encoding="utf-8").read()
check(f"`{RETAIL}.space.mcode.io`" in reg, f"registry names the current retail page {RETAIL}")
check(f"`{SA_HOSP}.space.mcode.io`" in reg, f"registry names the current SA-hospitality page {SA_HOSP}")
page_map = reg.split("## 4. PAGE", 1)[1].split("\n## ", 1)[0]
rule_sections = "".join(
    blk for blk in re.split(r"\n(?=## )", reg)
    if blk.startswith("## 2.") or blk.startswith("## 4b") or blk.startswith("## 4c")
    or blk.startswith("## 4d") or blk.startswith("## 4e") or blk.startswith("## 4f"))
for old in RETIRED:
    check(old not in page_map, f"page map no longer points at the retired slug {old}")
    check("`" + old + "`" not in rule_sections,
          f"no must-appear-on rule still names the retired slug {old}")

# 2 ----------------------------------------------------------- live page content
status, retail, retail_raw = fetch(RETAIL)
check(status == 200, f"retail page {RETAIL} is reachable (http {status})")
for amount in ("R325", "R1,250", "R8,400", "R999", "R4,599", "R295", "R495", "R850"):
    check(money(retail, amount), f"retail page shows {amount}")
for phrase in ("+27 84 421 6035", "+27 94 988 8737", "info@studexmeat.com",
               "Our Wagyu range is certified Halaal", "Oscietra Imperial"):
    check(phrase in retail, f"retail page keeps '{phrase}'")
for gone in ("R650", "R1,450", "R12,500", "R4,200", "R2,800", "R1,600", "R34,000",
             "R22,000", "per 100g", "100% Halaal Certified", "per 250g", "Sevruga Premium",
             "Siberian Reserve", "agent.studexmeat.com"):
    check(not money(retail, gone) and gone not in retail,
          f"retail page no longer shows '{gone}'")

status, hosp, hosp_raw = fetch(SA_HOSP)
check(status == 200, f"SA-hospitality page {SA_HOSP} is reachable (http {status})")
for amount in ("R325", "R1,250", "R8,400"):
    check(money(hosp, amount), f"SA-hospitality page shows {amount}")
for gone in ("R1,450", "R12,500", "R4,200", "R2,800", "R1,600", "Coming Soon",
             "Rainforest Alliance", "agent.studexmeat.com"):
    check(not money(hosp, gone) and gone not in hosp,
          f"SA-hospitality page no longer shows '{gone}'")
check(RETAIL in hosp_raw, f"SA-hospitality page links the current retail page ({RETAIL})")
check(INSTIT in hosp_raw, f"SA-hospitality page links the current sell sheet ({INSTIT})")
for dead in ("nmtmhtvhqgpw", "z7p9urw22jwb"):
    check(dead not in hosp_raw, f"SA-hospitality page no longer links the dead page {dead}")

status, caviar, _ = fetch(CAVIAR)
check(status == 200, f"caviar page {CAVIAR} is reachable (http {status})")
for amount in ("R4,200", "R2,800", "R1,600", "R34,000", "R22,000", "R12,500"):
    check(money(caviar, amount), f"caviar page still shows {amount}")
check("per 100g" in caviar, "caviar page still states the per 100g unit")

# 3 ------------------------------------------------- the guard must check the
#                                                     pages that are actually live
guard = open(GUARD, encoding="utf-8").read()
check(SA_HOSP in guard, f"price-ladder guard checks the live SA-hospitality page ({SA_HOSP})")
check(RETAIL in guard, f"price-ladder guard checks the live retail page ({RETAIL})")
guard_slugs = set(re.findall(r'"([a-z0-9]{12})":', guard))
for old in RETIRED:
    check(old not in guard_slugs,
          f"price-ladder guard no longer checks the retired slug {old}")

print(f"ladder-lock regression test: {checks - len(fails)}/{checks} assertions passed")
for f in fails:
    print("  FAIL:", f)
sys.exit(1 if fails else 0)
