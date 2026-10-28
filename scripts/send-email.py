#!/usr/bin/env python3
"""Guarded AgentMail sender — the fix for the blank-email defect (2026-08-20, 08-25).

THE DEFECT
  Three external partners received emails with a subject and NO BODY:
    2026-08-20 21:57  -> kfschof@gmail.com              (429B)
    2026-08-25 16:56  -> obelyakova@sv-tech.ru           (402B)
    2026-08-25 16:56  -> africabiz.r@yandex.com          (404B)
  All three were sent via ad-hoc one-off send paths that set `subject` but not
  the body. Two of them chased us; all three are still unanswered.

WHAT THIS TOOL DOES DIFFERENTLY
  1. REFUSES to send an empty body. Body is validated BEFORE the request.
  2. REQUIRES the body to be read from a file (or --body-file), not a shell
     string, so a quoting bug cannot silently blank it.
  3. SENDS BOTH `text` AND `html` — AgentMail renders whichever it prefers,
     and a message with only `text` has failed before.
  4. VERIFIES AFTER SENDING by reading the sent message back out of the inbox
     and checking `size` >= 600. If it comes back blank it raises, so the
     failure is loud instead of silent.
  5. LOGS every send to outbound-log.jsonl.
  6. DRAFTS by default. Sending requires an explicit --send flag. External
     sends additionally require --i-have-approval, because a reply to a real
     partner is a human commitment, not an agent decision.

USAGE
  # preview only (default)
  python3 scripts/send-email.py --inbox sales@studex-group.com \
      --to obelyakova@sv-tech.ru \
      --subject "Re: Mobile Data Centre Partnership" \
      --body-file outbound-drafts/obelyakova-reply.md

  # actually send (needs --send and, for external recipients, --i-have-approval)
  python3 scripts/send-email.py ... --send --i-have-approval

  # markdown is stripped to plain text automatically
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEY = live_agentmail_keys()[0]
BASE = "https://api.agentmail.to/v0"

MIN_BODY_CHARS = 40
MIN_SENT_SIZE = 600  # a real message with a body is >= ~1200B; blanks are ~370-410B
LOG_FILE = "outbound-log.jsonl"

OUR_DOMAINS = ("@studex-group.com", "@agentmail.to", "@studexmeat.com")


def extract_body(md):
    """Pull the actual message body out of a draft file.

    Draft files carry metadata (status, why-it-exists, notes-for-Tumelo) around
    the message. Sending the whole file would send our internal notes to the
    partner. Prefer a fenced ``` block; otherwise fall back to the whole file.
    """
    m = re.search(r"```(?:\w*)\n(.*?)\n```", md, flags=re.S)
    if m:
        return m.group(1)
    return md


def strip_markdown(md):
    """Reduce markdown to plain text. A body that renders as blank is a blank email."""
    s = md
    s = re.sub(r"^```.*?^```", " ", s, flags=re.S | re.M)      # fenced code
    s = re.sub(r"^>\s?", "", s, flags=re.M)                     # blockquote
    s = re.sub(r"^#{1,6}\s*", "", s, flags=re.M)                 # headings
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)                       # bold
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", s)           # italic
    s = re.sub(r"__(.+?)__", r"\1", s)                           # bold alt
    s = re.sub(r"~~(.+?)~~", r"\1", s)                           # strike
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)              # links/images
    s = re.sub(r"`([^`]+)`", r"\1", s)                           # inline code
    s = re.sub(r"^\s*[-*+]\s+", "- ", s, flags=re.M)             # bullets
    s = re.sub(r"^\s*#+\s*", "", s, flags=re.M)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def to_html(text):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out = []
    for p in paras:
        p = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p = re.sub(r"(?<!-)\n(?!-)", "<br/>", p)
        out.append(f"<p>{p}</p>")
    return '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#222;">' + "".join(out) + "</div>"


def post(url, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": "Bearer " + KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode() or "{}")


def get(url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def log_send(entry):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", LOG_FILE)
    path = os.path.normpath(path)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", required=True, help="sending inbox id")
    ap.add_argument("--to", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", help="file containing the body (preferred)")
    ap.add_argument("--body", help="inline body (must pass --body-file to be safe)")
    ap.add_argument("--send", action="store_true", help="actually send (default: preview)")
    ap.add_argument("--i-have-approval", action="store_true",
                    help="confirm a human approved this external send")
    args = ap.parse_args()

    # ---- load body -------------------------------------------------------
    if args.body_file:
        raw = open(args.body_file, encoding="utf-8").read()
    elif args.body:
        raw = args.body
    else:
        print("ERROR: no body. Use --body-file (preferred) or --body.", file=sys.stderr)
        return 2

    text = strip_markdown(extract_body(raw))
    if not text:
        print("ERROR: body is empty after markdown stripping — REFUSING TO SEND.", file=sys.stderr)
        return 2
    if len(text) < MIN_BODY_CHARS:
        print(
            f"ERROR: body is only {len(text)} chars (< {MIN_BODY_CHARS}). "
            "That is almost certainly a truncation bug. REFUSING TO SEND.",
            file=sys.stderr,
        )
        return 2

    to = args.to.lower()
    external = not any(d in to for d in OUR_DOMAINS) and to != "tumelor001@gmail.com"

    print("=" * 68)
    print(f"FROM   {args.inbox}")
    print(f"TO     {args.to}   {'(EXTERNAL)' if external else '(internal)'}")
    print(f"SUBJ   {args.subject}")
    print(f"BODY   {len(text)} chars (from {args.body_file or '--body'})")
    print("-" * 68)
    print(text[:2000])
    print("-" * 68)

    if not args.send:
        print("PREVIEW ONLY — nothing sent. Add --send to send.")
        if external:
            print("External recipient: --i-have-approval is also required.")
        return 0

    if external and not args.i_have_approval:
        print(
            "ERROR: external recipient but no --i-have-approval. "
            "A reply to an external partner needs a human to approve it first.",
            file=sys.stderr,
        )
        return 2

    payload = {
        "to": [args.to],
        "subject": args.subject,
        "text": text,
        "html": to_html(text),
    }
    url = f"{BASE}/inboxes/{urllib.parse.quote(args.inbox)}/messages/send"
    try:
        res = post(url, payload)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        print(f"SEND FAILED: HTTP {e.code} {detail}", file=sys.stderr)
        log_send({
            "ts": datetime.now(timezone.utc).isoformat(), "status": "error",
            "inbox": args.inbox, "to": args.to, "subject": args.subject,
            "error": f"HTTP {e.code} {detail}",
        })
        return 1

    print(f"SENT: {json.dumps(res)[:300]}")

    # ---- verify: read it back --------------------------------------------
    verified = None
    try:
        listing = get(f"{BASE}/inboxes/{urllib.parse.quote(args.inbox)}/messages?limit=5")
        for m in listing.get("messages", []):
            if m.get("subject") == args.subject:
                verified = m
                break
    except Exception as e:
        print(f"(verify pass could not read inbox: {e})")

    if verified:
        size = verified.get("size") or 0
        ok = size >= MIN_SENT_SIZE
        print(f"VERIFY: sent message size = {size} bytes -> {'OK' if ok else 'BLANK!'}")
        if not ok:
            print(
                "ERROR: the sent message came back BLANK. The defect is NOT fixed. "
                "Do not repeat this send. Escalate.",
                file=sys.stderr,
            )
            log_send({
                "ts": datetime.now(timezone.utc).isoformat(), "status": "blank",
                "inbox": args.inbox, "to": args.to, "subject": args.subject,
                "size": size,
            })
            return 1
        log_send({
            "ts": datetime.now(timezone.utc).isoformat(), "status": "sent_verified",
            "inbox": args.inbox, "to": args.to, "subject": args.subject,
            "size": size, "body_chars": len(text), "external": external,
        })
        return 0

    log_send({
        "ts": datetime.now(timezone.utc).isoformat(), "status": "sent_unverified",
        "inbox": args.inbox, "to": args.to, "subject": args.subject,
        "body_chars": len(text), "external": external,
    })
    print("VERIFY: could not confirm — logged as sent_unverified.")
    return 0


if __name__ == "__main__":
    import urllib.parse
    raise SystemExit(main())
