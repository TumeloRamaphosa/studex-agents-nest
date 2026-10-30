#!/usr/bin/env python3
"""Pre-flight the Daily Post publish path WITHOUT publishing anything.

A post that goes wrong at 09:00 SAST is a live post on the internet. The
same check 2 hours earlier costs nothing. This script answers, before the
cron fires:

  1. Is there a queue file for the target date+pillar?
  2. Does it parse (the "## Generated Post Content" block is present)?
  3. Does validate_brand() pass? (10 checks: pillar, forbidden claims, tags…)
  4. What EXACT text will each platform ship? (calls the real
     build_platform_texts(), not a re-implementation — a test that
     re-implements the logic proves nothing)
  5. Is there any markdown residue in that text? (a stray '**' is always
     wrong: social platforms do not render markdown)
  6. Does the media URL actually resolve? (a 404 image still "publishes")
  7. Is the image present and matched to the pillar?
  8. Which platforms will be SKIPPED because they already published?
  9. Are the Blotato account connections still alive for the platforms
     that WILL be attempted?

Exit 0 = safe to publish. Exit 1 = would publish something wrong.

Usage: python3 ops/preflight-daily-post.py [YYYY-MM-DD]
"""
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path("/workspace")
sys.path.insert(0, str(ROOT / "scripts"))

# The ONE source of truth for caption policy, shared with both publish
# paths. Path A reaches it through validate_brand(); path B reaches it
# through blotato-fallback.js. This pre-flight reaches it directly so
# the audit and the gate can never disagree.
import caption_policy  # noqa: E402

import importlib.util  # noqa: E402

# The real script is "daily-post.py" (hyphen) - import it by path so we call
# the ACTUAL functions, not a re-implementation. A pre-flight that copies the
# logic can stay green while the real script is broken.
_spec = importlib.util.spec_from_file_location(
    "daily_post", ROOT / "scripts" / "daily-post.py")
dp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dp)

FAILS = []
WARNS = []
NOTES = []

# The date this run is checking, set by main(). report() takes no arguments
# and cannot see main()'s locals, so the target date lives here.
TARGET_DATE = None


# Platforms that REJECT a post without an image (Instagram: 422 code 20000).
IMAGE_REQUIRED = {"instagram"}

# The script whose TARGETS decide which platforms path B actually reaches.
FB_SCRIPT = pathlib.Path(
    "/workspace/studex-content-automation/scripts/blotato-fallback.js")


def fail(m):
    FAILS.append(m)


def warn(m):
    WARNS.append(m)


def note(m):
    NOTES.append(m)


def media_verdict(media_url, staged_img):
    """Decide what the pre-flight says about the post's image.

    Returns "ok", "fail" or "warn".

    🔑 WHY THIS IS NOT JUST "is there a media URL?"
    The publisher resolves the image TWO ways, and they are NOT the same
    thing:
      * `media_url` — POST_MEDIA_URL, or the queue file's "**Media URL:**"
        line. THIS is the only thing sent to Blotato as `mediaUrls`.
      * `staged_img` — a LOCAL file at memory/<date>-<pillar>.png, found by
        `dp.find_image()`. The publisher uses it for VALIDATION and prints
        it in its summary line (`media_url or img or "none"`), but it is
        NOT sent to Blotato.

    So "no media URL" has two very different meanings:
      * no URL and NO staged image → a deliberate text-only post → WARN.
      * no URL but an image IS staged → the post publishes WITHOUT its
        image while the log prints the local path as if it were attached.
        That is a defect and it must BLOCK, because the 08:00 cron's
        instruction is "if it exits 0 (CLEAN), do NOTHING" — a warning
        about a post that WILL publish wrongly is invisible to everyone.

    This was live for 2026-10-28, the only recent queue file with no
    "**Media URL:**" line. Every other one had one.
    """
    if media_url:
        return "ok"
    if staged_img:
        return "fail"
    return "warn"


