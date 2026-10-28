#!/usr/bin/env python3
import json, urllib.request, urllib.error, os

def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400].decode(errors="replace")
    except Exception as e:
        return None, str(e)

bt = os.environ.get("BLOTATO_API_KEY", "")
H = {"blotato-api-key": bt}
st, body = http("https://backend.blotato.com/v2/users/me/accounts", H)
print("accounts ->", st)
try:
    for a in json.loads(body).get("items", []):
        print("  ", a.get("id"), a.get("platform"), a.get("username") or a.get("fullname"), "| status:", a.get("status"), "| channels:", a.get("channels"))
except Exception as e:
    print(body[:400])

for p in ["/v2/posts?limit=5", "/v2/media?limit=3"]:
    st, body = http("https://backend.blotato.com"+p, H)
    print("\n", p, "->", st, body[:300])
