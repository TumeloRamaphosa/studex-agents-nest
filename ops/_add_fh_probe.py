import re

p = '/workspace/ops/redact-live-secrets-in-place.py'
s = open(p).read()

old = '''    elif value.startswith("blt_"):
        st, _ = get(PROBES["blotato"][2], {"blotato-api-key": value})
    else:
        return "UNKNOWN", "no GET probe defined for this prefix"
    if st == 200:
        return "LIVE", "HTTP 200"
    if st in (401, 403):
        return "DEAD", "HTTP %s" % st
    if st == 0:
        return "UNKNOWN", "network error"
    return "UNKNOWN", "HTTP %s (request-shape error, NOT proof of death)" % st'''

new = '''    elif value.startswith("blt_"):
        st, _ = get(PROBES["blotato"][2], {"blotato-api-key": value})
    elif value.startswith("fh_"):
        # FeedHive needs a CONTROL probe. Its API answers 404 on every
        # endpoint - but it answers 404 for a FABRICATED key too, which
        # proves the SERVICE is gone rather than the credential being
        # rejected. Without the control, a 404 is indistinguishable from a
        # malformed request and the key stays UNKNOWN forever, so it gets
        # masked on every pass and re-masked on the next one, and the
        # "exposure" it reports is noise that hides real findings.
        #
        # The rule the control establishes:
        #   real key AND control key return the SAME status
        #       -> the endpoint cannot distinguish them -> DEAD.
        #          (The service is down / the route is gone / the account
        #           is gone. The credential is not the variable.)
        #   real key 404 but control key returns something else
        #       -> the endpoint is alive and answering -> UNKNOWN.
        st, body = get(PROBES["feedhive"][2], {"Authorization": "Bearer %s" % value})
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
        return "UNKNOWN", ("HTTP %s (real key) vs HTTP %s (control key) - "
                           "the endpoint is alive, so this is NOT proof of death"
                           % (st, ctl_st))
    else:
        return "UNKNOWN", "no GET probe defined for this prefix"
    if st == 200:
        return "LIVE", "HTTP 200"
    if st in (401, 403):
        return "DEAD", "HTTP %s" % st
    if st == 0:
        return "UNKNOWN", "network error"
    return "UNKNOWN", "HTTP %s (request-shape error, NOT proof of death)" % st'''

assert s.count(old) == 1
s = s.replace(old, new, 1)
open(p, 'w').write(s)
print("added the FeedHive control probe to classify()")
