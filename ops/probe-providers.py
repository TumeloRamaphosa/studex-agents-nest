#!/usr/bin/env python3
"""List LLM-ish keys in .env, and probe each candidate endpoint the content
agent could use, so we can point it at a provider that actually answers."""
import os, subprocess, json, re

env = {}
for line in open("/workspace/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

KEYWORDS = ("OPENAI", "MOONSHOT", "DASHSCOPE", "QWEN", "PERPLEXITY", "MINIMAX",
            "DEEPSEEK", "ANTHROPIC", "GROQ", "GEMINI", "GOOGLE", "ZAI", "GLM",
            "OPENROUTER", "HUGGING", "NVIDIA", "NVAPI", "HYVARE", "KIMI", "XAI",
            "TOGETHER", "FIREWORKS", "CEREBRAS", "LLAMA", "BAICHUAN", "AI21")

cands = {k: v for k, v in env.items()
         if any(w in k.upper() for w in KEYWORDS) and len(v) > 20}
print("=== candidate provider keys in /workspace/.env ===")
for k, v in sorted(cands.items()):
    print(f"  {k:28} {v[:10]}...{v[-4:]}  len={len(v)}")

print("=== which providers does the content agent try? ===")
src = open("/workspace/studex-content-automation/scripts/daily-content-agent.js").read()
for m in re.finditer(r".{0,100}(process\.env\.[A-Z_]+).{0,60}", src):
    print("  |", m.group(0).strip().replace("\n", " ")[:170])

print("=== provider order / fallback block ===")
for m in re.finditer(r"(async function call[A-Za-z]*|PROVIDERS?\s*=|fallback|providerOrder).{0,700}", src, re.S):
    seg = m.group(0)
    print("  ---")
    print("  " + seg[:700].replace("\n", "\n  "))
    break


def probe(name, url, headers, body):
    cmd = ["curl", "-s", "--max-time", "40", "-o", "/tmp/p.out", "-w", "%{http_code}",
           "-X", "POST", url]
    for h in headers:
        cmd += ["-H", h]
    cmd += ["-H", "Content-Type: application/json", "-d", body]
    try:
        rr = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except Exception as e:
        print(f"  {name:14} EXC {e}")
        return
    out = open("/tmp/p.out").read()[:150].replace("\n", " ")
    print(f"  {name:14} HTTP {rr.stdout}  {out}")


print("=== live probes ===")
if "DASHSCOPE_API_KEY" in env:
    probe("dashscope", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
          ["Authorization: Bearer " + env["DASHSCOPE_API_KEY"]],
          '{"model":"qwen-turbo","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
if "PERPLEXITY_API_KEY" in env:
    probe("perplexity", "https://api.perplexity.ai/chat/completions",
          ["Authorization: Bearer " + env["PERPLEXITY_API_KEY"]],
          '{"model":"sonar","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
for k in ("MINIMAX_API_KEY", "MINIMAX_API_KEY_INTL"):
    if k in env:
        probe("minimax:" + k, "https://api.minimax.chat/v1/text/chatcompletion_v2",
              ["Authorization: Bearer " + env[k]],
              '{"model":"MiniMax-Text-01","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
if "OPENROUTER_API_KEY" in env:
    probe("openrouter", "https://openrouter.ai/api/v1/chat/completions",
          ["Authorization: Bearer " + env["OPENROUTER_API_KEY"]],
          '{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
if "HUGGINGFACE_API_KEY" in env:
    probe("huggingface", "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct",
          ["Authorization: Bearer " + env["HUGGINGFACE_API_KEY"]],
          '{"inputs":"hi","max_new_tokens":5}')
if "NVAPI_API_KEY" in env:
    probe("nvidia", "https://integrate.api.nvidia.com/v1/chat/completions",
          ["Authorization: Bearer " + env["NVAPI_API_KEY"]],
          '{"model":"meta/llama-3.1-8b-instruct","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
if "KIMI_API_KEY" in env or "MOONSHOT_API_KEY" in env:
    key = env.get("KIMI_API_KEY") or env.get("MOONSHOT_API_KEY")
    probe("moonshot", "https://api.moonshot.cn/v1/chat/completions",
          ["Authorization: Bearer " + key],
          '{"model":"moonshot-v1-8k","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
