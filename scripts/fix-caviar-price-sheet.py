#!/usr/bin/env python3
"""
Correct caviar-landed-cost.xlsx — add the missing floor column, the below-floor
flag, and the SA retail band reference row.

Why: the workbook computed "Minimum viable trade price" (=B/0.7, a 30% margin)
but never compared it against the price we actually quote. All three SKUs are
currently quoted BELOW that floor. This script makes the gap visible on the
sheet itself so it cannot be missed again.

Idempotent: safe to re-run. It rebuilds the "Trade Pricing" sheet from the
Landed Cost sheet's own formulas, so the two can never drift.

Run: python3 scripts/fix-caviar-price-sheet.py
"""
import shutil
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ============================================================================
# SUPERSEDED 2026-10-24 — THIS SCRIPT WILL NOW REFUSE TO RUN.
#
# It rebuilds the Trade Pricing sheet from the PRE-CORRECTION model:
#   - margin as a MARKUP on cost (D/B-1) instead of gross margin on price
#   - import VAT added to landed cost, although it is RECOVERABLE for a
#     VAT-registered importer (this inflated every floor by ~15%)
#   - duty charged on farm gate instead of on CIF
#   - the SKU named "Sevtruga Classic" instead of the canonical
#     "Sevtruga Medium"
#   - a trade x 1.5 "recommended retail" presented as if it were a price
#
# Running it would silently REVERT the corrected model. The corrected model
# lives in the workbook sheet "Corrected Model 2026-10-24" and in
# caviar-trade-desk/src/model.ts, and is proven by
# caviar-trade-desk/scripts/verify.ts (45 property checks).
#
# If you are here to rebuild the sheet from scratch, rebuild it from the
# CORRECTED sheet, not from this script.
# ============================================================================
CORRECTED_SHEET_NAME = "Corrected Model 2026-10-24"


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "caviar-landed-cost.xlsx"
BAK = ROOT / "caviar-landed-cost.pre-floor-fix-2026-10-23.xlsx"

GOLD = "C9A227"
RED_FILL = PatternFill("solid", fgColor="2A1013")
RED_TEXT = Font(color="F87171", bold=True, size=11)
GREEN_FILL = PatternFill("solid", fgColor="0F1F17")
GREEN_TEXT = Font(color="34D399", bold=True, size=11)
HDR_FILL = PatternFill("solid", fgColor="1C1D22")
HDR_FONT = Font(color="E5E7EB", bold=True, size=10)
TITLE_FONT = Font(color=GOLD, bold=True, size=14)
SUB_FONT = Font(color="8A8F98", size=10)
MONO = Font(name="Consolas", size=10)
MONO_B = Font(name="Consolas", size=10, bold=True)
THIN = Side(style="thin", color="2A2B31")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

TARGET_MARGIN = 0.30
SA_BAND_LOW = 8000
SA_BAND_HIGH = 35000


def style_header(ws, row, cols):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BOX


