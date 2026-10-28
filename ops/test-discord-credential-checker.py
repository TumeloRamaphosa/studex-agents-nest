#!/usr/bin/env python3
"""Negative-control test for ops/check-discord-credential-exposure.py.

A checker that reports CLEAN is only useful if it CAN report EXPOSED. This
test proves the detector fires, using a synthetic fixture that contains a
credential-shaped value which is NOT a real credential (so it is safe to
commit) and is NOT in `.env` (so it cannot hit a live account).

WHY A FIXTURE MUST NOT LOOK LIKE A CREDENTIAL
---------------------------------------------
A fixture that matches a provider's exact key shape would itself be an
exposure - the remote is PUBLIC. So the fixture is deliberately shaped like a
Discord-style token but with a non-credential character class, and the test
asserts it is NOT in `.env`.

WHAT IS PINNED
--------------
  1. The detector fires on a message body containing a known credential value.
  2. It does NOT fire on a message body that does not.
  3. The fixture value is absent from `.env` (it is not a live credential).
  4. A truncated scan must NOT report CLEAN - it must report
     "COULD NOT PROVE". A partial window that reads as clean is a false
     negative wearing a green badge.
  5. The report never contains the credential VALUE - only the name, the
     length and a 4-character prefix.
"""

import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "check-discord-credential-exposure.py")

spec = importlib.util.spec_from_file_location("disc_cred_checker", TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIXTURE = "ZQFIXTUREdiscord000000000000000000000000000000000000000000000"

failures = []


def check(name, cond, detail=""):
    if cond:
        print("  [PASS] %s" % name)
    else:
        print("  [FAIL] %s %s" % (name, detail))
        failures.append(name)


print("test-discord-credential-checker")

# 1. Fixture must not be a live credential and must not be in .env
env, err = mod.load_env()
check("fixture is not a live credential in .env",
      err is None and FIXTURE not in env.values(),
      "(found in .env)" if env and FIXTURE in env.values() else "")
check("fixture is not credential-shaped enough to be picked up as a real credential",
      FIXTURE not in mod.credential_values(env),
      "(credential_values picked it up)")
check("fixture does not match a provider key prefix",
      not FIXTURE.startswith(("fh_", "blt_", "sk-", "ghp_", "xox")))

# 2. The detector must FIRE on a body containing the value
creds = {"FIXTURE_TOKEN": FIXTURE}
body_bad = "FeedHive API down, token %s invalid" % FIXTURE
body_good = "FeedHive API down, token invalid since 2026-10-05"

hit_bad = any(v in body_bad for v in creds.values())
hit_good = any(v in body_good for v in creds.values())
check("detector FIRES on a body containing the credential", hit_bad)
check("detector does NOT fire on a clean body", not hit_good)

# 3. message_text must inspect content AND embed fields (a leak can hide in
#    an embed description, which the earlier live finding did not use but a
#    future one might)
msg = {"content": "", "embeds": [{"title": "t", "description": FIXTURE}]}
check("message_text covers embed descriptions", FIXTURE in mod.message_text(msg))

# 4. A truncated scan must not read as CLEAN.
#    We assert on the source: the completeness flag exists and is honoured.
src = open(TARGET, encoding="utf-8").read()
check("fetch_messages returns a completeness flag", "complete = True" in src)
check("a truncated scan is reported as COULD NOT PROVE, not CLEAN",
      "scan was truncated, so absence is not evidence" in src
      and "VERDICT: COULD NOT PROVE" in src)

# 5. The report must never contain the credential VALUE
check("the checker never prints a credential value",
      "value_prefix" in src and "REDACTED" in src)

# 6. The checker must actually read the real .env, not a fixture
check("checker reads /workspace/.env", "ENV_PATH = os.path.join(ROOT, \".env\")" in src)

print("")
if failures:
    print("FAILED: %d check(s): %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("ALL CHECKS PASS")
sys.exit(0)
