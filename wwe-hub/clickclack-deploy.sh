#!/bin/bash
# =============================================================================
# WWE Hub — ClickClack Deployment Script
# =============================================================================
# Run on a fresh VPS (Ubuntu 22.04+) as root
# Usage: curl -fsSL https://your-server/setup.sh | bash
# =============================================================================

set -e

echo "========================================="
echo "WWE Hub — ClickClack Setup"
echo "========================================="

# Variables — edit these
CLICKCLACK_DOMAIN="hub.studexmeat.com"  # Your domain for the hub
CLICKCLACK_VERSION="latest"              # Or pin to v0.1.0
ADMIN_EMAIL="tumelo@studexmeat.com"

# -------------------------------------------------------------------
# 1. System prep
# -------------------------------------------------------------------
echo "[1/8] Updating system..."
apt update && apt upgrade -y

echo "[2/8] Installing prerequisites..."
apt install -y curl wget git ufw fail2ban

# -------------------------------------------------------------------
# 2. Docker
# -------------------------------------------------------------------
echo "[3/8] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
fi
echo "Docker version: $(docker --version)"

# -------------------------------------------------------------------
# 3. ClickClack binary
# -------------------------------------------------------------------
echo "[4/8] Fetching ClickClack..."
mkdir -p /opt/clickclack
cd /opt/clickclack

# Download latest release (v0.1.0 as of Jul 2026)
# Check https://github.com/openclaw/clickclack/releases for latest
wget -q https://github.com/openclaw/clickclack/releases/download/v0.1.0/clickclack-linux-amd64.tar.gz \
    -O clickclack.tar.gz || \
wget -q https://github.com/openclaw/clickclack/releases/latest/download/clickclack-linux-amd64.tar.gz \
    -O clickclack.tar.gz

tar -xzf clickclack.tar.gz
chmod +x clickclack
rm clickclack.tar.gz
echo "ClickClack installed: $(./clickclack --version 2>&1 || echo 'binary ready')"

# -------------------------------------------------------------------
# 4. Directory & data
# -------------------------------------------------------------------
echo "[5/8] Creating data directory..."
mkdir -p /data/clickclack
cd /data/clickclack

# -------------------------------------------------------------------
# 5. Environment config
# -------------------------------------------------------------------
echo "[6/8] Writing config..."
cat > /data/clickclack/.env << EOF
# ClickClack — WWE Hub Production Config
CLICKCLACK_PUBLIC_URL=https://${CLICKCLACK_DOMAIN}
CLICKCLACK_PORT=8080

# Auth — enable magic link + GitHub OAuth
CLICKCLACK_DEV_BOOTSTRAP=false

# GitHub OAuth (optional — set from environment)
# CLICKCLACK_GITHUB_CLIENT_ID=your_github_oauth_app_id
# CLICKCLACK_GITHUB_CLIENT_SECRET=your_github_oauth_secret
# CLICKCLACK_GITHUB_ALLOWED_ORG=your_org  # restrict to GitHub org members

# Admin email for magic links
ADMIN_EMAIL=${ADMIN_EMAIL}

# Optional: Caddy reverse proxy HTTPS (auto-managed)
ENABLE_CADDY=true
CADDY_DOMAIN=${CLICKCLACK_DOMAIN}
CADDY_EMAIL=letsencrypt@studexmeat.com
EOF

# -------------------------------------------------------------------
# 6. Systemd service
# -------------------------------------------------------------------
echo "[7/8] Creating systemd service..."
cat > /etc/systemd/system/clickclack.service << EOF
[Unit]
Description=ClickClack — WWE Hub Chat
After=network.target

[Service]
Type=simple
WorkingDirectory=/data/clickclack
ExecStart=/opt/clickclack/clickclack serve
Restart=always
RestartSec=5
EnvironmentFile=/data/clickclack/.env
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable clickclack
systemctl start clickclack
echo "ClickClack started: $(systemctl is-active clickclack)"

# -------------------------------------------------------------------
# 7. Firewall
# -------------------------------------------------------------------
echo "[8/8] Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

echo ""
echo "========================================="
echo "✅ ClickClack is installed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Visit: https://${CLICKCLACK_DOMAIN}"
echo "  2. Create your admin account"
echo "  3. Create a workspace: WWE Hub"
echo "  4. Set up channels (see CHANNELS.md)"
echo "  5. Generate bot tokens for each agent"
echo ""
echo "Service commands:"
echo "  systemctl status clickclack"
echo "  systemctl restart clickclack"
echo "  journalctl -u clickclack -f"
echo ""
echo "Config file: /data/clickclack/.env"
echo "Data dir:    /data/clickclack"
echo "Binary:      /opt/clickclack/clickclack"
echo "========================================="
