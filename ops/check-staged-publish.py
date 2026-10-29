#!/usr/bin/env python3
"""Fail when a staged social caption never reached any platform.

WHY THIS EXISTS
---------------
The Daily Content Agent (cron 84025fd8, 08:55 SAST, EVERY day) generates a
product caption and stages it in
`studex-content-automation/posts/pending/<date>.json`. That staging is only
half the job - the caption is supposed to be PUBLISHED.

The publisher for those staged captions is `blotato-fallback.js`. Nothing
schedules it: no cron message names it, no shell script calls it, and
`daily-content-agent.js` has never once invoked it (proved with
`git log -S "blotato-fallback" -- studex-content-automation/scripts/daily-content-agent.js`
-> empty). It last ran by hand on 2026-10-22.

So since 2026-10-22 the captions have staged cleanly and published nowhere.
Everything downstream stays green: the content agent exits 0, the 09:20 SAST
pending pre-flight reports CLEAN (it validates a publish that never happens),
and the pending file's own `status` still reads
`APPROVED_PENDING_FB_TOKEN` - which describes a WAITING state, not a
"never went out" state.

The trap: a staged caption that never published is indistinguishable from a
staged caption that is merely waiting for the Facebook token, unless you
actually look. Four were found on 2026-10-26 - Wagyu Ribeye Steak (10-23),
Oscietra Imperial Caviar (10-24), Washed Coffee (10-25), Fire & Feast Box
(10-26).

WHY A CHECKER AND NOT A REMINDER
--------------------------------
The daily-post.py guard already unions path A's marker and path B's marker so
the two publishers cannot both use one platform on one day. That guard
prevents DOUBLE posting. It says nothing about a caption that posts ZERO
times. The two failure modes are opposites and only one of them had a check.

RULES
-----
For every pending file:
  1. A caption counts as PUBLISHED if the pending file records a non-empty
     `fallback.posted` / `fallback.instagram`, OR the caption's opening text
     is found among the live Blotato posts (the live check catches a lost or
     hand-edited pending record).
  2. A caption that is not PUBLISHED is a FINDING once its date is in the
     PAST. Today's file is IN-FLIGHT until the publish window closes
     (staging lands ~09:05-09:13 SAST), so it is reported, not failed.
  3. A finding exits non-zero.

This checker NEVER publishes. It only reads pending files and (optionally) the
Blotato post list.

Run:  python3 ops/check-staged-publish.py            # local records only
      python3 ops/check-staged-publish.py --live     # + prove against live posts
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

SAST = timezone(timedelta(hours=2))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_DIR = os.environ.get(
    "STAGED_PENDING_DIR",
    os.path.join(ROOT, "studex-content-automation", "posts", "pending"),
)
BLOTATO_BASE = "https://backend.blotato.com/v2"
# How many leading words of the caption to match against a live post. Long
# enough to be specific, short enough to survive a leading emoji or a
# rewritten first line.
MATCH_WORDS = 8
# The last moment today's staged caption could still legitimately be in
# flight. The content agent stages at 08:55 SAST and takes ~18 minutes, so
# the pending file lands ~09:05-09:13 SAST; the 09:20 SAST pending
# pre-flight is the last checkpoint. After that, a staged caption that has
# not published is a finding, not a wait.
PUBLISH_CUTOFF = (9, 20)


def today_sast() -> str:
    return datetime.now(SAST).strftime("%Y-%m-%d")


def now_sast():
    return datetime.now(SAST)


def cutoff_passed(now=None) -> bool:
    """True once today's publish window has closed."""
    now = now or now_sast()
    return (now.hour, now.minute) >= PUBLISH_CUTOFF


def load_env(path: str) -> dict:
    env = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return env


