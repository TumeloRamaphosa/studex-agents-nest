#!/usr/bin/env python3
"""Point the registry at the newly deployed SPAs and retire the old URLs.

A redeploy creates a NEW url and the old one keeps serving the OLD copy - so
the page map AND the forbidden-string rows must both move, in the same commit
as the deploy. If only the page map moved, the forbidden-string assertions
would follow the dead slug, the new pages would have zero assertions, and the
checker would call them UNCHECKED again - which is exactly how two live pages
published "Rainforest Alliance certified" and "certified Russian caviar houses"
for a day while looking green.

  china-coffee-lead-capture: 1bl06cgsu643 -> jqbgl8pu0uyh
  studex-caviar:             2hkb7k7q2gni -> jgk62vzamgtk
"""
import pathlib, sys

REG = pathlib.Path("/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md")
r = REG.read_text(encoding="utf8")

MOVES = [("1bl06cgsu643", "jqbgl8pu0uyh"), ("2hkb7k7q2gni", "jgk62vzamgtk")]

# 1. the BARE backticked slugs (the "must not appear on" cells) move first,
#    while the retired table still holds them in full-domain form.
for old, new in MOVES:
    token = "`%s`" % old
    n = r.count(token)
    assert n >= 1, f"no bare slug {token} found"
    r = r.replace(token, "`%s`" % new)
    print(f"  moved bare slug {token} -> `{new}`  ({n} cell(s))")

# 2. the page map rows (full domain form) move too.
for old, new in MOVES:
    token = "`%s.space.mcode.io`" % old
    assert token in r, f"page-map row for {old} not found"
    r = r.replace(token, "`%s.space.mcode.io`" % new, 1)
    print(f"  moved page-map row {token} -> `{new}.space.mcode.io`")

# 3. the old URLs are RETIRED, not deleted - they keep serving the old copy.
anchor = "| `naq1ucjwxw49.space.mcode.io` | caviar trade, first clean rebuild | `2hkb7k7q2gni.space.mcode.io` |"
assert anchor in r
r = r.replace(anchor, anchor + """
| `1bl06cgsu643.space.mcode.io` | China lead capture — published **"Rainforest Alliance certified"** and linked `ceo@agent.studexmeat.com` (no DNS) while no assertion watched it | `jqbgl8pu0uyh.space.mcode.io` |
| `2hkb7k7q2gni.space.mcode.io` | caviar trade — published **"certified Russian caviar houses"** and "ethically sourced" while no assertion watched it | `jgk62vzamgtk.space.mcode.io` |""", 1)
print("  added retired-URL rows for both old SPA slugs")

# 4. record why the page map has SPA rows at all
note_anchor = "> **Price format rule (2026-10-21):**"
assert note_anchor in r
r = r.replace(note_anchor, """> **⚠️ CLIENT-RENDERED PAGES (React SPAs) — asserted against the BUILT BUNDLE, not the HTML.**
> A React page returns ~150 characters of HTML shell, so a text assertion against the fetched page
> proves nothing. These four were therefore UNCHECKED — and while nothing watched them,
> `china-coffee-lead-capture` published **"Rainforest Alliance certified"** (the unsourced claim
> we removed from the static China page on 2026-10-21) plus a link to `ceo@agent.studexmeat.com`,
> and `studex-caviar` published **"certified Russian caviar houses"** and "ethically sourced".
> All of it was live. The checker now asserts the built bundle for any page whose source dir
> ships a hashed `assets/` bundle, and it verifies that the live site is serving THAT build —
> a fixed source with no redeploy is reported as **STALE BUILD**, not as a pass.

""" + note_anchor, 1)
print("  added the SPA-checking note to the registry")

REG.write_text(r, encoding="utf8")
print("\nregistry updated.")
