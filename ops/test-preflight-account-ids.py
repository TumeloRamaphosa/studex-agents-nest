#!/usr/bin/env python3
"""The pre-flight must catch a STALE Blotato account id, not just a missing platform.

🔴 THE GAP (found 2026-10-28, 02:30 UTC)
------------------------------------------
`scripts/daily-post.py` publishes with a HARDCODED one-id-per-platform map:

    BLOTATO_ACCOUNTS = {
        "facebook": "38744", "instagram": "76978",
        "linkedin": "26628", "threads": "7701",
    }

The pre-flight's account check asked only:

    attempted = [a for a in rows if a.get("platform") in dp.BLOTATO_ACCOUNTS]
    missing  = set(dp.BLOTATO_ACCOUNTS) - {a.get("platform") for a in attempted}

i.e. "is SOME account of this platform connected?" - which stays TRUE when
the account we actually POST to has been removed or reconnected under a
different id.

So: the account id is stale, another account of the same platform is
connected, and the pre-flight prints

    accounts for platforms we attempt: ['facebook', 'instagram', ...]

in green - while the publisher POSTs into a void and that platform's post
is silently lost.

🔑 THIS IS NOT HYPOTHETICAL. Reconnecting Meta is the top blocker on the
board (the Meta Page token expired 27-Jun-2026) and reconnecting is
exactly the action that can change an account id. Until it happens this
check has no input - which is why it has to exist BEFORE, not after.

THE FIX
-------
`account_id_verdict(targeted, live_rows)` returns:
  stale      - a targeted id that is not live, while that platform HAS
               live accounts  -> BLOCKS
  untargeted - a live account on a platform we target that we do not post
               to               -> NOTE (informational)

A platform with NO live account at all is left to the existing
platform-level WARN: the other platforms still publish, so blocking there
would be over-severe.

NEGATIVE CONTROL
----------------
The ORIGINAL platform-only implementation is reconstructed here and applied
to the same fixtures, to prove it misses the stale-id case that the fixed
one catches.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "ops" / "preflight-daily-post.py"

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


def _fn(text, name):
    m = re.search(r"def %s\(.*?\n(?=\ndef |\nclass )" % name, text, re.S)
    if not m:
        return None
    ns = {}
    try:
        exec(compile(m.group(0), "<fn>", "exec"), ns)
    except Exception:
        return None
    return ns.get(name)


# The REAL hardcoded map, copied from scripts/daily-post.py.
TARGETED = {
    "facebook": "38744", "instagram": "76978",
    "linkedin": "26628", "threads": "7701",
}

# The live connections as of 2026-10-28 (GET /v2/users/me/accounts).
LIVE = [
    {"id": "38744", "platform": "facebook", "username": ""},
    {"id": "76978", "platform": "instagram", "username": "ramaphosatumelo"},
    {"id": "55765", "platform": "instagram", "username": "laisa_aesthetics"},
    {"id": "26628", "platform": "linkedin", "username": ""},
    {"id": "7701", "platform": "threads", "username": "ramaphosatumelo"},
]


def main():
    text = PREFLIGHT.read_text(encoding="utf8")

    verdict = _fn(text, "account_id_verdict")
    check("the pre-flight exposes account_id_verdict()", verdict is not None,
          "could not extract the function")
    if verdict is None:
        print("\nVERDICT: CHECKER BROKEN - refusing to report CLEAN.")
        print("%d passed, %d failed" % (len(PASSED), len(FAILED)))
        return 2

    # --- the healthy case: everything is live ---
    stale, untargeted = verdict(TARGETED, LIVE)
    check("no stale ids when every targeted account is live",
          stale == [], stale)
    check("the unused live account IS reported as untargeted",
          [u[1] for u in untargeted] == ["55765"], untargeted)
    check("the untargeted entry carries its username",
          untargeted and untargeted[0][2] == "laisa_aesthetics", untargeted)

    # --- THE DEFECT: our instagram id is gone, another one is connected ---
    stale2, _ = verdict({"instagram": "76978", "threads": "7701"},
                        [{"id": "55765", "platform": "instagram"},
                         {"id": "7701", "platform": "threads"}])
    check("a stale account id is detected", len(stale2) == 1, stale2)
    check("the stale entry names the platform and the stale id",
          stale2 and stale2[0] == ("instagram", "76978"), stale2)

    # --- a platform with NO live account is NOT a stale-id failure ---
    # (facebook is absent from the live rows entirely, so our facebook id
    # cannot be "stale" - the platform simply has no account, which the
    # existing platform-level WARN already owns.)
    stale3, _ = verdict({"facebook": "38744"},
                        [{"id": "55765", "platform": "instagram"}])
    check("a platform with no live account at all is NOT reported stale "
          "(the existing platform-level WARN owns that case)",
          stale3 == [], stale3)

    # --- ...but a platform WITH a live account and a stale id IS stale ---
    stale3b, _ = verdict({"facebook": "38744", "instagram": "76978"},
                         [{"id": "55765", "platform": "instagram"}])
    check("a stale id on a platform that has another live account IS stale",
          stale3b == [("instagram", "76978")], stale3b)
    check("a platform with no live account is not stale, but its sibling is",
          ("facebook", "38744") not in stale3b and
          ("instagram", "76978") in stale3b, stale3b)

    # --- no live rows at all must not invent a failure ---
    stale4, unt4 = verdict(TARGETED, [])
    check("no live rows produces no stale ids and no untargeted accounts",
          stale4 == [] and unt4 == [], (stale4, unt4))

    # --- ids may arrive as ints ---
    stale5, _ = verdict({"instagram": 76978}, [{"id": 76978, "platform": "instagram"}])
    check("an int account id matches a string target (and vice versa)",
          stale5 == [], stale5)

    # --- the call site must actually use it ---
    flat = re.sub(r"\s+", " ", text)
    check("the call site uses account_id_verdict()",
          "account_id_verdict(dp.BLOTATO_ACCOUNTS, rows)" in flat)
    check("a stale id BLOCKS (it calls fail(), not warn())",
          re.search(r"stale, untargeted = account_id_verdict\(dp\.BLOTATO_ACCOUNTS, rows\)\s+for platform, acct in stale:\s+fail\(", flat)
          is not None)
    check("an untargeted live account is a NOTE, not a failure",
          re.search(r"for platform, aid, user in untargeted:\s+note\(", flat)
          is not None)

    # --- NEGATIVE CONTROL: the ORIGINAL platform-only check ---
    def original_stale(targeted, live_rows):
        """The ORIGINAL check: platform presence only, never the id."""
        attempted = [a for a in live_rows
                     if a.get("platform") in targeted]
        missing = set(targeted) - {a.get("platform") for a in attempted}
        return missing

    orig = original_stale({"instagram": "76978", "threads": "7701"},
                          [{"id": "55765", "platform": "instagram"},
                           {"id": "7701", "platform": "threads"}])
    check("NEGATIVE: the ORIGINAL check reported NOTHING wrong "
          "(platform present, so it stayed silent)", orig == set(), orig)
    check("NEGATIVE: the FIXED check catches exactly that case",
          len(stale2) == 1)
    check("NEGATIVE: they differ - the original missed the stale id",
          orig == set() and len(stale2) == 1)
    check("NEGATIVE: the original DID catch a missing platform (so the "
          "new check is additive, not a replacement)",
          original_stale({"facebook": "38744"},
                         [{"id": "7701", "platform": "threads"}])
          == {"facebook"})

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        print("VERDICT: BROKEN - a stale Blotato account id would not be "
              "caught before the publish.")
        return 1
    print("VERDICT: CLEAN - a stale Blotato account id BLOCKS the post.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
