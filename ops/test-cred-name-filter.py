#!/usr/bin/env python3
"""Validate the shared credential-name filter: the PAT segment rule.

Proves:
  1. a PAT-named credential is SELECTED (the bug this fixes),
  2. PATH-shaped names are NOT (the false-positive the rule must avoid),
  3. every credential name the old filter caught is still caught,
  4. the tools actually import the shared module instead of re-inlining it.
"""
import importlib.util
import os
import re
import sys

spec = importlib.util.spec_from_file_location('cnf', '/workspace/ops/cred_name_filter.py')
cnf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cnf)

fails = []


def check(cond, msg):
    if cond:
        print(f"PASS  {msg}")
    else:
        print(f"FAIL  {msg}")
        fails.append(msg)


print("=== 1. a PAT-named credential is SELECTED ===")
for name in ('GITHUB_PAT', 'GH_PAT', 'PAT', 'GITHUB_PAT_TOKEN'):
    check(cnf.is_cred_name(name), f"{name} is treated as a credential name")

print()
print("=== 2. PATH-shaped names are NOT (no false positives) ===")
for name in ('PATH', 'GITHUB_PATH', 'COMPAT', 'PATCH', 'PATTERN', 'MYPATX'):
    check(not cnf.is_cred_name(name), f"{name} is NOT treated as a credential name")

print()
print("=== 3. everything the old filter caught is still caught ===")
old = re.compile(r"^(?:[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*)$")
for name in ('FEEDHIVE_API_KEY', 'GITHUB_TOKEN', 'OPENAI_API_KEY', 'DISCORD_BOT_TOKEN',
             'AWS_SECRET_ACCESS_KEY', 'SHOPIFY_ADMIN_TOKEN', 'DB_PASSWORD'):
    check(old.match(name) is not None and cnf.is_cred_name(name),
          f"{name} is still caught (no regression)")

print()
print("=== 4. the tools import the shared module instead of re-inlining it ===")
TOOLS = [
    'check-scanner-log-exposure.py',
    'check-tracked-live-credentials.py',
    'redact-live-secrets-in-place.py',
    'redact-session-transcript-credentials.py',
    'close-scanner-leak.py',
    'check-surfaced-candidates.py',
    'heartbeat-verify-report.py',
    'tmp-credential-coverage-check.py',
]
INLINE = 'KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*'
for fn in TOOLS:
    p = os.path.join('/workspace/ops', fn)
    src = open(p).read()
    check('cred_name_filter.py' in src, f"{fn} imports the shared filter")
    check(INLINE not in src, f"{fn} does not re-inline the old regex")

print()
if fails:
    print(f"{len(fails)} FAILED")
    sys.exit(1)
print("ALL CHECKS PASS")
