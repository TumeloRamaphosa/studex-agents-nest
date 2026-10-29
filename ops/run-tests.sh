#!/usr/bin/env bash
# Canonical test runner for the Studex workspace.
#
# There was no single entry point, so every session re-derived the test list by
# grepping HEARTBEAT.md and could silently drop one. This is the one command
# that runs EVERY ops test and fails if any of them fails.
#
# Usage: bash ops/run-tests.sh
set -u
cd /workspace || exit 1

PY_TESTS=(
  ops/test-publish-sanitize.py
  ops/test-publish-sanitize-negative.py
  ops/test-hashtag-cap.py
  ops/test-hashtag-guard.py
  ops/test-key-resolution.py
  ops/test-credential-resolution.py
  ops/test-credential-fence-check.py
  ops/test-cron-times-checker.py
  ops/test-cron-timeout-outliers.py
  ops/test-cron-range-checker.py
  ops/test-correction-rules.py
  ops/test-draft-rules.py
  ops/test-note-json-consistency.py
  ops/test-crosspath-guard.py
  ops/test-media-check-targets.py
  ops/test-fixture-immunity.py
  ops/test-spa-bundle-check.py
  ops/test-public-exposure.py
  ops/test-memory-shrink-guard.py
  ops/test-badge-sweep-coverage.py
  ops/test-dead-inbox-check.py
  ops/test-agentmail-inventory.py
  ops/test-cron-payload-claims.py
  ops/test-tmp-credential-surface.py
  ops/test-tmp-shape-surface-audit.py
  ops/test-tmp-shape-memory.py
  ops/test-doc-credential-pointers.py
  ops/test-scanner-log-exposure.py
  ops/test-client-secret-exposure.py
  ops/test-cost-model-exposure.py
  ops/test-staged-publish.py
  ops/test-blotato-probe-auth.py
  ops/test-price-on-feed.py
  ops/test-check-latest-mail.py
  ops/test-unbound-time-names.py
  ops/test-preflight-gate-wording.py
  ops/test-preflight-target-date.py
  ops/test-preflight-media-gate.py
  ops/test-preflight-account-ids.py
  ops/test-preflight-publish-health.py
  ops/test-china-tariff-claim.py
  ops/test-http-probe.py
  ops/test-runner-contract.py
  ops/test-heartbeat-registry.py
  ops/test-ladder-lock.py
  ops/test-discord-credential-checker.py
  ops/test-cred-name-filter.py
  ops/test-git-pre-push-guard.py
  ops/test-pre-push-guard-check.py
  ops/test-git-index-check.py
  ops/test-empty-repo-false-green.py
  ops/test-credential-slots.py
  ops/test-credential-slots-short.py
  ops/test-audit-credential-fragments.py
  ops/test-mask-credential-fragments.py
  ops/test-dead-service-instructions.py \
)
JS_TESTS=(
  scripts/test-no-markdown-leak.py
  ops/test-fallback-hashtag-cap.js
  ops/test-content-agent-hashtag-guard.js
  studex-content-automation/scripts/test-guard.js
  studex-content-automation/scripts/test-fallback-media.js
studex-content-automation/scripts/test-fallback-policy.js
studex-content-automation/scripts/test-no-price-in-caption-prompt.js
studex-content-automation/scripts/test-fallback-is-invoked.js
)

fail=0
for t in "${PY_TESTS[@]}"; do
  if [ ! -f "$t" ]; then
    echo "MISSING  $t"; fail=1; continue
  fi
  if timeout 180s python3 "$t" >/tmp/t.out 2>&1; then
    echo "PASS     $t"
  else
    echo "FAIL     $t"
    tail -n 12 /tmp/t.out | sed 's/^/         /'
    fail=1
  fi
done

for t in "${JS_TESTS[@]}"; do
  if [ ! -f "$t" ]; then
    echo "MISSING  $t"; fail=1; continue
  fi
  case "$t" in
    *.js) RUN="node $t" ;;
    *)   RUN="python3 $t" ;;
  esac
  if timeout 180s $RUN >/tmp/t.out 2>&1; then
    echo "PASS     $t"
  else
    echo "FAIL     $t"
    tail -n 12 /tmp/t.out | sed 's/^/         /'
    fail=1
  fi
done

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL TESTS PASS (${#PY_TESTS[@]} python + ${#JS_TESTS[@]} other)"
else
  echo "SOME TESTS FAILED"
fi
exit "$fail"
