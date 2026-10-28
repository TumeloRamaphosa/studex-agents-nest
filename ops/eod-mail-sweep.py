#!/usr/bin/env python3
"""EOD AgentMail sweep — external inbound only. Reads .env in-process (never argv)."""
import json, urllib.request, datetime

env = {}
for line in open('/workspace/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

KEYS = ['AGENTMAIL_CIIE_KEY', 'AGENTMAIL_API_KEY_GENERAL',
        'AGENTMAIL_WARMUP_API_KEY', 'AGENTMAIL_API_KEY']
BASE = 'https://api.agentmail.to/v0'


def get(path, key):
    req = urllib.request.Request(BASE + path, headers={'Authorization': 'Bearer ' + key})
    try:
        with urllib.request.urlopen(req, timeout=25) as f:
            return f.status, f.read().decode()
    except Exception as e:
        return getattr(e, 'code', 0) or str(e), ''


inboxes = {}
for name in KEYS:
    k = env.get(name)
    if not k:
        print(name, 'NOT-IN-ENV')
        continue
    st, body = get('/inboxes', k)
    print(name, '->', st)
    if st != 200:
        continue
    for ib in json.loads(body).get('inboxes', []):
        inboxes[ib.get('inbox_id') or ib.get('address')] = k

print('inboxes reachable:', len(inboxes))
internal = ('studex-group.com', 'agentmail.to', 'warmup')
external = []
for aid, k in inboxes.items():
    st, body = get('/inboxes/%s/messages?limit=20' % aid, k)
    if st != 200:
        continue
    try:
        msgs = json.loads(body).get('messages', [])
    except Exception:
        continue
    for m in msgs:
        ts = m.get('timestamp') or m.get('created_at') or ''
        frm = m.get('from')
        if isinstance(frm, list):
            frm = frm[0] if frm else ''
        frm = frm or ''
        if any(t in str(frm) for t in internal):
            continue
        external.append((ts, aid, frm, m.get('subject', '')))
external.sort(reverse=True)
print('--- external messages found:', len(external))
for e in external[:25]:
    print(str(e[0])[:19], '|', e[1], '|', str(e[2])[:40], '|', str(e[3])[:70])
