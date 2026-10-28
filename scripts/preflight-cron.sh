#!/bin/sh
# Wrapper for the 08:00 SAST Daily Post pre-flight cron.
# Picks the right date: the pre-flight should check the post that is ABOUT
# TO PUBLISH (09:00 SAST today), not yesterday's.
#
# The target is ALWAYS today's SAST date. There is deliberately no "fall back
# to tomorrow's" branch: tomorrow's post is published by tomorrow's 09:00 job
# and checked by tomorrow's 08:00 gate. Checking tomorrow's file today would
# gate the wrong post. (An earlier version of this comment claimed such a
# fallback that the script never implemented - the comment was wrong, not the
# code. ops/test-preflight-gate-wording.py now guards this.)
#
# If today's queue file is not staged, ops/preflight-daily-post.py warns and
# exits 0: the 09:00 job stages the file itself, so the 08:00 gate simply has
# no input on an un-staged day. See that script's NO QUEUE FILE branch.
set -e
cd /workspace

SAST_DATE=$(TZ=Africa/Johannesburg date +%Y-%m-%d)
TARGET="$SAST_DATE"

echo "pre-flight target: $TARGET"
python3 ops/preflight-daily-post.py "$TARGET"
