#!/usr/bin/env python3
import urllib.request, urllib.error, re, json
def http(url):
    try:
        with urllib.request.urlopen(url, timeout=25) as r: return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e: return e.code, e.read()[:200].decode(errors="replace")
    except Exception as e: return None, str(e)

st, body = http("https://studexmeat.com/")
print("home:", st, len(body))
links = sorted(set(re.findall(r'href="(/collections/[^"]+)"', body)))
print("collections found:", links)
for l in links[:8]:
    s, b = http("https://studexmeat.com" + l)
    print("  ", l, "->", s)

print("\nproducts.json:", http("https://studexmeat.com/products.json?limit=2")[0])
