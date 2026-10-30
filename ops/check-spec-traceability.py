#!/usr/bin/env python3
"""Every numeric QUALITY claim in the content catalog must trace to its owning source.

THE DEFECT (2026-10-30)
-----------------------
The caption machine published "marbling grade 5" about our Wagyu Ribeye
(Threads `8633885`, IG `8634450`). The machine did NOT invent it. It copied the
content catalog's own tagline, which said "Marbling grade 5 Wagyu", while the
owning source (`studex-products-catalog.csv`) says **"marble scores 8+ to 11+"**.

The price guard could never see this. `ops/check-catalog.py` compares the NUMERIC
PRICE against the registry - currency. This checker is about the OTHER kind of
number: a **quality tier**. "Grade 5" is a number, and no source supports it.

A grade claim is supported only when the number appears in the OWNING ROW of
that product (title + variant + description), where the row is found by
maximum token overlap between the content-catalog product name and the owning
source's product title. Corpus-wide matching would NOT do: the owning source
legitimately contains "Marble Score 7/8" (auction lot) and "All 5-7 marble
score" (Wagyu Black Box), so a corpus check would happily wave "grade 5"
through for a product that says 8+ to 11+.

EXIT CODES (the registry contract is clean=0, finding=1, could-not-prove=2):
  0  every claim traces to its owning source
  1  a claim does not trace, or a publishable product has no owning row
  2  the owning source or the catalog could not be read - nothing was proved
"""
import csv
import json
import os
import re
import sys

ROOT = "/workspace"
OWNING_CSV = os.path.join(ROOT, "studex-products-catalog.csv")
CATALOG = os.path.join(ROOT, "studex-content-automation", "products", "catalog.json")

# Words that carry no identifying weight when matching a product to its row.
STOP = {"our", "the", "and", "of", "a", "in", "with", "for", "to", "is", "on"}

# A quality-tier claim: marbling/marble + grade/score, or a bare "grade N".
CLAIM_TRIGGER = re.compile(r"(?:marbling|marble|grades?|scores?)[^.;]{0,28}", re.I)
# A number, not part of a price and not glued to a letter (so "A1" and "R950"
# are not numbers we can check).
NUMBER = re.compile(r"(?<![\w.])(\d+)")
PRICE = re.compile(r"\bR\s?[\d,]+(?:\.\d+)?\b")

# Columns of the owning source that carry SPEC text (never the price columns -
# prices are owned by ops/check-catalog.py, and letting a price satisfy a grade
# claim would be exactly the false green this checker exists to prevent).
TITLE_COL, VARIANT_COL, DESCRIPTION_COL = 0, 3, 7


def words(text):
    return {w for w in re.findall(r"[a-z]+", (text or "").lower())
            if w not in STOP and len(w) > 2}


def numbers_in(text):
    """Standalone numbers in a piece of spec text, with prices removed."""
    return set(NUMBER.findall(PRICE.sub(" ", text or "")))


def claims_in(text):
    """[(claimed_numbers, claim_text)] for every quality-tier claim in the text."""
    out = []
    for m in CLAIM_TRIGGER.finditer(text or ""):
        window = m.group(0)
        nums = numbers_in(window)
        if nums:
            out.append((sorted(nums, key=int), window.strip()))
    return out


def owning_rows(catalog_name):
    """The owning source row(s) for a product, by maximum token overlap."""
    tokens = words(catalog_name)
    best = 0
    picked = []
    with open(OWNING_CSV, newline="", encoding="utf8") as fh:
        for row in csv.reader(fh):
            if len(row) <= DESCRIPTION_COL:
                continue
            overlap = len(tokens & words(row[TITLE_COL]))
            if overlap > best:
                best, picked = overlap, [row]
            elif overlap == best and overlap:
                picked.append(row)
    if best < 2:
        return [], 0
    return picked, best


def main(argv):
    catalog_path = CATALOG
    if "--catalog" in argv:
        i = argv.index("--catalog")
        if i + 1 < len(argv):
            catalog_path = argv[i + 1]
    owning_path = OWNING_CSV
    if "--owning" in argv:
        i = argv.index("--owning")
        if i + 1 < len(argv):
            owning_path = argv[i + 1]

    try:
        cat = json.load(open(catalog_path, encoding="utf8"))
    except Exception as exc:
        print("spec-traceability: cannot read the content catalog (%s)" % exc)
        return 2
    try:
        with open(owning_path, newline="", encoding="utf8") as fh:
            if not fh.readline():
                return 2
    except Exception as exc:
        print("spec-traceability: cannot read the owning source (%s)" % exc)
        return 2

    products = cat.get("products", cat if isinstance(cat, list) else [])
    findings = []
    checked = 0
    for prod in products:
        pid = prod.get("id", "?")
        if not prod.get("available", True):
            print("  %-24s skipped - not available for the feed (not published)"
                  % pid)
            continue
        rows, overlap = owning_rows(prod.get("name", ""))
        if not rows:
            findings.append(
                "  %s: NO OWNING SOURCE ROW for %r - this product is publishable "
                "but its claims cannot be traced to %s"
                % (pid, prod.get("name"), os.path.basename(owning_path)))
            continue
        allowed = set()
        for row in rows:
            allowed |= numbers_in(" ".join([row[TITLE_COL], row[VARIANT_COL],
                                            row[DESCRIPTION_COL]]))
        checked += 1
        print("  %-24s owning row: %s  (token overlap %d, spec numbers %s)"
              % (pid, rows[0][TITLE_COL][:40], overlap,
                 ",".join(sorted(allowed, key=int))))
        for field in ("tagline", "description"):
            text = prod.get(field) or ""
            for nums, claim in claims_in(text):
                unsupported = [n for n in nums if n not in allowed]
                if unsupported:
                    findings.append(
                        "  %s: the %s claims %r (%s) but the owning source says "
                        "%s - %s not supported"
                        % (pid, field, claim, ",".join(nums),
                           rows[0][TITLE_COL], ",".join(unsupported)))
                else:
                    print("      %-11s %r -> traced (%s)"
                          % (field, claim[:44], ",".join(nums)))

    print("")
    if findings:
        print("SPEC TRACEABILITY - %d UNTRACED CLAIM(S):" % len(findings))
        for f in findings:
            print(f)
        print("VERDICT: an unsourced quality claim reached the content catalog - "
              "it will be published. Fix the catalog to match the owning source.")
        return 1
    print("VERDICT: OK - %d publishable product(s), every quality claim traced to "
          "its owning source row." % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
