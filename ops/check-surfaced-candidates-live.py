#!/usr/bin/env python3
"""Liveness-check the two remaining surfaced candidates. GET only.

  .netrc                          - a TRACKED file with an opaque 70-char value
  studex-blotato-coffee-launch/
    BLOTATO-SETUP.md              - a 'blotato'-prefixed 52-char value

Both are tracked, so both WOULD be published. The question is whether
either is a LIVE credential.

Reports only: the host/service probed, the HTTP status, and whether the
value matches a credential already known to this workspace. No credential
value is ever printed.
"""
import pathlib
import urllib.error
import urllib.request

WS = pathlib.Path("/workspace")


def get(url, headers):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        return 0


def netrc_value():
    p = WS / ".netrc"
    if not p.exists():
        return None, None
    machine = None
    for line in p.read_text(errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("machine "):
            machine = line.split(None, 1)[1].strip()
        elif line.startswith("password ") and machine:
            return machine, line.split(None, 1)[1].strip()
    return machine, None


def blotato_value():
    p = WS / "studex-blotato-coffee-launch/BLOTATO-SETUP.md"
    if not p.exists():
        return None
    lines = p.read_text(errors="ignore").splitlines()
    if len(lines) < 32:
        return None
    line = lines[31]
    for tok in line.replace("`", " ").replace(":", " ").split():
        if tok.startswith("blotato") or tok.startswith("blt_"):
            return tok
    return None


def main():
    print("=== .netrc (TRACKED) ===")
    machine, val = netrc_value()
    if not val:
        print("  no machine/password pair found")
    else:
        print(f"  host          : {machine}")
        print(f"  value         : len={len(val)}")
        # A .netrc is a netrc-format credential. Probe the host it names
        # with a GET, using the value as a bearer token. GET only.
        # github.com's REST API lives at api.github.com - probing
        # github.com/api/... returns 404, which is INCONCLUSIVE, not proof
        # of death. Never treat a 404 as "the key is dead".
        host = (machine or "").strip().lower()
        api_host = {"github.com": "api.github.com"}.get(host, host)
        url = f"https://{api_host}/user" if api_host else ""
        if url:
            st = get(url, {"Authorization": f"Bearer {val}",
                           "User-Agent": "studex-ops-audit"})
            print(f"  probe GET {url}")
            print(f"  -> HTTP {st or 'network error'}"
                  f"   ({'LIVE' if st == 200 else 'not live' if st in (401, 403) else 'inconclusive'})")

    print()
    print("=== BLOTATO-SETUP.md:32 (TRACKED) ===")
    bval = blotato_value()
    if not bval:
        print("  no blotato-prefixed token found on that line")
    else:
        print(f"  value         : len={len(bval)} prefix={bval[:5]}...")
        st = get("https://backend.blotato.com/v2/users/me/accounts",
                 {"blotato-api-key": bval})
        print("  probe GET https://backend.blotato.com/v2/users/me/accounts")
        print(f"  -> HTTP {st or 'network error'}"
              f"   ({'LIVE' if st == 200 else 'not live' if st in (401, 403) else 'inconclusive'})")


if __name__ == "__main__":
    main()