def pending_absence_verdict(target_date, now_sast):
    """Decide whether a MISSING path-B pending file is expected or a failure.

    🔑 THE CLOCK MUST BE MEASURED AGAINST THE TARGET DATE, NOT AGAINST
    "NOW".

    The content agent writes `<target>.json` at 08:55 SAST ON THE TARGET
    DATE. The original code compared the CURRENT wall clock to 08:55 and
    ignored which date was being checked, so asking about a FUTURE date
    produced a FALSE FAILURE:

        $ python3 ops/preflight-daily-post.py 2026-10-28   # at 19:58 SAST
        FAIL  no pending file at 2026-10-28.json - it should have been
              written at 08:55 SAST. The content agent did not run...

    It had not "failed to run" - it is scheduled to run tomorrow morning.
    A gate that reports a defect for something that has not been due yet
    teaches the next reader to ignore the gate, which is exactly how a
    real failure gets missed.

    Three cases, and only the third is a defect:
      * target is in the FUTURE  -> expected (the agent has not been due)
      * target is TODAY, before 08:55 SAST -> expected (not due yet)
      * target is TODAY after 08:55, or in the PAST -> a real failure

    `target_date` may be a date or a datetime; `now_sast` is a datetime
    (the caller passes a SAST-aware one).
    """
    tdate = target_date.date() if hasattr(target_date, "date") else target_date
    ndate = now_sast.date() if hasattr(now_sast, "date") else now_sast
    if tdate > ndate:
        return "expected"
    if tdate == ndate:
        return "expected" if (now_sast.hour * 60 + now_sast.minute
                              < 8 * 60 + 55) else "failed"
    return "failed"


def account_id_verdict(targeted, live_rows):
    """Compare the publisher's hardcoded account ids with the live connections.

    Returns (stale, untargeted):
      stale      - [(platform, account_id)] the publisher will POST to an
                   account id that is NOT a live connection, even though
                   that platform HAS live accounts.
      untargeted - [(platform, account_id, username)] live accounts on a
                   platform we target that we do NOT post to.

    🔑 WHY THE PLATFORM-LEVEL CHECK IS NOT ENOUGH
    `scripts/daily-post.py` publishes with a HARDCODED one-id-per-platform
    map (`BLOTATO_ACCOUNTS`). The pre-flight asked only "is SOME account of
    this platform connected?" - which stays true when the account we
    actually post to has been removed or reconnected under a different id.
    The publisher would then POST into a void while the pre-flight still
    printed "accounts for platforms we attempt: [...]" in green.

    That is not hypothetical: reconnecting Meta (the top blocker) is
    exactly the action that changes an account id, and until it happens
    this check has no input.

    🔑 A PLATFORM WITH NO LIVE ACCOUNT AT ALL IS NOT REPORTED HERE.
    The existing platform-level check already warns about that, and it is
    a WARN for a reason: the other platforms still publish. Only the
    "the platform is connected but OUR id is not" case is a blocking
    defect, because it means the publisher is aimed at a stale target
    while a live one sits unused.
    """
    ids = {}
    for a in (live_rows or []):
        aid = a.get("id")
        if aid is None:
            continue
        ids[str(aid)] = a
    if not ids:
        # Nothing to compare against. The caller already warns about a
        # missing platform; do not invent a blocking failure here.
        return [], []
    live_platforms = {a.get("platform") for a in ids.values()}
    stale = []
    for platform, acct in sorted(targeted.items()):
        if str(acct) in ids:
            continue
        if platform not in live_platforms:
            continue  # handled by the existing platform-level WARN
        stale.append((platform, str(acct)))
    targeted_ids = {str(v) for v in targeted.values()}
    untargeted = []
    for aid, a in sorted(ids.items()):
        if a.get("platform") in targeted and aid not in targeted_ids:
            untargeted.append((a.get("platform"), aid,
                               a.get("username") or a.get("fullname") or ""))
    return stale, untargeted


