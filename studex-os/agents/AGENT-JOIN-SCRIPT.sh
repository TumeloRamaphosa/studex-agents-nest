#!/usr/bin/env bash
# ============================================================
# Studex OS — Agent Join Script
# Usage: ./join.sh <agent-id> <role>
# Example: ./join.sh delivery-agent "Delivery Operations"
# ============================================================

set -e

AGENT_ID="${1:-}"
ROLE="${2:-}"
REGISTRY_FILE="/root/studex-os/agents/AGENT-REGISTRY.md"
GIT_DIR="/root/studex-os"
BASHRC="/root/.bashrc"

# ── Colours ────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Colour

log()  { echo -e "${GREEN}[ROBUSCA]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; }

# ── Checks ────────────────────────────────────────────────
if [[ -z "$AGENT_ID" ]]; then
  echo -e "${BOLD}Studex OS — Agent Registration${NC}"
  echo "Usage: ./join.sh <agent-id> <role>"
  echo "Example: ./join.sh delivery-agent 'Delivery Operations'"
  exit 1
fi

# ── Welcome Banner ────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     🐄 STUDEX OS — AGENT REGISTRATION     ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Verify environment ───────────────────────────
log "Verifying environment..."
if [[ ! -d "$GIT_DIR" ]]; then
  warn "Studex OS not found at $GIT_DIR"
  warn "Cloning from GitHub..."
  git clone https://github.com/TumeloRamaphosa/studex-os.git "$GIT_DIR"
else
  log "✓ Studex OS repo found at $GIT_DIR"
fi

cd "$GIT_DIR"

# ── Step 2: Verify env vars ──────────────────────────────
log "Checking required env vars..."
MISSING=()
for var in SHOPIFY_STORE ELEVENLABS_API_KEY; do
  if [[ -z "${!var}" ]]; then
    MISSING+=("$var")
  else
    log "✓ $var is set"
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  warn "Missing env vars: ${MISSING[*]}"
  warn "Set them in /root/.bashrc before joining:"
  for v in "${MISSING[@]}"; do
    echo "  export $v=<your-value-here>"
  done
fi

# ── Step 3: Verify store connection ─────────────────────
log "Testing Shopify connection..."
SHOPIFY_RESPONSE=$(curl -s \
  -H "X-Shopify-Access-Token: $SHOPIFY_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ shop { name } }"}' \
  "https://$SHOPIFY_STORE/admin/api/2025-01/graphql.json" 2>&1)

if echo "$SHOPIFY_RESPONSE" | grep -q "shop"; then
  SHOP_NAME=$(echo "$SHOPIFY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['shop']['name'])")
  log "✓ Connected to Shopify: $SHOP_NAME"
else
  warn "⚠ Shopify not connected yet — get token from Shopify Admin"
  warn "  Shopify Admin → Settings → Apps → Create app → Admin API"
fi

# ── Step 4: Register agent ──────────────────────────────
log "Registering agent: $AGENT_ID ($ROLE)..."

TIMESTAMP=$(date +%Y-%m-%d\ %H:%M\ SAST)

REGISTRY_ENTRY="
## $AGENT_ID — Added $TIMESTAMP
- **Role:** $ROLE
- **Status:** Active
- **Joined:** $TIMESTAMP
- **Last seen:** $TIMESTAMP
- **Shopify:** $([[ -n "$SHOP_NAME" ]] && echo "✓ Connected to $SHOP_NAME" || echo "⚠ Not connected")
- **ElevenLabs:** $(command -v elevenlabs &>/dev/null && echo "✓ Available" || echo "⚠ Not configured")
- **Rocket.Chat:** $(curl -s http://67.213.119.157:3000/api/info 2>/dev/null | grep -q "version" && echo "✓ Available at http://67.213.119.157:3000" || echo "⚠ Not running")
"

echo "$REGISTRY_ENTRY" >> "$REGISTRY_FILE"
log "✓ Agent registered in $REGISTRY_FILE"

# ── Step 5: Write agent-specific env ───────────────────
AGENT_ENV="# $AGENT_ID agent — added $(date +%Y-%m-%d)
export STUDEX_AGENT_ID=\"$AGENT_ID\"
export STUDEX_AGENT_ROLE=\"$ROLE\"
export STUDEX_ROCKETCHAT_URL=\"http://67.213.119.157:3000\"
export STUDEX_OS_PATH=\"$GIT_DIR\"
export STUDEX_GHOST_PATH=\"$GIT_DIR/ghost\"
export STUDEX_NOTION_SYNC=true
"

echo "$AGENT_ENV" >> "$BASHRC"
log "✓ Agent env written to $BASHRC"

# ── Step 6: Clone ghost (memory) repo ──────────────────
if [[ ! -d "$GIT_DIR/ghost" ]]; then
  log "Cloning ghost memory repo..."
  git clone https://github.com/TumeloRamaphosa/studex-ghost.git "$GIT_DIR/ghost" 2>/dev/null || {
    warn "Ghost repo not found — creating ghost directory..."
    mkdir -p "$GIT_DIR/ghost"
  }
fi

# ── Step 7: Agent health check ─────────────────────────
log "Running agent health check..."
echo ""
echo "--- Health Check ---"
echo "✅ Git: $(git --version | cut -d' ' -f1-3)"
echo "✅ Node: $(node --version 2>/dev/null || echo 'not installed')"
echo "✅ Python: $(python3 --version 2>/dev/null || echo 'not installed')"
echo "✅ Shopify: ${SHOPIFY_STORE:-not configured}"
echo "✅ Rocket.Chat: http://67.213.119.157:3000"
echo "✅ Ghost: $GIT_DIR/ghost"
echo "✅ Registry: $REGISTRY_FILE"
echo ""

# ── Step 8: Post to Rocket.Chat ───────────────────────
log "Posting join notification to Rocket.Chat..."
JOIN_PAYLOAD="{
  \"text\": \"🤖 **$AGENT_ID ($ROLE)** has joined the Studex OS!\\nTimestamp: $TIMESTAMP\",
  \"alias\": \"$AGENT_ID\",
  \"avatar\": \"https://api.dicebear.com/7.x/bottts/svg?seed=$AGENT_ID\"
}"

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$JOIN_PAYLOAD" \
  "http://67.213.119.157:3000/api/v1/chat.postMessage?token=ROCKETCHAT_ADMIN_TOKEN" 2>/dev/null || \
  warn "Rocket.Chat notification failed (will work once Rocket.Chat is running)"

# ── Complete ───────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ $AGENT_ID REGISTERED SUCCESSFULLY    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "1. Reload shell: source ~/.bashrc"
echo "2. Verify connection: curl \$STUDEX_OS_PATH/scripts/health-check.sh"
echo "3. Post your first report:"
echo "   git -C \$STUDEX_OS_PATH add . && git commit -m 'feat($AGENT_ID): initial commit'"
echo ""
echo -e "${BOLD}Your daily routine:${NC}"
echo "  08:00 SAST — Read overnight messages in Rocket.Chat"
echo "  09:00 SAST — Daily stand-up in #war-room"
echo "  17:00 SAST — Post daily report to ghost/"
echo "  20:00 SAST — Board meeting in #board-meeting"
echo "  22:00 SAST — Midnight build"
echo ""
echo -e "🐄 Studex OS · ${AGENT_ID} · ${TIMESTAMP}"
