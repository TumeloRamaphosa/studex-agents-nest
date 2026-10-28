#!/usr/bin/env python3
"""Negative test for the Instagram hashtag-cap bug (fixed 2026-10-23).

THE BUG: build_platform_texts() trimmed Instagram's excess hashtags with
    ig_content = ig_content.replace(t + " ", "", 1)
The LAST tag in a caption has NO trailing space, so the replace() found
nothing and the tag survived. Instagram then shipped 6 hashtags against
Blotato's 5-tag cap. (Corrected 2026-10-23: the publish did NOT fail -
Blotato truncates to the first 5 server-side; live IG post 8383092 went out
with 5 tags from a 7-tag source. The trim makes the cut deterministic.)
The queue file for 2026-10-23
had exactly 6 tags, so the Friday 09:00 SAST post was 2.5 hours from failing.

This is the same shape as the markdown-residue bug: a sanitiser that looks
right and silently does nothing on the one input that matters.

The test proves the fix GOES RED on the old behaviour and GREEN on the new.
A test that only ever passes is worthless.

Usage: python3 ops/test-hashtag-cap.py
"""
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path("/workspace")


def load_daily_post():
    spec = importlib.util.spec_from_file_location(
        "daily_post", ROOT / "scripts" / "daily-post.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dp = load_daily_post()

FAILS = []
PASSES = []

# The real 2026-10-23 caption, truncated to the part that matters.
CAPTION = (
    "Your AI Forgets Everything. Ours Doesn't.\n\n"
    "Open a chat window. Ask a question. Close it. Open it again - and it knows "
    "nothing. No memory of your suppliers, your prices, your customers.\n\n"
    "Connect with our team: info@studexmeat.com\n\n"
    "#StudexGM #SuperAgents #AgenticAI #AfricanTech #BusinessGhostMemory #AIInfrastructure"
)


def tags_of(text):
    return re.findall(r"#[A-Za-z][A-Za-z0-9]*", text)


# 1. The real caption must produce <=5 Instagram tags.
texts = dp.build_platform_texts(CAPTION)
ig = tags_of(texts["instagram"])
if len(ig) <= 5:
    PASSES.append(f"real caption: instagram has {len(ig)} tags (cap 5) -> {ig}")
else:
    FAILS.append(f"real caption: instagram has {len(ig)} tags (cap 5) -> {ig}")

# 2. The tag removed must be the LAST one (the one with no trailing space).
if "#AIInfrastructure" not in ig:
    PASSES.append("last tag (no trailing space) was removed")
else:
    FAILS.append("last tag survived - the 'tag + space' replace() bug is back")

# 3. The kept tags must be the FIRST five, in order.
if ig == ["#StudexGM", "#SuperAgents", "#AgenticAI", "#AfricanTech", "#BusinessGhostMemory"]:
    PASSES.append("the first five tags are kept, in order")
else:
    FAILS.append(f"wrong tags kept: {ig}")

# 4. The caption must not end with stray whitespace after the trim.
if texts["instagram"] != texts["instagram"].rstrip():
    FAILS.append("instagram text has trailing whitespace after the tag trim")
else:
    PASSES.append("no trailing whitespace after the trim")

# 5. Exactly 5 tags must NOT be trimmed (no off-by-one).
five = CAPTION.replace(" #AIInfrastructure", "")
t5 = tags_of(dp.build_platform_texts(five)["instagram"])
if len(t5) == 5 and "#BusinessGhostMemory" in t5:
    PASSES.append("exactly-5 caption is left untouched (no off-by-one)")
else:
    FAILS.append(f"exactly-5 caption was altered: {t5}")

# 6. 6 tags where the LAST has a trailing space must ALSO be trimmed
#    (the old code handled that case - the fix must not regress it).
six_sp = CAPTION + " "
t6 = tags_of(dp.build_platform_texts(six_sp)["instagram"])
if len(t6) <= 5:
    PASSES.append("6 tags with a trailing space are trimmed too")
else:
    FAILS.append(f"6 tags with trailing space not trimmed: {t6}")

# 7. NEGATIVE: the OLD implementation must FAIL the cap. If the old code
#    passes, the test is not testing anything.
def old_build(content):
    clean = dp.socialize(content)
    ig_tags = re.findall(r"#[A-Za-z][A-Za-z0-9]*", clean)
    ig_content = clean
    if len(ig_tags) > 5:
        for t in ig_tags[5:]:
            ig_content = ig_content.replace(t + " ", "", 1)
    return ig_content


old_ig = tags_of(old_build(CAPTION))
if len(old_ig) > 5:
    PASSES.append(f"negative control: the OLD implementation FAILS the cap "
                  f"({len(old_ig)} tags) - the test is real")
else:
    FAILS.append("negative control: the OLD implementation PASSED - this test "
                 "cannot detect the bug it was written for")

print("=" * 70)
for p in PASSES:
    print("  PASS  " + p)
for f in FAILS:
    print("  FAIL  " + f)
print("=" * 70)
print(f"{len(PASSES)} passed, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
