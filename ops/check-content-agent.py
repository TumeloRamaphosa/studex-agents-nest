#!/usr/bin/env python3
"""Raise the last too-tight timeout, probe the LLM providers the content agent
depends on, and check the product/price source it would publish."""
import json, subprocess, os, re, sys

# 🔑 The response travels on STDOUT, not through a file. A file that a
# failed curl leaves untouched made a dead provider print the PREVIOUS
# provider's answer - see ops/http_probe.py for the proof and the fix.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http_probe import probe_json, format_line

print("=== 1. raise CEO Standup 9:00 timeout (ran green at 150.9s vs a 180s cap) ===")
r = subprocess.run(["openclaw", "cron", "edit", "ceo-standup-0900",
                    "--timeout-seconds", "300", "--channel", "discord",
                    "--to", "channel:1538825048465481728"],
                   cwd="/workspace", capture_output=True, timeout=240)
print("  rc=", r.returncode)
# find its real id
jobs = json.load(open("/root/.openclaw/cron/jobs.json"))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
for b in jobs:
    if "9:00 AM SAST" in b.get("name", ""):
        print("  %s timeout=%s mode=%s channel=%s" % (
            b["name"], b.get("payload", {}).get("timeoutSeconds"),
            (b.get("delivery") or {}).get("mode"),
            (b.get("delivery") or {}).get("channel")))

print("=== 2. LLM providers used by the content agent ===")
env = {}
for line in open("/workspace/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

def probe(name, url, headers, body):
    res = probe_json(name, url, headers, body)
    print(format_line(res))
    return res

if "MOONSHOT_API_KEY" in env:
    probe("moonshot", "https://api.moonshot.cn/v1/chat/completions",
          ["Authorization: Bearer " + env["MOONSHOT_API_KEY"]],
          '{"model":"moonshot-v1-8k","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
else:
    print("  moonshot    NO KEY IN .env")

if "OPENAI_API_KEY" in env:
    probe("openai", "https://api.openai.com/v1/chat/completions",
          ["Authorization: Bearer " + env["OPENAI_API_KEY"]],
          '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
else:
    print("  openai      NO KEY IN .env")

if "DASHSCOPE_API_KEY" in env:
    probe("dashscope", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
          ["Authorization: Bearer " + env["DASHSCOPE_API_KEY"]],
          '{"model":"qwen-plus","messages":[{"role":"user","content":"hi"}],"max_tokens":5}')
else:
    print("  dashscope   NO KEY IN .env")

print("=== 3. what product/price would the content agent publish? ===")
p = "/workspace/studex-content-automation/scripts/daily-content-agent.js"
src = open(p).read()
for m in re.finditer(r".{0,90}(Classic Beef Biltong|R320|biltong|BILTONG).{0,90}", src):
    print("  |", m.group(0).strip().replace("\n", " ")[:180])
