#!/usr/bin/env python3
"""CEO Standup live probe — read-only. Shopify / AgentMail / Blotato / cron / git."""
import json, os, urllib.request, urllib.error, subprocess, datetime, re

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
        return e.code, e.read().decode('utf-8', 'replace')[:300]
    except Exception as e:
        return -1, str(e)[:200]

print("=" * 70)
print("1. SHOPIFY")
print("=" * 70)
shop = env.get('SHOPIFY_API_TOKEN', '')
store = 'studexmeat'
for label, path in (
    ("orders", f"/admin/api/2024-10/orders.json?status=any&limit=10"),
    ("shop_info", "/admin/api/2024-10/shop.json"),
    ("products_admin", "/admin/api/2024-10/products.json?limit=1"),
):
    st, body = get(f"https://{store}.myshopify.com{path}",
                   {'X-Shopify-Access-Token': shop, 'Content-Type': 'application/json'})
    print(f"  admin {label}: HTTP {st}")
    if st == 200:
        try:
            d = json.loads(body)
            if label == 'orders':
                orders = d.get('orders', [])
                print(f"     -> {len(orders)} orders")
                for o in orders[:6]:
                    print(f"        {o.get('created_at')} {o.get('name')} total={o.get('total_price')} "
                          f"{o.get('currency')} fin={o.get('financial_status')} email={(o.get('email') or '')[:28]}")
            elif label == 'shop_info':
                s = d.get('shop', {})
                print(f"     -> {s.get('name')} currency={s.get('currency')}")
        except Exception as e:
            print(f"     parse err {e}")
    else:
        print(f"     {body[:160]}")

for label, path in (("products.json", "/products.json?limit=250"),
                    ("cart_create", "/cart.js")):
    st, body = get(f"https://{store}.myshopify.com{path}")
    print(f"  storefront {label}: HTTP {st}")
    if label == "products.json" and st == 200:
        try:
            ps = json.loads(body).get('products', [])
            print(f"     -> {len(ps)} products")
            cav = [p['title'] for p in ps if 'caviar' in p['title'].lower()]
            print(f"     -> caviar in catalogue: {len(cav)} {cav[:4]}")
            bilt = [(p['title'], v['price'], v.get('title')) for p in ps
                    for v in p.get('variants', []) if 'biltong' in p['title'].lower()]
            for t, pr, vt in bilt[:14]:
                print(f"        {t[:42]:44s} {vt[:22]:24s} R{pr}")
        except Exception as e:
            print(f"     parse err {e}")

print()
print("=" * 70)
print("2. AGENTMAIL")
print("=" * 70)
INBOXES = [
    'robusca.romanov@studex-group.com', 'naledi-cmo@studex-group.com',
    'project-2571-studex-agent-2077@agentmail.to', 'sales@studex-group.com',
    'meat@studex-group.com', 't.ramaphosa@agentmail.to',
    't-ramaphosa-ceo@studex-group.com', 'support.superagents@studex-group.com',
    'info@studex-group.com', 'cto-darkfactory@studex-group.com',
    'cypher-trace-cto-superagents@studex-group.com', 'studex-2571@agentmail.to',
    'healthyprocess394@agentmail.to',
]
KEYS = [('main', env.get('AGENTMAIL_MAIN_API_KEY', '')),
        ('ciie', env.get('AGENTMAIL_CIIE_KEY', '')),
        ('gen', env.get('AGENTMAIL_API_KEY', ''))]

def probe_keys():
    out = []
    for name, k in KEYS:
        if not k:
            continue
        st, body = get('https://api.agentmail.to/v0/inboxes', {'Authorization': f'Bearer {k}'})
        if st == 200:
            try:
                ids = {i.get('inbox_id') or i.get('id') for i in json.loads(body).get('inboxes', [])}
                out.append((name, ids))
            except Exception:
                pass
    return out

live = probe_keys()
print(f"  live keys: {[n for n, _ in live]}")
known_ids = set().union(*[i for _, i in live]) if live else set()

