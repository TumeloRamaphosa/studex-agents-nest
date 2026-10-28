#!/usr/bin/env python3
"""
Studex — Page Drift Checker
===========================
Re-verifies every live customer-facing page against the price/contact facts that
OWN it (see studex-meat/PRICE-SOURCE-REGISTRY.md).

Every real defect found on 2026-10-21 was a page that had drifted from its
source: caviar units, coffee pricing, gifting quoting per-kg meat prices, a dead
contact in 3 email signatures. This catches that class automatically.

READ-ONLY. It fetches pages and compares strings. It never edits, never deploys,
never writes to a live site. Output is a report for a human (or the heartbeat)
to read.

Exit codes:  0 = all clean   1 = drift found   2 = network/other error
"""
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drift-manifest.json")
UA = "Mozilla/5.0 (compatible; StudexDriftCheck/1.0)"

# ---------------------------------------------------------------- normalise
def norm(s: str) -> str:
    """Whitespace-insensitive, dash-insensitive comparison."""
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("\xa0", " ")
    return re.sub(r"\s+", "", s).lower()

# ---------------------------------------------------------------- fetch
def fetch(url: str, timeout: int = 25):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        raw = r.read().decode("utf-8", "ignore")
        return r.status, raw

def visible(html: str) -> str:
    body = re.sub(r"<(script|style|noscript).*?</\1>", " ", html, flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    import html as _h
    return _h.unescape(body)


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
                        text += fh.read() + "\n"
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
    live_assets = set(re.findall(r"assets/([A-Za-z0-9_.\-]+)", html or ""))
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


# ---------------------------------------------------------------- check
def check(page):
    name = page["name"]
    url = page["url"]
    try:
        status, html = fetch(url)
    except Exception as e:
        return {"name": name, "url": url, "state": "UNREACHABLE",
                "detail": f"{type(e).__name__}: {e}", "issues": []}
    if status != 200:
        return {"name": name, "url": url, "state": "HTTP_" + str(status),
                "detail": f"status {status}", "issues": []}
    if page.get("spa"):
        return check_spa(page, html)
    text = visible(html)
    n = norm(text)
    issues = []
    for s in page.get("must", []):
        if norm(s) not in n:
            issues.append("MISSING: " + s)
    for s in page.get("must_not", []):
        if norm(s) in n:
            issues.append("FORBIDDEN PRESENT: " + s)
    for s in page.get("must_href", []):
        if norm(s) not in norm(html):
            issues.append("MISSING LINK: " + s)
    # A page with no assertions is not "clean" — it is UNCHECKED. This bit us
    # on 2026-10-21: a redeploy renamed a page's slug, its price rows stopped
    # resolving, the page ended up with zero assertions, and the checker still
    # reported CLEAN. Silent coverage loss is worse than a red check.
    n_assert = len(page.get("must", [])) + len(page.get("must_not", [])) + len(page.get("must_href", []))
    if n_assert == 0:
        issues.append("NO ASSERTIONS — this page is UNCHECKED (registry slug no longer resolves)")
    state = "DRIFT" if issues else "CLEAN"
    return {"name": name, "url": url, "state": state,
            "detail": f"{len(text)} visible chars · {n_assert} assertions", "issues": issues}

# ---------------------------------------------------------------- local assets
# CIIE booth/hall/stand specifics are unverified and must not reappear in
# outreach copy, landing pages or the seller. No live page carried the claim,
# but four CIIE nurture emails did — so the copy is guarded too.
FORBIDDEN = [
    (r"\bHall\s+\d", "hall number"),
    (r"[Bb]ooth\s+[0-9A-Z]{1,4}-?\d", "booth number"),
    (r"[Ss]tand\s+[0-9A-Z]{1,3}-\d", "stand number"),
    (r"Africa(an)?\s+(Nations\s+)?Pavilion", "pavilion claim"),
    (r"dedicated booth", "booth claim"),
    (r"\$\{lead\.", "unrendered template variable"),
    (r"Rainforest\s+Alliance", "unsourced certification claim"),
    (r"PROWTC\s+cert(ificate)?", "PROWTC is a buyer, not a certifier"),
    (r"(?<!3\.60-)5\.50/kg", "old A2 per-kg price (ours: USD 3,600-4,000/MT)"),
    (r"(?<!4\.20-)4\.80/kg", "old A1 per-kg price (ours: USD 4,200-4,800/MT)"),
    (r"EU and Middle East", "unsupported certification-equivalence claim"),
    (r"53 shipments", "unsourced track-record claim"),
    (r"Every product we produce", "page-level Halaal overclaim"),
    (r"100% Halaal Certified", "page-level Halaal overclaim"),
    (r"Halaal guaranteed", "page-level Halaal overclaim"),
    (r"certified Russian caviar houses", "unsourced caviar claim"),
    (r"certified farms", "unsourced certification claim"),
    (r"MJC Halal Trust", "wrong spelling of the certifier (MJC Halaal Trust)"),
    # Hardcoded status lines in the ops bot. The daily briefing published
    # "Orgo VM 47.236.124.79 ✅" (that IP is the Alibaba Cloud VM, and it is
    # DOWN) and "Shopify 🔴 77+ days dark" (the storefront is live and selling;
    # only the Admin API is dark). Status must be probed, never hardcoded.
    # These are deliberately LITERAL — an earlier loose pattern false-positived
    # on a variable name, which is how a rule teaches people to ignore it.
    (r"Orgo VM \(Alibaba\)", "47.236.124.79 is the Alibaba Cloud VM, not Orgo"),
    (r"Orgo VM 47\.236\.124\.79", "47.236.124.79 is the Alibaba Cloud VM, not Orgo"),
    (r"Shopify:\*\* 🔴 \d+\+ days dark", "storefront is live and selling — only the Admin API is dark"),
    (r"Storefront:\*\* dark", "storefront is live and selling — only the Admin API is dark"),
]
ASSET_PATHS = [
    "ciie-nurture/src/emails.ts", "ciie-nurture/dist/emails.js",
    "ciie-nurture/send-sequence.js", "ciie-nurture/src/cli.ts",
    "ciie-nurture/dist/cli.js", "ciie-buyer-brief/src/App.tsx",
    "ciie-coffee-landing/src/App.tsx", "ciie-bundle-pitch.md",
    "studex-war-room/src/components/CIIEOutreachPanel.tsx",
    "studex-war-room/src/components/ContentHub.tsx",
    "studex-war-room/src/components/CIIEBoothApplication.tsx",
    "studex-biltong/index.html",
    "studex-biltong/product-offer.html",
    "studex-biltong/subscription.html",
    "discord-ops-bot/src/index.js",
    "discord-ops-bot/src/sendSummary.js",
    # The email warmup engines send copy out of REAL Studex inboxes, so their
    # claims are as public as a landing page. They carried the same unverified
    # booth claim and prospect brand that were banned from the pages.
    "studex-email-warmup/index.js",
    "studex-email-warmup/warmup.js",
    "studex-email-warmup/daily-warmup-runner.js",
]
# Files whose copy lives inside template literals: code_only() would blank it,
# so these are scanned RAW. The "${lead." rule is skipped for them — inside a
# backtick it interpolates correctly.
RAW_SCAN = {
    "studex-war-room/src/components/CIIEOutreachPanel.tsx",
    "studex-war-room/src/components/ContentHub.tsx",
    "studex-war-room/src/components/CIIEBoothApplication.tsx",
    # The warmup engines keep their email copy in template literals too, and
    # that copy is what actually goes out.
    "studex-email-warmup/index.js",
    "studex-email-warmup/warmup.js",
    "studex-email-warmup/daily-warmup-runner.js",
}

# The warmup engines have their own copy rules. The registry's page rules do
# not reach them: a warmup email goes out of a REAL Studex inbox, so a false
# claim in it is as public as a false claim on a landing page. These engines
# carried the same unverified booth claim and prospect brand that were banned
# from the pages.
WARMUP_PATHS = {
    "studex-email-warmup/index.js",
    "studex-email-warmup/warmup.js",
    "studex-email-warmup/daily-warmup-runner.js",
}
WARMUP_FORBIDDEN = [
    (r"[Bb]ooth\s+[0-9A-Z]{1,4}-?\d", "booth number"),
    (r"booth\s+confirmed", "unverified CIIE booth claim"),
    (r"[Bb]ooth\s+is\s+confirmed", "unverified CIIE booth claim"),
    (r"Africa(an)?\s+(Nations\s+)?Pavilion", "pavilion claim"),
    (r"PROWTC", "PROWTC is a buyer, not a certifier or our brand"),
    (r"Sevruga", "retired caviar name"),
    (r"per\s+250g", "wrong caviar unit"),
    (r"500g per tin", "wrong caviar unit — we quote per 100g"),
    (r"R380/tin", "retired caviar price"),
    (r"14-21 days", "wrong caviar lead time — 7-14 days from DAFF permit issue"),
    (r"R(580|620|680)/kg", "biltong price not on our price list"),
    (r"Oscietra Gold|Kaluga Hybrid", "wrong caviar tier name"),
    (r"Rainforest\s+Alliance", "unsourced certification claim"),
    (r"dedicated booth", "booth claim"),
]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import secret_leak_scan
REGISTRY = os.path.join(ROOT, "studex-meat", "PRICE-SOURCE-REGISTRY.md")

# The rendered outreach copy — what a buyer actually receives. Rendered with a
# sample lead so the check covers subjects and bodies together.
RENDER_JS = r"""
const t = require('./ciie-nurture/dist/emails.js');
const lead = {id:'x', name:'Sample Buyer', company:'Sample Co',
              email:'buyer@example.com', source:'test', addedAt:'2026-01-01',
              tags:[], currentStep:0, status:'active'};
let out = '';
for (const x of t.EMAIL_TEMPLATES) {
  const subject = typeof x.subject === 'function' ? x.subject(lead) : x.subject;
  out += 'SUBJECT: ' + subject + '\n' + x.body(lead) + '\n';
}
process.stdout.write(out);
"""


def render_outreach():
    """Return (rendered_text, error). The email copy is checked as SENT."""
    try:
        r = subprocess.run(["node", "-e", RENDER_JS], cwd=ROOT,
                           capture_output=True, text=True, timeout=30)
        return r.stdout, r.stderr
    except Exception as e:  # node missing, timeout, bad module
        return "", f"{type(e).__name__}: {e}"


def outreach_rules():
    """Substring rules for the rendered emails, owned by the registry (§4g)."""
    rules = {"forbidden": [], "required": []}
    if not os.path.exists(REGISTRY):
        return rules
    lines = open(REGISTRY, encoding="utf-8").read().splitlines()
    in_sec = False
    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith("## 4g"):
            in_sec = True
            continue
        if in_sec and stripped.startswith("## "):
            break
        if not in_sec or not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        val = cells[0].strip().strip("`").strip()
        kind = cells[1].strip().lower()
        if not val or kind not in rules:
            continue
        if set(val) <= set("-: "):      # separator row
            continue
        rules[kind].append(val)
    return rules


def code_only(txt):
    """Strip template literals and comments.

    A ${lead.x} inside a backtick template is CORRECT (it interpolates).
    The bug we shipped was ${lead.x} inside a quoted string, which does not.
    Blanking template literals and comments leaves only real, live string
    content — so the remaining matches are genuine.
    """
    txt = re.sub(r"`(?:\\.|[^`\\])*`", "``", txt, flags=re.S)
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"(?<![:'\"/])//[^\n]*", " ", txt)
    return txt


