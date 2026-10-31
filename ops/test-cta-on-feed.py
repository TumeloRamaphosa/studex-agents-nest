#!/usr/bin/env python3
"""Test ops/check-cta-on-feed.py.

THE DEFECT (2026-10-31): Threads captions are capped at 500 chars and both
publish paths cut at 497 chars + "...", while the CTA lives at the END of a
caption - so the truncation deleted exactly the CTA. Measured on the LIVE
feed: Instagram 5/5 posts carry a CTA, Threads 0/5 do (every one exactly 500
chars). Threads 3 likes vs Instagram 47; EVERY post 0 comments, 0 follows,
0 shares.

The fix is in scripts/caption_policy.py (truncate_for_platform cuts the PROSE
and keeps the CTA + hashtags). This checker is the other half: it audits the
LIVE feed for posts that are ALREADY CTA-less, so they stay visible in the
hourly pass until a human fixes them (Blotato has no edit or delete route).

🔑 WHY THE NEGATIVE CONTROLS ARE THE POINT
A "is there a CTA?" check is trivially satisfiable by a rule that always
returns True or always returns False. The controls below pin down BOTH
edges:
  * a real CTA caption must NOT be flagged (no false positives - the remedy
    is a human editing a live post)
  * a truncated caption with a rhetorical "?" EARLY IN THE PROSE must be
    flagged (this is the false negative that a naive "contains a ?" test
    would miss - measured on live post 8591759, cut mid-word at 500 chars
    with a "?" at character 86)
  * another brand's account must be SKIPPED, never flagged
  * the contract must hold: 0 clean, 1 finding, 2 could-not-prove
"""
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "check-cta-on-feed.py"
FAILS = []


def check(cond, label):
    if cond:
        print("  PASS  %s" % label)
    else:
        print("  FAIL  %s" % label)
        FAILS.append(label)


