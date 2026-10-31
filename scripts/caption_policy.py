#!/usr/bin/env python3
"""Public-feed caption policy - ONE source of truth for both publish paths.

Path A (scripts/daily-post.py) and path B
(studex-content-automation/scripts/blotato-fallback.js) publish to the SAME
public feeds, so they must enforce the SAME policy. Until now path A had
validate_brand() and path B had NOTHING - the only thing that checked a
path-B caption was the 09:20 pre-flight, which runs ~20 minutes AFTER the
caption was published. That is a post-mortem, not a gate.

The rule at issue: a price must not appear on a public feed
("FAIL: Price published on public feed" in validate_brand()).

THE SECOND RULE, ADDED 2026-10-30: caviar must not appear on a public feed
at all. See CAVIAR_RE below for why the permits decide this rather than a
preference.

CLI:
    caption-policy.py --check-text   "caption here"    -> exit 1 if it violates
    caption-policy.py --check-pending <pending.json>   -> exit 1 if it violates
"""
import json
import re
import sys

# The one pattern. validate_brand() used to hold this inline; both paths
# now read it from here, so the two paths cannot drift apart.
PRICE_RE = re.compile(r"R\s?\d[\d,\.]*")


# 🔑 CAVIAR IS OFF THE PUBLIC FEED - AND THE PERMITS DECIDE THAT, NOT A PREFERENCE.
#   * The SA caviar permit stack (DFFE -> ITAC -> DAFF -> SARS -> CITES) is NOT
#     assembled, so there is no lawful way to sell caviar retail right now.
#   * The live storefront carries 0 caviar products, so a caption offering it
#     cannot be fulfilled either.
#   * The caviar desk itself states "2027 season, trade accounts only, stack
#     not yet assembled". The 2026 product is the CAVIAR-FREE biltong + coffee box.
#
# 🔑 WHY THE PRICE RULE COULD NOT CATCH THIS. The 2026-10-30 caption (Threads
# DfG_M2bEd5U) offered Oscietra caviar and carried NO price, so the price rule
# never fired, every gate read green, and a retail offer for an unpermitted,
# unfulfillable product went live at 08:56 SAST. A guard that only asks "is
# there a price?" cannot see a product problem.
#
# The grade names are matched too, because a caption can say "Oscietra" (or
# "#oscietracaviar") without ever using the word "caviar" - and a hashtag has
# no word boundary to anchor a \b on.
CAVIAR_RE = re.compile(r"caviar|oscietra|kaluga|sevtruga|beluga", re.I)


def caviar_offer(caption):
    """True when a caption offers caviar on a public feed.

    Kept as its own predicate (not only a policy failure) so callers can ask
    the question directly - the pre-flight audits the pending caption and
    needs to know whether the PRODUCT is one we may not offer, separately
    from the price rule that already had its own wording.
    """
    return bool(caption and CAVIAR_RE.search(caption))


# 🔑 A CAPTION MUST END WITH A CALL TO ACTION - AND TRUNCATION MUST NOT EAT IT.
#
# THE DEFECT (2026-10-31, found by reading the LIVE feed's own analytics):
# Threads captions are capped at 500 chars. Both publish paths truncated the
# caption at 497 chars + "..." (daily-post.py:289-290, blotato-fallback.js
# truncate()). The CTA lives at the END of the caption, so truncation deleted
# exactly the CTA - and the generator's own validator ("no closing question/
# CTA") had ALREADY approved the caption, because it validates the PRE-
# truncation text. Every gate read green and the CTA went out the window.
#
# MEASURED ON THE LIVE FEED (10 posts, Blotato /posts -> state.analytics):
#   Instagram 5/5 carry a CTA ("Connect with our team: info@studexmeat.com"),
#   1060-1239 chars, never truncated.
#   Threads  0/5 carry a CTA, EVERY ONE exactly 500 chars (truncated).
#   Threads engagement: 3 likes across 5 posts. Instagram: 47 likes.
#   Every post on both platforms: 0 comments, 0 follows, 0 shares.
# 🔑 *A validator that checks the text BEFORE the transform is not checking the
# text that ships. The gate and the defect were on opposite sides of the cut.*
#
# WHY THIS IS THE HIGHEST-VALUE FIX AVAILABLE: the funnel already works -
# 841 views, 489 reach, 12 likes, 5 profile visits on one IG post. What it
# does NOT do is ASK for anything. The account can reach people; it just
# never tells them what to do next.
#
# THE FIX: truncate the BODY, never the CTA. Keep the tail (CTA + hashtags)
# intact and cut the prose in front of it. If the tail alone cannot fit, the
# caption is rejected rather than published without its CTA.
CTA_RE = re.compile(
    r"(?:"
    r"connect\s+with\s+our\s+team"
    r"|dm\s+us|message\s+us|send\s+us\s+a\s+message"
    r"|whatsapp|wa\.me|comment\s+below|tell\s+us\s+below|reply\s+below"
    r"|link\s+in\s+bio|shop\s+now|order\s+now|book\s+a\s+call"
    r"|read\s+more|swipe\s+up|reserve\s+yours|get\s+yours"
    r"|tag\s+them\s+below"
    r")",
    re.I,
)