# ---------------------------------------------------------------- outbound drafts
# An email draft goes out of a REAL Studex inbox to a REAL external partner,
# so a false claim in one is as public as a false claim on a landing page.
# Until now the checker only covered the files it happened to know about.
# The drafts directory can be OVERRIDDEN so that a test can point drift-check
# at a sandbox copy instead of the LIVE directory.
#
# Same reasoning as CORRECTION_DIR above: `ops/test-draft-rules.py` proves the
# draft rules fire by writing a deliberately-bad draft and checking that
# drift-check flags it. Written into the LIVE directory, an interrupted run
# (timeout, kill, crash) leaves the fixture behind - and this directory holds
# REAL email drafts that go out to REAL external partners. A stray test file
# here is one stray approval away from being sent to a buyer.
DRAFT_DIR = os.environ.get("DRIFT_CHECK_DRAFT_DIR", "outbound-drafts")

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
    """Return every fenced block in the file, joined.

    The notes around a draft deliberately quote forbidden strings to explain
    what is wrong with them, so scanning the whole file would false-positive
    on its own documentation - only fenced blocks are content.

    ALL blocks are returned, not just the first: a draft may fence the email
    body AND a command to send it (kfschof-reply.md does exactly that). Taking
    only the first block means the body can be silently skipped if a file ever
    puts something else first, and an unchecked body is worse than a false
    positive.
    """
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    return "\n".join(blocks)


