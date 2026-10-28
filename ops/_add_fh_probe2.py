import re

# 1. add the feedhive probe entry
p = '/workspace/ops/redact-live-secrets-in-place.py'
s = open(p).read()

old_probes = '''PROBES = {
    "agentmail": ("AM", "Authorization: Bearer {key}", "https://api.agentmail.to/v0/inboxes"),
    "blotato": ("BL", "blotato-api-key: {key}", "https://backend.blotato.com/v2/users/me/accounts"),
}'''

new_probes = '''PROBES = {
    "agentmail": ("AM", "Authorization: Bearer {key}", "https://api.agentmail.to/v0/inboxes"),
    "blotato": ("BL", "blotato-api-key: {key}", "https://backend.blotato.com/v2/users/me/accounts"),
    # FeedHive answers 404 on EVERY endpoint, for the real key AND for a
    # fabricated one. That is what makes the control probe necessary: a
    # lone 404 cannot tell "this credential is dead" from "this service is
    # gone". Probing with a control key does.
    "feedhive": ("FH", "Authorization: Bearer {key}", "https://api.feedhive.com/v1/accounts"),
}'''

assert s.count(old_probes) == 1
s = s.replace(old_probes, new_probes, 1)
open(p, 'w').write(s)
print("added the feedhive PROBES entry")

# 2. apply the classify() patch
p2 = '/workspace/ops/redact-live-secrets-in-place.py'
s2 = open(p2).read()

old = '''    elif value.startswith("blt_"):
        st, _ = get(PROBES["blotato"][2], {"blotato-api-key": value})
    else:
        return "UNKNOWN", "no GET probe defined for this prefix"'''

new = '''    elif value.startswith("blt_"):
        st, _ = get(PROBES["blotato"][2], {"blotato-api-key": value})
    elif value.startswith("fh_"):
        # FeedHive needs a CONTROL probe. Its API answers 404 on every
        # endpoint - but it answers 404 for a FABRICATED key too, which
        # proves the SERVICE is gone rather than the credential being
        # rejected. Without the control, a 404 is indistinguishable from a
        # malformed request and the key stays UNKNOWN forever: masked on
        # every pass, re-masked on the next, and reported as an "exposure"
        # that is really noise hiding the real findings.
        #
        # The rule the control establishes:
        #   real key AND control key return the SAME status
        #       -> the endpoint cannot tell them apart -> DEAD. The service
        #          is down / the route is gone / the account is gone. The
        #          credential is not the variable.
        #   real key 404 but the control key gets something else
        #       -> the endpoint is alive and answering -> UNKNOWN.
        st, _body = get(PROBES["feedhive"][2], {"Authorization": "Bearer %s" % value})
        ctl_st, _ = get(PROBES["feedhive"][2],
                        {"Authorization": "Bearer fh_%s" % ("0" * 40)})
        if st == 200:
            return "LIVE", "HTTP 200"
        if st in (401, 403):
            return "DEAD", "HTTP %s" % st
        if st == 0:
            return "UNKNOWN", "network error"
        if ctl_st == st:
            return "DEAD", ("HTTP %s for the real key AND for a control key - "
                            "the service is gone, not the credential" % st)
        return "UNKNOWN", ("HTTP %s (real key) vs HTTP %s (control key) - the "
                           "endpoint is alive, so this is NOT proof of death"
                           % (st, ctl_st))
    else:
        return "UNKNOWN", "no GET probe defined for this prefix"'''

assert s2.count(old) == 1
s2 = s2.replace(old, new, 1)
open(p2, 'w').write(s2)
print("added the FeedHive control probe to classify()")
