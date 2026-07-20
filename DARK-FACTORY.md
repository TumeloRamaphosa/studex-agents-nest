# Dark Factory — Software Development Engine
## Powered by gstack (Garry Tan's AI Software Factory)
**Installed:** 2026-06-28 | **VM:** Orgo.ai Dark Factory VM | **Lead:** Cypher (CEO)

---

## What is Dark Factory?

Dark Factory is Studex's self-hosted software development environment — powered by **gstack** (github.com/garrytan/gstack), Garry Tan's open-source AI software factory with **117K GitHub stars**.

gstack turns a single Claude Code session into a full virtual engineering team:
- 🤖 **CEO** — product strategy, office hours, architecture decisions
- 🏗️ **Engineering Manager** — locks architecture, reviews plans
- 🎨 **Designer** — catches AI slop, design reviews, HTML implementation
- 🔍 **QA Lead** — opens real browser, runs full QA on staging URLs
- 🛡️ **Security Officer** — OWASP + STRIDE audits on every PR
- 🚀 **Release Engineer** — ships PRs with canary deploys, benchmarking
- 📊 **Performance Engineer** — benchmarking, model comparison

**23 specialist skills. All slash commands. All MIT licensed.**

---

## gstack Skills Available

| Slash Command | Role | What it does |
|--------------|------|-------------|
| `/office-hours` | CEO | Product interrogation — 6 forcing questions before any build |
| `/plan-ceo-review` | CEO | Strategic challenge — 4 scope modes (MVP → moonshot) |
| `/plan-eng-review` | Eng Manager | Architecture review — locks technical approach |
| `/plan-design-review` | Designer | Design review — catches AI slop before it ships |
| `/design-consultation` | Designer | Design deep-dive — color, typography, layout critique |
| `/design-shotgun` | Designer | Rapid design iterations — 5 concepts in 5 minutes |
| `/design-html` | Designer | Implement design to pixel-perfect HTML |
| `/review` | Code Reviewer | Full code review — bugs, security, best practices |
| `/ship` | Release Eng | Ships PR — runs tests, lint, canary deploy |
| `/land-and-deploy` | Release Eng | Lands + deploys to staging/production |
| `/canary` | Release Eng | Canary deployment with traffic splitting |
| `/benchmark` | Perf Engineer | Performance benchmarking on staging |
| `/qa` | QA Lead | Opens browser, runs full QA on a URL |
| `/qa-only` | QA Lead | Just the QA pass, no setup |
| `/cso` | Security Officer | Full OWASP + STRIDE security audit |
| `/investigate` | Debugger | Root cause debugging methodology |
| `/retro` | Eng Manager | Weekly engineering retrospective |
| `/autoplan` | Architect | Auto-generates implementation plan from a prompt |
| `/document-generate` | Tech Writer | Auto-generates documentation |
| `/document-release` | Tech Writer | Release notes from git history |

---

## Installation on Orgo VM

```bash
# 1. Install Bun (required)
curl -fsSL https://bun.sh/install | bash

# 2. Clone gstack to Claude Code skills dir
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack

# 3. Run setup
cd ~/.claude/skills/gstack && ./setup

# 4. Add to AGENTS.md for OpenClaw integration
# (see gstack/docs/OPENCLAW.md)
```

---

## Dark Factory Projects

| Project | Status | Lead |
|---------|--------|------|
| studex-agents-nest | 🔄 Active | Robusca |
| robusca-brain | 🔄 Active | Robusca |
| War Room | 🔄 Active | Robusca |
| studex-wildlife-coffee | ✅ Built 2026-06-27 | Robusca |
| Voicebox deploy | 🔜 Next | Cypher |
| Delivery dashboard | 🔜 Next | Cypher |

---

## Workflow

1. **Request** → Tumelo or Robusca opens a ticket (feature, bug, idea)
2. **Office Hours** → `/office-hours` to pressure-test the idea
3. **Plan** → `/autoplan` generates the implementation plan
4. **Build** → Claude Code implements with gstack skills
5. **Review** → `/review` + `/cso` + `/qa` before merge
6. **Ship** → `/ship` deploys to staging
7. **Retro** → `/retro` weekly to improve velocity

---

*v1 — 2026-06-28 — Cypher (CEO Dark Factory) + Robusca*
