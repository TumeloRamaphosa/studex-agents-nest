#!/usr/bin/env python3
"""One-shot: last 5 Blotato posts per StudEx account with metric freshness (read-only)."""
import json, urllib.request

env = {}
for line in open('/workspace/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

H = {'blotato-api-key': env.get('BLOTATO_API_KEY', ''), 'Content-Type': 'application/json'}

for acct, name in (('76978', 'instagram'), ('7701', 'threads')):
    req = urllib.request.Request(f'https://backend.blotato.com/v2/analytics?accountId={acct}&days=7', headers=H)
    d = json.load(urllib.request.urlopen(req, timeout=25))
    items = sorted(d.get('items', []), key=lambda i: i.get('createdAt', ''), reverse=True)[:5]
    print(f'== {name} ({acct})')
    for it in items:
        lm = it.get('latestMetrics') or {}
        m = lm.get('metrics', {})
        keep = {k: v for k, v in m.items() if k in ('reachCount', 'interactionsSum', 'likesCount', 'viewsCount', 'commentsCount', 'savesCount', 'sharesCount')}
        print(f"   {it.get('createdAt','')[:19]} {it['id']:9s} fetched={str(lm.get('fetchedAt'))[:19]} {json.dumps(keep)}")