def load_checker():
    spec = importlib.util.spec_from_file_location("cta_on_feed", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def post(pid, text, platform="threads", account_id="7701", account_name="ramaphosatumelo"):
    return {
        "id": pid,
        "platform": platform,
        "text": text,
        "postTime": "2026-10-29T06:56:34.000Z",
        "account": {"id": account_id, "name": account_name},
    }


def main():
    mod = load_checker()

    print("=== A. THE ORIGINAL DEFECT IS REAL: truncation removes the CTA ===")
    # The real pending caption from the repo (751 chars -> published at 500).
    import json
    real = json.loads(
        (REPO / "studex-content-automation" / "posts" / "pending" / "2026-10-29.json")
        .read_text(encoding="utf8"))["caption"]
    old_cut = real[:497].rsplit(" ", 1)[0] + "..."
    check("Now tell us" not in old_cut,
          "the old 497-char cut DID delete the CTA (defect reproduced)")
    check(mod.has_cta(old_cut) is False,
          "has_cta() is False on the truncated caption")
    check(mod.has_cta(real) is True,
          "has_cta() is True on the pre-truncation caption")

    print("\n=== B. a caption WITH a CTA is NOT flagged (no false positives) ===")
    good = [
        "Slow air-dried biltong. Which pack do you reach for? #studex",
        "Our Rwanda coffee, roasted here. Connect with our team: info@studexmeat.com",
        "A gift that lands. DM us to order. #studex",
        "Order online and we deliver anywhere in South Africa. Now tell us: "
        "are you team braai or team cast-iron pan? #studex",
    ]
    for cap in good:
        check(mod.has_cta(cap), "has_cta() is True on: %r" % cap[:48])
    hits, _ = mod.scan_items([post("1", c) for c in good], accounts={"7701"})
    check(hits == [], "no good caption is flagged")

    print("\n=== C. a DEAD-STOP caption IS flagged ===")
    dead = [
        "Slow air-dried biltong, cut into ribbons and seasoned the old way.",
        "Our Rwanda coffee is roasted in South Africa and shipped worldwide.",
        # A rhetorical question EARLY in the prose, then truncation: this is
        # the FALSE NEGATIVE a naive 'contains a ?' test would miss.
        "Ever wondered why biltong tastes different? It is the air drying over "
        "days that nothing else can rush - " + ("and more words here " * 40),
    ]
    for cap in dead:
        hits, _ = mod.scan_items([post("1", cap)], accounts={"7701"})
        check(len(hits) == 1, "a dead-stop caption IS flagged: %r" % cap[:48])

    print("\n=== D. the LIVE truncation case is caught (the false negative) ===")
    # Reproduces live post 8591759: cut mid-word at 500 chars, "?" at char 86.
    live_like = ("Ever wondered why biltong tastes different? It is the air "
                 "drying over days that nothing else can rush - " + ("x" * 430))[:500]
    hits, _ = mod.scan_items([post("8591759", live_like)], accounts={"7701"})
    check(len(hits) == 1,
          "a truncated caption with an early '?' IS flagged (the false negative)")
    check("?" in live_like[:90],
          "the negative control really does contain an early '?'")
    check(mod.has_cta(live_like) is False,
          "has_cta() is False even though the '?' is present early")

    print("\n=== E. another brand's account is SKIPPED, never flagged ===")
    items = [
        post("111", "Biltong that tastes like memory.", account_id="55765",
             account_name="laisa_aesthetics"),
        post("222", "Biltong that tastes like memory.", account_id="7701"),
    ]
    hits, skipped = mod.scan_items(items, accounts={"7701"})
    check(len(hits) == 1 and hits[0]["id"] == "222",
          "only OUR post is flagged")
    check(any("55765" in s for s in skipped),
          "the other brand is reported as skipped: %s" % skipped)

    print("\n=== F. the contract: 0 clean, 1 finding, 2 could-not-prove ===")
    # No key -> could-not-prove, never clean.
    env_backup = (REPO / ".env").read_text(encoding="utf8")
    try:
        lines = [l for l in env_backup.splitlines()
                 if not l.strip().startswith("BLOTATO_API_KEY=")]
        (REPO / ".env").write_text("\n".join(lines) + "\n", encoding="utf8")
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True,
                           text=True, timeout=60)
        check(r.returncode == 2,
              "no key -> rc=2 (could-not-prove), never a clean 0")
        check("cannot prove" in (r.stdout + r.stderr).lower(),
              "the no-key path says it cannot prove")
    finally:
        (REPO / ".env").write_text(env_backup, encoding="utf8")
    # A bad key -> also could-not-prove.
    env_backup = (REPO / ".env").read_text(encoding="utf8")
    try:
        (REPO / ".env").write_text(
            env_backup + "\nBLOTATO_API_KEY=not-a-real-key\n", encoding="utf8")
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True,
                           text=True, timeout=90)
        check(r.returncode in (1, 2),
              "a bad key -> rc is a finding or could-not-prove, never a clean 0")
    finally:
        (REPO / ".env").write_text(env_backup, encoding="utf8")

    print("\n=== G. the checker is registered in the canonical registry ===")
    reg = (REPO / "ops" / "heartbeat-checkers.tsv").read_text(encoding="utf8")
    check("cta-on-feed |" in reg, "cta-on-feed is registered")
    check("check-cta-on-feed.py" in reg, "it points at the right script")
    check("| yes |" in reg.split("cta-on-feed |")[1].split("\n")[0],
          "it is registered as a KNOWN escalation (not re-announced hourly)")

    print("\n=== H. the fix and the checker SHARE the predicate ===")
    pol = (REPO / "scripts" / "caption_policy.py").read_text(encoding="utf8")
    check("from caption_policy import has_cta" in CHECKER.read_text(encoding="utf8"),
          "the checker imports the publish path's predicate (not a copy)")
    check("def has_cta" in pol, "the predicate lives in the shared policy module")

    print("\n" + "=" * 66)
    if FAILS:
        print("FAILED (%d):" % len(FAILS))
        for f in FAILS:
            print("  - %s" % f)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
