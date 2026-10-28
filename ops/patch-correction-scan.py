"""Extend ops/drift-check.py to scan the outbound-corrections/ directory.

A correction note is an outbound email like any other — it goes to real external
buyers. It carries a specific new risk: to correct a false claim you must
QUOTE it, so a naive forbidden-string scan would either flag every correction
or force the writer to paraphrase the error into vagueness.

The rules that matter for a correction note:
  1. The forbidden claim must not be asserted. It may only appear inside a
     quotation of what we previously said. So each occurrence must be within a
     quoted/reported context.
  2. Every corrected price must be registry-owned (per MT, not per kg).
  3. No superseded URL, only canonical URLs.
  4. It must explicitly withdraw the old claims, not silently omit them.
  5. The recipient list must cover EVERY address that received the bad copy -
     including the ones absent from prospects.json.
"""
import json, re

P = "ops/drift-check.py"
src = open(P, encoding="utf8").read()
orig = src

helper = '''
# ---------------------------------------------------------------- outbound corrections
# A correction note goes to real external buyers too. The distinctive risk: to
# correct a false claim you must QUOTE it. So instead of banning the string, we
# require that every occurrence sits in a quoted / reported context - i.e. we are
# talking ABOUT what we said, not asserting it again.
CORRECTION_DIR = "outbound-corrections"
CORRECTION_RECIPIENTS = "outbound-corrections/ciie-correction-recipients.json"

# The exact false claims that went out. In a correction these may only appear
# inside a quotation - e.g. I wrote "PROWTC certified" - never as a fresh claim.
RETRACTED_CLAIMS = [
    r"PROWTC",
    r"Rainforest\\s*Alliance",
    r"USD\\s*4\\.60\\s*/\\s*kg",
    r"USD\\s*5\\.50\\s*/\\s*kg",
    r"halal[- ]slaughter\\s+available",
    r"cleared import channels",
    r"bilateral agricultural protocol",
]

# Context markers that indicate the claim is being QUOTED or withdrawn.
QUOTED_CONTEXT = re.compile(
    r"(i wrote|i said|we wrote|we said|i stated|i mentioned|i described|"
    r"earlier email|previous email|previous note|earlier note|that was|"
    r"was wrong|was an error|incorrect|withdraw|i withdraw|apolog|"
    r"not ours|should not have|unverified|cannot evidence|do not hold|"
    r"should have|instead of|\\"[^\\"]*\\"|'[^']*')",
    re.I,
)


def scan_outbound_corrections():
    """Check correction notes: quoted claims only, registry prices, full coverage."""
    issues = []
    cdir = os.path.join(ROOT, CORRECTION_DIR)
    if not os.path.isdir(cdir):
        return {"name": "Outbound correction notes", "url": "(local files)",
                "state": "CLEAN", "detail": "no corrections directory", "issues": []}

    reg = ""
    if os.path.exists(REGISTRY):
        reg = open(REGISTRY, encoding="utf-8", errors="ignore").read()
    reg_flat = reg.replace(",", "")

    notes = sorted(n for n in os.listdir(cdir) if n.endswith(".md"))
    n_checked = 0

    for name in notes:
        rel = f"{CORRECTION_DIR}/{name}"
        text = open(os.path.join(cdir, name), encoding="utf-8", errors="ignore").read()
        body = draft_body(text)
        if not body:
            issues.append(f"{rel} - no fenced body found; the text that would be sent is UNCHECKED")
            continue
        n_checked += 1

        # 1. every retracted claim must be in a quoted / withdrawal context
        for pat in RETRACTED_CLAIMS:
            for m in re.finditer(pat, body, flags=re.I):
                start = max(0, m.start() - 260)
                window = body[start:m.end() + 120]
                if not QUOTED_CONTEXT.search(window):
                    issues.append(
                        f"{rel} - retracted claim {m.group(0)!r} appears OUTSIDE a quoted or "
                        "withdrawal context; a correction must report the claim, not re-assert it")

        # 2. prices must exist in the registry
        if reg_flat:
            for m in re.finditer(r"\\b(?:R|USD)\\s?([0-9][0-9,]*(?:\\.[0-9]+)?)", body, re.I):
                amt = m.group(1).replace(",", "")
                if amt not in reg_flat:
                    issues.append(f"{rel} - price {m.group(0)!r} does not appear in the registry; "
                                  "verify it before sending")

        # 3. URL rules
        for slug in SUPERSEDED_URLS:
            if slug in body:
                issues.append(f"{rel} - shares a SUPERSEDED URL ({slug}); use the canonical URL")
        for m in re.finditer(r"https?://([a-z0-9]+)\\.space\\.mcode\\.io", body, re.I):
            if m.group(1) not in CANONICAL_URLS:
                issues.append(f"{rel} - non-canonical URL slug {m.group(1)!r}")

        # 4. it must explicitly withdraw, not just omit
        if not re.search(r"(wrong|incorrect|error|withdraw|apolog)", body, re.I):
            issues.append(f"{rel} - does not explicitly withdraw the earlier claims; a correction "
                          "that silently omits them leaves the false impression standing")

    # 5. recipient coverage: every address that received the bad copy must be listed
    rpath = os.path.join(ROOT, CORRECTION_RECIPIENTS)
    if os.path.exists(rpath):
        data = json.load(open(rpath, encoding="utf-8"))
        listed = {r["email"].lower() for r in data.get("recipients", [])}
        # the authoritative source: AgentMail-verified list in the same file
        for r in data.get("recipients", []):
            if not r.get("inProspectsJson") and not r.get("inDataStateJson"):
                issues.append(f"{CORRECTION_RECIPIENTS} - {r.get('email')} is in neither lead store; "
                              "confirm it was really contacted before sending")
        if data.get("totalRecipients") and data["totalRecipients"] != len(listed):
            issues.append(f"{CORRECTION_RECIPIENTS} - totalRecipients={data['totalRecipients']} but "
                          f"{len(listed)} listed")
        # the 3 named leads are the ones a prospects.json-only list would miss
        if not any(not r.get("inProspectsJson") for r in data.get("recipients", [])):
            issues.append(f"{CORRECTION_RECIPIENTS} - no recipient outside prospects.json is listed; "
                          "the named leads in data/state.json are the ones that get missed")
    else:
        issues.append(f"{CORRECTION_RECIPIENTS} - MISSING; the correction recipient list must be "
                      "machine-readable so it cannot be built from a partial source")

    return {
        "name": "Outbound correction notes",
        "url": "(local files)",
        "state": "DRIFT" if issues else "CLEAN",
        "detail": f"{n_checked}/{len(notes)} correction bodies scanned",
        "issues": issues,
    }


'''

anchor = "def scan_outbound_drafts():"
assert anchor in src, "scan_outbound_drafts() not found"
src = src.replace(anchor, helper.lstrip("\n") + anchor, 1)

old = "    results.append(scan_outbound_drafts())"
new = ("    results.append(scan_outbound_drafts())\n"
       "    results.append(scan_outbound_corrections())")
assert old in src, "call site not found"
src = src.replace(old, new, 1)

assert "def scan_outbound_corrections():" in src
assert "results.append(scan_outbound_corrections())" in src
assert src != orig
open(P, "w", encoding="utf8").write(src)
print("patched drift-check.py |", len(orig), "->", len(src))
