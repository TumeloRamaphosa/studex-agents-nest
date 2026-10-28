#!/usr/bin/env bash
# Watches for a pending OpenClaw device pairing request (the owner's Samsung phone
# scanning the MaxClaw "Connect a new device" QR) and auto-approves the newest one.
# Robust to transient CLI/gateway timeouts. Writes result to /tmp/phone_pair_result.txt.
LOG=/tmp/phone_pair_result.txt
: > "$LOG"
DEADLINE=$(( $(date +%s) + 3300 ))   # 55 minutes

list_devices() {
  for attempt in 1 2 3; do
    out=$(timeout 40 openclaw devices list 2>/dev/null \
          | grep -vE "MMLOG|Config warn|composio|matrix-claw|^\[plugins\]")
    if printf '%s' "$out" | grep -qiE "Pending|Paired"; then
      printf '%s' "$out"
      return 0
    fi
    sleep 3
  done
  return 1
}

while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  OUT=$(list_devices) || { sleep 10; continue; }
  # Count pending rows: lines under the "Pending" table that contain a device id
  RID=$(printf '%s\n' "$OUT" | awk '
    /^Pending/ {inpend=1; next}
    /^Paired/  {inpend=0}
    inpend && $0 ~ /[0-9a-f]{16}/ {
      for (i=1;i<=NF;i++) if ($i ~ /^[0-9a-f]{16,}/) { print $i; exit }
    }' | head -1)
  if [ -n "$RID" ]; then
    echo "$(date -u +%FT%TZ) pending request: $RID" >> "$LOG"
    RES=$(timeout 60 openclaw devices approve "$RID" --json 2>&1 \
          | grep -vE "MMLOG|Config warn|composio|matrix-claw|^\[plugins\]")
    echo "approve result: $RES" >> "$LOG"
    echo "--- final device table ---" >> "$LOG"
    list_devices >> "$LOG"
    exit 0
  fi
  sleep 10
done
echo "$(date -u +%FT%TZ) TIMEOUT: no pending pairing request in 55 min" >> "$LOG"
exit 0
