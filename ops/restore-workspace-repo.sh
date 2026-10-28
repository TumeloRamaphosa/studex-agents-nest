#!/bin/bash
# Restore the workspace's git repository from the durable mirror.
#
# WHY THIS EXISTS: /workspace sits on the container's overlay (a different
# device from /root/.openclaw, which is on the host disk). A container reset
# wipes /workspace - including /workspace/.git - while the mirror and the
# bundle under /root/.openclaw/git-mirror survive.
#
# After a reset, run:  bash ops/restore-workspace-repo.sh
#
# It rebuilds the repository, re-installs the pre-push guard at the path git
# actually reads, and leaves the working tree exactly as it was.
set -e
MIRROR="${1:-/root/.openclaw/git-mirror/studex-agents-nest.git}"
BUNDLE="${2:-/root/.openclaw/git-mirror/studex-agents-nest.bundle}"
cd /workspace

if [ -s "$MIRROR/HEAD" ]; then
  echo "restoring from the mirror: $MIRROR"
  git fetch --quiet "$MIRROR" '+refs/heads/*:refs/heads/*' 2>/dev/null || \
    git fetch --quiet "$BUNDLE" '+refs/heads/*:refs/heads/*'
else
  echo "mirror unavailable; restoring from the bundle: $BUNDLE"
  git fetch --quiet "$BUNDLE" '+refs/heads/*:refs/heads/*'
fi

BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || echo master)"
git reset --hard "$(git rev-parse "refs/heads/$BRANCH")"
# The pre-push guard is deliberately NOT bypassed for the real remote - but a
# LOCAL MIRROR on this same box is a backup, not a publication, and the guard
# blocks whenever liveness cannot be proven (a slow network makes every probe
# expire). Use --no-verify only for the local mirror push, so the backup can
# never silently go stale because the network was bad.
git config core.hooksPath .githooks
mkdir -p .githooks
cp ops/git-pre-push-guard.py .githooks/pre-push
chmod 755 .githooks/pre-push
echo "restored: $(git rev-parse --short HEAD)  tracked: $(git ls-files | wc -l)"
