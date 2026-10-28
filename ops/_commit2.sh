#!/bin/sh
cd /workspace || exit 1
git add -A
git commit -q -m "ops: post the credential-exposure closure to #ops

One post, on first appearance of a materially new finding (the source of the
leak was Discord + session transcripts, not the log). Includes the two
false negatives caught before shipping (single-page fetch; rate-limit
truncation) and the fact that the key itself is proven DEAD - api.feedhive.com
returns 404 for the real key AND a fabricated one, so the service is gone.

The one owner item that remains is the GitHub PAT: the key is still on the
public remote and push is unauthenticated." || echo "nothing to commit"
git log --oneline -1
