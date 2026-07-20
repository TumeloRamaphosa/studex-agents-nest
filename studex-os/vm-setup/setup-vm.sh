#!/bin/bash
# ============================================================
# StudEx OS — VM Setup Script
# Run this on the Orgo VM (root access)
# ============================================================
set -e
echo "=== StudEx OS VM Setup ==="

# ---- 1. Update system ----
echo "[1/7] Updating system..."
apt-get update -qq && apt-get upgrade -qq -y

# ---- 2. Install n8n ----
echo "[2/7] Installing n8n..."
npm install -g n8n
echo "n8n installed. Run: n8n start"

# ---- 3. Install Ollama ----
echo "[3/7] Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh
echo "Ollama installed."

# Pull recommended models (background — takes time)
echo "Pulling models in background..."
nohup sh -c '
  ollama pull phi4-mini &
  ollama pull qwen2.5:3b &
  ollama pull nomic-embed-text &
  wait
  echo "All models ready"
' &
echo "Models downloading in background (phi4-mini, qwen2.5:3b, nomic-embed-text)"

# ---- 4. Install DenchClaw ----
echo "[4/7] Installing DenchClaw..."
export DENCHCLAW_DAEMONLESS=1
npx denchclaw@latest bootstrap --skip-daemon-install
# After bootstrap:
# Access at http://localhost:3100
# Use: openclaw --profile dench <command>

# ---- 5. Install OpenWA (Docker) ----
echo "[5/7] Installing OpenWA WhatsApp Gateway..."
cd /root
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
docker compose -f docker-compose.dev.yml up -d
# Dashboard: http://localhost:2785
# API: http://localhost:2785/api

# ---- 6. Install CashClaw ----
echo "[6/7] Installing CashClaw..."
npm install -g cashclaw-agent moltlaunch
# Run: cashclaw
# Access at http://localhost:3777

# ---- 7. Systemd services (if available) ----
echo "[7/7] Setting up PM2 process manager..."
npm install -g pm2
pm2 startup  # Follow output to set up init script

# Save PM2 process list
pm2 save

echo ""
echo "=== Setup Complete ==="
echo ""
echo "SERVICES:"
echo "  n8n           → http://localhost:5678"
echo "  DenchClaw     → http://localhost:3100  (openclaw --profile dench)"
echo "  OpenWA        → http://localhost:2785  (Docker)"
echo "  CashClaw      → http://localhost:3777   (cashclaw)"
echo "  Ollama models → ollama run phi4-mini"
echo ""
echo "NEXT STEPS:"
echo "  1. Get Dench API key from dench.com/api"
echo "  2. Get fresh Meta token from.facebook.com"
echo "  3. Add GoDaddy DNS records (see ../docs/dns-records.md)"
echo "  4. Start n8n: n8n start"
echo "  5. Import n8n workflows from ../n8n-workflows/"
echo ""
