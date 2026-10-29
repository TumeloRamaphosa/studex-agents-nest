#!/usr/bin/env python3
"""CEO Standup probe 2 — AgentMail recency + order hunting, Blotato posts, price ladder."""
import json, urllib.request, urllib.error, subprocess, datetime

env = {}
for line in open('/workspace/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

def get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')[:200]
    except Exception as e:
        return -1, str(e)[:150]

AUTH = {'Authorization': f'Bearer {env.get("AGENTMAIL_MAIN_API_KEY") or env.get("AGENTMAIL_CIIE_KEY") or ""}'}
INBOXES = ['robusca.romanov@studex-group.com', 'naledi-cmo@studex-group.com',
           'project-2571-studex-agent-2077@agentmail.to', 'sales@studex-group.com',
           'meat@studex-group.com', 't.ramaphosa@agentmail.to',
           't-ramaphosa-ceo@studex-group.com', 'support.superagents@studex-group.com',
           'info@studex-group.com', 'cto-darkfactory@studex-group.com',
           'cypher-trace-cto-superagents@studex-group.com', 'studex-2571@agentmail.to']

NOW = datetime.datetime.utcnow()
print("=" * 70)
print("A. AGENTMAIL — messages in last 72h, any inbox, with real timestamps")
print("=" * 70)
schema_shown = False
recent = []
for inbox in INBOXES:
    st, body = get(f'https://api.agentmail.to/v0/inboxes/{inbox}/messages?limit=50', AUTH)
    if st != 200:
        print(f"  {inbox}: HTTP {st}")
        continue
    msgs = json.loads(body).get('messages', [])
    if msgs and not schema_shown:
        schema_shown = True
        print("  schema keys:", sorted(msgs[0].keys()))
    for m in msgs:
        ts = None
        for k in ('sent_at', 'received_at', 'created_at', 'timestamp', 'last_activity_at'):
            if m.get(k):
                ts = m[k]; break
        dt = None
        if ts:
            try:
                dt = datetime.datetime.fromisoformat(str(ts).replace('Z', '+00:00')).replace(tzinfo=None)
            except Exception:
                dt = None
        age_h = (NOW - dt).total_seconds() / 3600 if dt else 999
        if age_h <= 72:
            recent.append((age_h, inbox, m.get('from', ''), m.get('subject', ''), m.get('id', '')))
recent.sort()
print(f"  --- {len(recent)} messages in last 72h across {len(INBOXES)} inboxes ---")
for age, inbox, frm, subj, mid in recent[:45]:
    print(f"  {age:6.1f}h | {inbox[:34]:36s} | {str(frm)[:30]:32s} | {str(subj)[:58]}")
if not recent:
    print("  (none)")

print()
print("  --- ORDER / REVENUE keyword sweep across ALL inbox messages (last 50 each) ---")
KW = ('order', 'invoice', 'payment', 'checkout', 'cart', 'purchase', 'quote', 'rfq',
      'order confirmation', 'thank you for your order', 'booking', 'deposit')
hits = []
for inbox in INBOXES:
    st, body = get(f'https://api.agentmail.to/v0/inboxes/{inbox}/messages?limit=50', AUTH)
    if st != 200:
        continue
    for m in json.loads(body).get('messages', []):
        blob = f"{m.get('subject','')} {m.get('preview','') or ''} {m.get('text','') or ''}".lower()
        if any(k in blob for k in KW):
            ts = m.get('sent_at') or m.get('received_at') or ''
            hits.append((str(ts)[:19], inbox, str(m.get('from', ''))[:30], str(m.get('subject', ''))[:60]))
hits.sort(reverse=True)
print(f"  {len(hits)} keyword hits")
for h in hits[:25]:
    print(f"  {h[0]:20s} | {h[1][:30]:32s} | {h[2][:28]:30s} | {h[3]}")

print()
print("=" * 70)
print("B. BLOTATO — today's posts")
print("=" * 70)
BH = {'blotato-api-key': env.get('BLOTATO_API_KEY', ''), 'Content-Type': 'application/json'}
st, body = get('https://backend.blotato.com/v2/posts?limit=15', BH)
print(f"  /v2/posts HTTP {st}")
if st == 200:
    try:
        d = json.loads(body)
        items = d.get('items') or d.get('posts') or []
        for p in items[:12]:
            print(f"    {str(p.get('createdAt') or p.get('publishedAt'))[:19]} id={p.get('id')} "
                  f"acct={p.get('accountId')} status={p.get('status')} provider={p.get('provider')} "
                  f"text={str(p.get('text') or p.get('caption') or '')[:48]}")
    except Exception as e:
        print("   parse err", e, body[:200])
else:
    print("  ", body[:200])

print()
print("=" * 70)
print("C. PRICE LADDER — registry intent vs LIVE storefront")
print("=" * 70)
for f in ('/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md',
          '/workspace/studex-meat-deploy/PRICE-SOURCE-REGISTRY.md'):
    try:
        txt = open(f).read()
        print(f"  found {f} ({len(txt)} chars)")
        for line in txt.splitlines():
            low = line.lower()
            if ('450' in line or '650' in line or '1450' in line or '1250' in line
                    or '12500' in line or '8400' in line or '325' in line) and ('R' in line or 'r' in line):
                print("   ", line.strip()[:150])
        break
    except FileNotFoundError:
        continue
else:
    print("  registry not found at those paths")
    r = subprocess.run(['find', '/workspace', '-name', 'PRICE-SOURCE-REGISTRY.md',
                        '-not', '-path', '*/node_modules/*'], capture_output=True, text=True, timeout=30)
    print("  find:", r.stdout.strip()[:400])

st, body = get('https://studexmeat.myshopify.com/products.json?limit=250')
if st == 200:
    ps = json.loads(body).get('products', [])
    print(f"\n  LIVE storefront: {len(ps)} products")
    for p in ps:
        if 'biltong' in p['title'].lower():
            for v in p.get('variants', []):
                print(f"    {p['title'][:44]:46s} {v.get('title','')[:20]:22s} R{v['price']} avail={v.get('available')}")

print()
print("=" * 70)
print("D0. BLOTATO ANALYTICS — does accountId change the response?")
print("=" * 70)
import hashlib
for acct in ('38744', '26628', '76978', '7701', '99999'):
    st, body = get(f'https://backend.blotato.com/v2/analytics?accountId={acct}&days=7', BH)
    if st == 200:
        try:
            items = sorted(json.loads(body).get('items', []), key=lambda i: i.get('createdAt', ''), reverse=True)
            ids = [str(i.get('id')) for i in items[:6]]
            h = hashlib.sha1(json.dumps(items, sort_keys=True).encode()).hexdigest()[:12]
            print(f"  accountId={acct:6s} HTTP {st} items={len(items):3d} ids={ids} bodyhash={h}")
        except Exception as e:
            print(f"  accountId={acct}: parse err {e}")
    else:
        print(f"  accountId={acct}: HTTP {st}")

print()
print("=" * 70)
print("C2. REGISTRY ladder-lock intent")
print("=" * 70)
try:
    rl = open('/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md').read().splitlines()
    for i, l in enumerate(rl):
        low = l.lower()
        if any(k in low for k in ('ladder', 'r325', 'r8400', 'r1250', 'inverted', 'per-kg', 'per kg', '12500')):
            print(f"  {i}: {l.strip()[:165]}")
except Exception as e:
    print("  registry err", e)

print()
print("=" * 70)
print("E. CLICKUP (both tokens) + ORDER LEDGER SOURCES")
print("=" * 70)
for label, t in (('CLICKUP_API_TOKEN', env.get('CLICKUP_API_TOKEN', '')),
                 ('CLICKUP_API_TOKEN_OLD', env.get('CLICKUP_API_TOKEN_OLD', ''))):
    st, body = get('https://api.clickup.com/api/v2/team', {'Authorization': t})
    print(f"  {label}: HTTP {st} {body[:150]}")

import glob, os
print("\n  -- order/delivery ledger files --")
seen = set()
for pat in ('delivery-state.json', 'orders.json', '*order*.csv', 'orders*.json'):
    r = subprocess.run(['find', '/workspace', '-maxdepth', '7', '-name', pat,
                        '-not', '-path', '*/node_modules/*', '-not', '-path', '*/.git/*'],
                       capture_output=True, text=True, timeout=60)
    for f in r.stdout.split():
        if f in seen:
            continue
        seen.add(f)
        try:
            sz = os.path.getsize(f)
            head = open(f, errors='replace').read(300).replace('\n', ' ')
            print(f"    {f} ({sz}b) :: {head[:200]}")
        except Exception as e:
            print(f"    {f} ERR {e}")

print()
print("=" * 70)
print("F. EXPOSED / LEGACY PUBLIC DEPLOYS — live check")
print("=" * 70)
for u in ('ess0ocgcd9f0', 'nudsduvyrc12', 'bkqn328wj5a6', 'awyjxfplygag', 't56b7vkncytt',
          'oi28dhtke3yk'):
    st, body = get(f'https://{u}.space.mcode.io')
    print(f"    {u}.space.mcode.io  HTTP {st}")

print()
print("=" * 70)
print("G. BLOTATO PUBLISH HEALTH — can we still post to each platform?")
print("=" * 70)
for f in ('/workspace/studex-content-automation/scripts/check-tokens.js',):
    if os.path.exists(f):
        r = subprocess.run(['node', f], capture_output=True, text=True, timeout=60,
                           cwd='/workspace/studex-content-automation')
        print((r.stdout + r.stderr)[:900])

print()
print("=" * 70)
print("D. OPS CHECKERS (read-only) — price-on-feed, staged-publish")
print("=" * 70)
for cmd in (['python3', '/workspace/ops/check-price-on-feed.py'],
            ['python3', '/workspace/ops/check-staged-publish.py']):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, cwd='/workspace')
        out = (r.stdout + r.stderr).strip()
        print(f"  $ {' '.join(cmd[1].split('/')[-1])} rc={r.returncode}")
        for l in out.splitlines()[:14]:
            print("     ", l[:150])
    except Exception as e:
        print("  err", cmd[-1], e)
