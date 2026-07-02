# MEMORY.md - Long-Term Memory

## Model Usage Policy
- **MiniMax**: ~5% — routing/coordination only
- **Anthropic Claude Haiku**: ~70% — general tasks
- **Anthropic Claude Sonnet 4.5**: ~30% — complex tasks
- **Google Gemini**: Content generation + creative only
- **Perplexity**: Web research only
- **Ollama (local)**: All coding tasks exclusively

## APIs & Credentials

| Service | Status | Key/Notes |
|---------|--------|-----------|
| Google Gemini | ✅ | `AIzaSyDKo82xyTsBel0k0iIJS8UizWrOsJ4rb_c` |
| Perplexity | ⏳ | Not yet configured |
| Anthropic | ⏳ | Not yet configured |
| Ollama | ⏳ | Not yet configured |
| Discord (MiniMax Claw) | ✅ | Bot: Kilo StudEx, token in openclaw.json |
| Discord (MAxclaw Bot) | ✅ | Token: `MTQ4MDgzMzAzMjYzMzA1NzQwMQ...` |
| MiniMax | ✅ | Local proxy at 127.0.0.1:8766 |

## Platform Architecture

```
MAXCLAW (Robusca — this instance)
    ↓ GitHub push / Orgo API
ORGO.AI VM (StudEx Meat Auto Meat — VM ID: 946b3156-cab9-4187-a94b-056dfab35105)
    ├── War Room — running on port 5000
    ├── robusca-brain — /root/robusca/robusca-brain/ (synced)
    ├── claude-adhd-skills — /root/.claude/ (nudge, obsidian-vault, daily-journal)
    ├── Studex-Agents-Nest repo — /root/nest/ (latest from GitHub)
    └── Orgo API key: sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2
```

## Orgo VM Details
- **Access**: Orgo API — `https://www.orgo.ai/api/computers/{id}/bash`
- **Orgo Key**: `sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2`
- **VM ID**: `946b3156-cab9-4187-a94b-056dfab35105`
- **SSH**: `ssh root@67.213.119.157 -p <port>` (port in Orgo dashboard)
- **VNC**: https://www.orgo.ai/desktops/b454450e
- **War Room**: http://67.213.119.157:5000 — native (tmux, node dist/index.cjs)
  - **Start**: `tmux new-session -d -s war 'cd /root/nest/war-room && node dist/index.cjs > /tmp/war.log 2>&1'`
  - **Stack**: Express + React + Vite, better-sqlite3 (NOT PostgreSQL)
  - **Database**: `/root/nest/war-room/data/studex.db`
  - **Env**: `/root/nest/.env` (22 vars, written 2026-06-30)
- **GitHub sync**: /root/nest/ (SrudEx-Agents-Nest-Cloud-VM)

## gstack — Dark Factory Engine
- **URL:** github.com/garrytan/gstack — 117K stars, MIT license
- **Cloned:** /workspace/gstack/ (temporary — not pushed to GitHub, embedded repo issue)
- **Bun required:** Install on Orgo VM before gstack setup
- **Skills:** 23 slash commands — /office-hours, /plan-ceo-review, /review, /ship, /qa, /cso, /autoplan, etc.
- **Dark Factory spec:** /workspace/DARK-FACTORY.md
- **Next step:** Clone to Orgo VM + Bun install + ./setup

## GitHub Repos
| Repo | URL | Status |
|------|-----|--------|
| SrudEx-Agents-Nest-Cloud-VM | github.com/TumeloRamaphosa/SrudEx-Agents-Nest-Cloud-VM | ✅ Synced |
| robusca-brain | /root/robusca/robusca-brain/ | ✅ Synced |
| studex-obsidian-vault | /workspace/studex-obsidian-vault/ | ✅ Built |

## AgentMail
- Domain: send.studexmeat.com — PENDING DNS verification
- API: `am_us_24fcb06c6b1babba88c56d49b1a83fc33f1b8acf153acf3ef905136f335e7502`
- Cloudflare DNS: cfat_FucES954ZNssC1jUIFzGNWSpk7hSNhs8a39edIjY5b5866bf
- Pending records: MX, TXT (SPF), TXT (DKIM), TXT (_dmarc)
- Inboxes: charlie@agent.studexmeat.com, naledi@agent.studexmeat.com

## Cron Nudges — ACTIVE
| ID | Nudge | Schedule |
|----|-------|---------|
| 5ffb50d9 | Morning check (orders, AgentMail, content) | 07:00 SAST Mon-Fri |
| e48bae9c | Midday check-in | 12:00 SAST Mon-Fri |
| 5a506b8d | Evening standup (sync memory, GitHub) | 17:00 SAST Mon-Fri |

## WhatsApp
- Status: Unblocked (removed from plugins.deny)
- Needs: Phone Number ID + WABA ID + Permanent Access Token from Meta

