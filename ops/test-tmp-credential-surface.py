#!/usr/bin/env python3
"""Regression test for the /tmp credential-surface audit + the in-place redactor.

Proves the things that were broken on 2026-10-24:

  1. The audit script is NOT blind to a credential family it has no regex for.
     The original `KEY_RE` matched only `am_us_...`, so a `blt_...` key was
     invisible and the script reported "CLOSED" while 1,051 live literals sat
     in the active gateway log.

  2. The scan matches on the FULL VALUE of a credential, not a prefix regex.

  3. The audit script REFUSES to print a clean verdict while a live literal
     remains, and exits non-zero.

  4. The in-place redactor preserves the file's SIZE and INODE. The gateway
     holds the log open for append: swapping the inode would leave the
     process writing to an orphaned file while the visible log silently
     freezes. That is why we mask bytes in place rather than replacing the
     file.

  5. A DEAD key is left alone - masking a 403 key is not removing a usable
     secret.

  6. The redactor issues GET only. It must never mutate a provider.

No test fixture may carry a real credential. The real values are read from
.env AT RUNTIME and compared against the source files, so nothing secret is
written into this file.
"""
import importlib.util
import os
import pathlib
import re
import subprocess
import sys
import tempfile

WORKSPACE = pathlib.Path("/workspace")
AUDIT = WORKSPACE / "ops/tmp-credential-surface-audit.py"
REDACTOR = WORKSPACE / "ops/redact-live-secrets-in-place.py"
SELF = pathlib.Path(__file__).resolve()

failures = []
checks = 0


def check(cond, label):
    global checks
    checks += 1
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        failures.append(label)


def real_secrets():
    """Actual credential values from .env, read at runtime. Never printed."""
    out = []
    env = WORKSPACE / ".env"
    if not env.exists():
        return out
    name_re = re.compile(r"^(?:[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*)$")
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= 16 and name_re.match(k.strip()):
            out.append(v)
    return out


print("=== 1. the audit script is not blind to a credential family ===")
audit_src = AUDIT.read_text()
check("am_us_" in audit_src and "blt_" in audit_src,
      "audit script knows more than one provider family")
check("CRED_NAME_RE" in audit_src and "MIN_LEN" in audit_src,
      "audit script selects credentials by NAME, not by provider prefix")
check("CRED_NAME_RE.match" in audit_src,
      "audit script loads credentials via a name pattern (prefix-agnostic)")
# The old regex must be gone as the scanning mechanism.
check("KEY_RE.findall" not in audit_src,
      "the old prefix-regex findall scan is gone from the audit script")

print()
print("=== 2. the scan matches on the FULL VALUE of a credential ===")
check("data.count(value.encode())" in audit_src,
      "scan counts full-value occurrences")
check("encode()" in audit_src and "count(" in audit_src,
      "scan is a byte-level full-value count")

print()
print("=== 3. the audit script refuses a clean verdict while exposure remains ===")
check("EXPOSED" in audit_src and "VERDICT: CLEAN" in audit_src,
      "audit script has both an EXPOSED and a CLEAN verdict")
check("return 1" in audit_src,
      "audit script exits non-zero when exposure is found")
check("redact-live-secrets-in-place.py" in audit_src,
      "audit script points the reader at the tool that does the masking")

print()
print("=== 4. the in-place redactor preserves SIZE and INODE ===")
red_src = REDACTOR.read_text()
check("r+b" in red_src, "redactor opens the file r+b (in place, not replace)")
check('"wb"' not in red_src, "redactor never opens a file for truncate/rewrite")
check("st_ino" in red_src, "redactor reports the inode (proving it did not swap it)")
check("st_size" in red_src, "redactor reports the size (proving it did not truncate)")

print()
print("=== 5. the redactor's HTTP discipline ===")
# Look at CODE, not prose: the docstring legitimately contains the words
# "POST" and "DELETE" in sentences saying they are never used.
code_lines = [ln for ln in red_src.splitlines()
              if not ln.strip().startswith("#")
              and not re.search(r'"""|^\s*[^"].*"""', ln)]
code = "\n".join(code_lines)
# The only method= token in the source must be GET.
methods = re.findall(r'method\s*=\s*["\'](\w+)["\']', red_src)
check(methods == ["GET"], f"every request uses method=GET (found {methods})")
check("urlopen" in red_src, "redactor uses urlopen")
# No request-with-side-effect helpers.
for forbidden in ("urlopen(urllib.request.Request(url, data=",
                  "Request(url, data=", "shutil.rmtree", "os.remove", "os.unlink"):
    check(forbidden not in red_src, f"redactor does not use {forbidden!r}")

print()
print("=== 6. a DEAD key is left alone, a LIVE key is masked ===")
check('state == "DEAD"' in red_src and "left in place" in red_src,
      "redactor skips DEAD keys deliberately")