def publish_health(markers, platforms):
    """Which platforms actually PUBLISH? Evidence: our OWN publish markers.

    `markers` is a list of dicts, one per publish day, each carrying the
    "posted" and "failed" platform lists the publisher recorded.
    Returns {platform: {"posted": n, "failed": n}}.

    🔑 WHY THIS IS NOT THE SAME QUESTION AS "is the account connected?"
    A Blotato account can be CONNECTED and still be UNPUBLISHABLE: a Meta
    or LinkedIn grant expires while the connection record survives. The
    accounts API exposes NO grant-health field (verified 2026-10-28: the
    live records for the working and the failing accounts are
    indistinguishable apart from platform-idiomatic naming), so
    "connected" cannot answer this. The only honest source is what our
    last few publishes actually DID - memory/published-<date>-<pillar>.json,
    written by the publisher itself.

    🔑 AND THE FAILURE IS NOT FATAL TO THE POST. The publisher's loop
    records a per-platform result and continues, so a failed platform does
    not stop the others (proven across 4 consecutive days: facebook fails
    FIRST in the loop and instagram/threads still published every time).
    So a failing platform is a WARNING, never a blocker - blocking would
    kill the two platforms that DO work.
    """
    counts = {p: {"posted": 0, "failed": 0} for p in platforms}
    for m in markers:
        for p in set(m.get("posted") or []):
            if p in counts:
                counts[p]["posted"] += 1
        for p in set(m.get("failed") or []):
            if p in counts:
                counts[p]["failed"] += 1
    return counts


def unpublishable(health):
    """Platforms that are CONNECTED but have never once published.

    A platform that has BOTH posted and failed is intermittent, not dead -
    it is not listed here. A platform that has failed every time and never
    posted is unpublishable and will fail again.
    """
    return sorted(p for p, h in health.items() if h["failed"] and not h["posted"])