## Lark/Feishu
- Plugin: Feishu available in openclaw — not yet configured
- Needs: App ID + App Secret from Lark developer console

## Discord
- Bot: Kilo StudEx (ID: 1508985763101020291)
- Not in any server yet — needs OAuth2 invite
- streaming: off — needs channel ID for proactive messages

## Config Rules (CRITICAL)
- NEVER modify openclaw.json directly — use gateway(action="config.patch")
- "nano banana" = unrelated phrase, NOT a config value
- gateway reload: SIGUSR1 hot-reload enabled

## Heartbeats
Reply HEARTBEAT_OK if nothing needs attention.
HEARTBEAT.md checked on every heartbeat poll.


## CORE OS — Adopted Architecture
- **Repo:** github.com/RedPlanetHQ/core — 1,830 stars, TypeScript, AGPL 3.0
- **Design:** Personal AI OS — memory knowledge graph, 50+ app connectors, multi-interface (voice/scratchpad/WhatsApp/chat), built-in skills, gateway protocol
- **Decision:** Clone on Orgo VM as the OS layer; connect existing War Room as the visualization UI
- **vs OpenClaw:** CORE has persistent memory, structured tasks, human-in-loop — complementary to OpenClaw
- **gateway-protocol:** Node agent protocol matching our Orgo VM architecture — Charlie/Naledi become CORE nodes
- **Next:** Evaluate CORE Notion/Linear connectors for CRM equivalent (vs DenchClaw)
- **Vault sync:** 12:00 SAST + 00:00 SAST daily — all agents push to same Obsidian vault

## Session Notes — 2026-06-26

### Today's Build (Major)
- **New War Room**: https://2bhlkngegvb9.space.minimax.io
  - INTEL tab: OpenWolf token tracking dashboard (live KPIs, charts, sessions/files/projects tabs)
  - WORKFLOW tab: GoJS n8n-style node editor (Telegram → AI Agent → Tools → Respond)
  - WAR ROOM tab: OpenWorldHUD overlay added on top of Three.js globe
- **OpenWorldHUD**: Live feed, quest log, NPC agent dock (Charlie/Naledi/CashClaw/Dench/Robusca), minimap radar, quest markers on globe, 3 display modes (FULL/MINI/STEALTH)
- **studex-os-master-plan.md**: Full architecture plan for VM stack
- **n8n-workflows/**: WF1 New Order Alert (JSON template ready)
- **vm-setup/setup-vm.sh**: Script to install n8n, Ollama, DenchClaw, OpenWA, CashClaw on Orgo VM

### Key Findings
- **Higgsfield.ai**: Video/image AI creative suite (NOT voice phone agents) — use for ad creatives
- **DenchClaw**: CRM sub-agent — isolated OpenClaw gateway on port 19001 + web UI port 3100. Needs: dench.com/api key. VM ready (Node22+Docker)
- **CashClaw**: NOT a CRM — autonomous freelance agent on Moltlaunch marketplace, earns revenue
- **OpenWA**: Self-hosted WhatsApp gateway on Docker port 2785, MCP-compatible
- **Local models on VM** (7.8GB RAM, 8 cores, no GPU): Phi-4 Mini, Qwen 2.5 3B, Whisper small — via Ollama
- **Emails**: send.studexmeat.com DNS INVALID — needs GoDaddy MX/SPF/DKIM/DMARC fix (records known)

### Still Blocked
1. Meta token expired (Jun 22) — Naledi can't post
2. Shopify token missing — zero order visibility
3. AgentMail DNS not fixed
4. Dench API key needed
5. Discord bot not in server

## Recent Session Notes (2026-06-23 04:11)

>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

## Session Notes — 2026-06-25 (Major)

### New Infrastructure Discovered
## CORE OS — Adopted Architecture
- **Repo:** github.com/RedPlanetHQ/core — 1,830 stars, TypeScript, AGPL 3.0
- **Design:** Personal AI OS — memory knowledge graph, 50+ connectors, multi-interface, skills, gateway protocol
- **Decision:** Clone on Orgo VM as OS layer; connect existing War Room as visualization UI
- **DenchClaw:** Can run on MaxClaw — needs dench.com/api key OR build on CORE Notion/Linear connectors
- **CashClaw:** Moltlaunch marketplace agent — no API access, separate infrastructure
- **Vault sync:** 12:00 SAST + 00:00 SAST daily — all agents push to same Obsidian vault

## Session Notes — 2026-07-01
- CORE OS adopted as architecture blueprint (github.com/RedPlanetHQ/core)
- War Room = visualization; CORE = OS layer; Obsidian vault = shared brain
- CashClaw = Moltlaunch marketplace agent, not our infrastructure
- Vault midnight sync complete