# The dead-key skip must be in the MASKING phase, not the scan phase.
mask_phase = red_src.split("=== masking in place ===")[-1]
scan_phase = red_src.split("=== masking in place ===")[0].split("=== scan ===")[-1]
check('state == "DEAD"' in mask_phase, "dead-key skip lives in the masking phase")
check('state == "DEAD"' not in scan_phase, "scan phase does not silently drop dead keys")

print()
print("=== 7. the redactor masks a synthetic value in place, preserving the file ===")
with tempfile.TemporaryDirectory() as td:
    target = pathlib.Path(td) / "sample.log"
    fake = "blt_SYNTHETIC_VALUE_FOR_TESTING_0123456789"
    target.write_bytes(b"prefix " + fake.encode() + b" suffix " + fake.encode() + b" end")
    before_size = target.stat().st_size
    before_ino = target.stat().st_ino
    spec = importlib.util.spec_from_file_location("redactor_mod", REDACTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    n, sz_before, sz_after, ino_before, ino_after = mod.mask_in_place(str(target), fake)
    after = target.read_bytes()
    check(n == 2, "mask_in_place masked both occurrences")
    check(ino_before == ino_after, "mask_in_place reports the inode unchanged")
    check(sz_before == before_size and sz_after == before_size,
          "file size unchanged after in-place masking")
    check(target.stat().st_ino == before_ino, "inode unchanged after in-place masking")
    check(fake.encode() not in after, "the literal is gone from the file")
    check(len(after) == before_size, "byte length preserved exactly")
    check(b"prefix " in after and b" end" in after,
          "surrounding content untouched - only the secret was replaced")

print()
print("=== 9. the audit WALKS the directory it claims to cover ===")
# The 04:47 audit scanned a hardcoded list of five files while the redactor
# had been run over nine. A "quarantine" is a RENAME, not a deletion, so the
# quarantine itself held six files with the live Blotato key and the audit
# reported CLEAN throughout. A checker that scans the files it was told
# about is not a checker of the directory it claims to cover.
check("walk_tmp" in audit_src, "audit script has a directory walk")
check("os.walk" in audit_src, "audit script walks the tree rather than listing files")
check("STALE_LOG" not in audit_src and "ACTIVE_LOG" not in audit_src,
      "the hardcoded per-file target list is gone from the audit script")
check("CONCURRENT" not in audit_src,
      "the hardcoded concurrent-session file list is gone from the audit script")
check("COVERAGE" in audit_src,
      "audit script prints a COVERAGE block (so a verdict states what it read)")
check("files read" in audit_src,
      "audit script reports how many files it actually read")

print()
print("=== 10. the audit and the redactor AGREE on what 'exposure' means ===")
# The redactor masks LIVE and UNKNOWN. The audit's verdict counted only
# `state == "live"`, so a key it could not probe was masked on disk and
# still did not count as exposure in the verdict. The two tools disagreed,
# and the audit under-reported what the redactor fixed.
check("is_exposed" in audit_src,
      "audit script has a single shared definition of 'exposed'")
check('state.startswith("unknown")' in audit_src,
      "UNKNOWN counts as exposure - an unprobeable key is not thereby safe")
# The state strings are not a clean enum: "unknown (no probe for this
# prefix)" != "unknown". A membership test against ("live", "unknown")
# silently counts ZERO unknowns.
check('state in ("live", "unknown")' not in audit_src,
      "the enum-membership test that silently counted zero unknowns is gone")

print()
print("=== 11. a credential family with no prefix CAN be probed ===")
# The GoDaddy key has NO prefix on its key and authenticates as
# `sso-key <key>:<secret>`. A prefix probe never fires for it, so it stayed
# UNKNOWN and uncounted even though it authenticates.
check("GODADDY" in audit_src,
      "audit script knows about the GoDaddy family")
check("sso-key" in audit_src,
      "audit script authenticates to GoDaddy the way GoDaddy requires")
check("GODADDY_API_SECRET" in audit_src,
      "audit script pairs the GoDaddy key with its secret")
check("sso-key" in red_src,
      "redactor authenticates to GoDaddy the way GoDaddy requires")
check("GODADDY_API_SECRET" in red_src,
      "redactor pairs the GoDaddy key with its secret")
check("classify(value," in red_src,
      "redactor's classify() can reach the env map (needed to pair key+secret)")

print()
print("=== 11b. the Orgo family is probed, not merely unprefixed ===")
# The Orgo key (`sk_live_...`) has no distinctive prefix, so it fell through
# to "unknown (no probe for this prefix)" -> counted as exposure -> masked ->
# and then RE-CREATED by the next diagnostic that printed it. The audit was
# manufacturing its own finding, and a DEAD key (HTTP 401) was treated as an
# exposure.
check("ORGO_API_KEY" in audit_src,
      "audit script probes the Orgo family by env NAME (no usable prefix)")
check("orgo.ai/api/computers" in audit_src,
      "audit script probes the Orgo API with GET")
check("ORGO_API_KEY" in red_src,
      "redactor classifies the Orgo family the same way the audit does")
check("orgo.ai/api/computers" in red_src,
      "redactor probes the Orgo API with GET")

print()
print("=== 12. the coverage check agrees with the audit ===")
# ops/tmp-credential-coverage-check.py exists to answer a question the
# audit itself could not: does the audit actually cover /tmp?
COVERAGE = WORKSPACE / "ops/tmp-credential-coverage-check.py"
check(COVERAGE.exists(), "the coverage check exists")
if COVERAGE.exists():
    cov_src = COVERAGE.read_text()
    check("os.walk" in cov_src, "the coverage check walks the tree too")
    check("NOT ON THE AUDIT LIST" in cov_src,
          "the coverage check reports files the audit list would miss")

print()
print("=== 13. no source file carries a real credential ===")
secrets = real_secrets()
check(len(secrets) > 0, "read real credential values from .env at runtime")
for path in (AUDIT, REDACTOR, SELF):
    txt = path.read_text()
    hits = sum(1 for s in secrets if s in txt)
    check(hits == 0, f"{path.name} carries none of the {len(secrets)} real credentials "
                      f"({hits} found)")
if COVERAGE.exists():
    txt = COVERAGE.read_text()
    hits = sum(1 for s in secrets if s in txt)
    check(hits == 0, f"{COVERAGE.name} carries none of the {len(secrets)} real "
                      f"credentials ({hits} found)")

print()
print("=== 14. no measurement/surfacing tool PRINTS a credential ===")
# stdout is captured into the gateway session log - which is exactly how
# live AgentMail keys ended up in /tmp/openclaw/openclaw-*.log. A tool
# that hunts for credentials must report them by SHAPE, never by value.
MEASURE = WORKSPACE / "ops/measure-cred-shapes.py"
SURFACED = WORKSPACE / "ops/check-surfaced-candidates.py"
SURFACED_LIVE = WORKSPACE / "ops/check-surfaced-candidates-live.py"
for p in (MEASURE, SURFACED, SURFACED_LIVE):
    if not p.exists():
        continue
    txt = p.read_text()
    hits = sum(1 for s in secrets if s in txt)
    check(hits == 0, f"{p.name} carries none of the {len(secrets)} real credentials "
                      f"({hits} found)")
if MEASURE.exists():
    m_src = MEASURE.read_text()
    check("def mask(" in m_src,
          "the shape scanner masks a matched candidate instead of printing it")
    check("}!r}" not in m_src,
          "the shape scanner no longer prints a raw matched credential")
    check("prefix=" in m_src,
          "the shape scanner reports a short prefix for identification only")
if SURFACED_LIVE.exists():
    s_src = SURFACED_LIVE.read_text()
    check("api.github.com" in s_src,
          "the GitHub probe uses api.github.com - probing github.com/... "
          "returns 404, which is inconclusive, not proof of death")
    check("inconclusive" in s_src,
          "the live probe distinguishes inconclusive from not-live")

print()
print("=== 15. a probe must speak the API's DIALECT ===")
# The audit probed AgentMail with a bare `Authorization: am_us_...` header.
# The API answers 403 to that and 200 to `Authorization: Bearer <key>`. The
# probe therefore read every LIVE AgentMail key as DEAD - and DEAD is the
# one class the redactor leaves in place. A probe that speaks the wrong
# dialect reports the wrong world, and it failed in the most dangerous
# direction: calling the living dead.
check("Bearer" in audit_src,
      "the audit authenticates to AgentMail with the Bearer scheme the API requires")
check("Bearer" in red_src,
      "the redactor authenticates to AgentMail with the Bearer scheme too")
check('headers={"Authorization": key}' not in audit_src,
      "the bare-Authorization AgentMail probe is gone from the audit script")
check('headers={"Authorization": key}' not in red_src,
      "the bare-Authorization AgentMail probe is gone from the redactor")

print()
print("=== 16. the redactor does not SKIP a file that has no LIVE key ===")
# The redactor early-returned when a scan found no LIVE credential, and its
# verify step only re-checked the LIVE class. So a file holding only
# UNKNOWN literals - which the audit counts as exposure, and which the
# redactor's own docstring promises to mask - was reported as clean and
# left untouched. The tool said "no LIVE credential literal" and the
# reader heard "clean".
check("if not live_hits:" not in red_src,
      "the redactor no longer skips masking because a file had no LIVE hit")
check("if not total_hits:" in red_src,
      "the redactor skips only when there are NO credential literals at all")
verify_phase = red_src.split("=== verify ===")[-1]
check('state == "DEAD"' in verify_phase,
      "the verify step skips DEAD keys (a dead key is not a credential)")
check('state == "LIVE"' not in verify_phase,
      "the verify step no longer re-checks ONLY the LIVE class - that is how "
      "a file full of UNKNOWN literals gets reported as clean")

print()
print(f"{checks - len(failures)}/{checks} checks passed")
if failures:
    print("FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ALL PASS")
