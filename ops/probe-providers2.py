#!/usr/bin/env python3
"""Probe EVERY known LLM credential (from .env and from TOOLS.md) for one that
actually answers, so the Daily Content Agent has a live fallback. Also check
the product/price the agent would publish against the registry."""
import os, subprocess, json, re

env = {}
for line in open("/workspace/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

print("=== ALL keys in /workspace/.env (names only) ===")
print(" ", ", ".join(sorted(env.keys())))

# known keys from TOOLS.md that may not be in .env
TOOLS = {
    "PERPLEXITY": env.get("PERPLEXITY_API_KEY", ""),
    "ALI_MAAS": env.get("ALI_MAAS", ""),
    "ALI_MAAS_2": env.get("ALI_MAAS_2", ""),
    "HYVARE": env.get("HYVARE", ""),
    "NVAPI": env.get("NVIDIA_API_KEY", ""),
}
for k, v in TOOLS.items():
    env.setdefault("TOOLS_" + k, v)


def probe(name, url, key, body, extra=None):
    cmd = ["curl", "-s", "--max-time", "35", "-o", "/tmp/pp.out", "-w", "%{http_code}",
           "-X", "POST", url, "-H", "Authorization: Bearer " + key,
           "-H", "Content-Type: application/json", "-d", body]
    for h in (extra or []):
        cmd += ["-H", h]
    try:
        rr = subprocess.run(cmd, capture_output=True, text=True, timeout=55)
    except Exception as e:
        print(f"  {name:16} EXC {e}")
        return None
    code = rr.stdout
    out = open("/tmp/pp.out").read()[:120].replace("\n", " ")
    print(f"  {name:16} HTTP {code}  {out}")
    return code


print("=== probes ===")
results = {}
if env.get("PERPLEXITY_API_KEY") or env.get("TOOLS_PERPLEXITY", ""):
    results["perplexity"] = probe("perplexity", "https://api.perplexity.ai/chat/completions",
        env.get("PERPLEXITY_API_KEY") or env["TOOLS_PERPLEXITY"],
        '{"model":"sonar","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}')
for nm in ("ALI_MAAS", "ALI_MAAS_2"):
    k = env.get(nm) or env.get("TOOLS_" + nm)
    if k:
        results[nm] = probe(nm, "https://ws-ck212l55q0j2ll0b.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions",
            k, '{"model":"qwen-plus","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}')
if env.get("TOOLS_HYVARE"):
    results["hyvare"] = probe("hyvare", "https://api.hyvare.ai/v1/chat/completions",
        env.get("TOOLS_HYVARE", ""),
        '{"model":"default","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}')
if env.get("TOOLS_NVAPI"):
    results["nvapi"] = probe("nvapi", "https://integrate.api.nvidia.com/v1/chat/completions",
        env["TOOLS_NVAPI"],
        '{"model":"meta/llama-3.1-8b-instruct","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}')
# dashscope with the 2nd key
if env.get("TOOLS_ALI_MAAS_2"):
    results["ds2"] = probe("dashscope#2", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
        env["TOOLS_ALI_MAAS_2"],
        '{"model":"qwen-turbo","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}')

live = [k for k, v in results.items() if v and v.startswith("2")]
print("=== LIVE PROVIDERS ===", live or "NONE")

print("=== product/price the content agent would publish ===")
p = "/workspace/studex-content-automation/scripts/daily-content-agent.js"
src = open(p).read()
for pat in ("R320", "R380", "Classic", "PRODUCTS", "price", "biltong"):
    hits = [m.group(0).strip().replace("\n", " ") for m in
            re.finditer(r".{0,70}" + re.escape(pat) + r".{0,70}", src)]
    if hits:
        print(f"  -- {pat} ({len(hits)})")
        for h in hits[:3]:
            print("     |", h[:160])
print("=== is R320 / R380 in the registry? ===")
reg = open("/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md").read()
for tok in ("R320", "R380", "Classic Beef Biltong"):
    print(f"  {tok:22} in registry: {tok in reg}")