def read_publish_markers(limit=6):
    """Read the publisher's own marker files: memory/published-<date>-<pillar>.json

    Returns a list of {"date", "posted", "failed"}, oldest first. A marker
    with no recognisable platform lists is skipped rather than guessed at.
    """
    out = []
    for p in sorted(pathlib.Path(ROOT / "memory").glob("published-*.json")):
        try:
            d = json.loads(p.read_text(errors="ignore"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        res = d.get("results") if isinstance(d.get("results"), dict) else {}
        posted = res.get("posted") or d.get("posted") or []
        failed = res.get("failed") or d.get("failed") or []
        if not posted and not failed:
            continue
        out.append({"date": d.get("date") or p.stem,
                    "posted": list(posted), "failed": list(failed)})
    out.sort(key=lambda m: str(m["date"]))
    return out[-limit:]


def main():
    global TARGET_DATE
    date_str = sys.argv[1] if len(sys.argv) > 1 else dp.datetime.now(dp.SAST).strftime("%Y-%m-%d")
    day = dp.datetime.strptime(date_str, "%Y-%m-%d")
    dow = day.strftime("%A")
    pillar = dp.PILLARS.get(dow)
    # report() takes no arguments, so it cannot see main()'s locals. Record
    # the date being checked where report() can reach it.
    TARGET_DATE = day.date()
    print("=" * 72)
    print(f"DAILY POST PRE-FLIGHT — {date_str} ({dow}) — pillar {pillar}")
    print("=" * 72)

    if pillar is None:
        print(f"No pillar for {dow} — the post script skips. Nothing to pre-flight.")
        return 0

    # 1. queue file
    qf = dp.queue_file_for(date_str, pillar)
    if not qf:
        # An un-staged day is a legitimate state, not a defect. Treating it as
        # a blocking failure would page Discord every day the content agent has
        # not staged yet - a false alarm that trains us to ignore the page.
        #
        # FACT (verified 2026-10-26): the 09:00 SAST publish job STAGES the
        # queue file itself - on 26 Oct the 08:00 run warned here, and the
        # 09:00 job then wrote memory/post-queue/2026-10-26-monday-knowledge.md
        # and published. So the publish does NOT skip; this 08:00 gate simply
        # has no input to inspect. The 09:00 job either stages one and
        # publishes, or announces "No post queued for today".
        #
        # The earlier wording here said the publish "will legitimately skip".
        # That was factually wrong. A gate that lies about what it protects is
        # worse than a gate that is known to be inert: it teaches the next
        # reader that the 08:00 check matters, when on an un-staged day it
        # cannot. ops/test-preflight-gate-wording.py locks all of this down.
        warn(f"NO QUEUE FILE for {date_str} ({pillar}) - nothing to pre-flight: "
             "the 09:00 SAST publish job stages the queue file itself, so this "
             "08:00 gate had no input to inspect. Expected a file in "
             "memory/post-queue/ if a post IS expected today.")
        return report()
    print(f"[ OK ] queue file: {os.path.basename(qf)}")

    # 2. parse
    content = dp.extract_content(qf)
    if not content:
        fail(f"Queue file has no '## Generated Post Content' block — extract_content() "
             "returned empty, so the post would go out blank.")
        return report()
    print(f"[ OK ] content parsed ({len(content)} chars)")

    # 3. image
    img = dp.find_image(date_str)
    image_exists = img is not None
    if not image_exists:
        fail("No image found for this date — the pillar/date image match failed.")
    else:
        print(f"[ OK ] image: {img}")

    # 4. brand validation (the real function)
    issues = dp.validate_brand(content, pillar, image_exists)
    if issues:
        for i in issues:
            fail(f"validate_brand(): {i}")
    else:
        print("[ OK ] validate_brand() passed")

    # 5. exact per-platform text + markdown residue
    texts = dp.build_platform_texts(content)
    print("\n--- TEXT THAT WILL SHIP (exact) ---")
    for platform, t in texts.items():
        residue = re.findall(r"\*\*|__|`|^>\s", t, re.M)
        tags = re.findall(r"#[A-Za-z][A-Za-z0-9]*", t)
        print(f"\n[{platform}] {len(t)} chars, {len(tags)} hashtags")
        if platform == "instagram" and len(tags) > 5:
            fail(f"instagram: {len(tags)} hashtags — Blotato caps at 5")
        if platform == "threads" and len(t) > 500:
            fail(f"threads: {len(t)} chars — Blotato caps at 500")
        if residue:
            fail(f"{platform}: markdown residue {residue[:6]} — a stray '**' is always wrong")
        else:
            print("  markdown residue: none")
        print("  " + t[:300].replace("\n", "\n  "))

    # 6. media URL
    media_url = os.environ.get("POST_MEDIA_URL", "") or dp.extract_media_url(qf)
    staged_img = None
    try:
        staged_img = dp.find_image(date_str)
    except Exception:
        staged_img = None
    verdict = media_verdict(media_url, staged_img)
    if verdict == "fail":
        # 🔑 AN IMAGE WAS STAGED, BUT THE PUBLISHER WILL NOT ATTACH IT.
        # See media_verdict() for the whole story.
        fail("the queue file declares NO media URL, but an image IS staged "
             f"at {staged_img}. The publisher sends only the media URL to "
             "Blotato, so this post would publish WITHOUT its image while "
             "the log prints the local path as if it were attached. Add "
             "'**Media URL:** <public url>' to the queue file (and upload "
             "the image somewhere fetchable).")
    elif verdict == "warn":
        warn("No media URL in the queue file and no POST_MEDIA_URL set — "
             "the post would publish WITHOUT an image. (No local image is "
             "staged for this date+pillar either, so this looks "
             "deliberate.)")
    else:
        try:
            req = urllib.request.Request(media_url, method="HEAD")
            with urllib.request.urlopen(req, timeout=25) as r:
                ct = r.headers.get("Content-Type", "?")
                print(f"\n[ {'OK' if r.status == 200 else 'FAIL'} ] media URL {r.status} {ct}")
                if r.status != 200:
                    fail(f"media URL returned {r.status}")
        except Exception as e:
            # HEAD is not always allowed; fall back to a ranged GET
            try:
                req = urllib.request.Request(media_url, headers={"Range": "bytes=0-64"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    print(f"\n[ OK ] media URL {r.status} {r.headers.get('Content-Type','?')}")
            except Exception as e2:
                fail(f"media URL unreachable: {e2}")

    # 7. what will be SKIPPED (already published for this date+pillar)
    already = dp.already_published(date_str, pillar)
    print(f"\n--- ALREADY PUBLISHED for {date_str} ({pillar}): {sorted(already) or 'none'} ---")
    if already:
        note(f"will SKIP {sorted(already)} — a re-post would duplicate a live post")

    # 7b. PENDING-FILE CHECK. There are TWO live publish paths and the
    #     pre-flight was only covering one of them:
    #       PATH A  scripts/daily-post.py
    #              reads  memory/post-queue/<date>-<pillar>.md
    #              -> checked above
    #       PATH B  studex-content-automation/scripts/blotato-fallback.js
    #              reads  studex-content-automation/posts/pending/<date>.json
    #              -> written by the Daily Content Agent at 08:55 SAST
    #     PATH B is the path that ran on 2026-10-22 (status POSTED_VIA_FALLBACK).
    #     The pending caption is the one that actually reaches Threads and
    #     Instagram, and it is generated at 08:55 SAST - AFTER the 08:00
    #     pre-flight. So the 08:00 run structurally CANNOT see it.
    #     The "Daily Post pending pre-flight" cron (09:20 SAST) sees it,
    #     but that fires AFTER the 09:00 publish - so it is an AUDIT, not a
    #     pre-flight. The 08:00 run checks path A; the 09:20 run audits
    #     path B after the fact.
    pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"
    if not pending.exists():
        # The content agent writes this file at 08:55 SAST ON THE TARGET
        # DATE. Before then its absence is NORMAL and must not be reported
        # as a problem; after then it means the agent did not run and path B
        # will publish nothing. Say which case this is instead of always
        # warning.
        #
        # 🔑 The clock must be measured against the TARGET date, not against
        # "now" - see pending_absence_verdict() for why.
        now_sast = dp.datetime.now(dp.SAST)
        verdict = pending_absence_verdict(day.date(), now_sast)
        if verdict == "expected":
            note(f"no pending file yet at {pending.name} - the Daily Content "
                 "Agent writes it at 08:55 SAST on the target date. Expected "
                 "at this time.")
        else:
            fail(f"no pending file at {pending.name} - it should have been "
                 "written at 08:55 SAST. The content agent did not run, so "
                 "the fallback path (path B) has nothing to publish.")
    else:
        try:
            pdata = json.loads(pending.read_text())
        except Exception as e:
            fail(f"pending file is not valid JSON: {e}")
            pdata = None
        if pdata is not None:
            pcap = pdata.get("caption") or ""
            ptags = re.findall(r"#[A-Za-z][A-Za-z0-9]*", pcap)
            pres = re.findall(r"\*\*|__|`", pcap)
            print(f"\n--- PENDING FILE (path B: the caption that actually ships) ---")
            print(f"  {pending.name}: {len(pcap)} chars, {len(ptags)} hashtags, "
                  f"status={pdata.get('status')}")
            if len(ptags) > 5:
                # NOT a failure. The content agent is told to write "5-7
                # hashtags"; the platform truncates to the first 5 rather
                # than rejecting. Live proof: the 2026-10-22 pending caption
                # had 7 tags, the fallback published it, and live IG post
                # 8383092 shipped with 5. So this is a WARN - the extra tags
                # will silently not appear.
                warn(f"pending caption has {len(ptags)} hashtags - Instagram "
                     f"keeps the first 5 ({ptags[:5]}); the rest "
                     f"({ptags[5:]}) will NOT appear. This is not a publish "
                     "failure, but those tags will be silently dropped.")
            else:
                print(f"  hashtags OK ({len(ptags)}): {ptags}")
            if pres:
                fail(f"pending caption has markdown residue {pres[:4]} - social "
                     "platforms do not render markdown, so the asterisks go live.")
            else:
                print("  markdown residue: none")
            # Rule [10] - "no price on a public feed". This pre-flight is the
            # LAST gate before the caption is published, so a price that gets
            # past here goes live. Path A (scripts/daily-post.py) hard-fails on
            # this; path B (the content agent) has NO price guard at all, so
            # this check is the only thing standing between a staged price and
            # the public feed.
            # Live proof of the breach it catches: the 2026-10-22 caption
            # published R1,450 publicly (IG 8383092 + Threads 8383081) while
            # every status stayed green.
            pprices = re.findall(r"R\s?[\d][\d,]*(?:\.\d+)?", pcap)
            if pprices:
                fail(f"pending caption carries a price {sorted(set(pprices))} - "
                     "rule [10] is 'no price on a public feed'. Strip the price "
                     "or get explicit approval for this caption before it "
                     "publishes. (Path A fails on this; path B does not.)")
            else:
                print("  price: none (rule [10] OK)")

            # 🔑 CAVIAR ON THE FEED - the PRODUCT rule the price rule cannot see.
            # The 2026-10-30 pending caption offered Oscietra caviar and carried
            # NO price, so the rule [10] check above passed, every gate read
            # green, and a retail offer for an unpermitted and unfulfillable
            # product went live on Threads (DfG_M2bEd5U) at 08:56 SAST. A guard
            # that only asks "is there a price?" cannot see a product problem.
            if caption_policy.caviar_offer(pcap):
                fail("pending caption offers CAVIAR on a public feed - the SA "
                     "permit stack (DFFE -> ITAC -> DAFF -> SARS -> CITES) is "
                     "not assembled, 0 caviar products are purchasable on the "
                     "storefront, and caviar is off the retail path for 2026 "
                     "(trade desk only, 2027 season). This caption must not "
                     "publish. The publish gate (scripts/caption_policy.py) "
                     "refuses it too - but the audit has to say so as well, "
                     "because this gate ran and read CLEAN.")
            else:
                print("  caviar: none (policy OK)")
            fb = pdata.get("fallback") or {}
            if fb.get("posted"):
                print(f"  fallback already posted: {fb.get('posted')} "
                      f"(attempted {fb.get('attemptedAt')})")
                if fb.get("failed"):
                    print(f"  fallback failed: {fb.get('failed')}")
            else:
                print("  fallback has not published yet")
            pmedia = (pdata.get("media") or {}).get("image")
            if pmedia:
                try:
                    req = urllib.request.Request(pmedia, method="HEAD")
                    with urllib.request.urlopen(req, timeout=25) as r:
                        print(f"  media URL {r.status} {r.headers.get('Content-Type','?')}")
                        if r.status != 200:
                            fail(f"pending media URL returned {r.status}")
                except Exception:
                    try:
                        req = urllib.request.Request(pmedia, headers={"Range": "bytes=0-64"})
                        with urllib.request.urlopen(req, timeout=25) as r:
                            print(f"  media URL {r.status} {r.headers.get('Content-Type','?')}")
                    except Exception as e2:
                        fail(f"pending media URL unreachable: {e2}")
            else:
                # Is any IMAGE-REQUIRING platform actually going to receive
                # this caption? Read the fallback's real TARGETS - a
                # hardcoded copy of the platform list drifts the moment a
                # target is added.
                fb_targets = []
                try:
                    fb_src = FB_SCRIPT.read_text(encoding="utf8")
                    block = re.search(r"const\s+TARGETS\s*=\s*\[(.*?)\];",
                                      fb_src, re.S)
                    if block:
                        fb_targets = re.findall(
                            r"platform:\s*['\"](\w+)['\"]", block.group(1))
                except Exception:
                    fb_targets = []
                needs_image = [p for p in fb_targets if p in IMAGE_REQUIRED]
                if needs_image:
                    fail(f"pending file has no media image and {needs_image} "
                         "requires one (422 code 20000) - the post would be "
                         f"rejected. The fallback targets are {fb_targets}.")
                else:
                    warn(f"pending file has no media image, but the fallback "
                         f"targets are {fb_targets or ['unknown']} and none of "
                         "them require an image, so the caption publishes fine "
                         "as text. Instagram WOULD need an image if it is ever "
                         "added as a target.")

    # 8. LIVE-DUPLICATE CHECK. The marker file is LOCAL state; the Blotato
    #    API is the truth. If today's caption is already live on a platform
    #    the marker believes is unposted, the 09:00 SAST publish puts a
    #    SECOND copy in front of the audience - and there is NO delete route
    #    for a published post, so it cannot be undone.
    #    `GET /v2/posts?accountId=` IGNORES the accountId filter and returns
    #    the same list for every account, so we fetch once and filter
    #    CLIENT-SIDE on the top-level `platform` field.
    key = None
    for f in ("/workspace/.env", os.path.expanduser("~/.env")):
        if os.path.exists(f):
            key = dp.load_env((f,)).get("BLOTATO_API_KEY")
            if key:
                break
    if not key:
        warn("BLOTATO_API_KEY not found - cannot run the live-duplicate check.")
    else:
        print("\n--- LIVE DUPLICATE CHECK (GET /v2/posts) ---")
        try:
            req = urllib.request.Request(
                "https://backend.blotato.com/v2/posts",
                headers={"blotato-api-key": key})
            with urllib.request.urlopen(req, timeout=30) as r:
                live = json.load(r)
            items = live.get("items") or []
            print(f"  {len(items)} live post(s) returned")
            head = re.sub(r"\s+", " ", content.strip())[:60].lower()
            carrying = {}
            for it in items:
                plat = it.get("platform")          # TOP-LEVEL field
                acct = (it.get("account") or {}).get("id")
                tn = re.sub(r"\s+", " ", (it.get("text") or "").strip()).lower()
                if plat and head and (head in tn or tn[:60] in head):
                    carrying.setdefault(plat, []).append(f"{it.get('id')}@{acct}")
            for plat, ids in sorted(carrying.items()):
                print(f"  today's caption is ALREADY LIVE on {plat}: {ids}")
            if not carrying:
                print("  today's caption is not live on any platform")
            # A platform counts as "already published" if EITHER publisher
            # recorded it: the path A marker (memory/published-<date>-<pillar>.json)
            # OR the path B pending file's fallback record. Consulting only one
            # produces a false DUPLICATE RISK every day, because the other
            # publisher's success looks like an unrecorded platform.
            already = set(dp.already_published(date_str, pillar))
            pending_fb = set()
            pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"
            if pend_path.exists():
                try:
                    pd = json.loads(pend_path.read_text())
                    fb = pd.get("fallback") or {}
                    pending_fb = set(fb.get("posted") or [])
                    if fb.get("instagram"):
                        pending_fb.add("instagram")
                except Exception:
                    pass
            if pending_fb:
                print(f"  path B fallback recorded: {sorted(pending_fb)}")
            dup = sorted(set(carrying) - already - pending_fb)
            if dup:
                fail("DUPLICATE RISK: today's caption is already live on "
                     + ", ".join(dup) + " but the marker does not list it as "
                     "posted. The 09:00 SAST publish would put a second copy "
                     "in front of the audience, and Blotato has no delete "
                     "route for a published post.")
            else:
                print("  no duplicate: every platform already carrying the "
                      "caption is recorded in the marker")
        except urllib.error.HTTPError as e:
            warn(f"live-duplicate check could not run (HTTP {e.code})")
        except Exception as e:
            warn(f"live-duplicate check could not run ({e})")

    # 9. Blotato account health for the platforms that WILL be attempted
    key = None
    for f in ("/workspace/.env", os.path.expanduser("~/.env")):
        if os.path.exists(f):
            env = dp.load_env((f,))
            key = env.get("BLOTATO_API_KEY")
            if key:
                break
    if not key:
        warn("BLOTATO_API_KEY not found — cannot verify account connections.")
    else:
        print("\n--- BLOTATO ACCOUNT CONNECTIONS ---")
        try:
            req = urllib.request.Request(
                "https://backend.blotato.com/v2/users/me/accounts",
                headers={"blotato-api-key": key})
            with urllib.request.urlopen(req, timeout=25) as r:
                accounts = json.load(r)
            rows = accounts.get("items") or accounts.get("accounts") or []
            for a in rows:
                print(f"  {str(a.get('platform')):10} {str(a.get('id')):8} "
                      f"user={str(a.get('username') or a.get('fullname') or '')[:28]}")
            # Only the platforms we actually attempt matter.
            attempted = [a for a in rows if a.get("platform") in dp.BLOTATO_ACCOUNTS]
            print("  accounts for platforms we attempt: "
                  f"{sorted(a.get('platform') for a in attempted)}")
            missing = set(dp.BLOTATO_ACCOUNTS) - {a.get("platform") for a in attempted}
            if missing:
                warn("no Blotato account for: " + ", ".join(sorted(missing))
                     + " - those platforms will FAIL at publish time")
            # 🔑 The platform-level check above cannot see a STALE account
            # id: it only asks whether SOME account of that platform is
            # connected. The publisher POSTs to a HARDCODED id, so if that
            # id was removed or reconnected under a new one, the post goes
            # into a void while this pre-flight still reads green.
            stale, untargeted = account_id_verdict(dp.BLOTATO_ACCOUNTS, rows)
            for platform, acct in stale:
                fail(f"the publisher will POST to Blotato account {acct} for "
                     f"{platform}, but account {acct} is NOT a live "
                     f"connection - it was removed or reconnected under a "
                     f"different id, while another {platform} account is "
                     f"connected. The {platform} post would go nowhere. "
                     f"Update BLOTATO_ACCOUNTS in scripts/daily-post.py to "
                     f"the live {platform} id.")
            for platform, aid, user in untargeted:
                note(f"Blotato account {aid} ({platform}"
                     + (f" / {user}" if user else "")
                     + ") is connected but is NOT a target - we would not "
                       "post there. If this is a brand account, add it to "
                       "BLOTATO_ACCOUNTS in scripts/daily-post.py.")
            # 🔑 "CONNECTED" IS NOT "PUBLISHABLE" - and until now this
            # pre-flight said "connected" and stopped. Meta and LinkedIn
            # grants expire while the connection record survives: the
            # accounts API has no grant-health field, so the only honest
            # evidence is what our own last few publishes DID. On
            # 2026-10-22/23/26/27 facebook and linkedin failed on 4 of 4
            # publishes while this block still printed a green list of
            # attempted platforms - a false green, in the very block that
            # exists to tell the truth about accounts.
            markers = read_publish_markers()
            if markers:
                n = len(markers)
                health = publish_health(markers, list(dp.BLOTATO_ACCOUNTS))
                print(f"  publish health over the last {n} publish(es): "
                      + ", ".join(f"{p} {h['posted']}/{n} posted"
                                  for p, h in sorted(health.items())))
                broken = unpublishable(health)
                if broken:
                    warn("Blotato grant expired for: " + ", ".join(sorted(broken))
                         + f" - CONNECTED but unpublishable (0 posts in the "
                           f"last {n} publishes). Those platforms will not "
                           "post tonight; reconnect them in the Blotato "
                           "dashboard. The other platforms are unaffected: "
                           "the publisher records a per-platform result and "
                           "continues, so an unusable platform does not stop "
                           "the post going out on the ones that work.")
        except urllib.error.HTTPError as e:
            fail(f"Blotato accounts API returned HTTP {e.code}")
        except Exception as e:
            fail(f"Blotato accounts API unreachable: {e}")

    return report()


def report():
    print("\n" + "=" * 72)
    for n in NOTES:
        print("  NOTE  " + n)
    for w in WARNS:
        print("  WARN  " + w)
    for f in FAILS:
        print("  FAIL  " + f)
    if FAILS:
        # The same script runs twice: 08:00 SAST pre-flights path A (the
        # 09:00 publish), and 09:20 SAST audits path B (the pending caption)
        # AFTER 09:00 has already fired. Naming "the 09:00 SAST publish" in
        # the 09:20 run is false and actively misleading - it reads as "a bad
        # post went out at 09:00" when the 09:00 post was fine and the real
        # risk is the pending caption. Say which, based on the clock.
        now_sast = dp.datetime.now(dp.SAST)
        target_date = TARGET_DATE if TARGET_DATE is not None else now_sast.date()
        date_str = target_date.isoformat()
        if target_date > now_sast.date():
            # 🔑 A FUTURE target date has NOT published yet - saying
            # "the 09:00 SAST publish has already run" about tomorrow would
            # be false, and false is worse than absent.
            print(f"\nRESULT: {len(FAILS)} blocking issue(s) — for {date_str}, "
                  "which is in the FUTURE: its 09:00 SAST publish has not run "
                  "yet. Fix before it fires.")
        elif target_date < now_sast.date():
            print(f"\nRESULT: {len(FAILS)} blocking issue(s) — for {date_str}, "
                  "which is in the PAST: the 09:00 SAST publish has already "
                  "run; read the FAIL lines above to see WHICH path is at "
                  "risk (path A = the 09:00 publish, path B = the pending "
                  "caption the fallback publishes).")
        elif now_sast.hour * 60 + now_sast.minute < 9 * 60:
            print(f"\nRESULT: {len(FAILS)} blocking issue(s) — the 09:00 SAST "
                  "publish would go out wrong. Fix before it fires.")
        else:
            print(f"\nRESULT: {len(FAILS)} blocking issue(s) — Fix before the "
                  "affected publish fires. It is now "
                  f"{now_sast.strftime('%H:%M')} SAST, so the 09:00 SAST publish "
                  "has already run; read the FAIL lines above to see WHICH path "
                  "is at risk (path A = the 09:00 publish, path B = the pending "
                  "caption the fallback publishes).")
        print("=" * 72)
        return 1
    print(f"\nRESULT: pre-flight CLEAN ({len(WARNS)} warning(s)) — safe to publish.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
