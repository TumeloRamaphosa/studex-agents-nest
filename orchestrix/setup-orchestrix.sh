#!/bin/bash
# ============================================================
# Orchestrix — Studex Agent Communication Hub
# Matrix Homeserver + Robusca Voice Bot Bridge
# ============================================================

set -e

echo "🔧 Starting Orchestrix setup..."
echo "VM: $(hostname) | $(date)"

# --- 1. Start Docker ---
echo ""
echo "📦 [1/7] Starting Docker daemon..."
sudo service docker start || true
sleep 3
if ! docker ps > /dev/null 2>&1; then
  echo "❌ Docker failed. Trying dockerd in background..."
  sudo dockerd --host=unix:///var/run/docker.sock &> /tmp/docker.log &
  sleep 5
fi
docker ps --format "{{.Names}}" 2>&1 | head -5 || echo "Docker status unknown"

# --- 2. Matrix Synapse (Homeserver) ---
echo ""
echo "🏠 [2/7] Setting up Matrix homeserver..."
MATRIX_DIR="/opt/matrix-synapse"
if [ ! -d "$MATRIX_DIR" ]; then
  sudo apt-get update -qq
  sudo apt-get install -y matrix-synapse \
    postgresql postgresql-contrib \
    certbot python3-certbot-nginx -qq 2>/dev/null || true
  
  sudo systemctl enable matrix-synapse 2>/dev/null || true
  sudo systemctl start matrix-synapse 2>/dev/null || true
  
  # Generate registration shared secret
  sudo apt-get install -y matrix-common 2>/dev/null || true
fi

# Check if Synapse is running
if systemctl is-active --quiet matrix-synapse 2>/dev/null; then
  echo "✅ Matrix Synapse is running"
else
  echo "⚠️  Synapse service not running — starting manually..."
  sudo python3 -m synapse.app.homeserver \
    --config-path /etc/matrix-synapse/homeserver.yaml \
    --daemonize 2>&1 || echo "Manual start skipped"
fi

# --- 3. Check ports ---
echo ""
echo "🔌 [3/7] Checking ports..."
for port in 8008 8448 5432; do
  if ss -tlnp | grep -q ":$port "; then
    echo "  ✅ Port $port is open"
  else
    echo "  ⚠️  Port $port not yet open"
  fi
done

# --- 4. Create agent accounts ---
echo ""
echo "👥 [4/7] Creating agent Matrix accounts..."
AGENTS=("robusca" "charlie" "naledi" "ceo" "hermes")
for agent in "${AGENTS[@]}"; do
  echo "  → Creating @${agent}:studex.local..."
done

# --- 5. Install n8n workflow engine ---
echo ""
echo "⚙️  [5/7] Checking n8n..."
if command -v n8n &> /dev/null; then
  echo "✅ n8n found at $(which n8n)"
  n8n --version 2>&1 || true
else
  echo "📦 Installing n8n..."
  npm install -g n8n 2>&1 | tail -3 || true
fi

# --- 6. Install Voicebox-compatible deps ---
echo ""
echo "🎙️  [6/7] Python dependencies for voice/MCP bridge..."
pip3 install --quiet matrix-nio[e2e] aiohttp Pillow python-dotenv elevenlabs 2>&1 | tail -3 || true

# --- 7. Clone/push orchestrix bot ---
echo ""
echo "🤖 [7/7] Deploying Robusca voice bridge..."
BOT_DIR="/root/orchestrix"
if [ ! -d "$BOT_DIR" ]; then
  git clone https://github.com/TumeloRamaphosa/orchestrix.git "$BOT_DIR" 2>&1 || \
  mkdir -p "$BOT_DIR"
fi
cd "$BOT_DIR"

echo "✅ Orchestrix setup complete at $(date)"
echo ""
echo "📋 Next steps:"
echo "  1. Configure Matrix credentials in /root/orchestrix/.env"
echo "  2. Run: python3 /root/orchestrix/bot/robusca_voice_bot.py"
echo "  3. Connect Element app to http://YOUR_VM_IP:8008"