#!/usr/bin/env python3
"""Prove the publish path does NOT block on an over-cap hashtag caption.

Blotato truncates to the first 5 hashtags server-side - it does NOT reject
with a 422 (live proof: the 2026-10-22 pending caption had 7 tags, the
fallback published it, and the live IG post 8383092 carries 5).

So a caption with 6-7 hashtags is a COSMETIC problem, not a publish blocker.
The SKILL tells the content agent to write "5-7 hashtags", so this is a
daily condition, not a hypothetical.

The bug this test locks down: validate_brand() FAILED on >5 extra tags in
the RAW caption, while its own comment said the limit "is enforced in
build_platform_texts() ... not here". The comment was right; the code was
not. Path A refused to publish a caption path B published without trouble
- and a FAIL stops the WHOLE post on every platform, not just Instagram.

The guard must never be stricter than the failure it guards against.
"""
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("dp", ROOT / "scripts" / "daily-post.py")
dp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dp)

TAGS = ["#StudexGM", "#SuperAgents", "#AgenticAI", "#AfricanTech",
        "#BusinessGhostMemory", "#AIInfrastructure", "#ExtraSeven"]


def caption(n_tags):
    body = ("Your AI Forgets Everything. Ours Doesn't.\n\n"
            "A paragraph of real body copy so the caption is not trivially short.\n\n"
            "Connect with our team: info@studexmeat.com\n\n"
            + " ".join(TAGS[:n_tags]))
    return body


fails = []


def check(name, cond, detail=""):
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                           ("  -> " + detail) if detail and not cond else ""))
    if not cond:
        fails.append(name)


print("=" * 74)
print("HASHTAG GUARD — must not block a caption Blotato would publish")
print("=" * 74)

print("\n-- validate_brand() must not FAIL on an over-cap caption --")
for n in (5, 6, 7):
    issues = dp.validate_brand(caption(n), "Agents", True)
    tag_issues = [i for i in issues if "hashtag" in i.lower()]
    check("%d tags: validate_brand does not block" % n,
          not tag_issues,
          "blocked with: %s" % tag_issues)

print("\n-- and the Instagram text it ships must be at the cap --")
for n in (5, 6, 7):
    ig = dp.build_platform_texts(caption(n))["instagram"]
    got = re.findall(r"#[A-Za-z][A-Za-z0-9]*", ig)
    check("%d tags -> IG ships exactly %d tags" % (n, min(n, 5)),
          len(got) == min(n, 5), "got %d: %s" % (len(got), got))

print("\n-- the guard still fires if the CUT is broken (negative control) --")
# If build_platform_texts stopped trimming, the guard must catch it.
real_build = dp.build_platform_texts
try:
    dp.build_platform_texts = lambda content: {"instagram": content}
    issues = dp.validate_brand(caption(7), "Agents", True)
    tag_issues = [i for i in issues if "hashtag" in i.lower()]
    check("broken cut -> validate_brand DOES block",
          bool(tag_issues),
          "the guard failed to catch an untrimmed 7-tag caption")
finally:
    dp.build_platform_texts = real_build

print("\n-- other validate_brand checks are unaffected --")
issues = dp.validate_brand(caption(5), "Agents", True)
check("a clean caption still passes validate_brand", not issues,
      "unexpected issues: %s" % issues)

print()
if fails:
    print("FAILED: %s" % ", ".join(fails))
    sys.exit(1)
print("all hashtag-guard checks passed")
