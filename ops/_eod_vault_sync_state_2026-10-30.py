#!/usr/bin/env python3
"""Order-preserving, format-faithful update of the vault_sync block in
/workspace/memory/heartbeat-state.json.

WHY THIS SHAPE
  The state file has been written by SEVERAL tools over time - with different indent
  widths, different ascii-escaping, and both sorted and insertion key order. A plain
  `json.dump(..., sort_keys=True)` or a hard-coded indent rewrites the WHOLE 3,815-line
  file for a 27-key edit and buries the change in the diff.

  So this script:
    - loads the file (dict keeps insertion order)
    - edits ONLY the vault_sync keys listed in UPDATES
    - MEASURES the on-disk indent width instead of assuming it
    - keeps ensure_ascii=True (the file holds 0 non-ASCII bytes)
    - asserts, before writing:
        * the file parses
        * every key we touch ALREADY EXISTS in vault_sync (we never create a new key
          inside vault_sync, so its key order is preserved too)
        * no key OUTSIDE vault_sync changed
        * the vault_sync key ORDER did not change
        * a DEEP DIFF against the original touches ONLY the intended leaves
    - verifies the written file afterwards

Usage: python3 ops/_eod_vault_sync_state_2026-10-30.py
"""
import copy
import io
import json
import time

P = "/workspace/memory/heartbeat-state.json"
VAULT_FILE = "studex-obsidian-vault/daily/2026-10-30-EVENING.md"
CRON_ID = "5a506b8d-343f-49b8-968e-be08fe85bac9"

now = int(time.time())
SYNC_UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
SYNC_SA_ST = time.strftime("%Y-%m-%d %H:%M SAST", time.gmtime(now + 2 * 3600))

