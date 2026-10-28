#!/usr/bin/env python3
"""ops/check-cost-model-exposure.py - catch a PUBLIC page that leaks our cost model.

WHY THIS EXISTS
  On 2026-10-24 the caviar trade desk was found live on a public URL, rendering our farm-gate
  cost, our landed cost, our minimum viable price and our trade prices, with a banner calling our
  own prices a "pricing defect". It was OUTSIDE the price registry, so the drift checker - which
  compares a live page against its owning source - could never see it. A source-vs-live diff would
  also have given the wrong remedy: "redeploy this app" would have RE-PUBLISHED the model.

  So this asks a different question with a different answer:
      Q1 (drift-check):  does the live page match its owning source?   remedy: redeploy
      Q2 (this checker):  does a public page publish our unit economics? remedy: DELETE

GRAMMAR
  A page is EXPOSED when any token below appears in its served HTML **or in any of its JavaScript
  bundles**. A Vite SPA puts ALL of its content in the bundle - the HTML shell can be ~150
  characters - so a checker that only reads the HTML asserts nothing and calls it CLEAN.
  Matching is case-insensitive. The token list is fixed here, not in the caller.

EXIT CODES
  0 = CLEAN      no exposed page
  1 = EXPOSED    a listed page still publishes cost-model content
  2 = UNCHECKED  no input / empty list / unreadable page -> NOT "clean"

ENVIRONMENT
  COST_MODEL_CHECK_PAGES  comma-separated URLs to check (overrides the list file; used by the test)
  COST_MODEL_CHECK_LIST   path to the list file (default ops/exposed-pages.txt)
"""
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST_ENV = os.environ.get("COST_MODEL_CHECK_LIST") or str(ROOT / "ops" / "exposed-pages.txt")

# Tokens that must never appear on a public surface. These are MODEL KEYS and
# labels, not prose - "landed cost" is deliberately absent because the canonical
# caviar page legitimately says "duty and VAT quoted in the landed cost".
TOKENS = [
    "farm gate", "margin floor", "belowfloor", "landedzarperkg", "floorzarperkg",
    "farmgateusdperkg", "fximpact", "marginpct", "specialty_discount",
    "fxusdzar", "vatrate", "dutyrate",
]

BUNDLE_RE = re.compile(r"""(?:src|href)=["']([^"']+\.js[^"']*)["']""")


def fetch(url, timeout=25):
    try:
        if url.startswith("file://"):
            return Path(url[len("file://"):]).read_text(encoding="utf-8", errors="ignore")
        req = urllib.request.Request(url, headers={"User-Agent": "exposure-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError:
        return ""
    except Exception:
        return ""


def load_pages():
    override = os.environ.get("COST_MODEL_CHECK_PAGES")
    # An override that is set but EMPTY means "check nothing" -> UNCHECKED, not
    # "fall back to the list file". Otherwise a caller that clears the list
    # silently checks the real pages instead and reports on them.
    if override is not None:
        return [u.strip() for u in override.split(",") if u.strip()]
    p = Path(LIST_ENV)
    if not p.exists():
        return None
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug = line.split("\t")[0].split()[0]
        if "." in slug and "://" not in slug:
            out.append("https://" + slug)
        else:
            out.append(slug)
    return out


def scan(url):
    html = fetch(url)
    if not html:
        return None, []
    blobs = {"html": html}
    base = url.rsplit("/", 1)[0] + "/"
    for m in BUNDLE_RE.finditer(html):
        b = m.group(1)
        if b.startswith("/"):
            b = ("file://" + b) if url.startswith("file://") else (url.split("/")[0] + "//" + url.split("/")[2] + b)
        elif not b.startswith("http") and not b.startswith("file://"):
            b = base + b
        body = fetch(b)
        if body:
            blobs[b] = body
    low = {k: v.lower() for k, v in blobs.items()}
    hits = []
    for tok in TOKENS:
        for where, body in low.items():
            if re.search(r"\b" + re.escape(tok) + r"\b", body):
                hits.append((tok, where))
    return True, hits


def main():
    pages = load_pages()
    if pages is None:
        print("UNCHECKED - no page list at %s" % LIST_ENV)
        return 2
    if not pages:
        print("UNCHECKED - the page list is empty; nothing was checked")
        return 2
    exposed = []
    unchecked = []
    for url in pages:
        ok, hits = scan(url)
        if ok is None:
            unchecked.append(url)
            print("  UNREACHABLE  %s" % url)
            continue
        if hits:
            toks = sorted({t for t, _ in hits})
            print("  EXPOSED     %s" % url)
            print("               publishes: %s" % ", ".join(toks))
            exposed.append((url, toks))
        else:
            print("  CLEAN       %s" % url)
    if unchecked:
        print("UNCHECKED - %d page(s) could not be read" % len(unchecked))
        return 2
    if exposed:
        print("")
        print("EXPOSURE DETECTED - a live public page publishes our cost model.")
        print("The remedy is DELETION, not a redeploy: redeploying would re-publish it.")
        for url, toks in exposed:
            print("  %s -> %s" % (url, ", ".join(toks)))
        return 1
    print("CLEAN - %d exposed-page(s) checked, none publishes cost-model content" % len(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
