#!/bin/bash
# TenacitOS Setup for StudEx Mission Control
# Run: bash /tmp/setup-tenacitOS.sh

set -e
cd /root/.openclaw/workspace/mission-control

# Write .env.local with StudEx branding
python3 << 'PYEOF'
import secrets, os
auth = secrets.token_urlsafe(32)
env = f"""ADMIN_PASSWORD=StudExMeat2026!
AUTH_SECRET={auth}
OPENCLAW_DIR=/root/.openclaw
OPENCLAW_WORKSPACE=/root/.openclaw/workspace
NEXT_PUBLIC_AGENT_NAME=StudEx Mission Control
NEXT_PUBLIC_AGENT_EMOJI=🐾
NEXT_PUBLIC_AGENT_DESCRIPTION=AI-powered operating system for Studex Meat and Wildlife Coffee
NEXT_PUBLIC_COMPANY_NAME=STUDEX INC
NEXT_PUBLIC_OWNER_USERNAME=TumeloRamaphosa
NEXT_PUBLIC_OWNER_EMAIL=t.ramaphosa@studexwildlife.com
"""
with open(".env.local","w") as f: f.write(env)
print("ENV written, AUTH:", auth[:8])
PYEOF

# Copy example data files
for f in data/*.example.json; do
    target="${f%.example.json}"
    cp "$f" "$target" 2>/dev/null && echo "Copied: $target"
done

echo "=== Files ready ==="
ls data/

# Build
echo "=== Building ==="
npm run build 2>&1 | tail -4

# Start on port 3500
echo "=== Starting on port 3500 ==="
pm2 stop tenacitOS 2>/dev/null || true
pm2 delete tenacitOS 2>/dev/null || true
PORT=3500 nohup npm start > /tmp/tenacitOS.log 2>&1 &
echo "PID: $!"
sleep 6
curl -sf http://localhost:3500 > /dev/null && echo "✅ LIVE at http://localhost:3500" || (echo "Log:" && tail -15 /tmp/tenacitOS.log)
