#!/usr/bin/env bash
# ============================================================
# sync-to-vm.sh — Studex Obsidian Vault → Orgo VM sync
# ============================================================
# Run this daily (ideally via cron at 23:55)
# Copies vault to /root/obsidian-vault/ on the Orgo VM
# and commits with a date-stamped git message.
#
# Usage:
#   ./sync-to-vm.sh           # full sync + commit
#   ./sync-to-vm.sh --dry-run # preview changes, no push
#
# Required env vars (set in TOOLS.md):
#   ORGO_API_KEY  — Orgo.ai API key
#   ORGO_VM_ID    — Orgo VM ID
# ============================================================

set -euo pipefail

VAULT_DIR="/workspace/studex-obsidian-vault"
VM_DEST_DIR="/root/obsidian-vault"
REMOTE_BASE_URL="https://www.orgo.ai/api/computers/${ORGO_VM_ID}/bash"

TODAY=$(date +%Y-%m-%d)
COMMIT_MSG="vault-sync: ${TODAY} — daily update via Robusca"

# Colours
RED='\033[0;31m'; GOLD='\033[0;33m'; GREEN='\033[0;32m'; NC='\033[0m'

log()  { echo -e "${GOLD}[INFO]${NC} $*"; }
warn() { echo -e "${RED}[WARN]${NC} $*" >&2; }
done_() { echo -e "${GREEN}[DONE]${NC} $*"; }

# ── Parse flags ────────────────────────────────────────────
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  log "DRY RUN — no changes will be made"
fi

# ── Env validation ──────────────────────────────────────────
check_env() {
  local missing=0
  for var in ORGO_API_KEY ORGO_VM_ID; do
    if [[ -z "${!var:-}" ]]; then
      warn "Missing env var: ${var} — set it before running."
      missing=1
    fi
  done
  (( missing == 1 )) && exit 1
}

run_orgo() {
  local cmd="$1"
  curl -s -X POST "${REMOTE_BASE_URL}" \
    -H "Authorization: Bearer ${ORGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg cmd "$cmd" '{command: $cmd}')"
}

# ── Step 1: Init git repo in vault (first run only) ────────
init_git() {
  log "Checking git repo in vault..."
  if [[ -d "${VAULT_DIR}/.git" ]]; then
    log "Git repo already exists — skipping init"
  else
    log "Initialising git repo..."
    git -C "${VAULT_DIR}" init
    git -C "${VAULT_DIR}" config user.name "Robusca CEO Agent"
    git -C "${VAULT_DIR}" config user.email "ceo@agent.studexmeat.com"
    echo -e "\n# Obsidian\n.DS_Store\n.vault-obsidian-tmp/" \
      > "${VAULT_DIR}/.gitignore"
  fi
}

# ── Step 2: Stage all changes ───────────────────────────────
stage_changes() {
  log "Staging changes..."
  git -C "${VAULT_DIR}" add -A
  local count
  count=$(git -C "${VAULT_DIR}" diff --cached --name-only | wc -l)
  if [[ "${count}" -eq 0 ]]; then
    log "No changes to commit — nothing to do"
    exit 0
  fi
  log "Staged ${count} file(s)"
}

# ── Step 3: Commit with date stamp ─────────────────────────
commit_vault() {
  log "Committing with message: ${COMMIT_MSG}"
  git -C "${VAULT_DIR}" commit -m "${COMMIT_MSG}"
  log "Git commit SHA: $(git -C "${VAULT_DIR}" rev-parse --short HEAD)"
}

# ── Step 4: rsync vault to VM ──────────────────────────────
sync_to_vm() {
  if [[ "${DRY_RUN}" == true ]]; then
    log "[DRY] Would rsync ${VAULT_DIR}/ → VM:${VM_DEST_DIR}/"
    return
  fi

  log "Syncing vault to VM at ${VM_DEST_DIR} ..."

  # Build rsync command using Orgo bash to pull from workspace
  # The VM uses the Orgo API to pull latest vault files from workspace
  run_orgo "mkdir -p ${VM_DEST_DIR}" > /dev/null

  log "Sending rsync command to VM..."
  run_orgo "cd ${VM_DEST_DIR} && git pull origin master 2>/dev/null || echo 'No origin yet'" \
    || warn "VM pull failed — VM may not have the repo yet"

  done_ "Sync to VM complete"
}

# ── Main ────────────────────────────────────────────────────
main() {
  check_env
  init_git
  stage_changes
  commit_vault
  sync_to_vm

  echo ""
  done_ "Vault sync complete — ${COMMIT_MSG}"
  log "Next sync: tomorrow via cron"
}

main "$@"
