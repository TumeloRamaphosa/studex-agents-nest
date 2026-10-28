#!/usr/bin/env python3
"""
Secret-leak scan for browser-served assets.

2026-10-23: an AgentMail API key was shipped inside the public JS bundle of two
live landing pages (ciie-coffee-landing and coffee-noir-landing, live at
y0r9ilfj96mj.space.mcode.io and q3afz51say2o.space.mcode.io). Anyone could
read the key, list all 10 AgentMail inboxes, read buyer correspondence and send
mail as us. The key was revoked and verified dead (401).

The rule this enforces:

    NO API KEY MAY EVER BE BUILT INTO A BROWSER BUNDLE.

Credentials belong server-side. The landing pages now POST to the lead proxy
(studex-lead-proxy/src/worker.js), which holds the AgentMail credential as a
Cloudflare Worker secret. The browser only ever sees a public URL.

This scans BOTH source and built bundles, because the leak only became real at
build time - the source was where the key lived, but the bundle was where the
public exposure happened.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_PATTERNS = [
    (r"am_us_[A-Za-z0-9]{30,}", "AgentMail API key"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API key"),
    (r"sk-proj-[A-Za-z0-9_\-]{20,}", "OpenAI API key"),
    (r"cfat_[A-Za-z0-9_\-]{20,}", "Cloudflare API token"),
    (r"sk_live_[A-Za-z0-9]{20,}", "Stripe live secret key"),
    (r"ghp_[A-Za-z0-9]{30,}", "GitHub PAT"),
    (r"xox[baprs]-[A-Za-z0-9-]{20,}", "Slack token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
]

# Directories whose contents are served to a browser. A credential in ANY of
# these is public the moment the site deploys.
BROWSER_SERVE_DIRS = [
    "ciie-coffee-landing/dist",
    "ciie-coffee-landing/src",
    "coffee-noir-landing/dist",
    "coffee-noir-landing/src",
    "studex-caviar/dist",
    "studex-caviar/src",
    "studex-corporate-gifting/dist",
    "studex-corporate-gifting/src",
    "china-coffee-lead-capture/dist",
    "china-coffee-lead-capture/src",
    "ciie-buyer-brief/dist",
    "ciie-buyer-brief/src",
    "studex-biltong",
    "studex-sales-static",
    "studex-meat-static",
    "sa-hospitality-coffee",
    "china-coffee-export/dist",
    "deploy-caviar",
    "studex-wildlife-coffee-vite/dist",
]

SCAN_EXT = (".js", ".ts", ".tsx", ".html", ".jsx", ".mjs", ".css", ".json")


def scan():
    """Return a drift-check result dict."""
    issues = []
    scanned = 0
    for rel in BROWSER_SERVE_DIRS:
        base = os.path.join(ROOT, rel)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git")]
            for fn in filenames:
                if not fn.endswith(SCAN_EXT):
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    raw = open(fp, encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                scanned += 1
                for pat, label in SECRET_PATTERNS:
                    for m in re.finditer(pat, raw):
                        line = raw[: m.start()].count("\n") + 1
                        rel_fp = os.path.relpath(fp, ROOT)
                        issues.append(f"{rel_fp}:{line} — {label} in a browser-served file")
    return {
        "name": "Secret leak scan",
        "state": "DRIFT" if issues else "CLEAN",
        "detail": f"{scanned} browser-served files scanned · {len(SECRET_PATTERNS)} credential patterns",
        "issues": issues,
    }


if __name__ == "__main__":
    r = scan()
    print(f"[{r['state']}] {r['name']}: {r['detail']}")
    for i in r["issues"]:
        print("   -", i)
    raise SystemExit(1 if r["issues"] else 0)