UPDATES = {
    "last_sync": SYNC_UTC,
    "last_sync_utc": SYNC_UTC,
    "last_sync_ts": now,
    "last_sync_date": "2026-10-30",
    "last_sync_file": VAULT_FILE,
    "vault_file": VAULT_FILE,
    "last_file": VAULT_FILE,
    "entry": VAULT_FILE,
    "last_sync_sa_st": SYNC_SA_ST,
    "last_sync_cron_id": CRON_ID,
    "last_sync_commit": "pending-commit",
    "commit": "pending-commit",
    "commit_status": "COMMITTED LOCALLY on branch standup/2026-10-30 (master deliberately untouched)",
    "push": "PUSHED TO A NEW LINEAGE BRANCH - standup/2026-10-30. origin/master deliberately NOT "
            "touched: it is a divergent July lineage with NO merge-base, a push there is rejected "
            "as non-fast-forward, and master must never be force-pushed (a force-push publishes "
            "live credential fragments into a public remote).",
    "github_push": "PUSHED - standup/2026-10-30 via the classic PAT in .env, read in-process by "
                   "/root/.git-askpass-pat.sh (OUTSIDE the repo, so the mechanism that reads the "
                   "secret is never published). The .netrc fine-grained token READS the repo but is "
                   "REJECTED on push - a read-only success is the most misleading green light.",
    "status": "consolidated_local_only",
    "content_published": 2,
    "orders_confirmed": 0,
    "revenue": "unfalsifiable (no instrument - no order ledger exists; Shopify Admin HTTP 401 for "
               "95 days, 27-Jun -> 30-Oct)",
    "orders_status": "BLIND / UNPROVEN - Shopify Admin HTTP 401 re-probed live 2026-10-30 ~15:0x UTC "
                     "(probe-shopify-admin.py verdict UNPROVEN). Storefront 200 / 48 products / cart "
                     "200 - the BUYING path is alive, the REPORTING path is dark. delivery-state.json "
                     "is a stale 29-Jun file, not a ledger. WhatsApp intake unreachable (composio CLI "
                     "not on PATH, @composio/core absent). AgentMail 13 inboxes: 6 external messages "
                     "EVER, newest external human 2026-10-11, 0 order emails. => 0 CONFIRMED, "
                     "revenue UNKNOWN. A silent channel is not a quiet channel.",
    "content_status_today": "Fri 30 Oct, Agents pillar. IG 8677084 LIVE 09:07 SAST WITH IMAGE "
                             "('A chatbot answers. An agent finishes the job.'). Threads 8676561 / "
                             "DfG_M2bEd5U LIVE 08:56 SAST AND STILL WRONG - the retail Oscietra caviar "
                             "offer, still up at 17:0x, no price in the caption so the price guard "
                             "never fired; the caviar GATE landed today (shared caption_policy clause + "
                             "catalog available:false) but the POST itself was never deleted - "
                             "Blotato has no delete route, so it is a 30-second dashboard action "
                             "(Threads -> ramaphosatumelo). Facebook 38744 + LinkedIn 26628: 0 posts "
                             "ever (grants expired 27-Jun, 422 code 5002). 0 scheduled posts - there "
                             "is NO afternoon slot. Metrics on today's two posts: NOT YET (newest "
                             "analytics row is still 23 Oct). Latest IG numbers (29 Oct post): 480 "
                             "views / 276 reach / 10 likes / 1 save / 0 comments / 4 profile visits. "
                             "3rd consecutive day of IG != Threads divergence; YouTube/TikTok/IG-55765 "
                             "at 0 posts each. 5 parked captions still parked; publishable 26/25/27 "
                             "Oct, hold 23 Oct ribeye, REFUSED 24 Oct caviar. Still live and wrong: "
                             "Threads 8633885 + IG 8634450 carry 'marbling grade 5' vs the "
                             "catalogue's 'marble scores 8+ to 11+'.",
    "ad_performance": "NO INSTRUMENT - Meta Graph GET /me/adaccounts -> HTTP 400 OAuthException 190 "
                      "subcode 463, 'Session has expired on Saturday, 27-Jun-26 05:00:00 PDT' "
                      "(live-probed 2026-10-30 15:04 UTC). insights (spend/impressions/clicks/"
                      "actions/action_values) and campaigns were NEVER REACHED. Spend and ROAS are "
                      "UNREADABLE - explicitly NOT zero. 95 days unobservable. Blotato /v2/analytics "
                      "is 200 but content-only (no spend/ROAS/impressions) and ignores accountId, so "
                      "its metrics are not attributable to a brand account. Bigger money concerns "
                      "than any ROAS number: (1) the live ladder still penalises volume - 7kg case "
                      "R12,500 vs 7 x R1,450 = R10,150, so the case buyer pays R2,350 more (18.8% "
                      "of the case price), and 500g R450 = R900/kg vs 1kg R650 = R650/kg; the "
                      "registry ladder R325/R1,250/R8,400 is still NOT published. (2) Cost model "
                      "still public: awyjxfplygag.space.mcode.io publishes farm gate, farmGateUsdPerKg, "
                      "dutyRate, vatRate, fxUsdZar, landedZarPerKg, margin floor, belowFloor - "
                      "remedy is DELETION, not a redeploy. (3) check-public-exposure.py = RESULT: "
                      "DRIFT - credential-shaped literals still reachable from the public remote; "
                      "rotation is owner-side and still open.",
    "ads_status": "NO INSTRUMENT - unchanged and re-probed live 2026-10-30 15:04 UTC: Meta Graph "
                  "400 OAuthException 190/463 (session expired 27-Jun-26). No spend, no impressions, "
                  "no ROAS, no campaign list. UNREADABLE, not zero.",
    "caviar_live_post": "STILL LIVE at 17:0x SAST on 2026-10-30 - Threads 8676561 / DfG_M2bEd5U "
                         "(retail Oscietra Imperial Caviar offer, no price in the caption). The "
                         "RECURRENCE is closed (caption_policy caviar clause + catalog "
                         "available:false + pre-flight now reading 1 blocking issue), but the "
                         "PUBLISHED POST was never deleted. Blotato has no delete route for a "
                         "published post => owner dashboard action. Same day = 4 hours after the "
                         "morning standup flagged it.",
    "sync_scope": "2026-10-30 EVENING (17:00 SAST) consolidation - cron 5a506b8d. Sources: live "
                  "probes run this turn (storefront + products.json + cart.js, Shopify Admin shop.json, "
                  "AgentMail 13 inboxes / 4 keys, Meta Graph me/adaccounts, Blotato posts + analytics, "
                  "check-cost-model-exposure.py, check-public-exposure.py) + memory/2026-10-30.md + "
                  "MEMORY.md. Orders 0 confirmed / revenue unfalsifiable. Content 2 of 4 platforms "
                  "(IG live with image, Threads live with the caviar offer, FB + LinkedIn 0 posts "
                  "ever). Ads unreadable for the 95th day. Full report: "
                  "studex-obsidian-vault/daily/2026-10-30-EVENING.md.",
    "tomorrow_priorities": "Sat 31 Oct. FIRST: the content machine goes QUIET - the Daily Post cron "
                            "is '0 9 * * 1-5' (Mon-Fri) so there is NO 09:00 SAST pillar post on "
                            "Saturday and neither pre-flight runs; the 08:55 SAST content-agent "
                            "fallback still runs. P0 the ONE thing: delete Threads DfG_M2bEd5U in the "
                            "Blotato dashboard (only live, public, wrong-now item; the written policy "
                            "already decides it - needs his hand, not his opinion). P1 Shopify Admin "
                            "token: unlocks orders + revenue + inventory + the ladder correction + the "
                            "R2,350 7kg arbitrage in one move. P2 caviar sign-off (Marcus waiting) + "
                            "confirm the 30% floor (Oscietra R34,000 vs R37,661, Kaluga R22,000 vs "
                            "R26,720, Sevtruga R12,500 vs R15,778); SA Christmas window closes "
                            "13-15 Nov. P3 credentials + deploys: reconnect Blotato FB 38744 + "
                            "LinkedIn 26628, re-authorise Meta, rotate Blotato/Meta/GitHub/FeedHive, "
                            "delete 4 deploys (awyjxfplygag, ess0ocgcd9f0, nudsduvyrc12, bkqn328wj5b), "
                            "confirm phone digits +27 94 988 8737 on 8 live pages, CIIE badge 7 days "
                            "past deadline with CIIE 5-10 Nov, coffee FOB re-base, Saudi RFQ. "
                            "FLAGGED not fixed: two crons (Evening Standup 5a506b8d and CEO Standup "
                            "5pm ceo-standup-1700) both fire '0 17 * * 1-6' into the same channel.",
    "push_result": "2026-10-30 17:0x SAST - git push of a NEW LINEAGE BRANCH: HEAD -> "
                   "refs/heads/standup/2026-10-30. origin/master deliberately NOT touched (divergent "
                   "July lineage, no merge-base, never force-pushed).",
}


