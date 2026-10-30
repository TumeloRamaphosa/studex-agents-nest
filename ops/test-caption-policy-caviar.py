#!/usr/bin/env python3
"""Test the caviar rule in scripts/caption_policy.py.

THE DEFECT (2026-10-30): the pending caption for 2026-10-30 offered Oscietra
caviar and carried NO price, so the only caption rule - "no price on a public
feed" - never fired. Every gate read green and the caption went live on
Threads (DfG_M2bEd5U) at 08:56 SAST: a retail offer for a product with no SA
permit (the stack DFFE -> ITAC -> DAFF -> SARS -> CITES is unassembled) and 0
caviar products purchasable on the storefront.

THE RULE: a public feed caption must not offer caviar at all.

🔑 WHY THE NEGATIVE CONTROLS ARE THE POINT
A keyword rule is the easiest thing in the world to write wrong in the
dangerous direction: too narrow and it misses, too broad and it eats every
caption. So the controls below pin down BOTH edges:
  * a clean biltong/coffee/wagyu caption must NOT trip the rule
  * the pre-fix policy (no caviar clause) must NOT catch the offending
    caption - that is what proves this test is not vacuous
  * the EXISTING price rule must still fire - a fix that silences the rule it
    lives next to is not a fix
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
POLICY = REPO / "scripts" / "caption_policy.py"
CATALOG = REPO / "studex-content-automation" / "products" / "catalog.json"
AGENT = REPO / "studex-content-automation" / "scripts" / "daily-content-agent.js"
FAILS = []

# The exact caption that went live on 2026-10-30 (trimmed). It carries NO
# price, which is why it passed every gate.
CAVIAR_CAPTION = (
    "Some moments deserve more than champagne - they deserve caviar. Our "
    "Oscietra Imperial Caviar is the richest, most sought-after tier we "
    "carry: deep, nutty, with a clean finish and that unmistakable pop that "
    "turns an ordinary evening into a full-blown occasion. Just a chilled "
    "100g tin, a mother of pearl spoon, and good company. So tell us - who "
    "is the one person you'd share your first tin with? Tag them below, or "
    "send us a message to reserve yours.\n\n#oscietracaviar #studex "
    "#luxuryfoodsa #southafrica #gourmetliving"
)

CLEAN_CAPTIONS = [
    "Slow air-dried Wagyu biltong, cut into ribbons. Tag us below.",
    "Our Rwanda washed coffee is roasted in South Africa and shipped worldwide.",
    "One box. Every premium taste. The Fire & Feast Box is a gift that lands.",
    "A chatbot answers. An agent finishes the job. You ask a chatbot to do it.",
]


def check(label, cond, detail=""):
    if cond:
        print("PASS  %s" % label)
    else:
        print("FAIL  %s %s" % (label, detail))
        FAILS.append(label)


def run_cli(policy, args):
    p = subprocess.run([sys.executable, str(policy)] + args,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def pre_fix_policy(tmpdir):
    """A copy of caption_policy.py with the caviar clause removed.

    This is the NEGATIVE CONTROL: the pre-fix policy must NOT catch the
    offending caption. If it did, the test would be proving nothing.
    """
    src = POLICY.read_text(encoding="utf8")
    # strip the clause from policy_failures and the predicate it calls
    stripped = src.replace("if caviar_offer(caption):", "if False:")
    assert stripped != src, "the caviar clause is not where the test expects it"
    p = pathlib.Path(tmpdir) / "caption_policy_prefix.py"
    p.write_text(stripped, encoding="utf8")
    return p


print("=== A. THE REAL DEFECT (2026-10-30) - A PRICE-LESS CAVIAR OFFER ===")
rc, out = run_cli(POLICY, ["--check-text", CAVIAR_CAPTION])
check("a caviar offer with no price is a violation", rc == 1, "rc=%d out=%s" % (rc, out[-300:]))
check("the failure names caviar", "Caviar" in out, out[-300:])
check("the failure names the permit stack", "CITES" in out, out[-300:])
check("the failure does not merely complain about a price",
      "Price published on public feed" not in out, out[-300:])

print("\n=== B. NEGATIVE CONTROL - THE PRE-FIX POLICY DOES NOT CATCH IT ===")
with tempfile.TemporaryDirectory() as td:
    prefix = pre_fix_policy(td)
    rc2, out2 = run_cli(prefix, ["--check-text", CAVIAR_CAPTION])
    check("the pre-fix policy passes the offending caption", rc2 == 0,
          "rc=%d out=%s" % (rc2, out2[-300:]))
    check("so the test above is not vacuous", rc2 == 0 and rc == 1,
          "prefix rc=%d, fixed rc=%d" % (rc2, rc))

print("\n=== C. CLEAN CAPTIONS MUST NOT TRIP THE RULE ===")
for cap in CLEAN_CAPTIONS:
    rc3, out3 = run_cli(POLICY, ["--check-text", cap])
    check("clean caption is publishable: %r" % cap[:38], rc3 == 0,
          "rc=%d out=%s" % (rc3, out3[-200:]))

print("\n=== D. THE EXISTING PRICE RULE MUST STILL FIRE ===")
rc4, out4 = run_cli(POLICY, ["--check-text", "Wagyu Biltong Gold R1,450 per box."])
check("a price is still a violation", rc4 == 1, "rc=%d out=%s" % (rc4, out4[-200:]))
check("the price rule still names itself", "Price published on public feed" in out4, out4[-200:])

print("\n=== E. THE GRADE NAMES AND HASHTAG FORMS ARE CAUGHT TOO ===")
for probe in ["Oscietra, the aristocrat of the sea.", "Kaluga amber, reserve a tin.",
              "Sevtruga for the holidays.", "#oscietracaviar on sale tonight.",
              "Beluga, if you must ask."]:
    rc5, out5 = run_cli(POLICY, ["--check-text", probe])
    check("caught: %r" % probe[:40], rc5 == 1, "rc=%d out=%s" % (rc5, out5[-200:]))

print("\n=== F. THE UPSTREAM FIX - CAVIAR IS OUT OF THE FEED ROTATION ===")
cat = json.loads(CATALOG.read_text(encoding="utf8"))
products = cat.get("products", cat)
cav = [p for p in products if p.get("id") == "caviar-oscietra"]
check("the caviar record still exists (the price stays registry-owned)",
      len(cav) == 1, "catalog has %d caviar records" % len(cav))
check("caviar is NOT available for the feed rotation",
      cav and cav[0].get("available") is False, str(cav[0].get("available")) if cav else "-")
check("the retirement is documented in the record",
      cav and bool(cav[0].get("_feed_retired")), "no _feed_retired note")
avail = [p["id"] for p in products if p.get("available")]
check("the rotation pool no longer contains caviar",
      "caviar-oscietra" not in avail, str(avail))
agent_src = AGENT.read_text(encoding="utf8")
check("the agent's rotation really filters on `available`",
      "filter(p => p.available)" in agent_src,
      "getTodayProduct does not filter on p.available")
check("a forced caviar cannot bypass the rotation either",
      "if (p && p.available) return p;" in agent_src,
      "forceId does not require p.available")

print("\n=== G. THE PENDING-FILE CLI PATH CATCHES IT TOO ===")
with tempfile.TemporaryDirectory() as td:
    pf = pathlib.Path(td) / "pending.json"
    pf.write_text(json.dumps({"caption": CAVIAR_CAPTION}), encoding="utf8")
    rc6, out6 = run_cli(POLICY, ["--check-pending", str(pf)])
    check("--check-pending exits 1 on a caviar caption", rc6 == 1,
          "rc=%d out=%s" % (rc6, out6[-200:]))
    pf2 = pathlib.Path(td) / "clean.json"
    pf2.write_text(json.dumps({"caption": CLEAN_CAPTIONS[0]}), encoding="utf8")
    rc7, out7 = run_cli(POLICY, ["--check-pending", str(pf2)])
    check("--check-pending exits 0 on a clean caption", rc7 == 0,
          "rc=%d out=%s" % (rc7, out7[-200:]))

print("\n=== H. THE PUBLISH GATE (path B) READS THIS SAME POLICY ===")
fb = REPO / "studex-content-automation" / "scripts" / "blotato-fallback.js"
fb_src = fb.read_text(encoding="utf8")
check("path B's policyFailures() calls caption_policy.py",
      "caption_policy.py" in fb_src, "blotato-fallback.js does not call the policy")
check("path B's policyFailures() keys on the FAIL marker",
      "startsWith('FAIL')" in fb_src, "policyFailures does not read the FAIL lines")
dp = REPO / "scripts" / "daily-post.py"
dp_src = dp.read_text(encoding="utf8")
check("path A's validate_brand() calls the same policy_failures()",
      "caption_policy.policy_failures(content)" in dp_src,
      "daily-post.py does not call caption_policy.policy_failures")

print("")
if FAILS:
    print("%d CHECK(S) FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("ALL CHECKS PASS")
