#!/usr/bin/env python3
"""
Studex Daily Posting Pipeline — pillar-driven, queue-driven, self-healing.

Run:  python3 /workspace/scripts/daily-post.py            # today (SAST)
      python3 /workspace/scripts/daily-post.py 2026-10-23 # a specific date

Flow:
  1. Resolve today's date + pillar from the rotation.
  2. Load the queued copy from memory/post-queue/<date>-<day>-<pillar>.md
  3. Run validate_brand()  — MANDATORY, blocks publishing on failure.
  4. Publish: try FeedHive first; if FeedHive is down, fall back to Blotato.
  5. Log the outcome to memory/post-log.md.

Notes:
  - CTA is info@studexmeat.com. agent.studexmeat.com has NO DNS — never publish it.
  - FeedHive has been 404 since 2026-10-15 (token invalid since 2026-10-05).
    Blotato is the live path. Both are attempted; neither failure is fatal.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caption_policy
from datetime import datetime, timedelta, timezone

SAST = timezone(timedelta(hours=2))
FH_TOKEN = os.environ.get("FEEDHIVE_API_KEY", "")
FH_BASE = "https://api.feedhive.com/v1"
BLOTATO_BASE = "https://backend.blotato.com/v2"

ROOT = "/workspace"
QUEUE_DIR = os.path.join(ROOT, "memory", "post-queue")
LOG_PATH = os.path.join(ROOT, "memory", "post-log.md")

PILLARS = {
    "Monday": "Knowledge", "Tuesday": "Africa", "Wednesday": "Build",
    "Thursday": "Business", "Friday": "Agents", "Saturday": "Community",
}
# The platforms we actually publish to. Derived from BLOTATO_ACCOUNTS below
# so it can never drift from what is really attempted — the previous
# hardcoded list named "twitter" (never attempted) and omitted "threads"
# (always attempted), so every daily log misreported the platforms.
PLATFORMS = None  # set from BLOTATO_ACCOUNTS once that dict exists

# Blotato account ids (verified live 2026-10-22 via GET /v2/users/me/accounts)
BLOTATO_ACCOUNTS = {
    "facebook": "38744", "instagram": "76978",
    "linkedin": "26628", "threads": "7701",
}

PLATFORMS = sorted(BLOTATO_ACCOUNTS)
FACEBOOK_PAGE_ID = "108934711902801"


def load_env(paths=("/workspace/.env", os.path.expanduser("~/.env"))):
    """Read KEY=VALUE lines from each file, first hit wins.

    STUDEX_ENV_FILE overrides the list. WITHOUT it, the "publisher refuses
    without a credential" case could not be tested at all: the test strips
    BLOTATO_API_KEY from the ENVIRONMENT, but the publisher reads the .env
    FILE, so the credential was still there and the case passed for the
    wrong reason - it never exercised the path it claimed to.
    """
    override = os.environ.get("STUDEX_ENV_FILE")
    if override:
        paths = [override]
    env = {}
    for f in paths:
        if not os.path.exists(f):
            continue
        for line in open(f, encoding="utf-8", errors="ignore"):
            t = line.strip()
            if not t or t.startswith("#") or "=" not in t:
                continue
            k, v = t.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ---------------------------------------------------------------- validation
def validate_brand(content, pillar, image_exists=False):
    """MANDATORY. Returns list of failure strings; empty == pass."""
    checks = []
    low = content.lower()

    if "#StudexGM" not in content:
        checks.append("FAIL: Missing #StudexGM")

    # CTA — the only sanctioned address. The old handle has no DNS.
    if re.search(r"@agent\.studexmeat\.com", content):
        checks.append("FAIL: CTA uses dead domain @agent.studexmeat.com")
    if "info@studexmeat.com" not in content:
        checks.append("FAIL: CTA info@studexmeat.com missing")

    for w in ("guaranteed returns", "will make you rich", "our competitors",
              "risk-free", "guaranteed profit"):
        if w in low:
            checks.append("FAIL: Suspicious claim '%s'" % w)

    if pillar not in ("Business", "Africa") and "global markets" in low:
        checks.append("FAIL: 'Global Markets' reference outside Business/Africa pillar")

    # CIIE booth is unconfirmed — do not assert participation publicly.
    if re.search(r"\b(our|the)\s+(booth|stand|pavilion)\b", content, re.I):
        checks.append("FAIL: Unverified booth/stand/pavilion claim")

    # The price rule lives in caption_policy.py so that path B
    # (studex-content-automation/scripts/blotato-fallback.js) enforces the
    # SAME rule BEFORE it publishes. Two publish paths, one policy - a rule
    # that only one of them enforces is not a rule.
    for _f in caption_policy.policy_failures(content):
        if _f not in checks:
            checks.append(_f)

    # The SOURCE may carry more than 5 tags - the content agent is told to
    # write "5-7 hashtags at the end", and the IG CUT is what drops the
    # extras (the SKILL: "drop the extra tag from the IG cut only").
    # So the limit that matters is enforced in build_platform_texts(), where
    # the per-platform text is actually built - not here.
    # (Live evidence: the 2026-10-22 pending caption had 7 tags, the
    # fallback published it, and the live IG post 8383092 shipped with 5.
    # Blotato truncates to the first 5 - it does NOT reject with a 422.)
    tags = re.findall(r"#[A-Za-z][A-Za-z0-9]*", content)
    if len([t for t in tags if t.lower() != "#studexgm"]) > 5:
        # Blotato TRUNCATES to the first 5 server-side; it does NOT reject
        # with a 422 (live proof: a 7-tag pending caption published fine and
        # the live IG post carries 5). The IG cut in build_platform_texts()
        # drops the extras deterministically, so extra tags are NOT a
        # publish blocker - blocking them stops the WHOLE post (every
        # platform) over a condition that the cut already fixes.
        #
        # This guard used to FAIL here on the RAW caption, while the comment
        # above said the limit "is enforced in build_platform_texts() ... not
        # here". The comment was right and the code was not: path A refused
        # to publish a 7-tag caption that path B published without trouble.
        # The SKILL tells the content agent to write "5-7 hashtags", so this
        # was a live, recurring outage risk on every over-cap day.
        #
        # A guard must never be stricter than the failure it guards against.
        # So: check the ACTUAL text Instagram will ship, not the raw caption.
        ig_text = build_platform_texts(content).get("instagram", content)
        ig_tags = re.findall(r"#[A-Za-z][A-Za-z0-9]*", ig_text)
        if len(ig_tags) > 5:
            checks.append("FAIL: Instagram output has %d hashtags (cap 5) "
                          "after the IG cut" % len(ig_tags))

    if len(content) > 2000:
        checks.append("FAIL: Exceeds 2000 char Twitter limit (%d)" % len(content))

    if not image_exists:
        checks.append("FAIL: No image attached for this pillar")

    return checks


# ------------------------------------------------------------------- helpers
def http(method, url, headers=None, payload=None, timeout=20):
    data = json.dumps(payload).encode() if payload is not None else None
    hdrs = dict(headers or {})
    if data:
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:
        return None, str(e)[:300]


def queue_file_for(date_str, pillar):
    day = datetime.strptime(date_str, "%Y-%m-%d")
    dow = day.strftime("%A").lower()
    p = pillar.lower()
    exact = os.path.join(QUEUE_DIR, "%s-%s-%s.md" % (date_str, dow, p))
    if os.path.exists(exact):
        return exact
    # tolerate a differently-labelled pillar in the filename
    for fn in sorted(os.listdir(QUEUE_DIR)):
        if fn.startswith(date_str):
            return os.path.join(QUEUE_DIR, fn)
    return None


def extract_content(path):
    md = open(path, encoding="utf-8").read()
    m = re.search(r"##\s*Generated Post Content\s*\n+(.*?)\n---", md, re.S)
    return m.group(1).strip() if m else None


def extract_media_url(path):
    """Media URL declared in the queue file, if any."""
    md = open(path, encoding="utf-8").read()
    m = re.search(r"\*\*Media URL:\*\*\s*(\S+)", md)
    return m.group(1) if m else ""


def find_image(date_str):
    """Match the image to the PILLAR, not just the date — otherwise a stale
    image from a different pillar gets attached."""
    day = datetime.strptime(date_str, "%Y-%m-%d")
    pillar = PILLARS.get(day.strftime("%A"), "").lower()
    names = [f"{date_str}-{pillar}.png"] if pillar else []
    names += [f"{date_str}-business.png", f"{date_str}-build.png",
              f"{date_str}-agents.png", f"{date_str}-africa.png",
              f"{date_str}-knowledge.png", f"{date_str}-community.png"]
    for n in names:
        p = os.path.join(ROOT, "memory", n)
        if os.path.exists(p):
            return p
    return None


# ------------------------------------------------------------------ publish
def socialize(text):
    """Social platforms do NOT render markdown. '**bold**' shows up as literal
    asterisks. Strip emphasis markers, and collapse the '> ' blockquote prefix
    that queue files use for readability.

    NOTE: the emphasis regex must use re.DOTALL. Without it, '.+?' will not
    cross a newline, so a bold span that wraps across lines ('**China Just
    Opened Its Doors to African\nAmericans...**') does NOT match and the
    asterisks survive onto the live post.
    """
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.S)
    t = re.sub(r"(?m)^\s*>\s?", "", t)
    t = t.replace("__", "").replace("`", "")
    return t.strip()


def try_feedhive(content, media_url, publish_at):
    h = {"Authorization": "Bearer " + FH_TOKEN}
    st, body = http("GET", FH_BASE + "/accounts", h)
    if st != 200:
        return False, "FeedHive GET /accounts -> %s" % st
    st, body = http("POST", FH_BASE + "/posts/schedule", h, {
        "content": socialize(content), "media_urls": [media_url] if media_url else [],
        "platforms": PLATFORMS, "publish_at": publish_at,
    })
    if st in (200, 201):
        try:
            return True, json.loads(body).get("id", "unknown")
        except Exception:
            return True, body[:120]
    return False, "FeedHive POST /posts/schedule -> %s %s" % (st, body[:120])


def build_platform_texts(content):
    """Return {platform: final text that will be published}.

    Extracted from try_blotato so the exact text that ships can be tested
    WITHOUT publishing anything. A test that re-implements this logic instead
    of calling it proves nothing — it can stay green while the real script is
    broken, which is exactly what happened to the first version of
    ops/test-publish-sanitize.py.

    Sanitize ONCE, UP FRONT — markdown must be resolved BEFORE any truncation.
    If a bold span is cut in half by a character limit, the opening '**' loses
    its closing partner, the `\*\*(.+?)\*\*` regex can no longer match it, and
    the literal asterisks survive onto the live post. (Live post 8384191 had
    exactly this: a bold headline cut at the Threads/Instagram limit.)
    """
    clean = socialize(content)
    ig_tags = re.findall(r"#[A-Za-z][A-Za-z0-9]*", clean)
    ig_content = clean
    if len(ig_tags) > 5:
        # Remove the excess tags by REGEX, not by string replace of "tag + space".
        # The LAST tag in a caption has no trailing space, so a replace() on
        # "tag " silently did nothing and the tag survived.
        # The lookahead matches end-of-string as well as a space.
        #
        # NOTE: Blotato truncates to the first 5 tags server-side rather than
        # rejecting (live proof: pending caption 815 chars/7 tags -> live IG
        # post 8383092 793 chars/5 tags, published OK). So this trim is not
        # about avoiding a publish failure - it makes the cut deterministic
        # and local instead of relying on undocumented platform behaviour.
        for t in ig_tags[5:]:
            ig_content = re.sub(r"[ \t]*" + re.escape(t) + r"(?=\s|$)", "",
                                ig_content, count=1)
        ig_content = ig_content.rstrip()
    threads = clean
    if len(threads) > 500:
        threads = threads[:497].rsplit(" ", 1)[0] + "..."

    texts = {}
    for platform in ("facebook", "instagram", "linkedin", "threads"):
        text = ig_content if platform == "instagram" else threads if platform == "threads" else clean
        if platform == "linkedin":
            text = clean + "\n\n- Tumelo Ramaphosa | Studex"
        # Final safety net: a caption with an ODD number of '**' never matches
        # the pair regex, so drop any leftover markers outright. Social
        # platforms do not render markdown — a stray '**' is always wrong.
        text = text.replace("**", "").replace("__", "").replace("`", "")
        texts[platform] = text
    return texts


def try_blotato(content, media_url, key, skip=()):
    """Blotato caps: instagram max 5 hashtags TOTAL, threads max 500 chars.

    skip = set of platforms already published for this date+pillar. They are
    NOT re-posted (that is how a platform ends up with two identical posts).
    """
    res = {}
    texts = build_platform_texts(content)

    for platform in ("facebook", "instagram", "linkedin", "threads"):
        if platform in skip:
            res[platform] = (None, "skipped - already published for this date")
            continue
        account = BLOTATO_ACCOUNTS[platform]
        text = texts[platform]
        target = {"targetType": platform}
        if platform == "facebook":
            target["pageId"] = FACEBOOK_PAGE_ID
        payload = {"post": {"accountId": account,
                            "content": {"platform": platform, "text": text,
                                        "mediaUrls": [media_url] if media_url else []},
                            "target": target}}
        st, body = http("POST", BLOTATO_BASE + "/posts",
                        {"blotato-api-key": key}, payload)
        res[platform] = (st, "ok" if st in (200, 201) else body[:160])
    return res


# --------------------------------------------------------------------- main
def marker_path(date_str, pillar):
    return os.path.join(ROOT, "memory", "published-%s-%s.json" % (date_str, pillar.lower()))


def pending_published(date_str):
    """Platforms already published by the FALLBACK path for this date.

    The fallback (studex-content-automation/scripts/blotato-fallback.js)
    publishes the pending caption and records it in the pending file's own
    `fallback.posted` list. It and this script are two INDEPENDENT publishers
    that both target Instagram and Threads: on 2026-10-22 Instagram received
    two different captions the same day (8383092 biltong from the fallback,
    8384191 coffee from this script) because neither could see the other's
    record. Reading the other path's record closes that hole.
    """
    path = os.path.join(ROOT, "studex-content-automation", "posts", "pending",
                        "%s.json" % date_str)
    if not os.path.exists(path):
        return set()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return set()
    fb = data.get("fallback") or {}
    posted = set(fb.get("posted") or [])
    if fb.get("instagram") == "POSTED":
        posted.add("instagram")
    return {p for p in posted if isinstance(p, str)}


def already_published(date_str, pillar):
    """Per-PLATFORM guard. Returns the SET of platforms already published for
    this date+pillar.

    This must be per-platform, not all-or-nothing. A post often lands on some
    platforms and fails on others (Blotato FB/LinkedIn connections expired),
    and a Friday post can also go out early on one channel by mistake. An
    all-or-nothing marker either double-posts the healthy platform or blocks
    the broken one from ever being filled. Per-platform lets a re-run post
    ONLY the missing platforms.

    The set is the UNION of this path's marker AND the fallback path's
    record, so the two publishers cannot both use one platform on one day.
    """
    path = marker_path(date_str, pillar)
    published = set()
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = None
        if data:
            res = data.get("results") or data
            posted = set(res.get("posted") or [])
            posted |= set(data.get("posted") or [])
            published |= {p for p in posted if isinstance(p, str)}
    return published | pending_published(date_str)


def write_marker(date_str, pillar, results):
    """Union the new results with anything already recorded — never lose a
    platform that was published by an earlier run."""
    path = marker_path(date_str, pillar)
    prev = already_published(date_str, pillar)
    posted = sorted(prev | set(results.get("posted") or []))
    failed = sorted(set(results.get("failed") or []))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"date": date_str, "pillar": pillar,
                   "results": {"posted": posted, "failed": failed},
                   "posted": posted,
                   "at": datetime.now(SAST).isoformat()}, f, indent=2)


def resolve_blotato_key():
    """Return the Blotato key, or (None, reason) if it is not usable.

    2026-10-28. The publisher used to read the key and publish. It had no
    guard at all, so a redaction artefact left in the .env slot was sent
    straight to the Blotato API - and a redaction artefact is exactly what
    the credential slot checker refuses to call a credential.

    THE ORDER IS THE POINT. The credential is a PRECONDITION: if it is not
    a credential, nothing downstream can be trusted, and the message must
    come BEFORE any content validation. Otherwise a broken credential is
    only ever reported when the caption happens to be valid - the guard
    was in the wrong place to protect anything.

    The classification is SHARED with ops/check-credential-slots.py (via
    cred_env) so the pre-flight and the checker cannot disagree about
    what a credential is.
    """
    env = load_env()
    raw = os.environ.get("BLOTATO_API_KEY")
    source = "the environment"
    if not raw:
        raw = env.get("BLOTATO_API_KEY")
        source = "the .env file"
    if not raw:
        return None, ("BLOTATO_API_KEY is not set in the environment or the "
                      ".env file")
    try:
        import cred_env
        kind = cred_env._classify_credential(raw)
    except Exception:
        kind = "UNKNOWN"
    if kind != "CREDENTIAL":
        return None, ("BLOTATO_API_KEY is not shaped like a credential "
                      "(it is %s, from %s)" % (kind, source))
    return raw, None


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now(SAST).strftime("%Y-%m-%d")
    day = datetime.strptime(date_str, "%Y-%m-%d")
    dow = day.strftime("%A")
    pillar = PILLARS.get(dow)
    now = datetime.now(SAST)
    print("=== Studex Daily Post ===")
    print("Date: %s (%s) | Pillar: %s | Now: %s SAST" % (date_str, dow, pillar, now.isoformat()))

    # 🔑 PRECONDITION FIRST. The credential gate runs BEFORE the pillar
    # check, before the queue lookup and before any content validation.
    # A publisher with an unusable key must refuse before it does
    # anything at all - otherwise "no post queued" masks "your credential
    # is broken", and the operator fixes the wrong thing.
    key, key_problem = resolve_blotato_key()
    if key_problem:
        print("REFUSING TO PUBLISH: %s." % key_problem)
        print("A credential that is not shaped like a credential cannot "
              "publish anything - fix the slot, then re-run.")
        return 1

    if pillar is None:
        print("No pillar for %s — skipping." % dow)
        return 0

    qf = queue_file_for(date_str, pillar)
    if not qf:
        print("NO POST QUEUED for %s (%s). Nothing to publish." % (date_str, pillar))
        return 0

    # Never publish a future date early — that would post tomorrow's copy today.
    target_day = datetime.strptime(date_str, "%Y-%m-%d").date()
    today_day = datetime.now(SAST).date()
    if target_day > today_day:
        print("REFUSING TO PUBLISH: %s is in the future (today is %s SAST). "
              "Queue file %s is staged only." % (date_str, today_day, os.path.basename(qf)))
        return 0

    content = extract_content(qf)
    if not content:
        print("Queued file found but no '## Generated Post Content' block: %s" % qf)
        return 0

    img = find_image(date_str)
    image_exists = img is not None
    print("Queue file: %s" % os.path.basename(qf))
    print("Image: %s" % (img or "NONE FOUND"))

    issues = validate_brand(content, pillar, image_exists)
    if issues:
        print("VALIDATION FAILED — not publishing:")
        for i in issues:
            print("  " + i)
        return 1
    print("OK validate_brand() passed (10 checks)")

    media_url = os.environ.get("POST_MEDIA_URL", "") or extract_media_url(qf)
    if not media_url:
        print("NOTE: no media URL for this post — publishing without an image. "
              "Add '**Media URL:** <url>' to the queue file or set POST_MEDIA_URL.")
    publish_at = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if publish_at < now:
        publish_at = now
    publish_at_utc = publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    already = already_published(date_str, pillar)
    if already:
        print("Already published on: %s — only the missing platforms will be posted."
              % ", ".join(sorted(already)))

    fh_ok, fh_detail = try_feedhive(content, media_url, publish_at_utc)
    print("FeedHive: %s (%s)" % ("SCHEDULED" if fh_ok else "unavailable", fh_detail))

    bres = {}
    if key:
        bres = try_blotato(content, media_url, key, skip=already)
        for plat, (st, note) in bres.items():
            print("Blotato %-9s -> %s %s" % (plat, st, note))
    else:
        print("BLOTATO_API_KEY not set — no fallback publish")

    posted = [p for p, (st, note) in bres.items() if note == "ok"]
    skipped = [p for p, (st, note) in bres.items() if st is None]
    failed = [p for p, (st, note) in bres.items() if note != "ok" and st is not None]
    if posted or skipped:
        write_marker(date_str, pillar, {"posted": posted, "failed": failed})

    entry = """
## %s (%s — %s) — daily-post cron

**Content:** %s
**Platforms:** %s
**Scheduled:** 09:00 SAST target (%s)
**Media:** %s
**FeedHive post ID:** %s
**Status:** %s
**Notes:** validate_brand() passed (10 checks). FeedHive: %s. Blotato posted: %s. Blotato failed: %s.%s
---
""" % (date_str, dow, pillar, content[:300].replace("\n", " ") + "...",
       ", ".join(PLATFORMS), publish_at_utc, media_url or img or "none",
       fh_detail if fh_ok else "N/A — FeedHive unavailable (%s)" % fh_detail,
       "PARTIAL — posted: %s" % (", ".join(posted) or "none"),
       fh_detail, ", ".join(posted) or "none", ", ".join(failed) or "none",
       (" Skipped (already published): %s." % ", ".join(skipped)) if skipped else "")

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    print("Logged to %s" % LOG_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
