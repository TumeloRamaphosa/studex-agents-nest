#!/usr/bin/env python3
"""Extend the drift checker so client-rendered pages are ACTUALLY checked.

THE GAP THIS CLOSES
--------------------
A React SPA returns ~150 visible characters of HTML shell, so a text assertion
against the fetched page proves nothing. The four React landing pages therefore
had ZERO assertions - the checker reported them "UNCHECKED" - and while nothing
watched them, two of them went on publishing claims the registry forbids:

  china-coffee-lead-capture  "Rainforest Alliance certified" + "Direct Trade
                             Origin" + mailto:ceo@agent.studexmeat.com (no DNS)
  studex-caviar              "certified Russian caviar houses" + "ethically sourced"

Both are live, and the China one is China-facing.

THE FIX
-------
For an SPA the artefact that IS the page is its built bundle, so:
  1. the bundle is what gets asserted (must / must_not / must_href), and
  2. the live site must be proven to be serving THAT build - if the live HTML
     does not reference the current local asset filename, the site is still
     serving an older bundle and the fix has not reached the world. That is
     reported as STALE BUILD, not as a silent pass.

`check_spa(page, html, dist)` is deliberately pure so it can be negative-tested
without touching the network.
"""
import json, os, pathlib, re, sys

ROOT = "/workspace"
REG = pathlib.Path("/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md")
DRIFT = pathlib.Path("/workspace/ops/drift-check.py")
MANIFEST_BUILDER = pathlib.Path("/workspace/ops/build-manifest.py")

# ---------------------------------------------------------------- 1. build-manifest.py
old_pm = '''            slug = m.group(1)
            url_by_id[slug] = f"https://{slug}.space.mcode.io"
            name_by_id[slug] = c[0].strip()'''
new_pm = '''            slug = m.group(1)
            url_by_id[slug] = f"https://{slug}.space.mcode.io"
            name_by_id[slug] = c[0].strip()
            # The source dir tells us WHAT KIND of artefact the page is. A React
            # app serves a client-rendered shell, so its content lives in the
            # built bundle - the checker has to know that, or it will assert
            # against 150 characters of shell and call it a pass.
            if len(c) >= 3:
                src_by_id[slug] = c[1].strip().strip("`").rstrip("/")'''
assert old_pm in MANIFEST_BUILDER.read_text(encoding="utf8")
t = MANIFEST_BUILDER.read_text(encoding="utf8")
t = t.replace(old_pm, new_pm, 1)
t = t.replace("    url_by_id, name_by_id = {}, {}",
              "    url_by_id, name_by_id, src_by_id = {}, {}, {}", 1)
t = t.replace("""    return (url_by_id, name_by_id, prices_by_id, facts_by_id, links_by_id,
            forbidden_by_id)""",
              """    return (url_by_id, name_by_id, src_by_id, prices_by_id, facts_by_id,
            links_by_id, forbidden_by_id)""", 1)
t = t.replace("""    (url_by_id, name_by_id, prices_by_id, facts_by_id, links_by_id,
     forbidden_by_id) = parse_registry()""",
              """    (url_by_id, name_by_id, src_by_id, prices_by_id, facts_by_id,
     links_by_id, forbidden_by_id) = parse_registry()""", 1)
old_page = """        pages.append({
            "name": name_by_id.get(slug, prev.get("name", slug)),
            "url": url_by_id[slug],
            "must": must,
            "must_href": href,
            "must_not": nots,
        })"""
new_page = """        # Is this page a client-rendered SPA? If its source dir ships a hashed
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
        })"""
assert old_page in t
t = t.replace(old_page, new_page, 1)
MANIFEST_BUILDER.write_text(t, encoding="utf8")
print("patched ops/build-manifest.py  (source dir + spa flag)")

# ---------------------------------------------------------------- 2. drift-check.py
d = DRIFT.read_text(encoding="utf8")

