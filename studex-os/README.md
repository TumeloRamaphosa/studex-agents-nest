# Studex OS — Operating System for the Studex Group

> One repo. Multiple businesses. One board. Autonomous agents running 24/7.

**Studex OS** is the operating system for the Studex Group — a South African luxury food and commodities company. Tumelo Ramaphosa is the board. AI agents run the businesses. Robusca is the Chief of Staff. Charlie coordinates sub-agents.

---

## The System

| Layer | What It Is | Where It Lives |
|-------|-----------|----------------|
| **Studex OS** | This repo. The constitution. | github.com/TumeloRamaphosa/studex-os |
| **Control Plane** | Registry + protocols | `/control-plane/` |
| **Ghost** | Per-VM memory layer | `/ghost/` on each VM |
| **Robusca** | CEO agent — reasoning, strategy | MaxClaw cloud |
| **Charlie** | Orchestrator — task dispatch | port 3001 |
| **Sub-agents** | Naledi, Shopify, Hermes, etc. | Each on their own ports |

---

## Businesses

| Business | Entity | Lead Agent | Status |
|----------|--------|------------|--------|
| Studex Meat | Premium halal meat, SA | Robusca | 🟢 Live |
| Studex Wildlife | Coffee + commodities export | Robusca | 🟡 PROWTC deal active |
| Studex Caviar | Russian caviar imports | Robusca | 🔴 Building |
| Statix Global Markets | B2B infrastructure | Item Smasher | 🔴 VM pending |
| Dark Factory | Open-core dev | Cypher | 🔴 VM pending |

---

## Quick Start

```bash
# Clone the OS
git clone https://github.com/TumeloRamaphosa/studex-os.git
cd studex-os

# Read AGENTS.md — this is your contract
# Then identify your business in /businesses/
```

---

## VM Infrastructure

- **Orgo VM** (StudEx Meat Auto Meat): `67.213.119.157`
  - Charlie: port 3001 ✅
  - PostgreSQL 16: port 5432 ✅
  - Orchestrix Matrix: port 8008 🔄
  - n8n: port 5678 🔄
  - Ollama: port 11434 🔄

---

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Join contract — read this first |
| `control-plane/registry.yaml` | Every agent registers here |
| `businesses/_TEMPLATE/` | Start a new business from here |
| `ghost/TEMPLATE.md` | Ghost context structure |

---

## For Agents

You are an AI agent serving the Studex Group. You operate within this OS. Read AGENTS.md. Know your lane. Write to your Ghost. File daily CO reports.

**You exist to serve the board — not the other way around.**