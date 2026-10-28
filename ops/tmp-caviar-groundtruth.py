#!/usr/bin/env python3
"""Ground truth: what does the landed-cost model + registry say our caviar ORIGIN actually is?"""
import re, zipfile, os, sys

ROOT = "/workspace"

# ---- 1. the xlsx (no openpyxl dependency assumed) ----
p = os.path.join(ROOT, "caviar-landed-cost.xlsx")
print("=" * 74)
print("1. caviar-landed-cost.xlsx  (shared strings)")
print("=" * 74)
try:
    import openpyxl
    wb = openpyxl.load_workbook(p, data_only=False)
    for ws in wb.worksheets:
        print(f"\n--- sheet: {ws.title}  dims={ws.dimensions} ---")
        for row in ws.iter_rows():
            vals = []
            for c in row:
                if c.value is not None:
                    vals.append(f"{c.coordinate}={c.value!r}")
            if vals:
                print("   " + " | ".join(vals))
except Exception as e:
    print("openpyxl failed:", e)
    z = zipfile.ZipFile(p)
    ss = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
    strs = re.findall(r"<t[^>]*>(.*?)</t>", ss, re.S)
    for i, s in enumerate(strs):
        print(f"  [{i}] {s}")
