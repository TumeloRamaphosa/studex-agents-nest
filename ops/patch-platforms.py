"""Fix: PLATFORMS must be derived from BLOTATO_ACCOUNTS.

The log entry printed "**Platforms:** " + ", ".join(PLATFORMS). That list was
["facebook", "instagram", "twitter", "linkedin"]:
  - it listed 'twitter', which is NOT in BLOTATO_ACCOUNTS and is NEVER attempted
  - it omitted 'threads', which IS in BLOTATO_ACCOUNTS and IS always attempted

So the daily log misreported the platforms on every post. A log that names a
platform we never posted to is exactly the class of false claim this repo keeps
fighting. Derive the list from the single source of truth so it cannot drift.
"""
import re

P = "scripts/daily-post.py"
src = open(P, encoding="utf8").read()
orig = src

old = 'PLATFORMS = ["facebook", "instagram", "twitter", "linkedin"]'
assert old in src, "PLATFORMS literal not found"

# BLOTATO_ACCOUNTS is defined after PLATFORMS in the file, so derive the list
# AFTER the dict instead of hardcoding it twice.
new = ('# The platforms we actually publish to. Derived from BLOTATO_ACCOUNTS below\n'
       '# so it can never drift from what is really attempted — the previous\n'
       '# hardcoded list named "twitter" (never attempted) and omitted "threads"\n'
       '# (always attempted), so every daily log misreported the platforms.\n'
       'PLATFORMS = None  # set from BLOTATO_ACCOUNTS once that dict exists')
src = src.replace(old, new, 1)

# Insert the derivation right after the BLOTATO_ACCOUNTS dict closes.
m = re.search(r'BLOTATO_ACCOUNTS\s*=\s*\{.*?\n\}\n', src, re.S)
assert m, "BLOTATO_ACCOUNTS dict not found"
src = src[:m.end()] + '\nPLATFORMS = sorted(BLOTATO_ACCOUNTS)\n' + src[m.end():]

assert 'PLATFORMS = None' in src
assert 'PLATFORMS = sorted(BLOTATO_ACCOUNTS)' in src
assert src != orig
open(P, "w", encoding="utf8").write(src)
print("PLATFORMS now derived from BLOTATO_ACCOUNTS")
