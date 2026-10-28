#!/usr/bin/env python3
"""Heartbeat pass 10 — one shot, no polling."""
import json, os, pathlib, subprocess, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

ROOT = "/workspace"
SAST = timezone(timedelta(hours=2))
now = datetime.now(timezone.utc)
print(f"HEARTBEAT PASS 10  {now:%Y-%m-%d %H:%M:%S} UTC / {now.astimezone(SAST):%H:%M} SAST\n")

def sh(cmd, timeout=120, cwd=ROOT):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, shell=isinstance(cmd, str))
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, f"ERR {e}"

# ---------- 1. infra ----------
print("=" * 70); print("1. INFRA (expect: unchanged DOWN, do not repost)"); print("=" * 70)
for port, label in [("3000", "Gitea"), ("3778", "Registry")]:
    rc, out = sh(f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 5 http://100.95.66.29:{port}/ 2>&1 || echo TIMEOUT", timeout=20)
    print(f"  hub {port} ({label}): {out.strip() or 'no response'}")
rc, out = sh("ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o PasswordAuthentication=no root@47.236.124.79 'echo ALI_OK' 2>&1", timeout=25)
print(f"  Alibaba 47.236.124.79: {'REACHABLE' if 'ALI_OK' in out else 'DOWN (timeout)'}")
rc, out = sh("curl -s -o /dev/null -w '%{http_code}' --max-time 8 https://studexmeat.com 2>&1 || echo ERR", timeout=20)
print(f"  Shopify storefront studexmeat.com: HTTP {out.strip()}")

# ---------- 2. drift ----------
print("\n" + "=" * 70); print("2. DRIFT"); print("=" * 70)
rc, out = sh([sys.executable, "ops/build-manifest.py"], timeout=180)
print("  build-manifest:", out.strip().splitlines()[-1] if out.strip() else "(no output)")
rc, out = sh([sys.executable, "ops/drift-check.py"], timeout=280)
for l in out.strip().splitlines()[-14:]:
    print("  " + l)
print(f"  drift-check exit={rc}  (0=clean, 1=drift, 2=unreachable)")

# ---------- 3. cron ----------
print("\n" + "=" * 70); print("3. CRON FLEET"); print("=" * 70)
jobs = json.loads(pathlib.Path("/root/.openclaw/cron/jobs.json").read_text())
jobs = jobs.get("jobs", jobs if isinstance(jobs, list) else [])
en = [j for j in jobs if j.get("enabled")]
fail = [j for j in en if (j.get("state") or {}).get("consecutiveErrors", 0)]
print(f"  ENABLED JOBS: {len(en)} | FAILING: {len(fail)}")
for j in fail:
    st = j.get("state") or {}
    print(f"    FAIL {j.get('name','')[:44]:44} consec={st.get('consecutiveErrors')} last={st.get('lastStatus')}")
ciie = [j for j in jobs if j.get("id") in ("36bc4f61-54cd-4c0a-8cac-b5c20217ad77", "766d1f8a-b04f-4486-80de-d45b4e794f44")]
print(f"  CIIE crons enabled: {sum(1 for j in ciie if j.get('enabled'))} (must be 0)")
rc, out = sh([sys.executable, "ops/check-cron-times.py"], timeout=60)
print("  cron-time check: exit", rc, "|", out.strip().splitlines()[-1] if out.strip() else "")
# next 3 scheduled runs
rows = []
for j in en:
    nr = (j.get("state") or {}).get("nextRunAtMs")
    if nr:
        rows.append((nr, j.get("name", "")))
rows.sort()
print("  next scheduled runs:")
for nr, n in rows[:4]:
    t = datetime.fromtimestamp(nr/1000, tz=timezone.utc).astimezone(SAST)
    print(f"    {t:%a %H:%M} SAST  {n[:52]}")

# ---------- 4. AgentMail both accounts ----------
print("\n" + "=" * 70); print("4. AGENTMAIL — BOTH ACCOUNTS, limit=1000, assert not truncated"); print("=" * 70)
KEYS = {"main": os.environ.get("AM_MAIN", ""), "ciie": os.environ.get("AM_CIIE", "")}
try:
    for line in pathlib.Path(f"{ROOT}/.env").read_text().splitlines():
        for nm in ("AGENTMAIL_API_KEY", "AGENTMAIL_CIIE_KEY", "AGENTMAIL_WARMUP_KEY"):
            if line.startswith(nm + "="):
                pass
except Exception:
    pass
# read keys from the env file by name
envtxt = pathlib.Path(f"{ROOT}/.env").read_text() if pathlib.Path(f"{ROOT}/.env").exists() else ""
def envval(name):
    for line in envtxt.splitlines():
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None
cand = {
    "main": envval("AGENTMAIL_API_KEY"),
    "ciie": envval("AGENTMAIL_CIIE_NURTURE_KEY") or envval("AGENTMAIL_DEDICATED_KEY"),
    "warmup": envval("AGENTMAIL_WARMUP_KEY"),
}
INTERNAL = {"robusca.romanov@studex-group.com", "naledi-cmo@studex-group.com", "t.ramaphosa@agentmail.to",
            "project-2571-studex-agent-2077@agentmail.to", "tumelor001@gmail.com", "naledi.services@gmail.com",
            "robusca.romanov@outlook.com", "t-ramaphosa-ceo@studex-group.com", "info@studex-group.com"}
for acct, key in cand.items():
    if not key:
        print(f"  [{acct}] NO KEY FOUND IN .env")
        continue
    try:
        req = urllib.request.Request("https://api.agentmail.to/v0/inboxes", headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"  [{acct}] inbox list FAILED: {e}")
        continue
    ib = data.get("inboxes", data if isinstance(data, list) else [])
    tot, trunc, ext = 0, [], []
    for inbox in ib:
        iid = inbox.get("inbox_id") or inbox.get("id")
        try:
            req = urllib.request.Request(f"https://api.agentmail.to/v0/inboxes/{iid}/messages?limit=1000",
                                        headers={"Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=40) as r:
                msgs = json.loads(r.read().decode())
            msgs = msgs.get("messages", msgs if isinstance(msgs, list) else [])
            if len(msgs) >= 1000:
                trunc.append(iid)
            tot += len(msgs)
            for m in msgs:
                frm = (m.get("from") or "")
                addr = frm if isinstance(frm, str) else (frm.get("email") or frm.get("address") or "")
                addr = addr.lower().strip()
                if addr and addr not in INTERNAL and "@" in addr:
                    ts = m.get("sent_at") or m.get("created_at") or ""
                    ext.append((ts, addr, (m.get("subject") or "")[:50]))
        except Exception:
            pass
    ext.sort(reverse=True)
    print(f"  [{acct}] inboxes={len(ib)} messages={tot} truncated={len(trunc)} external_senders={len(set(e[1] for e in ext))}")
    for ts, a, s in ext[:5]:
        print(f"       {ts[:19]:19} {a:38} {s}")

# ---------- 5. CIIE safety state ----------
print("\n" + "=" * 70); print("5. CIIE SAFETY STATE"); print("=" * 70)
for f, needle in [("ciie-nurture/send-sequence.js", "CIIE_NURTURE_ARMED"),
                  ("ciie-nurture/dist/cli.js", "CIIE_NURTURE_ARMED")]:
    p = pathlib.Path(f"{ROOT}/{f}")
    if p.exists():
        t = p.read_text(errors="ignore")
        armed = "CIIE_NURTURE_ARMED !== '1'" in t or 'CIIE_NURTURE_ARMED !== "1"' in t
        print(f"  {f}: kill switch present={armed}")

# ---------- 6. repo ----------
print("\n" + "=" * 70); print("6. REPO"); print("=" * 70)
rc, out = sh("git log --oneline -6", timeout=30)
print(out.strip())
rc, out = sh("git status --short | wc -l", timeout=60)
print(f"  modified/untracked paths: {out.strip()}")
rc, out = sh("git status --short -- .matrix-chat-history/ memory/ builds/ research/ studex-obsidian-vault/ | head -5", timeout=60)
print("  skip-listed paths still dirty:", (out.strip() or "(none)")[:200])
print("\nDONE")