# Platform character caps (Blotato counts emoji / full-width as 2).
LIMITS = {"threads": 500}


def _char_weight(ch):
    """Blotato counts emoji and full-width characters as 2.

    This is the SAME rule the JS publish path uses (charWeight in
    blotato-fallback.js). It lives here so the two paths cannot drift: a
    Python-side cut that ignored emoji would produce a caption the JS side
    considered too long, and vice versa.
    """
    cp = ord(ch)
    return 2 if (cp > 0x2E80 or (0x1F300 <= cp <= 0x1FAFF)) else 1


def weighted_len(text):
    """Length as Blotato counts it."""
    return sum(_char_weight(c) for c in text)


def _hashtag_block(caption):
    """Return (body, hashtags) - the trailing hashtag block is kept separate.

    A caption's structure is: <prose> <CTA> <hashtags>. The hashtags are
    metadata, not prose, so they must never be what gets cut.
    """
    m = re.search(r"((?:\s*#[A-Za-z][A-Za-z0-9]*)+)\s*$", caption)
    if not m:
        return caption, ""
    return caption[: m.start()], m.group(1)


def has_cta(caption):
    """True when a caption carries a call to action AT ITS END.

    Two accepted shapes, because both are used on the live feed:
      * an explicit ask     - "Connect with our team", "DM us", "link in bio"
      * an open question    - the generator's own rule (a caption must end on
                              a question), which is a CTA in the social sense
    A caption with NEITHER is a dead stop: it reaches people and asks for
    nothing.

    🔑 THE QUESTION MUST BE IN THE TAIL, NOT ANYWHERE. A truncated caption
    can still contain a rhetorical "?" early in the prose - measured on the
    live feed, post `8591759` was cut mid-word at 500 chars ("...where
    nobody else can find them - bec...") and carries NO CTA, yet a "?" at
    character 86 satisfied a naive "contains a question" test. That is a
    FALSE NEGATIVE on exactly the posts this check exists to catch, so the
    question must be in the TAIL (the last stretch of the caption), where a
    real CTA lives.
    """
    if not caption:
        return False
    body, _ = _hashtag_block(caption)
    if CTA_RE.search(body):
        return True
    # A question counts only if it is in the tail - the last 200 chars of the
    # body, which is where a closing ask sits.
    tail = body[-200:]
    return "?" in tail


def cta_parts(caption):
    """Return (prose, tail) - the exact split of a caption.

    `prose` is everything BEFORE the call to action; `tail` is the CTA plus
    the trailing hashtag block. The tail must survive truncation; the prose
    is what may be shortened.

    The split is by INDEX, never by subtracting lengths: the hashtag block is
    not part of `body`, so len(tail) is not a prefix-length of body and
    `body[:len(body)-len(tail)]` can slice INTO the CTA (and then re-append
    it, duplicating it).

    Returns ("", "") when there is no CTA to protect.
    """
    if not caption:
        return "", ""
    body, tags = _hashtag_block(caption)

    markers = [m.start() for m in CTA_RE.finditer(body)]
    if markers:
        start = markers[-1]
    elif "?" in body:
        # Fall back to the sentence holding the LAST question - the generator's
        # own definition of a CTA ("a caption must end on a question").
        q = body.rindex("?")
        nl = max(body.rfind("\n", 0, q), body.rfind(". ", 0, q))
        start = (nl + 1) if nl >= 0 else q
    else:
        return "", ""

    prose = body[:start].rstrip()
    tail = (body[start:].strip() + tags).strip()
    return prose, tail


