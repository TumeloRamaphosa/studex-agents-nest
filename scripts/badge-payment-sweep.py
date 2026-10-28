"""CIIE badge payment-record sweep (CNY 200).

Runs the deadline escalation check:
  - sweeps EVERY live AgentMail key (main + warmup + warroom + ciie-nurture)
  - every inbox any key can see
  - limit=1000 with a truncation assert (a truncated sweep silently excludes
    the window under investigation)
  - looks for a payment record: CNY 200, transfer receipt, payment confirmation

Prints VERDICT: PAID | NOT_PAID. Exit 0 either way; the caller decides.
"""
import json, re, sys, pathlib, urllib.request, urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys, assert_not_truncated

KEYS = live_agentmail_keys()
LIMIT = 1000

# Payment evidence patterns (subject + body-ish fields).
PAY = re.compile(
    r"(cny\s*200|cny200|rmb\s*200|¥\s*200|200\s*(?:元|rmb|cny)"
    r"|payment\s*(?:confirm|receipt|received|complete|success)"
    r"|(?:payment|transfer|remittance)\s+receipt"
    r"|transfer\s*receipt|receipt\s*(?:for\s*)?payment"
    r"|转账凭证|付款凭证|已付款|支付成功|缴款成功|付款确认"
    r"|bank\s*transfer|swift\s*copy|交易回执)", re.I)
# Badge / CIIE context, used to widen the net.
CTX = re.compile(r"(badge|c\s*i\s*i\s*e|进博会|中国国际进口博览会|入场券|参展|visitor\s*pass)", re.I)

# Strong, unambiguous payment tokens are enough on their own.
STRONG = re.compile(r"(payment\s*(?:confirm|receipt|received|complete|success)"
                    r"|transfer\s*receipt|付款凭证|转账凭证|支付成功|已付款"
                    r"|cny\s*200|rmb\s*200|¥\s*200)", re.I)


def matched_tags(blob):
    tags = []
    if re.search(r"cny\s*200", blob, re.I) or re.search(r"¥\s*200", blob):
        tags.append("CNY200")
    if re.search(r"payment\s*(?:confirm|receipt|received|complete|success)", blob, re.I):
        tags.append("PAYMENT")
    if re.search(r"transfer\s*receipt", blob, re.I):
        tags.append("TRANSFER_RECEIPT")
    if re.search(r"(转账凭证|付款凭证|支付成功|已付款|付款确认|缴款成功)", blob):
        tags.append("ZH_PAYMENT")
    if re.search(r"bank\s*transfer|swift\s*copy|交易回执", blob, re.I):
        tags.append("BANK_TRANSFER")
    return sorted(set(tags))


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)[:90]}


# ---- enumerate every inbox any key can see -------------------------------
inbox_key = {}
dead_keys = []
readable = set()
failed_inboxes = []
for k in KEYS:
    code, d = get("https://api.agentmail.to/v0/inboxes", k)
    print(f"[key {k[:12]}…] /v0/inboxes -> {code} count={d.get('count')}")
    if code != 200:
        print("  !! key did not answer 200 - sweep would be a FALSE NEGATIVE")
        dead_keys.append((k[:12] + "…", code))
        continue
    for ib in d.get("inboxes", []):
        iid = ib.get("inbox_id") or ib.get("id")
        if iid and iid not in inbox_key:
            inbox_key[iid] = (ib.get("address") or ib.get("name") or iid, k)

print(f"\nINBOXES VISIBLE ACROSS ALL KEYS: {len(inbox_key)}")
if not inbox_key:
    print("VERDICT: UNKNOWN (no inbox readable - cannot conclude)")
    raise SystemExit(2)

# ---- pull wide ----------------------------------------------------------
hits = []
near = []
total = 0
scanned = 0
for iid, (addr, k) in inbox_key.items():
    code, d = get(f"https://api.agentmail.to/v0/inboxes/{iid}/messages?limit={LIMIT}", k)
    if code != 200:
        print(f"  !! {addr} -> HTTP {code} {d.get('error','')}")
        failed_inboxes.append((addr, code))
        continue
    readable.add(addr)
    msgs = d.get("messages") or d.get("items") or []
    assert_not_truncated(len(msgs), LIMIT)
    total += len(msgs)
    for m in msgs:
        scanned += 1
        subj = m.get("subject") or ""
        frm = m.get("from") or ""
        if isinstance(frm, list):
            frm = " ".join(str(x) for x in frm)
        frm = str(frm)
        blob = " ".join(str(m.get(k2) or "") for k2 in
                        ("subject", "text", "preview", "snippet", "body", "html", "last_reply_at"))
        strong = STRONG.search(blob) or STRONG.search(subj + " " + frm)
        ctx = CTX.search(blob) or CTX.search(subj + " " + frm)
        rec = {
            "inbox": addr,
            "date": (m.get("sent_at") or m.get("created_at") or "")[:19],
            "from": frm[:70],
            "subject": subj[:110],
            "size": m.get("size"),
            "message_id": m.get("message_id") or m.get("id"),
            "matched": matched_tags(blob),
        }
        if strong:
            hits.append(rec)
        elif ctx:
            near.append(rec)

print(f"\nMESSAGES SCANNED: {total}")
print(f"STRONG PAYMENT HITS: {len(hits)}")
print(f"CIEE/BADGE-CONTEXT (no payment token): {len(near)}")

# ---- COVERAGE: what this sweep could NOT read ---------------------------
#
# A verdict that does not state its coverage asserts more than it checked.
# This sweep only enumerates inboxes a key can SEE, so an inbox that 404s
# cannot be enumerated and therefore could not even be reported as missing.
# Comparing what we READ against what we BELIEVE is active is the only way
# that hole becomes visible.
from agentmail_watch import WATCH, coverage_report, verdict_lines  # noqa: E402


_cov_lines, _gap, _missing = coverage_report(WATCH, readable, dead_keys, failed_inboxes)
print("\n=== COVERAGE ===")
print(f"  keys usable: {len(KEYS) - len(dead_keys)}/{len(KEYS)}   "
      f"inboxes read: {len(readable)}   messages scanned: {total}")
if _cov_lines:
    for l in _cov_lines:
        print(l)
    print(f"  ⚠️ COVERAGE GAPS: {_gap} - this sweep's verdict is QUALIFIED.")
else:
    print("  no gaps: every watched address was read and every key answered.")

def show(title, rows, n=40):
    if not rows:
        return
    print(f"\n--- {title} ---")
    rows = sorted(rows, key=lambda r: str(r["date"]), reverse=True)
    for r in rows[:n]:
        print(f"  {r['date']} | {r['size']}B | {r['inbox'][:30]:30} | {r['from'][:40]:40} | {r['subject'][:60]} | {r['matched']}")

show("STRONG PAYMENT CANDIDATES", hits)
show("CIIE/BADGE CONTEXT (near misses)", near)

json.dump({"hits": hits, "near": near, "total": total,
           "scanned_inboxes": len(inbox_key),
           "coverage_gap": _gap,
           "coverage_lines": _cov_lines,
           "missing_watch": _missing},
          open("/tmp/badge_payment_sweep.json", "w"), indent=2)

for _l in verdict_lines(hits, _gap, len(readable), total):
    print(_l)