total_msgs = 0
for inbox in INBOXES:
    for name, ids in live:
        if inbox in ids or inbox.split('@')[0] in {i.split('@')[0] for i in ids}:
            st, body = get(f'https://api.agentmail.to/v0/inboxes/{inbox}/messages?limit=25',
                           {'Authorization': f'Bearer {env.get("AGENTMAIL_MAIN_API_KEY") or ""}'})
            if st != 200:
                st, body = get(f'https://api.agentmail.to/v0/inboxes/{inbox}/messages?limit=25',
                               {'Authorization': f'Bearer {env.get("AGENTMAIL_CIIE_KEY") or ""}'})
            if st == 200:
                try:
                    msgs = json.loads(body).get('messages', [])
                    total_msgs += len(msgs)
                    newest = msgs[0] if msgs else {}
                    print(f"  {inbox:48s} [{name}] {len(msgs):3d} msgs | newest={str(newest.get('sent_at') or newest.get('received_at'))[:19]} "
                          f"from={str(newest.get('from'))[:34]} subj={str(newest.get('subject'))[:44]}")
                except Exception as e:
                    print(f"  {inbox}: parse err {e}")
            else:
                print(f"  {inbox:48s} [{name}] HTTP {st}")
            break
    else:
        print(f"  {inbox:48s} NOT on any live key")

print()
print("=" * 70)
print("3. BLOTATO")
print("=" * 70)
BH = {'blotato-api-key': env.get('BLOTATO_API_KEY', ''), 'Content-Type': 'application/json'}
st, body = get('https://backend.blotato.com/v2/accounts', BH)
print(f"  accounts: HTTP {st}")
if st == 200:
    try:
        for a in json.loads(body).get('items', []):
            print(f"    {a.get('id'):>7} {a.get('name','')[:26]:28s} provider={a.get('provider')} status={a.get('status')} "
                  f"posts={a.get('postCount')} connected={a.get('connected')}")
    except Exception as e:
        print("   parse err", e)

for acct, nm in (('38744', 'facebook'), ('26628', 'linkedin'), ('76978', 'instagram'), ('7701', 'threads')):
    st, body = get(f'https://backend.blotato.com/v2/analytics?accountId={acct}&days=7', BH)
    if st == 200:
        try:
            items = sorted(json.loads(body).get('items', []), key=lambda i: i.get('createdAt', ''), reverse=True)[:3]
            for it in items:
                lm = it.get('latestMetrics') or {}
                m = lm.get('metrics', {})
                keep = {k: v for k, v in m.items() if k in ('reachCount', 'interactionsSum', 'likesCount', 'viewsCount', 'commentsCount')}
                print(f"    {nm:10s} {it.get('createdAt','')[:10]} id={it.get('id')} fetched={str(lm.get('fetchedAt'))[:19]} {json.dumps(keep)}")
        except Exception as e:
            print(f"    {nm} parse err {e}")
    else:
        print(f"    {nm}: HTTP {st}")

print()
print("=" * 70)
print("4. CRON FLEET")
print("=" * 70)
try:
    out = subprocess.run(['openclaw', 'cron', 'list'], capture_output=True, text=True, timeout=60).stdout
    for line in out.splitlines():
        if any(k in line.lower() for k in ('ceo-standup', 'content-agent', 'daily-post', 'warmup', 'research', 'nudge',
                                           'vault', 'build', 'error', '✓', '✗')):
            print("   ", line[:160])
except Exception as e:
    print("  cli err", e)

print()
print("=" * 70)
print("5. GIT")
print("=" * 70)
for cmd in (['git', '-C', '/workspace', 'status', '--porcelain'],
            ['git', '-C', '/workspace', 'log', '--oneline', '-3'],
            ['git', '-C', '/workspace', 'rev-list', '--count', 'HEAD'],
            ['git', '-C', '/workspace', 'ls-remote', '--heads', 'origin']):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        o = (r.stdout or r.stderr).strip()
        lines = o.splitlines()
        print(f"  $ {' '.join(cmd[-2:])}: rc={r.returncode} lines={len(lines)}")
        for l in lines[:8]:
            print("     ", l[:140])
    except Exception as e:
        print("  err", cmd[-1], e)

print()
print("NOW:", datetime.datetime.utcnow().isoformat(), "UTC")
