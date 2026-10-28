#!/usr/bin/env python3
"""Negative-test drift rule 4b: the note must agree with the authoritative JSON.

This rule was written AFTER the bug it catches actually happened: the
recipients JSON said 29 emails and the human-facing draft note still said 26,
and every check passed. So it must be proven to fire, and proven not to
false-positive on the legitimate historical figures the note must quote.

Run: python3 ops/test-note-json-consistency.py
"""
import json
import pathlib
import shutil
import subprocess
import sys

CORR = pathlib.Path("outbound-corrections")
BACKUP = pathlib.Path("/tmp/note-json-backup")
NOTE = CORR / "ciie-correction-note.md"
RJSON = CORR / "ciie-correction-recipients.json"

# (label, mutate_note_fn, expect_drift)
CASES = [
    ("stale total count (26 instead of 29) -> MUST FAIL",
     lambda t: t.replace("29 emails to 12 external buyers", "26 emails to 12 external buyers")
                .replace("12 external recipients, 29 emails", "12 external recipients, 26 emails"),
     True),
    ("wrong recipient count (9 instead of 12) -> MUST FAIL",
     lambda t: t.replace("12 external recipients", "9 external recipients"),
     True),
    ("wrong per-recipient count -> MUST FAIL",
     lambda t: t.replace("| 3 | 25 Sep, 29 Sep, 3 Oct |", "| 2 | 25 Sep, 29 Sep, 3 Oct |", 1),
     True),
    ("quoted historical '21 emails to 9 buyers' -> MUST PASS (we withdraw it)",
     lambda t: t.replace("## 📋 WHO — 12 external recipients, 29 emails",
                         "## 📋 WHO — 12 external recipients, 29 emails\n\n"
                         "The vault said \"21 emails to 9 buyers\" — wrong on both counts."),
     False),
    ("unmodified note -> MUST PASS", lambda t: t, False),
]

if BACKUP.exists():
    shutil.rmtree(BACKUP)

# A stale fixture from an INTERRUPTED run of ops/test-correction-rules.py
# ("ok.md") makes drift-check report DRIFT on outbound-corrections/ok.md for
# EVERY case - so the "MUST PASS" cases below fail, and the real drift check
# cries wolf on a test artefact. Remove it before taking the backup so the
# backup only ever contains real files.
STALE_FIXTURE = CORR / "ok.md"
if STALE_FIXTURE.exists():
    STALE_FIXTURE.unlink()
    print("  (removed a stale test fixture left by an interrupted run)")

shutil.copytree(CORR, BACKUP)

FAILS = []


def run():
    r = subprocess.run([sys.executable, "ops/drift-check.py"], capture_output=True, text=True, timeout=300)
    return r.stdout


try:
    for label, fn, expect in CASES:
        original = NOTE.read_text(encoding="utf8")
        NOTE.write_text(fn(original), encoding="utf8")
        out = run()
        drift = "DRIFT DETECTED" in out
        ok = drift == expect
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:<58} drift={drift} expected={expect}")
        if not ok:
            FAILS.append(label)
        for l in [x.strip() for x in out.splitlines()
                  if x.strip().startswith("- outbound-corrections/ciie-correction-note.md")][:2]:
            print(f"          {l[:150]}")
        NOTE.write_text(original, encoding="utf8")
finally:
    NOTE.write_text((BACKUP / NOTE.name).read_text(encoding="utf8"), encoding="utf8")
    shutil.rmtree(BACKUP, ignore_errors=True)

print("\nrestored note from backup")
if FAILS:
    print(f"RESULT: {len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("RESULT: rule 4b proven to fire and not to false-positive")