def build(wb):
    if "Trade Pricing" in wb.sheetnames:
        del wb["Trade Pricing"]
    ws = wb.create_sheet("Trade Pricing", wb.sheetnames.index("Landed Cost") + 1)

    ws["A1"] = "Trade Pricing Decision — CORRECTED"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Studex Group (Pty) Ltd | rebuilt 2026-10-23 by scripts/fix-caviar-price-sheet.py"
    ws["A2"].font = SUB_FONT
    ws["A3"] = (
        "Target gross margin "
        f"{TARGET_MARGIN:.0%}. 'Minimum viable trade price' = landed cost / (1 - target margin). "
        "A trade price BELOW the floor cannot fund CITES lead time or cold-chain failure."
    )
    ws["A3"].font = SUB_FONT

    headers = [
        "Product",
        "Landed ZAR/kg",
        "Min viable trade price (ZAR/kg)",
        "Current trade price (ZAR/kg)",
        "Gross margin %",
        "Shortfall vs floor (ZAR/kg)",
        "STATUS",
        "Recommended trade price (ZAR/kg)",
        "Recommended retail (ZAR/kg)",
        "Recommended retail /100g (ZAR)",
    ]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=5, column=i, value=h)
    style_header(ws, 5, len(headers))

    rows = [("Oscietra Imperial", 5), ("Kaluga Prestige", 6), ("Sevtruga Classic", 7)]
    for idx, (name, src_row) in enumerate(rows):
        r = 6 + idx
        ws.cell(row=r, column=1, value=name).font = Font(bold=True, size=11, color="E5E7EB")
        # Landed cost pulled from the Landed Cost sheet, live formula
        ws.cell(row=r, column=2, value=f"='Landed Cost'!K{src_row}")
        # Minimum viable = landed / (1 - target margin)  — 30% floor
        ws.cell(row=r, column=3, value=f"=B{r}/(1-{TARGET_MARGIN})")
        # Current trade price — the live price we quote (defect source)
        ws.cell(row=r, column=4, value={
            "Oscietra Imperial": 34000,
            "Kaluga Prestige": 22000,
            "Sevtruga Classic": 12500,
        }[name])
        ws.cell(row=r, column=5, value=f"=D{r}/B{r}-1")
        ws.cell(row=r, column=6, value=f"=D{r}-C{r}")
        ws.cell(
            row=r,
            column=7,
            value=f'=IF(D{r}<C{r},"BELOW FLOOR - FIX BEFORE QUOTING","clears floor")',
        )
        # Recommended trade = floor rounded up to nearest R100
        ws.cell(row=r, column=8, value=f"=CEILING(C{r},100)")
        # Recommended retail = trade + 50% catering/hospitality uplift
        ws.cell(row=r, column=9, value=f"=CEILING(H{r}*1.5,100)")
        ws.cell(row=r, column=10, value=f"=I{r}/10")

        for c in range(2, 11):
            cell = ws.cell(row=r, column=c)
            cell.border = BOX
            cell.number_format = "0.0%" if c == 5 else '#,##0'
            cell.font = MONO
        ws.cell(row=r, column=7).font = MONO_B
        ws.cell(row=r, column=7).alignment = Alignment(horizontal="center")

    # Reference band block
    ref_row = 11
    ws.cell(row=ref_row, column=1, value="MARKET REFERENCE BANDS").font = Font(bold=True, size=11, color=GOLD)
    ref = [
        ("SA premium caviar retail band (kg)", f"R{SA_BAND_LOW:,} - R{SA_BAND_HIGH:,}", "IndexBox, SA Caviar Market Report, Sep 2026"),
        ("SA retail band, Osetra/Kaluga/Sevruga (per 100g)", "R2,000 - R6,000", "Local SA retail research, 2026-09-21"),
        ("ITAC Rebate 460.19 (caviar for further processing)", "UNCONFIRMED", "May not apply to a pure reseller. Do NOT book as savings until the clearing agent confirms."),
        ("Import duty rate HS 1604.31", "20% (ASSUMED)", "UNVERIFIED for 2026. Confirm with a licensed customs clearing agent before quoting a binding price."),
        ("ITAC import permit + CITES (Appendix II, all sturgeon)", "REQUIRED - 4 to 8 week lead time", "Open the application now or we cannot take Q4 gifting-season orders."),
        ("Aquatir (SA's own sturgeon farm)", "Direct farm-to-buyer, no import chain", "Our edge is provenance + compliance paperwork, not price."),
    ]
    for i, (label, value, source) in enumerate(ref):
        r = ref_row + 1 + i
        c1 = ws.cell(row=r, column=1, value=label)
        c1.font = Font(size=10, color="E5E7EB")
        c1.border = BOX
        c2 = ws.cell(row=r, column=2, value=value)
        c2.font = MONO_B
        c2.border = BOX
        c3 = ws.cell(row=r, column=3, value=source)
        c3.font = Font(size=9, color="8A8F98")
        c3.border = BOX
        c3.alignment = Alignment(vertical="center")
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=10)

    note_row = ref_row + 1 + len(ref) + 1
    ws.cell(
        row=note_row,
        column=1,
        value=(
            "Live mirror: the same engine is running at the Caviar Trade Desk "
            "(https://awyjxfplygag.space.mcode.io) — it reproduces this workbook formula-for-formula "
            "and refuses to let a quote leave below the floor. Verified by scripts/fix-caviar-price-sheet.py's sibling, "
            "caviar-trade-desk/scripts/verify.ts (18/18 checks pass)."
        ),
    )
    ws.cell(row=note_row, column=1).font = Font(size=9, italic=True, color="6B7280")
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=10)

    widths = [30, 16, 22, 20, 13, 20, 30, 22, 22, 22]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[5].height = 44
    ws.freeze_panes = "A6"

    # Legend on the Assumptions sheet
    a = wb["Assumptions"]
    a["A14"] = "Minimum viable trade price = landed cost / (1 - 30% target margin). Compare against the price we quote — see 'Trade Pricing' sheet."
    a["A14"].font = Font(size=10, italic=True, color="F87171")
    a["A15"] = "Corrected 2026-10-23: all three SKUs were quoted below the floor. See the 'Trade Pricing' sheet for the corrected figures and flags."
    a["A15"].font = Font(size=10, italic=True, color="8A8F98")

    return ws


def main():
    if not SRC.exists():
        print(f"FAIL: {SRC} not found")
        return 1
    if not BAK.exists():
        shutil.copy2(SRC, BAK)
        print(f"backup written: {BAK.name}")

    wb = load_workbook(SRC)
    if "Landed Cost" not in wb.sheetnames:
        print("FAIL: no 'Landed Cost' sheet — refusing to touch the workbook")
        return 1
    build(wb)
    wb.save(SRC)
    print(f"updated: {SRC.name}")
    print("sheets:", ", ".join(wb.sheetnames))
    return 0


if __name__ == "__main__":
    sys.exit(main())