# ---------------------------------------------------------------- outbound corrections
# A correction note goes to real external buyers too. The distinctive risk: to
# correct a false claim you must QUOTE it. So instead of banning the string, we
# require that every occurrence sits in a quoted / reported context - i.e. we are
# talking ABOUT what we said, not asserting it again.
# The corrections directory can be OVERRIDDEN so that a test can point
# drift-check at a sandbox copy instead of the LIVE directory.
#
# Why this matters: `ops/test-correction-rules.py` proves the correction rules
# fire by writing a deliberately-bad note and checking that drift-check flags
# it. When it wrote that note into the LIVE directory, an interrupted run
# (timeout, kill, crash) left the fixture behind - and then drift-check
# reported DRIFT on that fixture for EVERY subsequent run. The real drift
# check cried wolf on a test artefact, and the test's own "MUST PASS" cases
# failed for the wrong reason.
#
# A test that writes into the live tree can poison the tree it then checks.
# Point it at a sandbox and the live directory is never touched.
CORRECTION_DIR = os.environ.get("DRIFT_CHECK_CORRECTION_DIR", "outbound-corrections")
CORRECTION_RECIPIENTS = os.path.join(CORRECTION_DIR, "ciie-correction-recipients.json")

# The exact false claims that went out. In a correction these may only appear
# inside a quotation - e.g. I wrote "PROWTC certified" - never as a fresh claim.
RETRACTED_CLAIMS = [
    r"PROWTC",
    r"Rainforest\s*Alliance",
    r"USD\s*4\.60\s*/\s*kg",
    r"USD\s*5\.50\s*/\s*kg",
    r"halal[- ]slaughter\s+available",
    r"cleared import channels",
    r"bilateral agricultural protocol",
]

