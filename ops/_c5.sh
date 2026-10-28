#!/bin/sh
cd /workspace || exit 1
git add -A
git commit -q -F - <<'MSG'
ops: a pre-push guard, because installing a working PAT removed our safety net

Installing the recovered GitHub PAT made `git push` authenticate for the
first time in months. That is what we wanted - but it also REMOVED an
accidental safety net.

Until now the local history was safe BY ACCIDENT: push could not
authenticate, so the 954 unpushed commits - which carry additional copies of
two live credentials - could not leave the machine. The moment push works, a
fast-forward would publish those copies into a PUBLIC repo and turn a known
exposure into a larger one.

ops/git-pre-push-guard.py is installed at .git/hooks/pre-push and BLOCKS a
push whose commits carry a credential that still authenticates. It reads the
pushed BLOBS (not the working tree), and only objects that are new relative
to the remote - re-publishing an object that is already published adds no
new exposure, and blocking on that would make the guard unusable.

  * LIVE    - the provider CONFIRMED it still authenticates. Active breach.
  * UNKNOWN - the provider could not be probed. Blocked anyway, because
              UNKNOWN is not safe, but reported separately because it calls
              for different urgency.
  * DEAD    - allowed. It authenticates to nothing; it is noise.

Blocking is the safe default: a false block is recoverable with
--no-verify, a published live key is not.

MEASURED AGAINST THE REAL PUSH: the guard BLOCKS the current pending push.
The local history carries credential material for 17 names across 100+
blobs. This is the number the owner needs, and until now nothing in the
stack could produce it.

THE HOOK IS NOT TRACKED BY GIT
------------------------------
.git/hooks/pre-push lives inside .git/, so git status never shows it, a
clone never gets it, and someone can edit ops/git-pre-push-guard.py without
reinstalling it - leaving an OLDER policy enforcing the push. So the
installation is itself checked:

  ops/check-pre-push-guard.py  - PASS checker, registered in
                                 ops/heartbeat-checkers.tsv. It compares the
                                 INSTALLED hook against its source
                                 byte-for-byte and confirms it is
                                 executable.

A control that is not itself checked is a control that decays.

Suite: 40 python + 3 other.
MSG
echo "COMMIT_RC=$?"
git log --oneline -1
git status --short | head -3