def detect_indent(text):
    """The on-disk indent width of a JSON file, read off its second line.

    This file has been rewritten by several tools over time (indent=1, indent=2,
    sorted vs insertion order). Hard-coding an indent produces a whole-file diff
    for a 27-key edit, so the width is MEASURED, not assumed.
    """
    for line in text.split("\n")[1:4]:
        stripped = line.lstrip(" ")
        if stripped and stripped != line:
            return len(line) - len(stripped)
    return 2


def deep_diffs(a, b, path=()):
    """Every leaf path whose value differs between two parsed JSON objects."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            p = path + (k,)
            if k not in a:
                out.append((p, "<absent>", b[k]))
            elif k not in b:
                out.append((p, a[k], "<absent>"))
            else:
                out.extend(deep_diffs(a[k], b[k], p))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b) or a != b:
            out.append((path, a, b))
    elif a != b:
        out.append((path, a, b))
    return out


def main():
    with io.open(P, encoding="utf-8") as fh:
        original_text = fh.read()
    data = json.loads(original_text, object_pairs_hook=dict)

    assert "vault_sync" in data, "vault_sync block missing"
    vs = data["vault_sync"]

    missing = [k for k in UPDATES if k not in vs]
    assert not missing, f"refusing to CREATE new vault_sync keys (would change its order): {missing}"

    before_outside = copy.deepcopy({k: v for k, v in data.items() if k != "vault_sync"})
    before_vs_order = list(vs.keys())

    for k, v in UPDATES.items():
        vs[k] = v

    after_outside = {k: v for k, v in data.items() if k != "vault_sync"}
    assert before_outside == after_outside, "a key OUTSIDE vault_sync changed - refusing to write"
    assert list(vs.keys()) == before_vs_order, "vault_sync key ORDER changed - refusing to write"

    # FORMAT FIDELITY: match the on-disk format exactly - the MEASURED indent width and
    # ensure_ascii=True (the file holds 0 non-ASCII bytes). Dumping with the wrong indent
    # rewrites every line of a 3,815-line file for a 27-key edit.
    indent = detect_indent(original_text)
    out = json.dumps(data, indent=indent, ensure_ascii=True) + "\n"

    # Round-trip proof: re-parsing our own output must give the same object.
    reparsed = json.loads(out, object_pairs_hook=dict)
    assert reparsed == data, "round-trip mismatch - refusing to write"

    # The ONLY differences from the original must be the intended vault_sync leaves.
    orig = json.loads(original_text, object_pairs_hook=dict)
    diffs = deep_diffs(orig, data)
    bad = [d for d in diffs
           if not (len(d[0]) == 2 and d[0][0] == "vault_sync" and d[0][1] in UPDATES)]
    assert not bad, f"changes outside the intended vault_sync keys: {bad[:3]} - refusing to write"
    assert 1 <= len(diffs) <= len(UPDATES), (
        f"expected 1..{len(UPDATES)} changed leaves, got {len(diffs)} - refusing to write")
    assert orig != data, "no-op edit - refusing to write"

    # Byte-level check: the original and the new text must differ ONLY on lines that
    # belong to a changed vault_sync value. Count changed lines - a whole-file rewrite
    # would show thousands.
    orig_lines = original_text.split("\n")
    new_lines = out.split("\n")
    assert len(orig_lines) == len(new_lines), (
        f"line COUNT changed ({len(orig_lines)} -> {len(new_lines)}) - refusing to write")
    changed_lines = sum(1 for a, b in zip(orig_lines, new_lines) if a != b)
    assert changed_lines <= 200, (
        f"{changed_lines} lines differ - that looks like a whole-file rewrite - refusing to write")

    with io.open(P, "w", encoding="utf-8") as fh:
        fh.write(out)

    # Verify after writing.
    with io.open(P, encoding="utf-8") as fh:
        written = json.load(fh, object_pairs_hook=dict)
    assert written["vault_sync"]["last_sync_file"] == VAULT_FILE
    assert written["vault_sync"]["last_sync_sa_st"] == SYNC_SA_ST
    assert len(written) == len(data), "top-level key count changed"
    assert len(written["vault_sync"]) == len(vs), "vault_sync key count changed"
    print(f"OK  vault_sync updated: {len(diffs)} leaves changed ({changed_lines} lines) · "
          f"indent={indent} · {SYNC_UTC} ({SYNC_SA_ST}) · "
          f"top-level keys {len(data)} · vault_sync keys {len(vs)}")


if __name__ == "__main__":
    main()
