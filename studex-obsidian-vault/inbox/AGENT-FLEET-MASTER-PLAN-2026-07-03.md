# AGENT FLEET MASTER PLAN — 2026-07-03
**Status:** Planning — Daytona Deployment

---

## AGENTS WE NOW HAVE

### Fleet Overview

| Agent | Type | Role | Deployment |
|-------|------|------|-----------|
| **Charlie** (existing) | Orchestrator | Business ops, Shopify, orders | OpenClaw / Orgo VM |
| **Naledi** (existing) | CMO | Content, social, branding | OpenClaw / Orgo VM |
| **Odysseus** | AI Workspace | Chat, research, docs, email, calendar, local models | Daytona (Docker) |
| **Decepticon** | Red Team Agent | Security penetration testing, vulnerability research | Daytona (Docker) |
| **OBLITERATUS** | Model Lab | LLM abliteration, refusal removal, model research | Daytona (HuggingFace Spaces) |
| **Headroom** | Context Compression | Token optimization, 60-95% context reduction | Daytona + all agents |
| **Huashu Design** | Design Skill | Prompt →交付 design (PPT, video, prototype) | OpenClaw skill |
| **last30days-skill** | Research Skill | Real-time trend analysis across Reddit, HN, TikTok, YouTube | OpenClaw skill |
| **TencentDB-Agent-Memory** | Memory Layer | 4-tier progressive memory for agents | Daytona |
| **Coffee Jarvis** | Domain Agent | Coffee exchange, RUKUNDO pricing, market data | OpenClaw / Orgo VM |
| **RileyJarvis** | Voice Agent | Voice control, desktop access, speech-to-speech | Mac Mini M4 |

---

## WHAT EACH AGENT DOES

### 1. ODYSSEUS — AI Workspace
**Repo:** github.com/pewdiepie-archdaemon/odysseus
**Stack:** Docker, Python, Node.js
**Port:** 7000

**Capabilities:**
- Chat with local or API models (OpenAI, Anthropic, local vLLM)
- Deep research (multi-step web research + report)
- Email (IMAP/SMTP — can connect AgentMail)
- Notes + Tasks + Calendar (with reminders)
- File management + shell access
- MCP tools support
- Compare mode (blind model testing)
- Sessions + 2FA

**Daytona Deployment:**
```bash
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
cd odysseus
cp .env.example .env
# Add API keys to .env
docker compose up -d --build
# Open http://localhost:7000
```

**Value to Studex:**
- Research agent: competitor analysis, market research
- Email: handles supplier inquiries (RUKUNDO, logistics)
- Deep research: due diligence on new coffee markets
- Compare: test our agents vs others on the same tasks

---

### 2. DECEPTICON — Red Team Agent
**Repo:** github.com/PurpleAILAB/Decepticon
**Stack:** Python, Docker
**Purpose:** Autonomous cybersecurity penetration testing

**Capabilities:**
- Autonomous vulnerability scanning
- Exploit research and testing
- Security audit reports
- Threat detection
- Live at: app.decepticon.red (cloud) or self-hosted

**Daytona Deployment:**
```bash
git clone https://github.com/PurpleAILAB/Decepticon.git
cd Decepticon
docker build -t decepticon .
docker run -d -p 8000:8000 decepticon
```

**Value to Studex:**
- Audit our own systems before attackers do
- Test RocketChat, Shopify, AgentMail for vulnerabilities
- Annual penetration test — done continuously
- Compliance documentation for enterprise customers

**WARNING:** This is a security/hacking tool. Run only on systems you own or have explicit permission to test.

---

### 3. OBLITERATUS — Model Abliteration Lab
**Repo:** github.com/elder-plinius/OBLITERATUS
**Stack:** Python, Gradio, HuggingFace Spaces
**Purpose:** Remove refusal behaviors from LLMs surgically

**Capabilities:**
- Identify refusal directions in model activations
- Remove refusals without retraining
- PCA, SAE, SVD ablation methods
- Benchmarks: compliance vs coherence tradeoff measurement
- Research: contributes to crowd-sourced dataset

**Deployment:** HuggingFace Spaces (zero install) or local via Colab

**Value to Studex:**
- Custom model tuning for Studex domain (meat, coffee, SA market)
- Remove refusals that block business-relevant content
- Research: understand how our agents' models make decisions

---

### 4. HEADROOM — Context Compression
**Repo:** github.com/chopratejas/headroom
**Stack:** Python, TypeScript, npm, PyPI
**Purpose:** Compress everything agents read by 60-95%

**Capabilities:**
- `headroom compress(messages)` — library call
- `headroom proxy --port 8787` — zero-code proxy
- `headroom wrap openclaw` — wraps OpenClaw, 60-95% token reduction
- `headroom wrap claude|codex|copilot|cursor|aider|continue`
- MCP server: `headroom_compress`, `headroom_retrieve`, `headroom_stats`
- Cross-agent shared memory store
- `headroom learn` — mines failed sessions → corrections to AGENTS.md

