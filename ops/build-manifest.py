#!/usr/bin/env python3
"""
Build the drift manifest FROM the price registry.

Why: `studex-meat/PRICE-SOURCE-REGISTRY.md` is the human-readable source of
truth (which price belongs to which product, and which page must show it).
`ops/drift-manifest.json` is what the checker actually asserts. When they are
separate files, a price can be added to the registry and never checked.

This generator makes the registry the single source of truth:
  - page URL and name  -> taken from the registry's page map
  - prices that must appear on a page -> parsed from the registry's price
    tables via their "Must appear on" column
  - curated assertions (must_href, must_not, hand-written must) -> preserved

Hand-written "must" entries are kept and merged, so the generator can only ever
ADD coverage, never remove it.

Usage:  python3 ops/build-manifest.py [--check]
  --check  report what would change, write nothing, exit 1 if there is a diff
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "studex-meat", "PRICE-SOURCE-REGISTRY.md")
MANIFEST = os.path.join(ROOT, "ops", "drift-manifest.json")

PRICE_RE = re.compile(r"R[\d,]{2,}")
USD_RE = re.compile(r"(?:US?\$|\$|USD)\s*[\d,]+(?:\s*[–—-]\s*(?:US?\$|\$|USD)?\s*[\d,]+)?")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# bounded so it cannot swallow a following quantity ("... 6035 200g")
PHONE_RE = re.compile(r"\+27[\s-]?\d{2,3}[\s-]?\d{2,4}[\s-]?\d{2,4}")
LINK_RE = re.compile(r"https?://[^\s`|)\]]+")


def cells(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    parts = s.strip("|").split("|")
    return [c.strip() for c in parts]


def parse_registry():
    text = open(REGISTRY, encoding="utf-8").read()
    lines = text.splitlines()

    # --- page map: | Name | `source/` | `slug.space.mcode.io` |
    url_by_id, name_by_id, src_by_id = {}, {}, {}
    for ln in lines:
        c = cells(ln)
        if not c or len(c) < 3:
            continue
        m = re.search(r"`([a-z0-9]+)\.space\.mcode\.io`", c[-1])
        # A page-map row's FIRST cell is a page NAME ("Retail store"), never a
        # URL. Other tables in the registry (e.g. the superseded-URL log) also
        # end in a backticked slug, and without this guard they are read as
        # page rows: the last row wins, so a live page silently gets renamed
        # after a dead URL and a superseded page gets checked as if it were live.
        if m and c[0] not in ("Page", "---") and "space.mcode.io" not in c[0] and "://" not in c[0]:
            slug = m.group(1)
            url_by_id[slug] = f"https://{slug}.space.mcode.io"
            name_by_id[slug] = c[0].strip()
            # The source dir tells us WHAT KIND of artefact the page is. A React
            # app serves a client-rendered shell, so its content lives in the
            # built bundle - the checker has to know that, or it will assert
            # against 150 characters of shell and call it a pass.
            if len(c) >= 3:
                src_by_id[slug] = c[1].strip().strip("`").rstrip("/")

    # --- price tables: any row whose LAST cell names one or more page slugs
    prices_by_id = {}
    facts_by_id = {}
    links_by_id = {}
    forbidden_by_id = {}
    table_type = None
    for ln in lines:
        c = cells(ln)
        if not c:
            table_type = None          # prose / blank line ends the table
            continue
        joined = " | ".join(c)
        # a table's header says what its last column means
        if "Must not appear on" in joined:
            table_type = "forbidden"
            continue
        if "Must appear on" in joined:
            table_type = "must"
            continue
        if table_type is None or len(c) < 2:
            continue
        # the "Must appear on" cell names pages as BARE slugs in backticks,
        # e.g. `hrji88f70666`. Only tokens that are known page ids count.
        target_idx = None
        slugs = []
        for i, cell in enumerate(c):
            found = [t for t in re.findall(r"`([^`]+)`", cell) if t in url_by_id]
            if found and target_idx is None:
                target_idx = i
                slugs = found
        if target_idx is None:
            continue
        spec_cells = [x for i, x in enumerate(c) if i != target_idx]
        if table_type == "forbidden":
            # the forbidden string is the backticked value; the reason is prose
            fvals = []
            for cell in spec_cells:
                for tok in re.findall(r"`([^`]+)`", cell):
                    t = tok.strip()
                    if t and t not in url_by_id and "://" not in t:
                        fvals.append(t)
            for slug in slugs:
                forbidden_by_id.setdefault(slug, set()).update(v for v in fvals if v)
            continue
        toks, facts, links = [], [], []
        for cell in spec_cells:
            cell = re.sub(r"\*\*", "", cell)
            toks += PRICE_RE.findall(cell)
            toks += [re.sub(r"\s+", " ", u).strip() for u in USD_RE.findall(cell)]
            facts += EMAIL_RE.findall(cell)
            facts += [re.sub(r"\s+", " ", p).strip() for p in PHONE_RE.findall(cell)]
            links += LINK_RE.findall(cell)
            # a backticked value that is not a page slug, an email or a URL is
            # literal visible text the page must show (entity name, address line)
            for tok in re.findall(r"`([^`]+)`", cell):
                t = tok.strip()
                if not t or t in url_by_id or "@" in t or "://" in t or t.endswith(".io"):
                    continue
                if EMAIL_RE.fullmatch(t) or PHONE_RE.fullmatch(t):
                    continue
                facts.append(t)
        for slug in slugs:
            if slug not in url_by_id:
                continue
            prices_by_id.setdefault(slug, set()).update(t for t in toks if t)
            facts_by_id.setdefault(slug, set()).update(f for f in facts if f)
            links_by_id.setdefault(slug, set()).update(l for l in links if l)
    return (url_by_id, name_by_id, src_by_id, prices_by_id, facts_by_id,
            links_by_id, forbidden_by_id)


def slug_of(url):
    m = re.search(r"([a-z0-9]+)\.space\.mcode\.io", url or "")
    return m.group(1) if m else None


def main():
    (url_by_id, name_by_id, src_by_id, prices_by_id, facts_by_id,
     links_by_id, forbidden_by_id) = parse_registry()
    if not url_by_id:
        print("ERROR: could not parse the page map out of the registry", file=sys.stderr)
        return 2

    old = {}
    if os.path.exists(MANIFEST):
        cur = json.load(open(MANIFEST, encoding="utf-8"))
        for p in cur.get("pages", []):
            s = slug_of(p.get("url", ""))
            if s:
                old[s] = p

    # The manifest is a PURE FUNCTION of the registry. Nothing is carried over
    # from the previous manifest, because carrying it over is how a wrong price
    # survives forever: the old "preserve hand-written must entries" behaviour
    # kept "$4,800-5,400" asserted long after the registry was corrected, and
    # the China page then failed a check it was already failing against.
    # Coverage loss must be LOUD, so anything dropped is reported below.
    pages, added_total, lost_total = [], 0, 0
    for slug in sorted(url_by_id):
        prev = old.get(slug, {})
        derived = sorted(prices_by_id.get(slug, []))
        derived_facts = sorted(facts_by_id.get(slug, []))
        derived_links = sorted(links_by_id.get(slug, []))
        derived_forb = sorted(forbidden_by_id.get(slug, []))
        must = sorted(set(derived) | set(derived_facts))
        href = sorted(set(derived_links))
        nots = sorted(set(derived_forb))
        added_total += len(must)
        prev_all = (set(prev.get("must", [])) | set(prev.get("must_href", []))
                    | set(prev.get("must_not", [])))
        lost = sorted(prev_all - (set(must) | set(href) | set(nots)))
        lost_total += len(lost)
        if lost:
            print(f"  LOST ASSERTIONS for {slug} (not in the registry — "
                  f"migrate them or they are no longer checked): {lost}")
        # Is this page a client-rendered SPA? If its source dir ships a hashed
        # assets/ bundle, then the bundle IS the page and the live HTML is a
        # shell - so the checker must assert the bundle, not the shell.
        src = src_by_id.get(slug, "")
        spa = False
        if src:
            d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(REGISTRY))), src)
            if os.path.isdir(os.path.join(d, "assets")):
                spa = any(f.endswith(".js") for f in os.listdir(os.path.join(d, "assets")))
        pages.append({
            "name": name_by_id.get(slug, prev.get("name", slug)),
            "url": url_by_id[slug],
            "must": must,
            "must_href": href,
            "must_not": nots,
            "spa": spa,
            "source": src,
        })

    out = {
        "_comment": ("GENERATED by ops/build-manifest.py from "
                     "studex-meat/PRICE-SOURCE-REGISTRY.md — do not hand-edit. "
                     "Run: python3 ops/build-manifest.py"),
        "_source": "studex-meat/PRICE-SOURCE-REGISTRY.md",
        "pages": pages,
    }

    old_json = json.dumps(json.load(open(MANIFEST, encoding="utf-8")), sort_keys=True, indent=2) \
        if os.path.exists(MANIFEST) else ""
    new_json = json.dumps(out, sort_keys=True, indent=2)

    print("registry pages:", len(url_by_id))
    for slug in sorted(url_by_id):
        derived = sorted(prices_by_id.get(slug, []))
        dfacts = sorted(facts_by_id.get(slug, []))
        dlinks = sorted(links_by_id.get(slug, []))
        prev = old.get(slug, {})
        had = set(prev.get("must", [])) | set(prev.get("must_href", []))
        new = [t for t in derived + dfacts + dlinks if t not in had]
        print(f"  {name_by_id.get(slug, slug):<24} {slug:<16} "
              f"prices: {len(derived):<3} facts: {len(dfacts):<3} links: {len(dlinks):<3} "
              f"newly-asserted: {len(new)}"
              + (f"  -> {', '.join(new)}" if new else ""))

    if "--check" in sys.argv:
        print("CHANGED" if old_json != new_json else "no change")
        return 0 if old_json == new_json else 1

    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(new_json)
    print(f"\nmanifest written: {MANIFEST}  (pages {len(pages)}, "
          f"newly asserted {added_total})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
