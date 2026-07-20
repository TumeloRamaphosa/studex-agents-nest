# studex-cto-playbook

> 📋 **CTO Playbook & Technical Documentation** — The engineering operating manual for the entire Studex Group.

## Overview

This repository is the single source of truth for all technical decisions, development standards, architecture documentation, and operational protocols across the Studex Group tech stack.

It is maintained by the **CTO Department** and covers:

- 🏗️ **Architecture** — System design, data models, integration patterns
- 🤖 **AI Agents** — Agent definitions, SKILL.md files, orchestration patterns
- 📜 **Protocols** — Standard operating procedures for every automated workflow
- 🔧 **Dev Standards** — Code standards, PR etiquette, deployment rules
- 📊 **Tech Stack** — Tool selection rationale, when to use what
- 🚀 **Playbooks** — Step-by-step guides for complex multi-system operations

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDEX TECH STACK                        │
├──────────────────┬──────────────────────────────────────────┤
│  Brand Layer     │  Naledi (content AI)                    │
│                  │  WhatsApp Business / Meta Graph API      │
├──────────────────┼──────────────────────────────────────────┤
│  Store Layer     │  Shopify (studexmeat.com)                │
│                  │  Shopify Webhooks → studex-auto-meat     │
├──────────────────┼──────────────────────────────────────────┤
│  Data Layer      │  Supabase (production DB)                │
│                  │  Airtable (content calendar / ops)       │
│                  │  Affine (planning / whiteboarding)       │
├──────────────────┼──────────────────────────────────────────┤
│  Automation      │  N8n (workflow engine)                   │
│                  │  OpenClaw (agent runtime)                │
├──────────────────┼──────────────────────────────────────────┤
│  Infrastructure  │  Vercel (web hosting)                    │
│                  │  Google Drive (assets)                   │
│                  │  WhatsApp Business API (notifications)   │
├──────────────────┼──────────────────────────────────────────┤
│  Development     │  BMAD (multi-agent build framework)     │
│                  │  CodeRabbit (AI code review)             │
│                  │  Ollama (local GPU coding)               │
└──────────────────┴──────────────────────────────────────────┘
```

## Repository Map

| Repo | Purpose | Status |
|------|---------|--------|
| `studex-auto-meat` | Shopify auto-fulfilment agent | 🟡 In Dev |
| `studex-naledi-content` | AI social media content agent | 🟡 In Dev |
| `studex-app-warehouse` | Client app factory / template library | 🔴 Planning |
| `robusca-brain` | Core orchestration brain / OpenClaw skills | 🟢 Active |

## Tech Stack Decisions

### Data Layer: Supabase vs Airtable vs Affine

| Tool | Best For | NOT For |
|------|----------|---------|
| **Supabase** | Production data, orders, real-time, auth | Simple spreadsheets |
| **Airtable** | Content calendars, campaigns, non-tech team visibility | Large-scale data |
| **Affine** | Planning, whiteboarding, brainstorming | Production use |

### AI Layer

| Model | Use Case |
|-------|----------|
| **Current cloud model** | Light tasks: captions, summaries, quick answers |
| **Ollama (Tailscale)** | Heavy tasks: full app builds, complex architecture (GPU-accelerated) |
| **Claude Code / Codex** | Agentic coding tasks |
| **CodeRabbit** | Automated PR code review |

### Notification Stack

| Channel | Tool | Status |
|---------|------|--------|
| WhatsApp Business | WhatsApp Business API | 🟢 Active |
| SMS | Termii / ClickSend | 🟡 Configured |
| Email | Resend / SendGrid | 🟡 Configured |
| Push | OneSignal | 🟡 Planned |

## BMAD Workflow

BMAD = Build More Architect Dreams — AI multi-agent framework used for all app development.

```
1. Brief → PM agent creates Product Requirements Doc
2. Architect designs system architecture + ERD
3. Dev tasks broken into sprint tickets
4. Developer agents implement with code review
5. Test Architect writes & runs test strategy
6. Deploy
```

Install BMAD:
```bash
npx bmad-method install --directory /project --modules bmm --tools claude-code --yes
```

## Protocols

| Protocol | Description |
|----------|-------------|
| Fulfilment SOP | Auto-fulfilment decision tree |
| Content Approval | Naledi → Manager → Schedule pipeline |
| Incident Response | What to do when automation fails |
| Client App Delivery | Warehouse SLA and quality gates |
| Agent Handoff | How agents pass context to each other |

## Directory Structure

```
studex-cto-playbook/
├── architecture/
│   ├── system-overview.md       # High-level system diagram + description
│   ├── data-models.md           # ERD and data model docs
│   └── integration-patterns.md  # How systems talk to each other
├── agents/
│   └── [agent-name]/
│       └── SKILL.md             # Agent skill definition
├── protocols/
│   ├── fulfilment-sop.md
│   ├── content-approval.md
│   ├── incident-response.md
│   └── agent-handoff.md
├── standards/
│   ├── code-standards.md        # Linting, formatting, commit messages
│   ├── pr-etiquette.md          # PR review process
│   └── deployment-checklist.md  # Pre-deploy verification
├── integrations/
│   ├── shopify.md               # Shopify API guide
│   ├── supabase.md              # Supabase setup guide
│   ├── whatsapp-business.md     # WhatsApp Business API setup
│   ├── n8n.md                   # N8n workflow setup
│   └── meta-graph-api.md        # Facebook/Instagram Graph API
├── playbooks/
│   ├── new-client-app.md        # Step-by-step new app delivery
│   ├── new-campaign.md           # Content campaign SOP
│   └── local-dev-setup.md       # Setting up local dev environment
├── decisions/
│   └── ADR-001-why-supabase.md  # Architecture Decision Records
├── configs/
│   ├── .env.example             # Master env var template
│   └── deployment-approval.md  # Deployment gates
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## License

All documentation and code in this repository is MIT licensed.

---

_Maintained by the **Studex CTO Department** — Tumelo Ramaphosa, CTO._