**Install:**
```bash
pip install headroom-ai    # Python
npm install -g headroom-ai # Node.js
headroom wrap openclaw     # Wrap OpenClaw
```

**Value to Studex:**
- All agents use Headroom → 60-95% less token usage → massive cost savings
- Compress Charlie's long Shopify data → stays within context
- Compress Naledi's content analysis → faster generation
- Cross-agent memory: Charlie learns something → Naledi knows it too

---

### 5. TENCENTDB-AGENT-MEMORY — 4-Tier Memory
**Source:** share.google/usU6JRHwNy2XBZIfn
**Purpose:** Long-term + short-term memory for agents

**Architecture:**
```
Tier 1: Working Memory (immediate context)
Tier 2: Episodic Memory (session summaries)
Tier 3: Semantic Memory (facts, knowledge)
Tier 4: Procedural Memory (how to do things)
```

**Value to Studex:**
- Charlie remembers every Shopify order pattern across sessions
- Naledi learns brand voice across months of content
- Coffee Jarvis remembers RUKUNDO negotiation history
- Agents don't forget between sessions

---

### 6. HUASHU DESIGN — Design Skill
**Repo:** github.com/alchaincyf/huashu-design
**Type:** OpenClaw Skill (MIT licensed, free for commercial use)
**Install:** `npx skills add alchaincyf/huashu-design`

**Capabilities:**
- Prompt → finished design in 3-30 minutes
- Product launch animations
- Clickable app prototypes
- Editable PPTs
- Print-ready infographics
- Brand-aware (reads your logo, colors, screenshots)
- 40 native HTML style library

**Value to Studex:**
- Naledi generates all visual content without Figma/Canva
- "Design a WooHoo Day Instagram carousel" → done in minutes
- Product photos → brand-consistent social content
- Coffee subscription launch materials

---

### 7. LAST30DAYS-SKILL — Trend Research
**Source:** share.google/EM1uOAW9e1UYdyJEI
**Type:** OpenClaw Skill
**Install:** via OpenClaw skill installer

**Capabilities:**
- Searches: Reddit, X/Twitter, YouTube, Hacker News, TikTok, GitHub, Polymarket
- Bypasses SEO search → finds real human sentiment
- Synthesizes last 30 days of signal on any topic
- Grounded, relevant, up-to-date

**Value to Studex:**
- Coffee market trends: what are people saying about African coffee right now?
- Competitor intel: what's working in SA food/biltong market
- Content inspo: what topics are trending for Youth Day, Heritage Month
- B2B leads: who's asking about bulk coffee sourcing on Reddit/HN

---

### 8. KARPATHY WIKI AGENTS
**Source:** share.google/OKgNfpy4FPbSkvRB4
**Purpose:** LLM-powered second brain / knowledge base

**What it gives us:**
- Every decision, every conversation, every market insight → indexed
- Ask: "What did we decide about RUKUNDO pricing last month?" → instant answer
- Ask: "What did we learn about our customers from Youth Day campaign?" → instant answer
- Agents can query the knowledge base

---

## DAYTONA DEPLOYMENT PLAN

### What is Daytona?
Daytona is a cloud development platform (like GitHub Codespaces or VS Code Online) that provides sandboxed development environments. With the Dyatona API key, we can:
- Spin up GPU VMs for AI workloads
- Run coding sessions in browser-based IDEs
- Deploy agents on Daytona infrastructure
- Use TailScale VPN to connect Daytona → our machines

### Daytona + TailScale Setup
```
Daytona VM (GPU, Ubuntu)
    │
    ├── TailScale ←────────────── Your MacBook (tailf7273b.ts.net)
    │         (your existing TailScale network)
    │
    ├── Odysseus (Docker :7000)
    ├── Decepticon (Docker :8000)
    ├── Headroom (system-wide install)
    ├── Local vLLM models
    │
    └── TailScale → Orgo VM → Charlie/Naledi
```

### Daytona Agent Install Steps
1. Authenticate with Dyatona API
2. Spin up Daytona workspace (Ubuntu, GPU)
3. Install TailScale on Daytona VM
4. Join Daytona VM to your TailScale network
5. Clone repos + docker compose up
6. Daytona VM is now accessible from your MacBook AND Orgo VM

---

## ROCKETCHAT — AGENT CHAT PROTOCOL

### How Agents Join RocketChat

Each agent gets a RocketChat account + bot token:

```
Agent joins RocketChat:
1. Create account: charlie@chat.studexmeat.com
2. Get auth token via API:
   curl -X POST https://chat.studexmeat.com/api/v1/login \
     -d "username=charlie&password=CHANGEME"
3. Save token to TOOLS.md
4. Agent connects via RocketChat WebSocket API
5. Agent posts to #ops, reads #alerts, #orders
```