# Context markers that indicate the claim is being QUOTED or withdrawn.
QUOTED_CONTEXT = re.compile(
    r"(i wrote|i said|we wrote|we said|i stated|i mentioned|i described|"
    r"earlier email|previous email|previous note|earlier note|that was|"
    r"was wrong|was an error|incorrect|withdraw|i withdraw|apolog|"
    r"not ours|should not have|unverified|cannot evidence|do not hold|"
    r"should have|instead of|\"[^\"]*\"|'[^']*')",
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

    all_notes = sorted(n for n in os.listdir(cdir) if n.endswith(".md"))
    # Documentation is not a draft. Skip it by an explicit name convention so
    # the skip is intentional and visible, while a real draft that has lost its
    # fenced body is still flagged.
    notes = [n for n in all_notes if not n.upper().startswith("README")]
    n_skipped = len(all_notes) - len(notes)


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
            for m in re.finditer(r"\b(?:R|USD)\s?([0-9][0-9,]*(?:\.[0-9]+)?)", body, re.I):
                amt = m.group(1).replace(",", "")
                if amt not in reg_flat:
                    issues.append(f"{rel} - price {m.group(0)!r} does not appear in the registry; "
                                  "verify it before sending")

        # 3. URL rules
        for slug in SUPERSEDED_URLS:
            if slug in body:
                issues.append(f"{rel} - shares a SUPERSEDED URL ({slug}); use the canonical URL")
        for m in re.finditer(r"https?://([a-z0-9]+)\.space\.mcode\.io", body, re.I):
            if m.group(1) not in CANONICAL_URLS:
                issues.append(f"{rel} - non-canonical URL slug {m.group(1)!r}")

        # 4. it must explicitly withdraw, not just omit
        if not re.search(r"(wrong|incorrect|error|withdraw|apolog)", body, re.I):
            issues.append(f"{rel} - does not explicitly withdraw the earlier claims; a correction "
                          "that silently omits them leaves the false impression standing")

    # 4b. THE NOTE MUST AGREE WITH THE AUTHORITATIVE JSON.
    # This rule exists because it did NOT: the JSON said 29 and the draft body
    # still said 26, and the checker passed. A number that lives in two places
    # will drift unless something compares them.
    rpath0 = os.path.join(ROOT, CORRECTION_RECIPIENTS)
    if os.path.exists(rpath0):
        d0 = json.load(open(rpath0, encoding="utf8"))
        auth_total = d0.get("totalEmails")
        auth_recs = d0.get("totalRecipients")
        for name in notes:
            rel = f"{CORRECTION_DIR}/{name}"
            raw = open(os.path.join(cdir, name), encoding="utf8", errors="ignore").read()
            # A number that is QUOTED as the old/wrong figure is a historical
            # reference we are withdrawing - not a claim about what was sent.
            historical = re.compile(
                r"(said|claims?|claimed|wrote|previously|previously said|old\s+|wrong\s+"
                r"figure|\"[^\"]*\"|\'[^\']*\')", re.I)

            def is_historical(text, pos):
                window = text[max(0, pos - 120):pos + 40]
                return bool(historical.search(window))

            # every "<n> emails" claim in the note must match the authoritative total
            for m in re.finditer(r"\b(\d+)\s+emails?\b", raw, re.I):
                n = int(m.group(1))
                if n in (1, 2, 3):
                    continue  # per-recipient counts are checked below
                if auth_total and n != auth_total:
                    if is_historical(raw, m.start()):
                        continue
                    issues.append(
                        f"{rel} - says '{n} emails' but the authoritative recipient list says "
                        f"{auth_total}; the note a human approves must match the file")
            for m in re.finditer(r"\b(\d+)\s+external recipients\b|\b(\d+)\s+recipients\b", raw, re.I):
                n = int(m.group(1) or m.group(2))
                if auth_recs and n != auth_recs:
                    if is_historical(raw, m.start()):
                        continue
                    issues.append(
                        f"{rel} - says '{n} recipients' but the authoritative recipient list says "
                        f"{auth_recs}")
            # per-recipient email counts in the note's table must match the JSON.
            # The count is the cell IMMEDIATELY AFTER the email cell - the first
            # numeric cell is the row number, and the date cells also contain numbers.
            for rr in d0.get("recipients", []):
                em = rr.get("email")
                for line in raw.splitlines():
                    if not (em and em in line and "|" in line):
                        continue
                    cells = [c.strip() for c in line.split("|")]
                    idx = next((i for i, c in enumerate(cells) if em in c), None)
                    if idx is None:
                        continue
                    # The count is the FIRST purely-numeric cell after the email
                    # cell. The table has a Company column in between, and the
                    # date cell ("25 Sep, 29 Sep, 3 Oct") is not purely numeric,
                    # so this picks the count and nothing else.
                    cnt = next((c for c in cells[idx + 1:] if c.isdigit()), None)
                    if cnt is not None and int(cnt) != rr.get("emails"):
                        issues.append(
                            f"{rel} - row for {em} says {cnt} email(s) but the authoritative "
                            f"list says {rr.get('emails')}")

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
        "detail": f"{n_checked}/{len(notes)} correction bodies scanned"
                  + (f" ({n_skipped} doc file(s) skipped)" if n_skipped else ""),
        "issues": issues,
    }


