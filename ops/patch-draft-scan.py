"""Patch ops/drift-check.py to scan outbound email drafts.

The drafts in outbound-drafts/ are email copy that goes out of a REAL Studex
inbox to REAL external partners. That makes them exactly as public as a landing
page -- but until now NO checker scanned them. The checker only covered the
files it happened to know about (pages + warmup engines + CIIE copy).

A checker only covers the files it scans. This adds the missing scan.

Rules applied to drafts:
  1. The same FORBIDDEN / WARMUP_FORBIDDEN claim rules as every other channel.
  2. No SUPERSEDED URL -- the registry lists URLs that still serve old copy.
  3. Every mcode.io URL in a draft must be a CURRENT canonical URL.
  4. Every price mentioned must exist in the registry.

Applied to the draft BODY only (the fenced block that would actually be sent),
not the surrounding notes -- the notes legitimately quote forbidden strings to
explain what is wrong with them.
"""
import re

P = "ops/drift-check.py"
src = open(P, encoding="utf8").read()
orig = src

# ---------------------------------------------------------------- 1. helpers
helper = '''
# ---------------------------------------------------------------- outbound drafts
# An email draft goes out of a REAL Studex inbox to a REAL external partner,
# so a false claim in one is as public as a false claim on a landing page.
# Until now the checker only covered the files it happened to know about.
DRAFT_DIR = "outbound-drafts"

# The URL bodies that are still live but serve OLD copy (registry section 4
# superseded table). Sharing one of these republishes a corrected-away claim.
SUPERSEDED_URLS = [
    "hrji88f70666", "x2tvaieb5qgz", "z7p9urw22jwb", "lyf0l7cahlbd",
    "j439h3l2g94g", "llox95u1dtfg", "klre58fvhmdc", "tex91uns0obh",
    "8fk34ak7bp5o", "fa4xt0vnu67u", "nhlcdtr7ritv", "6hchke5o5dui",
    "fu8qyf0qg18j", "9xms7l52m71c", "y0r9ilfj96mj", "suzfmm8at06c",
    "ddnave0dco76", "gr1swkg77b8o", "1poi6r0sw6a1", "f4345txsmlkw",
    "0osny82hcvj4", "2eumijearf87", "fprncut7na9x", "jy13ixd8o4sl",
    "nzj87hus15vc",
]

# Canonical live URLs (registry section 4 page -> source -> URL table).
CANONICAL_URLS = [
    "nudsduvyrc12", "hhsmhunf1xci", "oi28dhtke3yk", "ess0ocgcd9f0",
    "de6xdoikz95g", "psq9xaisb9kf", "fr7m7fzyailo", "4mak476g6rmo",
    "3zryumjeuemk",
]


def draft_body(text):
    """Return the fenced block that would actually be sent.

    The notes around a draft deliberately quote forbidden strings to explain
    what is wrong with them, so scanning the whole file would false-positive
    on its own documentation.
    """
    m = re.search(r"```[a-zA-Z]*\\n(.*?)```", text, re.S)
    return m.group(1) if m else ""


def scan_outbound_drafts():
    """Check outbound email drafts against the same rules as every page."""
    issues = []
    ddir = os.path.join(ROOT, DRAFT_DIR)
    if not os.path.isdir(ddir):
        return {"name": "Outbound email drafts", "url": "(local files)",
                "state": "CLEAN", "detail": "no drafts directory", "issues": []}

    names = sorted(n for n in os.listdir(ddir) if n.endswith(".md"))
    reg = ""
    if os.path.exists(REGISTRY):
        reg = open(REGISTRY, encoding="utf-8", errors="ignore").read()

    n_bodies = 0
    for name in names:
        rel = f"{DRAFT_DIR}/{name}"
        full = os.path.join(ddir, name)
        text = open(full, encoding="utf-8", errors="ignore").read()
        body = draft_body(text)
        if not body:
            issues.append(f"{rel} — no fenced draft body found; the body that would be "
                          "sent is UNCHECKED")
            continue
        n_bodies += 1

        for pat, label in FORBIDDEN + WARMUP_FORBIDDEN:
            for m in re.finditer(pat, body, flags=re.I):
                issues.append(f"{rel} — {label}: {m.group(0)!r}")

        for slug in SUPERSEDED_URLS:
            if slug in body:
                issues.append(f"{rel} — shares a SUPERSEDED URL ({slug}); it still serves "
                              "the old copy. Use the canonical URL.")

        for m in re.finditer(r"https?://([a-z0-9]+)\\.space\\.mcode\\.io", body, re.I):
            slug = m.group(1)
            if slug not in CANONICAL_URLS:
                issues.append(f"{rel} — non-canonical URL slug {slug!r}; it is not a current "
                              "canonical page. Check the registry section 4 table.")

        # Every price in the body must exist in the registry. Normalise the
        # thousands separator so "R1,050" is matched against "R1050".
        if reg:
            reg_flat = reg.replace(",", "")
            for m in re.finditer(r"\\b(?:R|USD)\\s?([0-9]+(?:\\.[0-9]+)?)", body, re.I):
                amt = m.group(1)
                if amt not in reg_flat:
                    issues.append(f"{rel} — price {m.group(0)!r} does not appear in the "
                                  "registry; verify it before sending")

    return {
        "name": "Outbound email drafts",
        "url": "(local files)",
        "state": "DRIFT" if issues else "CLEAN",
        "detail": f"{n_bodies}/{len(names)} draft bodies scanned",
        "issues": issues,
    }


'''

anchor = "def scan_local_assets():"
assert anchor in src, "scan_local_assets() not found"
src = src.replace(anchor, helper.lstrip("\n") + anchor, 1)

# ---------------------------------------------------------------- 2. wire in
old = "    results.extend(scan_local_assets())"
new = ("    results.extend(scan_local_assets())\n"
       "    results.append(scan_outbound_drafts())")
assert old in src, "main() call site not found"
src = src.replace(old, new, 1)

assert "def scan_outbound_drafts():" in src
assert "results.append(scan_outbound_drafts())" in src
assert src != orig

open(P, "w", encoding="utf8").write(src)
print("patched drift-check.py |", len(orig), "->", len(src))
