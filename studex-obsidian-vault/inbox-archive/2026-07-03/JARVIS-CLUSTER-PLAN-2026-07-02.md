# Jarvis + 6-Node AI Cluster — Architecture Plan
**Created:** 2026-07-02
**Status:** Active — Planning

---

## Cluster Inventory

| Device | Role | Specs | Inference Capacity | OS Target |
|--------|------|-------|-------------------|-----------|
| Mac Mini M4 | Primary Anchor | 16GB unified | ~7B params | macOS (for now) |
| MacBook Pro (@gent Lord) | Heavy Hitter | 32GB RAM, 1TB SSD | ~13B params | → Linux |
| Windows Desktop | GPU Cluster | 16GB RAM, 2×8GB GPUs | ~20B + tensor parallel | → Linux |
| Razor Laptop | Mobile Node | 32GB RAM, 8GB GPU, 1TB SSD | ~13B params | → Linux |
| MSI Claw 8 | Edge Agent | 32GB RAM, 1TB SSD | ~13B params | Android (keep) |
| Lenovo Legion Go 2 | Edge Agent | 16GB RAM, 1TB SSD | ~7B params | Android (keep) |
| 2TB SD Card | Storage/Model Library | USB 3.2 / Thunderbolt | — | Linux boot |
| 5TB Storage Drive | NAS / Model Store | USB 3.2 / Thunderbolt | — | Linux + network share |

---

## Phase 1 — Migration to Linux

### Windows Desktop → Linux (HEAVY LIFT)
**Target OS:** Ubuntu Server 24.04 LTS + CUDA drivers
**Why:** 2×8GB GPUs — your most powerful node. vLLM + tensor parallel on this machine alone can serve ~20B models with full throughput.

**Install:**
```bash
# Create bootable USB with Ubuntu Server 22.04 LTS
# Install CUDA 12.4 + cuDNN 9
# Mount 5TB drive as /models (model library)
# Mount 2TB SD as /data (datasets, cache)

# Key packages
sudo apt install nvidia-driver-545 cuda-12-4 python3.11 python3-pip
pip install vllm ray[default] fastapi uvicorn
```

### MacBook Pro → Linux
**Options (in order of ease):**
1. **External Linux boot** — 2TB SD card as boot drive (no macOS change, plug in when needed)
2. **Dual boot** — Install Ubuntu alongside macOS (Mac Mini M4 can do this)
3. **VM** — Parallels/UTM on macOS for Linux dev work

**Recommended:** Option 1 for MacBook Pro (portable, no risk to macOS). Option 2 for Mac Mini M4.

**Why Linux on MacBook Pro:** 32GB RAM = serious inference node. Can run ~13B models in 4-bit quantization at full speed.

### Mac Mini M4 → Keep macOS for now
**Reason:** RileyJarvis (Electron + OpenAI Realtime API) runs natively on macOS. This is your voice control node. Keep macOS, install Linux on the 2TB SD as an alternative boot.

### Android Devices → Keep as-is
**MSI Claw + Lenovo Legion Go** — already running LiteRT-LM with Qwen2.5-1.5B, Gemma3-1B, DeepSeek-R1-Distill. These are your **edge inference nodes** — perfect for offline/low-latency tasks.

---

## Phase 2 — Jarvis + OS Integration

### What RileyJarvis Does
- **Voice:** OpenAI Realtime API → speech-to-speech conversation
- **Face:** Animated companion face (listening, thinking, speaking, working states)
- **Artifacts:** Markdown, notes, diagrams, generated images
- **Computer Use:** Opens apps, clicks, types, takes screenshots (macOS only)
- **Local Data:** Stores notes and records in `data/` directory

### How to Integrate Jarvis into Studex OS
```
RileyJarvis (Mac Mini M4 — voice node)
    ↓ OpenAI Realtime API (or → local LLM)
Studex OS (War Room / Obsidian vault)
    ↓ wake word / trigger phrase
Charlie / Naledi / Coffee Jarvis agents
    ↓ action
Shopify / AgentMail / Discord / RUKUNDO prices
```

**Jarvis becomes the VOICE FRONTEND for all agents.**
Instead of typing to Charlie, you speak to Jarvis: *"Hey Jarvis, check if any new Shopify orders came in."*

### Jarvis → Private AI API Bridge
RileyJarvis currently uses OpenAI's Realtime API. We replace the backend with your cluster:
```
RileyJarvis → local vLLM endpoint (your cluster)
            ↓
        Your MacBook Pro or Windows Desktop (13-20B model)
            ↓
        Response returned to Jarvis → spoken back to you
```
**Result:** Fully private voice AI, no OpenAI dependency, unlimited use.

---

## Phase 3 — vLLM Cluster Architecture

### On Each Linux Node
```bash
# Install vLLM
pip install vllm

# Run as server
vllm serve Qwen2.5-7B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype half \
  --max-model-len 8192
```

### Cluster Coordination (Ray)
```python
# coordinator.py
import ray
import vllm

@ray.remote(num_gpus=2)  # Windows Desktop — 2 GPUs
def heavy_inference(prompt):
    # routes to Windows Desktop node
    return result

@ray.remote(num_gpus=1)  # MacBook Pro
def medium_inference(prompt):
    # routes to MacBook Pro
    return result
```