def scan_outbound_drafts():
    """Check outbound email drafts against the same rules as every page."""
    issues = []
    ddir = os.path.join(ROOT, DRAFT_DIR)
    if not os.path.isdir(ddir):
        # NOT "CLEAN". A missing directory means nothing was checked - and a
        # green tick that asserted nothing is worse than no checker. This also
        # catches a typo'd DRIFT_CHECK_DRAFT_DIR pointing at a path that does
        # not exist, which would otherwise read as "the drafts are fine".
        return {"name": "Outbound email drafts", "url": "(local files)",
                "state": "UNCHECKED",
                "detail": "no drafts directory at %s - NOTHING WAS CHECKED" % DRAFT_DIR,
                "issues": ["outbound-drafts - the drafts directory is missing, so every "
                           "draft is UNCHECKED (this is not a pass)"]}

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

        for m in re.finditer(r"https?://([a-z0-9]+)\.space\.mcode\.io", body, re.I):
            slug = m.group(1)
            if slug not in CANONICAL_URLS:
                issues.append(f"{rel} — non-canonical URL slug {slug!r}; it is not a current "
                              "canonical page. Check the registry section 4 table.")

        # Every price in the body must exist in the registry. Normalise the
        # thousands separator so "R1,050" is matched against "R1050".
        if reg:
            reg_flat = reg.replace(",", "")
            for m in re.finditer(r"\b(?:R|USD)\s?([0-9][0-9,]*(?:\.[0-9]+)?)", body, re.I):
                amt = m.group(1).replace(",", "")
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