def live_posts(env: dict) -> list:
    """Return the live Blotato posts, or [] when unavailable.

    Never raises: an unreachable API must not masquerade as 'nothing
    published', and must not crash the checker either. A missing live list
    downgrades the verdict to LOCAL, which is reported honestly.
    """
    key = env.get("BLOTATO_API_KEY")
    if not key:
        return []
    req = urllib.request.Request(
        BLOTATO_BASE + "/posts?limit=50", headers={"blotato-api-key": key}
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.load(r)
    except Exception:
        return []
    items = data.get("items") if isinstance(data, dict) else data
    return items if isinstance(items, list) else []


def fallback_recorded(pending: dict) -> list:
    """Platforms the pending file itself says were published."""
    fb = pending.get("fallback") or {}
    out = set()
    for p in fb.get("posted") or []:
        if isinstance(p, str):
            out.add(p)
    if fb.get("instagram") == "POSTED":
        out.add("instagram")
    if fb.get("threads") == "POSTED":
        out.add("threads")
    return sorted(out)


def caption_key(caption: str) -> str:
    return " ".join((caption or "").split()[:MATCH_WORDS]).lower()


def live_match(caption: str, posts: list) -> str:
    """Return the platform of a live post whose opening text matches."""
    key = caption_key(caption)
    if not key:
        return ""
    for p in posts:
        text = p.get("text") or p.get("caption") or ""
        if key and key in " ".join(text.split()).lower():
            return p.get("platform") or "?"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="also prove each verdict against the live Blotato post list")
    ap.add_argument("--today", default=os.environ.get("STAGED_TODAY") or "",
                    help="treat this YYYY-MM-DD as today (SAST)")
    ap.add_argument("--now", default=os.environ.get("STAGED_NOW") or "",
                    help="pretend the current SAST time is HH:MM (testing)")
    args = ap.parse_args()

    today = args.today or today_sast()
    now = now_sast()
    if args.now:
        try:
            hh, mm = args.now.split(":")
            now = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
        except ValueError:
            pass
    window_closed = cutoff_passed(now)
    env = load_env(os.path.join(ROOT, ".env"))

    posts = []
    if args.live:
        posts = live_posts(env)
        if not posts:
            print("  ! live post list unavailable - verdicts fall back to LOCAL records only")
    live_known = bool(posts)

    if not os.path.isdir(PENDING_DIR):
        print("STAGED PUBLISH CHECK")
        print("  pending dir not found: %s" % PENDING_DIR)
        print("VERDICT: CLEAN - nothing to check")
        return 0

    files = sorted(f for f in os.listdir(PENDING_DIR) if f.endswith(".json"))
    rows = []
    findings = []
    for name in files:
        date_str = name[:-5]
        try:
            with open(os.path.join(PENDING_DIR, name), encoding="utf-8") as f:
                pending = json.load(f)
        except Exception:
            continue
        caption = pending.get("caption") or ""
        recorded = fallback_recorded(pending)
        matched = live_match(caption, posts) if live_known else ""
        if recorded or matched:
            verdict = "PUBLISHED"
            detail = ",".join(recorded) or ("live:" + matched)
        elif date_str > today:
            verdict = "FUTURE"
            detail = "not yet staged"
        elif date_str == today and not window_closed:
            verdict = "IN-FLIGHT"
            detail = "awaiting publish window"
        elif date_str == today:
            verdict = "STAGED-NOT-PUBLISHED"
            detail = "window closed, never published"
            findings.append((date_str, name, pending.get("status") or "?"))
        else:
            verdict = "STAGED-NOT-PUBLISHED"
            detail = "no fallback record, not found live"
            findings.append((date_str, name, pending.get("status") or "?"))
        rows.append((date_str, verdict, detail, pending.get("status") or "-"))

    print("STAGED PUBLISH CHECK  (today %s SAST %s, live=%s, window %s)"
          % (today, now.strftime("%H:%M"),
             "yes" if live_known else "no",
             "closed" if window_closed else "open"))
    print("-" * 96)
    print("  %-12s %-22s %-34s %s" % ("DATE", "VERDICT", "DETAIL", "FILE STATUS"))
    for date_str, verdict, detail, status in rows:
        print("  %-12s %-22s %-34s %s" % (date_str, verdict, detail[:34], status[:34]))
    if not rows:
        print("  (no pending files)")
    print("-" * 96)

    if findings:
        print("  %d staged caption(s) never reached any platform:" % len(findings))
        for date_str, name, status in findings:
            print("    - %s  %s  (status=%s)" % (date_str, name, status))
        print()
        print("VERDICT: EXPOSED - staged content that never published.")
        print("  Root cause (2026-10-29): the Facebook Graph token died on")
        print("  27 Jun 2026 (FB190 'session has expired'). The caption was")
        print("  queued and nothing published it, because the publisher")
        print("  (studex-content-automation/scripts/blotato-fallback.js) was")
        print("  an ORPHAN - no cron job, no script and no checklist entry")
        print("  invoked it. Threads and Instagram were healthy the whole")
        print("  time. FIXED: daily-content-agent.js now runs the fallback")
        print("  when its Facebook post fails, so a dead Facebook token no")
        print("  longer silences every other platform.")
        print("  This checker does not publish - it only reports.")
        return 1

    print("VERDICT: CLEAN - every staged caption reached a platform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