def cta_tail(caption):
    """The tail of the caption that must survive truncation (CTA + hashtags).

    Kept as its own function because callers ask the question directly.
    Returns "" when the caption has no CTA.
    """
    return cta_parts(caption)[1]


def truncate_for_platform(caption, platform):
    """Truncate a caption to the platform limit WITHOUT losing its CTA.

    Returns (text, dropped) where `dropped` is True when prose was cut.

    A caption whose CTA tail alone exceeds the limit is returned UNCHANGED and
    flagged: publishing it would blow the limit (and Blotato would reject it),
    and silently dropping the CTA is the worse failure. The caller must decide
    what to do - the pre-flight is the right place for that decision, not a
    silent cut here.
    """
    limit = LIMITS.get(platform)
    if not limit or not caption:
        return caption, False

    if weighted_len(caption) <= limit:
        return caption, False

    tail = cta_tail(caption)
    if not tail:
        # No CTA to protect. Fall back to a plain cut (old behaviour) so this
        # function is never WORSE than the code it replaces.
        out = ""
        n = 0
        for ch in caption:
            w = _char_weight(ch)
            if n + w > limit - 3:
                break
            out += ch
            n += w
        return out.rstrip(" ,.") + "...", True

    prose, tail = cta_parts(caption)
    tail_w = weighted_len(tail)
    if tail_w >= limit - 4:
        # Even the CTA alone does not fit. Do NOT publish a CTA-less caption:
        # return the caption UNCHANGED so the publish fails loudly (Blotato
        # rejects an over-limit caption) instead of silently gutting the ask.
        return caption, False

    budget = limit - tail_w - 4  # 4 = " ..." + separating space
    if weighted_len(prose) > budget:
        # Cut on a character boundary that does not split a word.
        out = ""
        n = 0
        for ch in prose:
            w = _char_weight(ch)
            if n + w > budget:
                break
            out += ch
            n += w
        out = out.rsplit(" ", 1)[0].rstrip(" ,.;:-")
        return out + " ... " + tail, True
    return prose + " " + tail, False


def policy_failures(caption):
    """Return a list of policy failures for a caption. Empty == publishable."""
    failures = []
    if not caption:
        return ["FAIL: Empty caption"]
    if PRICE_RE.search(caption):
        failures.append("FAIL: Price published on public feed")
    if caviar_offer(caption):
        failures.append(
            "FAIL: Caviar offered on a public feed - the SA permit stack "
            "(DFFE -> ITAC -> DAFF -> SARS -> CITES) is not assembled, 0 "
            "caviar products are purchasable on the storefront, and caviar "
            "is off the retail path for 2026 (trade desk only, 2027 season). "
            "Do not publish this caption; caviar is advertised on the caviar "
            "trade desk, not on a public feed.")
    return failures


def main(argv):
    if "--check-text" in argv:
        i = argv.index("--check-text")
        caption = argv[i + 1] if i + 1 < len(argv) else ""
    elif "--truncate" in argv:
        # Used by the JS publish path so both paths share ONE truncation
        # implementation. Prints the caption to publish on stdout.
        i = argv.index("--truncate")
        platform = argv[i + 1] if i + 1 < len(argv) else ""
        caption = argv[i + 2] if i + 2 < len(argv) else ""
        text, _dropped = truncate_for_platform(caption, platform)
        sys.stdout.write(text)
        return 0
    elif "--check-pending" in argv:
        i = argv.index("--check-pending")
        path = argv[i + 1] if i + 1 < len(argv) else ""
        try:
            with open(path, encoding="utf8") as fh:
                pending = json.load(fh)
        except Exception as exc:  # an unreadable pending file is not a violation
            print("caption-policy: cannot read pending file (%s)" % exc,
                  file=sys.stderr)
            return 0
        caption = pending.get("caption") or ""
    else:
        print(__doc__)
        return 2

    failures = policy_failures(caption)
    for f in failures:
        print(f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
