#!/usr/bin/env python3
"""Remove the forbidden claims from the two React SPAs that publish them.

china-coffee-lead-capture  -> publishes "Rainforest Alliance certified" (the unsourced
  claim removed from the static China page on 2026-10-21), "Direct Trade Origin"
  (retired, unsourced badge) and links ceo@agent.studexmeat.com (a domain with no DNS).
studex-caviar -> publishes "ethically sourced" (retired, unsourced) and "certified
  Russian caviar houses" (an explicit forbidden string: the caviar source page makes
  no such claim).

Also corrects the China page's tariff date. The registry §4c owns it:
  China import tariff start = 1 May 2026 (53 African countries, to 30 Apr 2028).
The SPA said "Tariff-free entry into China from July 20, 2026" and labelled Jul 20 the
"Policy Effective Date" - that date is the unified phytosanitary system, NOT the tariff.

Every replacement is asserted to apply exactly the expected number of times, so a
failed patch is loud rather than silent.
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path("/workspace")

CHINA = ROOT / "china-coffee-lead-capture/src/App.tsx"
CHINA_HTML = ROOT / "china-coffee-lead-capture/index.html"
CAVIAR = ROOT / "studex-caviar/src/App.tsx"

PATCHES = [
    # ---------------- china SPA ----------------
    (CHINA,
     "Premium Rwanda A1 &amp; A2 grade Arabica coffee. Tariff-free entry into China from July 20, 2026. Rainforest Alliance certified. CIF Shanghai pricing.",
     "Premium Rwanda A1 &amp; A2 grade Arabica coffee. Zero import tariff since 1 May 2026. Full origin documentation. CIF Shanghai pricing.",
     1),
    (CHINA,
     "            '✓ Rainforest Alliance Certified',\n            '✓ Direct Trade Origin',\n",
     "            '✓ Full Origin Documentation',\n",
     1),
    (CHINA,
     "'✓ Zero Tariff — China 2026',",
     "'✓ Zero Tariff Since 1 May 2026',",
     1),
    (CHINA,
     "{ title: 'Rainforest Alliance', desc: 'Full RA certification across all supply chain stages. The single most important credential for EU and now China premium buyers.', accent: false },",
     "{ title: 'Origin Documentation', desc: 'Phytosanitary certificate, certificate of origin, certificate of analysis, bill of lading, cupping score and lot traceability with every shipment. No third-party certification is held by Studex.', accent: false },",
     1),
    (CHINA,
     "{ v: 'Jul 20', l: 'Policy Effective Date' },",
     "{ v: '1 May', l: 'Tariff Effective Date' },",
     1),
    (CHINA,
     "🇨🇳 China Market · Effective July 20, 2026",
     "🇨🇳 China Market · Effective 1 May 2026",
     1),
    (CHINA,
     "cert: ['Rainforest Alliance'] }",
     "cert: ['Full Origin Documentation'] }",
     2),
    (CHINA,
     "cert: ['Rainforest Alliance', 'Direct Trade'] }",
     "cert: ['Full Origin Documentation'] }",
     1),
    (CHINA,
     "background: c === 'Direct Trade' ? 'rgba(201,168,76,0.15)' : 'rgba(46,94,58,0.1)', color: c === 'Direct Trade' ? '#8A6A2A' : GREEN,",
     "background: 'rgba(46,94,58,0.1)', color: GREEN,",
     1),
    (CHINA,
     "'Full Rainforest Alliance documentation',",
     "'Full origin documentation (phytosanitary, COO, COA, B/L)',",
     1),
    (CHINA,
     'Or email <a href="mailto:ceo@agent.studexmeat.com" style={{ color: GOLD }}>ceo@agent.studexmeat.com</a> directly · Response within 24 hours',
     'Or email <a href="mailto:sales@studex-group.com" style={{ color: GOLD }}>sales@studex-group.com</a> directly · Response within 24 hours',
     1),
    (CHINA,
     '<a href="mailto:ceo@agent.studexmeat.com" style={{ color: GREEN, textDecoration: \'none\' }}>ceo@agent.studexmeat.com</a> ·',
     '<a href="mailto:info@studexmeat.com" style={{ color: GREEN, textDecoration: \'none\' }}>info@studexmeat.com</a> ·',
     1),
    (CHINA_HTML,
     "Rainforest Alliance certified. CIF Shanghai pricing.",
     "Full origin documentation. CIF Shanghai pricing.",
     1),
    # ---------------- caviar SPA ----------------
    (CAVIAR,
     "Authentic Caspian Sea caviar, ethically sourced and professionally imported.",
     "Authentic Caspian Sea caviar, professionally imported.",
     1),
    (CAVIAR,
     "We work directly with certified Russian caviar houses — producers who have operated for generations",
     "We work directly with established Russian caviar producers — suppliers who have operated for generations",
     1),
]

failed = []
for path, old, new, expect in PATCHES:
    if not path.exists():
        failed.append(f"MISSING FILE {path}")
        continue
    t = path.read_text(encoding="utf8")
    n = t.count(old)
    if n != expect:
        failed.append(f"{path.relative_to(ROOT)}: expected {expect} occurrence(s) of {old[:60]!r}, found {n}")
        continue
    path.write_text(t.replace(old, new), encoding="utf8")
    print(f"  patched {path.relative_to(ROOT)}  x{n}  {old[:64]!r}")

if failed:
    print("\nFAILED PATCHES:")
    for f in failed:
        print("   " + f)
    sys.exit(1)

# ---------------- verify no forbidden strings remain ----------------
FORB = ["Rainforest Alliance", "PROWTC", "agent.studexmeat.com", "Direct Trade",
        "ethically sourced", "certified Russian caviar houses", "Sevruga Premium",
        "Siberian Reserve", "per 250g", "Coming Soon", "500+ MT", "July 20, 2026"]
print("\n--- source scan for forbidden strings ---")
bad = 0
for app in ["china-coffee-lead-capture", "studex-caviar", "ciie-coffee-landing", "coffee-noir-landing"]:
    src = ROOT / app / "src"
    hits = []
    for p in list(src.rglob("*.tsx")) + list(src.rglob("*.ts")) + [ROOT / app / "index.html"]:
        if not p.exists():
            continue
        t = p.read_text(errors="ignore")
        for f in FORB:
            if f in t:
                hits.append(f"{p.relative_to(ROOT)}: {f}")
    print(f"  {app:32} {'CLEAN' if not hits else 'HITS: ' + '; '.join(hits)}")
    bad += len(hits)

# ---------------- rebuild ----------------
print("\n--- rebuild ---")
for app in ["china-coffee-lead-capture", "studex-caviar"]:
    d = ROOT / app
    r = subprocess.run(["npm", "run", "build"], cwd=str(d), capture_output=True, text=True, timeout=300)
    print(f"  {app}: rc={r.returncode}")
    if r.returncode:
        print((r.stdout or "")[-1500:])
        print((r.stderr or "")[-1500:])
        bad += 1

print("\n--- dist scan for forbidden strings ---")
for app in ["china-coffee-lead-capture", "studex-caviar"]:
    d = ROOT / app / "dist"
    hits = []
    for p in list(d.rglob("*.js")) + list(d.rglob("*.html")):
        t = p.read_text(errors="ignore")
        for f in FORB:
            if f in t:
                hits.append(f"{p.relative_to(ROOT)}: {f}")
    print(f"  {app:32} {'CLEAN' if not hits else 'HITS: ' + '; '.join(hits)}")
    bad += len(hits)

print("\nRESULT:", "ALL CLEAN" if bad == 0 else f"{bad} PROBLEM(S)")
sys.exit(0 if bad == 0 else 1)
