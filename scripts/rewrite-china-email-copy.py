#!/usr/bin/env python3
"""Update the China coffee outreach email copy (sheet + outreach file):
   - price line -> live band
   - remove unsourced certification claims (PROWTC / Rainforest Alliance / Wildlife Verified)
   - add the Best of Rwanda halo, correctly framed as a ceiling proof
"""
import sys

EDITS = {
    'china-coffee-sheet-copy-paste.md': [
        (
            """**Subject:** South African Coffee — Rwanda A1 Grade, Wildlife Verified, PROWTC Certified

Dear [Buyer Name / Procurement Team],

I hope this message finds you well. My name is Tumelo Ramaphosa, founder of Studex Meat, a South African premium food and beverage company now expanding into green coffee exports.""",
            """**Subject:** South African Coffee — Rwanda A1 Grade, 87.49–91.81% SCA (Best of Rwanda 2026)

Dear [Buyer Name / Procurement Team],

I hope this message finds you well. My name is Tumelo Ramaphosa, founder of Studex Meat, a South African premium food and beverage company now expanding into green coffee exports.""",
            'sheet-subject-1',
        ),
        (
            """**What we offer:**
- Rwanda SPOT Premium Grade A1 — Washed: jasmine, stone fruit, clean finish
- Rwanda SPOT Premium Grade A2 — Natural: blueberry, dark chocolate, full body
- PROWTC certified, Rainforest Alliance certified
- FOB Kigali pricing from USD 4.80/kg
- Minimum order: 60kg bags""",
            """**What we offer:**
- Rwanda SPOT Premium Grade A1 — Washed: jasmine, stone fruit, clean finish
- Rwanda SPOT Premium Grade A2 — Natural: blueberry, dark chocolate, full body
- Sourced from a single washing station in the Nyamasheke region, 1,500–2,000m altitude
- FOB Kigali, **USD 6.07–6.75/kg**, priced live against the ICE Arabica C benchmark
- Minimum order: 60kg bags

**Why Rwanda, why now:** at the Best of Rwanda 2026 auction on 21 October, the top lot — a Geisha from K-Organics, Huye — reached **US$452/kg**, roughly 66× the average international price, and 20 winners scored **87.49–91.81%** on the SCA scale. That is a micro-lot result, not a market rate, but it tells you what this origin is capable of when the picking and the processing are right.""",
            'sheet-offer-1',
        ),
        (
            """| 1 - Initial | July 20 (window opens) | South African Coffee — Rwanda A1 Grade, Wildlife Verified, PROWTC Certified | All 🔴 HIGH priority | See Email Draft 1 below |""",
            """| 1 - Initial | July 20 (window opens) | South African Coffee — Rwanda A1 Grade, 87.49–91.81% SCA (Best of Rwanda 2026) | All 🔴 HIGH priority | See Email Draft 1 below |""",
            'sheet-sequence-subject',
        ),
    ],
    'china-coffee-outreach.md': [
        (
            """**Subject:** South African Coffee — Rwanda A1 Grade, Wildlife Verified, PROWTC Certified""",
            """**Subject:** South African Coffee — Rwanda A1 Grade, 87.49–91.81% SCA (Best of Rwanda 2026)""",
            'outreach-subject-1',
        ),
        (
            """**What we offer:**
- Rwanda SPOT Premium Grade A1 — Washed: jasmine, stone fruit, clean finish
- Rwanda SPOT Premium Grade A2 — Natural: blueberry, dark chocolate, full body
- PROWTC certified ( Proof of Sustaining Wildlife & Trade Credentials)
- Rainforest Alliance certified
- FOB Kigali pricing from USD 4.80/kg
- Minimum order: 60kg bags""",
            """**What we offer:**
- Rwanda SPOT Premium Grade A1 — Washed: jasmine, stone fruit, clean finish
- Rwanda SPOT Premium Grade A2 — Natural: blueberry, dark chocolate, full body
- Sourced from a single washing station in the Nyamasheke region, 1,500–2,000m altitude
- FOB Kigali, **USD 6.07–6.75/kg**, priced live against the ICE Arabica C benchmark
- Minimum order: 60kg bags

**Why Rwanda, why now:** at the Best of Rwanda 2026 auction on 21 October, the top lot — a Geisha from K-Organics, Huye — reached **US$452/kg**, roughly 66× the average international price, and 20 winners scored **87.49–91.81%** on the SCA scale. That is a micro-lot result, not a market rate, but it tells you what this origin is capable of when the picking and the processing are right.""",
            'outreach-offer-1',
        ),
        (
            """- Include: company profile, sample packaging, Rwanda origin certificates, PROWTC certificate, price list""",
            """- **Include:** company profile, sample packaging, origin documentation, the live price band, and the Best of Rwanda 2026 result""",
            'outreach-booth-include',
        ),
        (
            """For a blend component or single-origin offering, it's a strong story — provenance, certification, and cup quality in one.""",
            """For a blend component or single-origin offering, it's a strong story — provenance, process, and cup quality in one.""",
            'outreach-email3-cert',
        ),
    ],
}

total = 0
for path, edits in EDITS.items():
    s = open(path, encoding='utf-8').read()
    for old, new, label in edits:
        n = s.count(old)
        if n == 0 and new in s:
            print(f"  SKIP {path}:{label} (already applied)")
            continue
        if n != 1:
            print(f"FAIL[{path}:{label}]: marker count = {n}")
            sys.exit(1)
        s = s.replace(old, new)
        print(f"  OK {path}:{label}")
        total += 1
    open(path, 'w', encoding='utf-8').write(s)

print(f"\n{len(EDITS)} files, {total} edits applied")
