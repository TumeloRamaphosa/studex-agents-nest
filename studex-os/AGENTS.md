# AGENTS.md — The Join Contract

Every agent that joins this repo reads THIS FILE FIRST.

---

## The Architecture

Each business is a **computer** — its own VM, its own OpenClaw "open floor" of Hermes agents, its own Ghost. They all report **UP** to this central OS. Tumelo Ramaphosa is the board.

```
Tumelo (The Board)
    ↑
Robusca (CEO — Chief of Staff)
    ↑
Charlie (Orchestrator)
    ↑     ↑     ↑     ↑
Naledi  Shopify  Hermes  [other agents]
(CMO)   (E-Comm)  (CTO)
```

---

## On Join — Step by Step

When any agent joins this repo:

1. **Read this file** and `/README.md`
2. **Identify your business** in `/businesses/`. If new, copy `/businesses/_TEMPLATE`
3. **Register** in `/control-plane/registry.yaml`
4. **Read your business brief:** `/businesses/<you>/AGENTS.md`
5. **Write everything to your VM's Ghost** (`/ghost`)
6. **Daily:** Compile a CO report → `/businesses/<you>/reports/daily/` and push

---

## Hard Rules (Non-Negotiable)

| Rule | Why |
|------|-----|
| **Secrets NEVER enter this repo** | Env vars or secrets manager only. Zero exceptions. |
| **Human gates on money, contracts, client-facing, legal** | Draft → Approve → Execute. Never skip. |
| **Stay in your lane** | Your business, your VM, your Ghost. Coordinate via Charlie. |
| **Record everything to Ghost** | If it's not written down, it didn't happen. |

---

## Directory Structure

```
studex-os/
├── AGENTS.md              ← You are here. Read first.
├── README.md              ← System overview
├── businesses/            ← One folder per business entity
│   ├── _TEMPLATE/         ← Copy this to add a new business
│   ├── studex-meat/       ← Studex Meat (E-Commerce)
│   ├── studex-wildlife/   ← Studex Wildlife (Coffee/Commodities)
│   └── studex-caviar/     ← Studex Caviar (Luxury imports)
├── control-plane/         ← Registry, shared protocols, OS config
│   ├── registry.yaml      ← Every agent registers here
│   └── protocols/         ← Shared comms standards
├── ghost/                 ← Studex OS Ghost (shared memory layer)
├── reports/               ← Cross-business reports for Tumelo
│   └── daily/             ← One file per day, named YYYY-MM-DD.md
└── vault/                 ← Obsidian vault — full knowledge base
```

---

## The Ghost Layer

The Ghost (`/ghost`) is the persistent memory and context layer that lives on each VM. It contains:

- **Context.md** — current state of the business, active deals, blockers
- **Knowledge/** — structured knowledge base, learnings, contacts
- **Daily/** — rolling daily log, like a journal
- **Reports/** — compiled CO (Chief of Staff) reports

Every agent writes to their VM's Ghost daily. Robusca compiles the board report.

---

## Communication Protocol

| Channel | Use |
|---------|-----|
| **Matrix (Orchestrix)** | Real-time voice + text. All agents in `StudexCommandCenter` |
| **Robusca (this system)** | Reasoning, strategy, Tumelo escalation |
| **Charlie (port 3001)** | Task dispatch, sub-agent coordination |
| **GitHub** | Code, docs, reports, push-to-deploy |

---

## Agent Registry

Every agent must register in `/control-plane/registry.yaml` with:
- `name` — agent identifier
- `role` — CMO, CTO, E-Commerce, etc.
- `business` — which entity they serve
- `vm` — their VM address
- `status` — `active` | `standby` | `offline`
- `last_seen` — ISO timestamp

---

## CO Report Format

Daily Chief of Staff report (one per business, compiled by Robusca):

```markdown
# 📋 CO Report — [Business Name]
**Date:** YYYY-MM-DD | **Agent:** [Name] | **Status:** 🟢/🟡/🔴

## Highlights
- [What happened today]

## Blockers
- [What is stuck, who owns it]

## Tomorrow
- [Priority actions for next day]

## Metrics
- [Key numbers: orders, revenue, leads, engagement]
```

---

_This file is the law. Read it. Obey it. Write everything down._
_Last updated: 2026-06-28 — Studex OS v1_