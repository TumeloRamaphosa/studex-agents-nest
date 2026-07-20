# StudEx Agentic OS — Architecture Blueprint
**Status:** Draft v1 — 2026-07-13 | Author: Amara

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                 COMMAND CENTER (Cowork)               │
│  Cron Jobs | Strategy | Human-in-the-Loop Approval    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              CLICKCLACK (Self-Hosted Chat)            │
│  Channels: #general #content #devops #meat #strategy │
│  Bot Tokens: Robusca, Naledi, Auto-Meat, Hermes      │
│  Bridge: ← → Slack Workspace                         │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
│  VAPI Voice  │ │ RAG/Memory│ │  Obsidian  │
│  TTS + STT   │ │ ChromaDB  │ │  2nd Brain │
│  Squads      │ │ LlamaIndex│ │  Vault     │
│  Meetings    │ │ Ollama    │ │  Wiki      │
└──────────────┘ └───────────┘ └────────────┘
```

---

## AGENT DEFINITIONS

### 1. ROBUSCA — Chief of Staff / Orchestrator
- ROLE: Orchestrator, strategist, morning briefings, meeting participant
- VOICE: Professional, strategic, concise. South African English
- CLICKCLACK: #general, #strategy, #content
- VAPI: "I am Robusca, Chief of Staff at StudEx. I coordinate our agent fleet."
- CRON: 7am news scan, 8am brief, 10pm analysis

### 2. NALEDI — CMO / Content Lead
- ROLE: Content creation, social media, competitor analysis, brand voice
- VOICE: Creative, trend-aware, energetic
- CLICKCLACK: #content, #general
- VAPI: "I am Naledi, CMO at StudEx."
- CRON: Content review queue, competitor scan 2x daily

### 3. AUTO-MEAT — E-Commerce / Shopify Agent
- ROLE: Order fulfillment, inventory, customer comms, Shopify admin
- VOICE: Operational, efficient, detail-oriented
- CLICKCLACK: #meat-store, #general
- CRON: Hourly inventory check, 8pm daily report

### 4. HERMES — CTO / DevOps
- ROLE: Infrastructure, deployments, CI/CD, VM management, security
- VOICE: Technical, precise, security-conscious
- CLICKCLACK: #devops, #general
- CRON: Deployment checks, PR reviews, VM health

---

## VOICE STACK
- PRIMARY: VAPI (vapi.ai) — works on VM + website + phone
- BACKUP: OpenJarvis (MacBook only)
- Agent-Reach: 13-platform internet access for agents

---

## BRANDS
- **StudEx Meat** — e-commerce, biltong, biltong products
- **B.C.C — Biltong · Café · Caviar** — NEW brand (details TBD)

---

## BLOCKERS (as of 2026-07-13)
1. Orgo VM — "desktop not found" — VM ID changed, needs recovery
2. VAPI — no key yet
3. Shopify — no token
4. AgentMail — charlie@agent.studexmeat.com inbox missing
5. Blotato — 0 accounts connected
