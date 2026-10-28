import urllib.request
import urllib.error
import json
import os

FH_TOKEN = os.environ.get("FEEDHIVE_API_KEY", "")

endpoints = [
    "/v1/accounts",
    "/public/v1/accounts",
    "/v1/profile",
    "/v1/user",
    "/v1/media/upload",
]

FH_BASE = "https://api.feedhive.com"

for ep in endpoints:
    try:
        req = urllib.request.Request(f"{FH_BASE}{ep}", headers={"Authorization": f"Bearer {FH_TOKEN}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            print(f"GET {ep} -> {resp.status}: {body[:300]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"GET {ep} -> HTTP {e.code}: {body[:300]}")
    except Exception as e:
        print(f"GET {ep} -> ERROR: {type(e).__name__}: {e}")