def scan_secret_leaks():
    """No credential may ever be built into a browser bundle.

    See ops/secret-leak-scan.py for the 2026-10-23 incident that motivated it:
    an AgentMail key shipped inside two live landing-page JS bundles.
    """
    try:
        return secret_leak_scan.scan()
    except Exception as _e:
        return {
            "name": "Secret leak scan",
            "state": "UNREACHABLE",
            "detail": f"could not run: {_e}",
            "issues": [],
        }


def scan_local_assets():
    out = []
    issues = []
    for rel in ASSET_PATHS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        raw = open(p, encoding="utf-8", errors="ignore").read()
        txt = raw if rel in RAW_SCAN else (code_only(raw) if rel.endswith((".ts", ".js")) else raw)
        pats = [x for x in FORBIDDEN if not (rel in RAW_SCAN and x[0] == r"\$\{lead\.")]
        if rel in WARMUP_PATHS:
            pats = pats + WARMUP_FORBIDDEN
        for pat, label in pats:
            for m in re.finditer(pat, txt, flags=re.I):
                line = txt[:m.start()].count("\n") + 1
                issues.append(f"{rel}:{line} — {label}: {m.group(0)!r}")
    # the sender must stay disarmed until the CIIE status is confirmed
    cli = os.path.join(ROOT, "ciie-nurture", "dist", "cli.js")
    if os.path.exists(cli) and "CIIE_NURTURE_ARMED" not in open(cli, encoding="utf-8", errors="ignore").read():
        issues.append("ciie-nurture/dist/cli.js — sender kill switch missing")
    # A source file and the copy that actually gets deployed must be identical.
    # They drifted today: the deployed copy was corrected and the source was
    # not, so the next rebuild would have silently restored every false claim.
    src = os.path.join(ROOT, "studex-biltong", "index.html")
    dep = os.path.join(ROOT, "studex-biltong", "dist", "index.html")
    if os.path.exists(src) and os.path.exists(dep):
        if open(src, "rb").read() != open(dep, "rb").read():
            issues.append("studex-biltong/index.html — differs from dist/index.html: the "
                          "deployed copy is not derived from the source, so a rebuild would "
                          "revert every correction")
    # send-sequence.js is the script that actually sent the 21 emails of
    # 25 Sep / 29 Sep / 3 Oct. It carried its OWN copy of the emails — with a
    # fabricated CIIE meeting, a "PROWTC (Rainforest Alliance)" certification
    # that is not ours, and a claim that two named prospects "have already
    # expressed interest" — and it had NO kill switch. There must be exactly
    # ONE copy of the email text, and both senders must be disarmed.
    seq = os.path.join(ROOT, "ciie-nurture", "send-sequence.js")
    if os.path.exists(seq):
        seq_txt = open(seq, encoding="utf-8", errors="ignore").read()
        if "CIIE_NURTURE_ARMED" not in seq_txt:
            issues.append("ciie-nurture/send-sequence.js — sender kill switch missing")
        if "dist/emails" not in seq_txt:
            issues.append("ciie-nurture/send-sequence.js — does not use the shared templates "
                          "(a second copy of the email copy is the root cause)")
    # --- the RENDERED email copy, not the source file -------------------
    # The scan above blanks template literals, and every email body IS one.
    # That is how "Thank you for meeting the Studex Meat Co. team at CIIE
    # 2026 in Shanghai" passed on 2026-10-21, to 9 real coffee buyers.
    # Render the sequence with a sample lead and check what would be SENT.
    rendered, err = render_outreach()
    n_rules = 0
    if not rendered:
        issues.append(f"ciie-nurture/dist/emails.js — could not render the templates: "
                      f"{err.strip()[:140] if err else 'no output'}")
    else:
        rules = outreach_rules()
        n_rules = len(rules["forbidden"]) + len(rules["required"])
        if n_rules == 0:
            issues.append("registry §4g — no outreach rules found; the email copy is UNCHECKED")
        low = rendered.lower()
        for s in rules["forbidden"]:
            if s.lower() in low:
                issues.append(f"RENDERED EMAIL — forbidden string present: {s!r}")
        for s in rules["required"]:
            if s.lower() not in low:
                issues.append(f"RENDERED EMAIL — required string missing: {s!r}")
        for pat, label in FORBIDDEN:
            for m in re.finditer(pat, rendered, flags=re.I):
                issues.append(f"RENDERED EMAIL — {label}: {m.group(0)!r}")
    out.append({
        "name": "CIIE asset copy",
        "url": "(local files)",
        "state": "DRIFT" if issues else "CLEAN",
        "detail": f"{len(ASSET_PATHS)} files scanned · {n_rules} rendered-copy rules",
        "issues": issues,
    })
    return out


