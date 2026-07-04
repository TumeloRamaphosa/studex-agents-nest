# STUDEX AUTO-MEAT — System Architecture
**Purpose:** Physical server OS for the Studex meat processing + commodity trading business
**VM:** Orgo.ai (studex-meat-auto-meat) · 67.213.119.157
**Last Updated:** 2026-07-03

---

## 🖥️ Hardware Profile

| Resource | Value | Status |
|---|---|---|
| Disk (root) | 30GB / 5.7GB free | ⚠️ 80% — clean up |
| RAM | 7.8GB total / 6.5GB avail | ✅ |
| CPU | 8 cores | ✅ |
| GPU | None | ❌ |
| OS | Ubuntu 24.04 LTS | ✅ |

**Disk pressure is critical.** Top consumers:
- `/root/nest/war-room` — 663MB
- `/root/robusca/robusca-brain` — 520MB
- `/root/SrudEx-Agents-Nest-Cloud-VM/` — multiple clones

---

## 📁 Folder Structure — studex-auto-meat

```
/root/nest/studex-auto-meat/
├── operations/          — daily logs, system health, cron jobs
├── finance/             — revenue, costs, supplier payments
├── marketing/           — Naledi content queue, ad spend
├── sales/               — orders, leads, pipeline
├── engineering/         — code, deployments, War Room
├── compliance/          — halal certificates, import docs
├── executive/
│   ├── ceo-reports/    — Tumelo morning briefs, board reports
│   └── board/          — board meeting outputs
└── daily-standups/     — EOD standup logs from all agents
```

**Rule:** Every agent saves here. Robusca (this VM), Charlie, Naledi, Polsia all write to this vault daily.

---

## 🤖 Agents Running on This VM

| Agent | Home | Brain | How it runs |
|---|---|---|---|
| Robusca (Chief of Staff) | `/root/robusca` | `/root/robusca/robusca-brain` | OpenClaw (cloud) + Claude Code |
| Polsia (In-VM operator) | `/root/polsia` | `/root/polsia/polsia-brain` | `tmux` background session via `polsia.sh` |

---

## 🔊 Voice — Voicebox

**Status:** Cloned at `/root/voicebox` · Bun not installed — needs Bun first
**Goal:** Voice access from Mac + phone to this VM

**Install Bun:**
```bash
curl -fsSL https://bun.sh/install | bash
```

**Voicebox then runs as:** Desktop app via Tauri — not headless server
**For Mac + phone voice:** Need to set up a voice API server on this VM instead:
- Option A: OpenAI Realtime API proxy on VM → connect from Mac
- Option B: ElevenLabs voice synthesis API → works from anywhere

---

## 📓 Obsidian Vaults

| Vault | Path | Purpose |
|---|---|---|
| `vm-memory` | `/root/vm-memory/` | System-wide agent memory, daily logs |
| `studex-obsidian-vault` | `/root/nest/studex-obsidian-vault/` | Full business knowledge graph |

Both connected to Obsidian GUI on the VM desktop.

---

## 🌐 Mobile Linux Server — auto-meat-vm

See: `/root/robusca/robusca-brain/os/auto-meat-vm/`

**Vision:** A portable Linux server on an SD card that Tumelo can plug into any screen + network and have his full business OS running.

**Best hardware for SD card Linux server:**
1. **Raspberry Pi 5** (8GB) + 128GB high-endurance SD → ±R2,500 — portable, GPIO for hardware projects
2. **Rock 5B** (16GB) + 128GB eMMC → ±R3,500 — faster, more powerful
3. **Beelink EQ12** (16GB, Intel N100) + 256GB NVMe → ±R4,500 — most reliable, runs local LLMs

**Best OS for portable server:**
- **Ubuntu Server 24.04** (same as Orgo VM) — consistent with current stack
- **Alpine Linux** — lighter, faster boot, more resilient on SD card
- **Armbian** — optimized for single-board computers

**Studex-auto-meat on the SD card:**
- Same folder structure as this VM
- Connects back to Orgo VM via Tailscale VPN
- Agents sync via the Obsidian vault
- Requires: power + ethernet/WiFi + screen (HDMI)

---

## 🔌 Integrations Status

| Service | Connected? | Notes |
|---|---|---|
| Shopify | ❌ | No API token |
| Meta/Facebook | ❌ | Token expired Jun 22 |
| AgentMail | 🔶 | DNS pending for @agent.studexmeat.com |
| NotebookLM | ❌ | User needs to authenticate on Mac |
| Blotato | ❌ | 0 accounts connected |
| GitHub | 🔶 | No push credentials |
| Tailscale | ❌ | No auth key configured |
| Linear | ❌ | No API key |
| Notion | ❌ | No API key |