### Load Balancing
| Model Size | Node | Reason |
|------------|------|--------|
| 1.5B–3B (fast, cheap) | MSI Claw / Legion Go | Edge, low latency |
| 7B | Mac Mini M4 | Light tasks, voice |
| 13B | MacBook Pro / Razor Laptop | Daily agent work |
| 20B+ | Windows Desktop (2×GPU) | Complex reasoning, long context |

---

## Phase 4 — Private AI API Business

### API Endpoints (your cluster = private AI API)
```
POST /v1/chat/completions  → Charlie, Naledi, Coffee Jarvis
POST /v1/completions       → Code generation
POST /v1/embeddings        → RAG / search
```

### Who Pays for Private AI API
1. **Other African startups** — can't afford OpenAI prices, need private deployment
2. **Healthcare / Legal** — data privacy requirements, need on-premise
3. **Enterprise** — want AI without sending data to US companies

### Revenue Model
| Service | Price Point |
|---------|------------|
| Self-hosted API (up to 1M tokens/mo) | R5,000/month |
| Unlimited API access | R15,000/month |
| Custom fine-tuned model | R50,000 setup + R8,000/mo |
| On-premise installation | R200,000 once-off |

---

## Phase 5 — Your Agents on Local Models

### Current vs. Local

| Agent | Currently | On Local Cluster |
|-------|-----------|-----------------|
| Charlie (Orchestrator) | OpenAI/Claude API | MacBook Pro (13B) |
| Naledi (CMO) | OpenAI/Claude API | MacBook Pro (13B) |
| Coffee Jarvis | OpenAI API | Windows Desktop (20B) |
| RileyJarvis (Voice) | OpenAI Realtime API | Mac Mini M4 → local |

### How It Works
```
You: "Jarvis, check new orders"
Jarvis (Mac Mini, voice) → receives audio
    → transcribed locally
    → routed to Charlie (Windows Desktop, 20B)
    → Charlie checks Shopify API
    → Response sent back to Jarvis
    → spoken aloud to you
```

---

## Phase 6 — Network & Storage Architecture

### Storage Layout
```
2TB SD Card (Linux boot drive)
├── /models/          ← 7B, 13B model files
├── /data/           ← datasets, cache
└── /logs/           ← cluster logs

5TB Storage Drive (Network Mount)
├── /models-library/ ← 20B+ model files (too large for SD)
├── /backups/        ← vault, Shopify data, configs
└── /shared/         ← accessible to all nodes
```

### Network (TailScale)
```
Mac Mini M4 (voice node)     → tailnet: macmini.tailXXX.ts.net
MacBook Pro (agent node)    → tailnet: macbookpro.tailXXX.ts.net
Windows Desktop (GPU node)  → tailnet: desktop.tailXXX.ts.net
Razor Laptop (agent node)  → tailnet: razor.tailXXX.ts.net
MSI Claw (edge)            → tailnet: msiclaw.tailXXX.ts.net
Legion Go (edge)           → tailnet: legiongo.tailXXX.ts.net
Orgo VM (brain)            → tailnet: orgo.tailXXX.ts.net (already running)
```

---

## Immediate Action Items

### This Week
- [ ] Install Ubuntu on Windows Desktop (GPU node) — use 5TB as model storage
- [ ] Flash 2TB SD with Ubuntu, test boot on MacBook Pro
- [ ] Set up vLLM on Windows Desktop → serve first local model
- [ ] Configure TailScale on all Linux nodes
- [ ] Mount 5TB as network share (`192.168.x.x:/models`)

### Next Week
- [ ] Replace OpenAI backend in RileyJarvis with local vLLM endpoint
- [ ] Test Charlie on MacBook Pro (13B model)
- [ ] Set up Ray cluster across 3 nodes (Windows + MacBook + Orgo)
- [ ] Connect Coffee Jarvis to RUKUNDO price feed

### Month 2
- [ ] Soft launch private AI API to 3 beta customers
- [ ] Build `/jarvis` page in War Room — live voice agent dashboard
- [ ] RileyJarvis voice running on Mac Mini → controls all agents

---

## Model Recommendations by Node

| Node | Recommended Models | Quantization | Context |
|------|------------------|--------------|---------|
| MSI Claw / Legion Go | Qwen2.5-1.5B-Instruct | F16 | 8K |
| Mac Mini M4 | Gemma-3-4B-IT | 4-bit | 8K |
| MacBook Pro | Qwen2.5-14B-Instruct | AWQ | 8K |
| Razor Laptop | Qwen2.5-14B-Instruct | AWQ | 8K |
| Windows Desktop | Qwen2.5-32B-Instruct | GPTQ | 16K |
| Orgo VM | Qwen2.5-7B-Instruct | F16 | 8K |

**Total model storage needed:** ~80GB for full model suite
**5TB drive:** More than enough for 20+ models

---

## Stack Summary

```
Voice Layer:     RileyJarvis (Electron) → local vLLM
Agent Layer:     Charlie + Naledi + Coffee Jarvis (OpenClaw)
Model Layer:     vLLM + Ray (distributed)
Inference Nodes: Windows Desktop (GPU), MacBook Pro, Mac Mini
Edge Nodes:      MSI Claw, Legion Go (Android/LiteRT)
Storage:         2TB SD (boot) + 5TB (models)
Network:         TailScale VPN
OS:              Linux (Ubuntu) on all except Mac Mini (macOS)
```

---

*Last updated: 2026-07-02 21:45 UTC*