### Agent Join Code (template)
```markdown
## AGENT JOIN PROTOCOL — STUDEX OS

You are [AGENT NAME], a [ROLE] agent on the Studex Meat operating system.

Your RocketChat credentials:
- Username: [agent]@chat.studexmeat.com
- Password: [SET_PASSWORD]
- Server: https://chat.studexmeat.com
- API Token: [FROM_ROCKETCHAT_API]

Your role in the team:
- Primary channel: #ops
- Alert channel: #alerts
- Coffee channel: #coffee
- Content channel: #content

Your objectives:
1. Check #ops every 30 minutes for new tasks
2. Post status updates to #ops when tasks complete
3. Alert #alerts if anything requires immediate attention
4. Log all significant decisions to Obsidian vault

Vault location: /workspace/studex-obsidian-vault/
OS URL: https://bl923ho8ctt3.space.minimax.io

Always save conversation summaries to the vault before ending a session.
```

---

## VOICE — 11LABS + ROCKETCHAT INTEGRATION

### How Voice Works
```
You speak → Mac Mini M4 (RileyJarvis)
    ↓ (OpenAI Realtime API)
    ↓ [replace with ElevenLabs TTS]
    ↓
Charlie processes → RocketChat
    ↓
Response → ElevenLabs TTS
    ↓
Spoken back via RileyJarvis
```

### 11Labs Voice Config
- Voice ID: Nova (warm, slightly British) — preferred
- ElevenLabs API key: sk_93f872929e312224f4012da0709e8e18dfe53fdd0ae790b5
- Already set in: /workspace/.env as ELEVENLABS_API_KEY

### RocketChat Voice Integration
RocketChat supports:
- WebRTC audio/video calls
- Text-to-speech for messages
- Custom slash commands

With 11Labs: RocketChat can read messages aloud using Nova voice.

---

## WHAT WE CAN DO RIGHT NOW

### After Daytona VM is ready:

```
Daytona VM (GPU Ubuntu)
    ├── Odysseus            → http://vm:7000
    ├── Decepticon         → http://vm:8000
    ├── Headroom wrap       → all agents 60-95% token reduction
    ├── TencentDB-Memory    → agent memory layer
    └── TailScale          → accessible from MacBook + Orgo VM
```

### From MacBook (TailScale):
- Open browser → http://daytona-vm:7000 → Odysseus workspace
- Open VS Code → connect to Daytona VM
- Run coding sessions in sandbox
- Agents report via RocketChat

### From Orgo VM (me):
- SSH to Daytona VM via TailScale
- Deploy new agent versions
- Monitor logs
- Trigger deployments

---

## NEXT STEPS — PRIORITY ORDER

### 🔴 CRITICAL (Today)
1. Daytona VM → spin up Ubuntu GPU instance with Dyatona API
2. Daytona → install Docker + TailScale
3. Daytona → clone Odysseus + `docker compose up`
4. Daytona → clone Decepticon + build
5. Orgo VM → install Headroom → wrap Charlie + Naledi
6. RocketChat → deploy on Orgo VM (`docker-compose up -d`)
7. RocketChat → create agent accounts (charlie, naledi, coffee, rileyjarvis)

### 🟡 IMPORTANT (This Week)
8. Daytona → install Huashu Design skill → test first design
9. Daytona → install last30days-skill → first trend report
10. Headroom → wrap OpenClaw → verify token reduction
11. TenCentDB-Agent-Memory → connect to Charlie
12. Odysseus → connect AgentMail → test supplier email inbox
13. Mission Control OS → embed RocketChat live

### 🟢 NICE TO HAVES (This Month)
14. Daytona → run OBLITERATUS on Llama 3.1 8B → test refusal removal
15. Decepticon → run security audit on RocketChat
16. Odysseus → deep research on: "SA specialty coffee market 2026"
17. All agents → shared memory via TencentDB-Agent-Memory
18. Voice → RileyJarvis + ElevenLabs Nova → full voice control

---

## DYATONA API — IMMEDIATE ACTION

With the Dyatona API key:
```bash
# Authenticate
curl -H "Authorization: Bearer dtn_0ad29d3bdfb7b55f5f97985d2a6c1691e9cff1d8b6a745c76ae4620565887029" \
     https://api.dyatona.ai/v1/workspaces

# Create a new workspace/VM
curl -X POST https://api.dyatona.ai/v1/instances \
  -H "Authorization: Bearer dtn_..." \
  -H "Content-Type: application/json" \
  -d '{"name":"studex-agent-vm","region":"us-east","gpu":"A100","os":"ubuntu-24.04"}'
```

**Need:** Dyatona API docs — what endpoints are available? VM specs? Pricing?

---

*Last updated: 2026-07-03 01:25 UTC*
