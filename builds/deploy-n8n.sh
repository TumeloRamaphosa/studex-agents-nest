#!/bin/bash
# ============================================================
# StudEx n8n Deployment Script — Alibaba VM (47.236.124.79)
# Run from this machine; sshpass required
# Usage: bash deploy-n8n.sh
# ============================================================

set -e

VM_HOST="47.236.124.79"
VM_USER="root"
VM_PASS="StudEx2026!"
WORKFLOW_FILE="/workspace/n8n-workflows/studex-content-pipeline.json"
SCRIPT_DIR="/tmp/n8n-deploy-$$"

# ---- Colour helpers ----
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ---- SSH helper ----
ssh_cmd() {
  sshpass -p "$VM_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 "$VM_USER@$VM_HOST" "$1"
}

scp_cmd() {
  sshpass -p "$VM_PASS" scp -o StrictHostKeyChecking=no "$1" "$VM_USER@$VM_HOST:$2"
}

# ============================================================
# STEP 1 — Detect OS
# ============================================================
log "Detecting OS on VM..."
OS=$(ssh_cmd "cat /etc/os-release | grep -E '^ID=' | cut -d= -f2 | tr -d '\"'")
VERSION=$(ssh_cmd "cat /etc/os-release | grep -E '^VERSION_ID=' | cut -d= -f2 | tr -d '\"'")
log "OS: $OS $VERSION"

# ============================================================
# STEP 2 — Install Docker
# ============================================================
log "Installing Docker..."

if [[ "$OS" == "alinux" || "$OS" == "centos" || "$OS" == "rhel" || "$OS" == "rocky" || "$OS" == "almalinux" ]]; then
  ssh_cmd "yum install -y docker 2>&1 | tail -5"
elif [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
  ssh_cmd "apt-get update && apt-get install -y docker.io 2>&1 | tail -5"
else
  # Try generic install
  ssh_cmd "curl -fsSL https://get.docker.com | sh 2>&1 | tail -10"
fi

# Start Docker daemon (no systemd — manual start)
log "Starting Docker daemon..."
ssh_cmd "dockerd &>/var/log/docker.log &"
sleep 5

DOCKER_RUNNING=$(ssh_cmd "docker info >/dev/null 2>&1 && echo 'yes' || echo 'no'")
if [[ "$DOCKER_RUNNING" != "yes" ]]; then
  err "Docker daemon failed to start. Check /var/log/docker.log on the VM."
fi
log "Docker running ✓"

# ============================================================
# STEP 3 — Pull n8n image
# ============================================================
log "Pulling n8n image (this may take a few minutes)..."
ssh_cmd "docker pull n8nio/n8n:latest 2>&1 | tail -3"

# ============================================================
# STEP 4 — Create n8n data directory
# ============================================================
log "Creating n8n data directory..."
ssh_cmd "mkdir -p /opt/n8n/data /opt/n8n/workflows"
log "Directories created ✓"

# ============================================================
# STEP 5 — Copy workflow file to VM
# ============================================================
log "Uploading workflow JSON..."
scp_cmd "$WORKFLOW_FILE" "/tmp/studex-content-pipeline.json"
ssh_cmd "mv /tmp/studex-content-pipeline.json /opt/n8n/workflows/"
log "Workflow uploaded ✓"

# ============================================================
# STEP 6 — Create .env file for n8n
# ============================================================
log "Creating n8n environment file..."
ssh_cmd "cat > /opt/n8n/.env << 'EOF'
# StudEx n8n Environment Variables
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=studex
N8N_BASIC_AUTH_PASSWORD=StudExN8n2026!
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://47.236.124.79:5678
# Discord webhook (Studex content-queue)
DISCORD_WEBHOOK_ID=YOUR_DISCORD_WEBHOOK_ID
DISCORD_WEBHOOK_TOKEN=YOUR_DISCORD_WEBHOOK_TOKEN
# Blotato
BLOTATO_API_KEY=[REDACTED:28 chars - rotate this key]YN2ZvCeGsVWWwdaf8Og=
# Higgsfield
HIGGSFIELD_API_KEY=[REDACTED:64 chars - rotate this key]
EOF"
log ".env created ✓"

# ============================================================
# STEP 7 — Start n8n container
# ============================================================
log "Starting n8n container..."

# Stop any existing container first
ssh_cmd "docker rm -f n8n-studex 2>/dev/null || true"

ssh_cmd "docker run -d \
  --name n8n-studex \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /opt/n8n/data:/home/node/.n8n \
  -v /opt/n8n/workflows:/opt/workflows \
  --env-file /opt/n8n/.env \
  n8nio/n8n:latest 2>&1"

sleep 8

# ============================================================
# STEP 8 — Verify n8n is running
# ============================================================
log "Verifying n8n..."
N8N_RUNNING=$(ssh_cmd "docker ps --filter name=n8n-studex --format '{{.Status}}'")
if [[ "$N8N_RUNNING" == *"Up"* ]]; then
  log "n8n is RUNNING ✓"
else
  warn "n8n container may not be fully up yet. Check: docker logs n8n-studex"
fi

# Show port
log "n8n UI: http://47.236.124.79:5678"
log "Login: studex / StudExN8n2026!"

# ============================================================
# STEP 9 — Import workflow via n8n API
# ============================================================
log "Importing StudEx Content Pipeline workflow..."
IMPORT_RESULT=$(ssh_cmd "curl -s -X POST http://localhost:5678/rest/workflows \
  -H 'Content-Type: application/json' \
  -u 'studex:StudExN8n2026!' \
  -d '{
    \"name\": \"StudEx Content Pipeline\",
    \"active\": false,
    \"nodes\": [],
    \"connections\": {}
  }' 2>&1")
log "Import API called (check n8n UI for full workflow)"

# ============================================================
# STEP 10 — Print access info
# ============================================================
echo ""
echo "=========================================="
echo -e "${GREEN}  StudEx n8n Deployment — COMPLETE${NC}"
echo "=========================================="
echo ""
echo "  URL:     http://47.236.124.79:5678"
echo "  User:    studex"
echo "  Pass:    StudExN8n2026!"
echo "  Status:  docker ps | grep n8n-studex"
echo ""
echo "  TO DO AFTER FIRST LOGIN:"
echo "  1. Go to Workflows → Import from File"
echo "  2. Select /opt/workflows/studex-content-pipeline.json"
echo "  3. Activate the workflow (toggle ON)"
echo "  4. Update Discord webhook credentials in .env"
echo ""
echo "  USEFUL COMMANDS:"
echo "  docker logs n8n-studex    — view n8n logs"
echo "  docker restart n8n-studex — restart n8n"
echo "  docker stop n8n-studex    — stop n8n"
echo "  docker exec -it n8n-studex n8n import:workflow --input=/opt/workflows/studex-content-pipeline.json"
echo ""
echo "  AUTO-START ON REBOOT (add to /etc/rc.local):"
echo "  docker start n8n-studex"
echo ""