def main():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    pages = manifest["pages"]
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(check, pages))
    results.extend(scan_local_assets())
    results.append(scan_secret_leaks())
    results.append(scan_outbound_drafts())
    results.append(scan_outbound_corrections())
    results.sort(key=lambda r: r["name"])
    drift = [r for r in results if r["state"] == "DRIFT"]
    bad = [r for r in results if r["state"] not in ("CLEAN", "DRIFT")]
    print("=" * 68)
    print("STUDEX PAGE DRIFT CHECK")
    print("=" * 68)
    for r in results:
        mark = {"CLEAN": "[ OK ]", "DRIFT": "[DRIFT]", }.get(r["state"], "[FAIL]")
        print(f"{mark} {r['name']:<22} {r['state']:<12} {r['detail']}")
        for i in r["issues"]:
            print(f"         - {i}")
    print("-" * 68)
    print(f"pages: {len(results)}  clean: {len(results)-len(drift)-len(bad)}  "
          f"drift: {len(drift)}  unreachable: {len(bad)}")
    if drift:
        print("\nDRIFT DETECTED — a live page no longer matches its owning source.")
        print("Check the owner file in studex-meat/PRICE-SOURCE-REGISTRY.md, fix the")
        print("SOURCE first, then redeploy the affected page. Do not patch the page alone.")
    return 1 if drift else (2 if bad else 0)

if __name__ == "__main__":
    sys.exit(main())