SPA_FUNC = '''
# ---------------------------------------------------------------- SPA bundles
# A client-rendered React page returns ~150 visible characters of HTML shell.
# Asserting against that proves nothing, so these pages ended up with zero
# assertions - the checker called them UNCHECKED, and while nothing was
# watching them two of them published claims the registry forbids
# ("Rainforest Alliance certified" on the China page, "certified Russian caviar
# houses" on the caviar page). Both were live.
#
# For an SPA the artefact that IS the page is its built bundle. So the bundle
# is what gets asserted, and the live site must be PROVEN to be serving that
# build: if the live HTML does not reference the current local asset filename,
# the site is still serving an older bundle and the fix has not reached the
# world. That is reported as STALE BUILD, never as a silent pass.
def check_spa(page, html, dist=None):
    src = page.get("source") or ""
    dist = dist or os.path.join(ROOT, src)
    issues = []
    text = ""
    n_files = 0
    if os.path.isdir(dist):
        for dp, dn, fn in os.walk(dist):
            dn[:] = [d for d in dn if d not in ("node_modules", ".git")]
            for f in fn:
                if f.endswith((".js", ".html", ".css", ".json")):
                    n_files += 1
                    with open(os.path.join(dp, f), encoding="utf-8", errors="ignore") as fh:
                        text += fh.read() + "\\n"
    else:
        issues.append("source dir %r not found - there is nothing to assert against" % src)
    n = norm(text)
    for s in page.get("must", []):
        if norm(s) not in n:
            issues.append("MISSING: " + s)
    for s in page.get("must_not", []):
        if norm(s) in n:
            issues.append("FORBIDDEN PRESENT: " + s)
    for s in page.get("must_href", []):
        if norm(s) not in n:
            issues.append("MISSING LINK: " + s)
    n_assert = len(page.get("must", [])) + len(page.get("must_not", [])) + len(page.get("must_href", []))
    if n_assert == 0:
        issues.append("NO ASSERTIONS - this page is UNCHECKED (registry slug no longer resolves)")
    local_assets = set()
    adir = os.path.join(dist, "assets")
    if os.path.isdir(adir):
        local_assets = {f for f in os.listdir(adir) if f.endswith((".js", ".css"))}
    live_assets = set(re.findall(r"assets/([A-Za-z0-9_.\\-]+)", html or ""))
    stale = sorted(a for a in local_assets if a not in live_assets)
    if local_assets and stale:
        issues.append("STALE BUILD - the live site is not serving the current bundle (%s "
                      "is missing from the live HTML), so the local fix has NOT reached the "
                      "world. Redeploy this app." % stale[0])
    state = "DRIFT" if issues else "CLEAN"
    return {"name": page["name"], "url": page["url"], "state": state,
            "detail": "%d bundle file(s) - %d assertion(s) - %s"
                      % (n_files, n_assert,
                         "live serves this build" if (local_assets and not stale) else "bundle"),
            "issues": issues}

'''
d = d.replace("# ---------------------------------------------------------------- check\ndef check(page):",
              SPA_FUNC + "\n# ---------------------------------------------------------------- check\ndef check(page):", 1)
old_check = """    text = visible(html)
    n = norm(text)
    issues = []"""
new_check = """    if page.get("spa"):
        return check_spa(page, html)
    text = visible(html)
    n = norm(text)
    issues = []"""
assert old_check in d
d = d.replace(old_check, new_check, 1)
DRIFT.write_text(d, encoding="utf8")
print("patched ops/drift-check.py  (check_spa + SPA branch)")

# ---------------------------------------------------------------- 3. registry
r = REG.read_text(encoding="utf8")
REG_EDITS = [
    # dead domain: guard every SPA too
    ("| `agent.studexmeat.com` | dead domain, no DNS | `3zryumjeuemk` · `ess0ocgcd9f0` · `nudsduvyrc12` · `4mak476g6rmo` · `de6xdoikz95g` · `oi28dhtke3yk` · `fr7m7fzyailo` · `psq9xaisb9kf` · `hhsmhunf1xci` |",
     "| `agent.studexmeat.com` | dead domain, no DNS | `3zryumjeuemk` · `ess0ocgcd9f0` · `nudsduvyrc12` · `4mak476g6rmo` · `de6xdoikz95g` · `oi28dhtke3yk` · `fr7m7fzyailo` · `psq9xaisb9kf` · `hhsmhunf1xci` · `9yk65ajlg1s9` · `qefqcvvpd8al` · `1bl06cgsu643` · `2hkb7k7q2gni` |"),
    # unsourced RA claim: the China SPA published it while UNCHECKED
    ("| `Rainforest Alliance` | no source document exists for any Studex coffee — claim removed 2026-10-21 | `fr7m7fzyailo` · `de6xdoikz95g` · `psq9xaisb9kf` |",
     "| `Rainforest Alliance` | no source document exists for any Studex coffee — claim removed 2026-10-21 | `fr7m7fzyailo` · `de6xdoikz95g` · `psq9xaisb9kf` · `9yk65ajlg1s9` · `qefqcvvpd8al` · `1bl06cgsu643` · `2hkb7k7q2gni` |"),
]
for old, new in REG_EDITS:
    assert old in r, old[:80]
    r = r.replace(old, new, 1)

# new forbidden rows for the SPA claims that were live and unchecked
anchor = "| `certified Russian caviar houses` | the caviar source page makes no such claim | `nudsduvyrc12` |"
assert anchor in r
r = r.replace(anchor, anchor + """
| `certified Russian caviar houses` | the React caviar page made this claim while UNCHECKED — live 2026-10-23 | `2hkb7k7q2gni` |
| `ethically sourced` | retired unsourced claim (removed from the coffee pages 2026-10-21) | `2hkb7k7q2gni` |
| `Direct Trade` | retired unsourced badge — "single washing station" is the honest line | `1bl06cgsu643` · `9yk65ajlg1s9` · `qefqcvvpd8al` |
| `Tariff-free entry into China from July 20, 2026` | wrong tariff date — the tariff started 1 May 2026; 20 July is the unified phytosanitary system | `1bl06cgsu643` |""", 1)
REG.write_text(r, encoding="utf8")
print("patched studex-meat/PRICE-SOURCE-REGISTRY.md  (SPA slugs now asserted)")
print("\nDone.")
