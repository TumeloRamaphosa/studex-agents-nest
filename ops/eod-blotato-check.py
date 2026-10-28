#!/usr/bin/env python3
"""EOD Blotato check — accounts + today's published posts. Reads .env in-process."""
import json, urllib.request

env = {}
for line in open('/workspace/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

key = env.get('BLOTATO_API_KEY')
print('key present:', bool(key))
if not key:
    raise SystemExit(1)
H = {'Authorization': key, 'Content-Type': 'application/json'}


def get(path):
    req = urllib.request.Request('https://backend.blotato.com/v2' + path, headers=H)
    try:
        with urllib.request.urlopen(req, timeout=25) as f:
            return f.status, f.read().decode()
    except Exception as e:
        return getattr(e, 'code', 0) or str(e), ''


st, body = get('/users/me/accounts')
print('accounts:', st)
try:
    accs = json.loads(body)
    if isinstance(accs, dict):
        accs = accs.get('accounts', accs.get('data', []))
    for a in accs:
        print('  ', a.get('id'), a.get('name'), a.get('provider'), '| subaccounts:', a.get('subaccounts'))
except Exception as e:
    print('  parse fail', e, body[:200])

for path in ['/posts?limit=20', '/posts?limit=50&order_by=-createdAt']:
    st, body = get(path)
    print(path, '->', st)
    if st != 200:
        continue
    try:
        posts = json.loads(body)
        if isinstance(posts, dict):
            posts = posts.get('posts', posts.get('data', []))
    except Exception:
        print(body[:300])
        continue
    print('  posts returned:', len(posts))
    for p in posts[:12]:
        print('   ', str(p.get('createdAt'))[:19], p.get('id'), p.get('provider'), str(p.get('text'))[:60].replace('\n', ' '))
    break
