#!/bin/bash
# ============================================================
# Charlie Agent — Deployment Script for Orgo VM
# Node.js 20 + Express + SQLite (PostgreSQL-ready)
# Connects to: Orchestrix Matrix + Robusca OpenClaw
# ============================================================

set -e
echo "⚔️  Charlie Agent — Deployment Starting..."
echo "============================================="

# --- 1. System dependencies ---
echo ""
echo "📦 [1/6] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  postgresql-16 postgresql-client-16 \
  redis-server \
  ffmpeg \
  2>&1 | tail -5

# --- 2. Start PostgreSQL ---
echo ""
echo "🗄️  [2/6] Starting PostgreSQL 16..."
sudo pg_ctlcluster 16 main start 2>&1 || \
  sudo service postgresql start 2>&1 || \
  echo "PostgreSQL may need manual config"

sleep 2
pg_isready 2>&1 && echo "✅ PostgreSQL is running" || echo "⚠️  PostgreSQL status unknown"

# --- 3. Create Charlie DB ---
echo ""
echo "🗃️  [3/6] Creating Charlie database..."
sudo -u postgres psql -c "CREATE USER charlie WITH PASSWORD 'charlie_secure_2026';" 2>&1 || echo "User exists"
sudo -u postgres psql -c "CREATE DATABASE charlie_db OWNER charlie;" 2>&1 || echo "DB exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE charlie_db TO charlie;" 2>&1

# --- 4. Create Charlie system user ---
echo ""
echo "👤 [4/6] Setting up charlie user..."
id charlie 2>/dev/null || sudo useradd -m -s /bin/bash charlie
sudo mkdir -p /opt/charlie
sudo chown charlie:charlie /opt/charlie

# --- 5. Install Charlie from repo ---
echo ""
echo "🤖 [5/6] Installing Charlie agent..."
if [ -d /root/nest/studex-agent-os ]; then
  echo "  → Found studex-agent-os in /root/nest"
  sudo cp -r /root/nest/studex-agent-os /opt/charlie/app
elif [ -d /root/robusca/robusca-brain ]; then
  echo "  → Building Charlie from robusca-brain..."
  sudo mkdir -p /opt/charlie/app
fi

cd /opt/charlie/app

# Install Node.js deps
sudo -u charlie npm install 2>&1 | tail -5

# Create .env
cat > /opt/charlie/app/.env << 'EOF'
# Charlie Agent — Environment Configuration
NODE_ENV=production
PORT=3001

# Database
DATABASE_URL=postgresql://charlie:charlie_secure_2026@localhost:5432/charlie_db
DB_TYPE=postgresql

# Robusca / OpenClaw
ROBUSCA_URL=http://localhost:8001
ROBUSCA_API_KEY=charlie_internal_key_2026
ROBUSCA_WS_URL=ws://localhost:8001/ws

# Orchestrix Matrix
MATRIX_HOMESERVER=http://localhost:8008
MATRIX_USER=charlie
MATRIX_PASSWORD=changeme
MATRIX_ROOM=StudexCommandCenter

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/charlie/app.log

# Agents
AGENT_NAME=Charlie
AGENT_ROLE=Orchestrator
AGENT_EMOJI=🎯
PARENT_AGENT=Robusca

# Features
ENABLE_VOICE=false
ENABLE_OBSIDIAN_SYNC=true
ENABLE_DISCORD_BRIDGE=true
ENABLE_MATRIX_BRIDGE=true
EOF

echo "✅ .env configured at /opt/charlie/app/.env"

# --- 6. Start Charlie ---
echo ""
echo "🚀 [6/6] Starting Charlie agent..."
sudo -u charlie mkdir -p /var/log/charlie
sudo -u charlie touch /var/log/charlie/app.log

# Start as background service
cat > /tmp/charlie.service << 'SRV'
[Unit]
Description=Charlie AI Orchestrator
After=network.target postgresql.service

[Service]
Type=simple
User=charlie
WorkingDirectory=/opt/charlie/app
ExecStart=/usr/bin/node app.js
Restart=always
RestartSec=10
StandardOutput=append:/var/log/charlie/app.log
StandardError=append:/var/log/charlie/app.log

[Install]
WantedBy=multi-user.target
SRV

sudo mv /tmp/charlie.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable charlie 2>&1 || echo "systemd not available — using nohup"
sudo systemctl start charlie 2>&1 || {
  echo "⚠️  systemd unavailable — starting with nohup"
  sudo -u charlie nohup node /opt/charlie/app/app.js > /var/log/charlie/app.log 2>&1 &
  echo "Charlie started with PID: $!"
}

sleep 3
curl -s http://localhost:3001/health 2>&1 || echo "Health check — will retry..."
curl -s http://localhost:3001/health 2>&1 && echo "✅ Charlie is LIVE on port 3001" || echo "⚠️  Check logs at /var/log/charlie/app.log"

echo ""
echo "============================================="
echo "  Charlie deployed ✅"
echo "  Health: http://localhost:3001/health"
echo "  API:    http://localhost:3001/api"
echo "============================================="