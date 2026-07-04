#!/usr/bin/env python3
"""TenacitOS Setup for StudEx Mission Control"""
import os, secrets, shutil, subprocess, time

os.chdir('/root/.openclaw/workspace/mission-control')

# Write .env.local
auth = secrets.token_urlsafe(32)
env_lines = [
    "ADMIN_PASSWORD=StudExMeat2026!",
    "AUTH_SECRET=" + auth,
    "OPENCLAW_DIR=/root/.openclaw",
    "OPENCLAW_WORKSPACE=/root/.openclaw/workspace",
    "NEXT_PUBLIC_AGENT_NAME=StudEx Mission Control",
    "NEXT_PUBLIC_AGENT_EMOJI=",
    "NEXT_PUBLIC_AGENT_DESCRIPTION=AI operating system for Studex Meat",
    "NEXT_PUBLIC_COMPANY_NAME=STUDEX INC",
    "NEXT_PUBLIC_OWNER_USERNAME=TumeloRamaphosa",
    "NEXT_PUBLIC_OWNER_EMAIL=t.ramaphosa@studexwildlife.com",
]
with open('.env.local','w') as f:
    f.write('\n'.join(env_lines) + '\n')
print('ENV OK, AUTH:', auth[:8])

# Copy example data files
for fn in os.listdir('data'):
    if fn.endswith('.example.json'):
        src = os.path.join('data', fn)
        dst = os.path.join('data', fn[:-13] + '.json')
        shutil.copy2(src, dst)
        print('Copied:', dst)
print('DATA FILES OK')

# Build
r = subprocess.run(['npm','run','build'], capture_output=True, text=True,
                   cwd='/root/.openclaw/workspace/mission-control')
print('BUILD OUT:', r.stdout[-300:] if r.stdout else 'none')
print('BUILD ERR:', r.stderr[-300:] if r.stderr else 'none')
print('BUILD RC:', r.returncode)

# Start
subprocess.run(['pm2','stop','tenacitOS'], capture_output=True)
subprocess.run(['pm2','delete','tenacitOS'], capture_output=True)
pid = subprocess.Popen(
    ['sh','-c','cd /root/.openclaw/workspace/mission-control && PORT=3500 nohup npm start > /tmp/tenacitOS.log 2>&1 &'],
    cwd='/root/.openclaw/workspace/mission-control'
).pid
print('Started PID:', pid)
time.sleep(7)
ok = subprocess.run(['curl','-sf','http://localhost:3500']).returncode == 0
print('HEALTH CHECK:', 'LIVE at http://localhost:3500' if ok else 'CHECK LOG')
log = subprocess.run(['cat','/tmp/tenacitOS.log'], capture_output=True, text=True).stdout
print('LOG TAIL:', log[-600:] if log else 'no log')
