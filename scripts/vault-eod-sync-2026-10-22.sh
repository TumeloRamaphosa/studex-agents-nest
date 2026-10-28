#!/usr/bin/env bash
# Vault EOD sync — commit + push attempt for 2026-10-22
set -uo pipefail
cd /workspace || exit 1

echo "=== STAGE ==="
git add studex-obsidian-vault/ builds/ research/ memory/
git status --short | head -20

echo "=== COMMIT ==="
git commit -m "vault: 2026-10-22 EOD sync — full day consolidated" 2>&1 | tail -15

echo "=== HEAD ==="
git log --oneline -1

echo "=== PUSH ==="
git push origin master 2>&1 | tail -10
echo "push_exit=${PIPESTATUS[0]}"

echo "=== AHEAD ==="
git rev-list --count origin/master..master

echo "=== GDRIVE ==="
if command -v rclone >/dev/null 2>&1; then
  rclone copy studex-obsidian-vault/daily/2026-10-22.md gdrive:1vzzTYCpo0hSwHkIF293msDgKtUy6RdlK/Daily_Logs/ 2>&1 | tail -3
  rclone copy builds/2026-10-22.md gdrive:1vzzTYCpo0hSwHkIF293msDgKtUy6RdlK/Builds/ 2>&1 | tail -3
  echo "gdrive_exit=$?"
else
  echo "rclone missing"
fi
