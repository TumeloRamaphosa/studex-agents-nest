#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/skills/minimax-pdf
bash scripts/make.sh run \
  --title "Studex Meat — Premium Halal Meat" \
  --type proposal \
  --author "Studex Meat" \
  --date "June 2026" \
  --subtitle "Premium Farm-to-Table Meat — South Africa" \
  --accent "#8B1A1A" \
  --cover-bg "#0a0505" \
  --content /workspace/studex-pitch/content.json \
  --out /workspace/studex-pitch/Studex-Meat-Pitch-Deck.pdf
echo "PDF_READY"
