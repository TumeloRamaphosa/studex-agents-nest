# STUDEX — Mobile Linux Server + Voice + Local Models Plan
**Created:** 2026-07-04 | **VM Status:** ✅ Ollama running · 🔶 Bun installed

---

## 📍 Where We Are Right Now (04:33 SAST)

### VM Disk — BEFORE cleanup
| Item | Size |
|---|---|
| npm cache | 2.9GB → cleared to 570MB ✅ |
| Ollama models | 2.4GB ✅ running |
| voicebox | 1.1GB 🔶 needs Bun |
| n8n (node_modules) | 2.5GB — not running, investigate |
| **Free after npm clean** | ~8GB+ |

### What's Running on VM
| Service | Status | How |
|---|---|---|
| Ollama (local LLMs) | ✅ Running | `ollama serve` on port 11434 |
| qwen3:4b model | ✅ Active | Ready for inference |
| Voicebox | 🔶 Bun installed, not started | `bun run dev` |
| n8n | ❌ Not running | Was installed but no pm2 process |

---

## 🔊 VOICE — Mac + Phone, Anywhere

### Architecture
```
[Mac — RileyJarvis] --voice--> [Orgo VM: Voicebox + Ollama]
[Phone — WhatsApp]  --text--> [OpenClaw / AgentMail]
[Mac — Terminal]    --CLI-->  [Ollama local inference]
```

### Voicebox (on VM) — IN PROGRESS
Voicebox is at `/root/voicebox` — Bun installed, starting now.
- **Mac:** Connect via Tailscale VPN (need Tailscale auth key)
- **Phone:** Connect via WhatsApp or Browser-based voice panel
- **Real-time two-way:** Needs OpenAI Realtime API or similar

### Immediate Voice Wins
1. **I already have ElevenLabs** — I can call `batch_text_to_audio` and send you voice messages right now via any messaging channel
2. **Voicebox on VM** — once Tailscale is set up, your Mac runs Voicebox locally and talks to the VM
3. **WhatsApp voice** — connect WhatsApp plugin to OpenClaw, send/receive voice notes

### What's Needed
- [ ] Tailscale auth key (free at tailscale.com → Settings → Keys)
- [ ] WhatsApp plugin configured
- [ ] OpenAI Realtime API key (for full duplex voice)

---

## 🤖 LOCAL MODELS — Already Running on VM

Ollama is live with `qwen3:4b` — no GPU needed, runs on CPU.
Access via:
```bash
curl http://67.213.119.157:11434/api/generate \
  -d '{"model":"qwen3:4b","prompt":"What is Studex Meat?"}'
```

**More models we can install** (7.8GB RAM, 8 cores):
- `phi4-mini` — 2.3GB, fast, good coding
- `qwen2.5:3b` — 2GB, multilingual
- `mistral:7b` — 4.1GB, strong reasoning
- `codellama:7b` — 3.8GB, code specialist

Install: `ollama pull phi4-mini`

---

## 💾 MOBILE LINUX SERVER (SD Card / Portable)

### The Vision
A pocket-sized Linux server on an SD card or small SSD that Tumelo can:
- Plug into any screen + ethernet + power
- Boot into his full business OS in 30 seconds
- Have all agents, files, and dashboards instantly available

### Best Hardware Options

| Device | Price | RAM | Storage | Why |
|---|---|---|---|---|
| **Raspberry Pi 5 (8GB)** | ~R2,500 | 8GB | 128GB SD | Cheapest, GPIO, community |
| **Rock 5B (16GB)** | ~R3,500 | 16GB | 128GB eMMC | Fastest, runs local LLMs |
| **Beelink EQ12 (16GB)** | ~R4,500 | 16GB | 256GB NVMe | Most reliable, silent, desktop-grade |

**Recommendation: Rock 5B (16GB)** — can run actual local models (qwen3, phi4) at decent speed. Boot from eMMC or NVMe, not SD card.

### Portable OS Setup

**Step 1: Flash Ubuntu Server 24.04 to SD/NVMe**
```bash
# Download Ubuntu Server 24.04 ARM64
wget https://cdimage.ubuntu.com/ubuntu-server/noble/daily-live/...
# Flash to SD with Balena Etcher on your Mac
```

**Step 2: Install agents + voice + Ollama**
```bash
curl -fsSL https://raw.githubusercontent.com/TumeloRamaphosa/auto-meat-install/main/setup.sh | bash
```

**Step 3: Connect to Orgo VM via Tailscale**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --authkey=<your-auth-key>
```

### Portable Server Spec
```
Auto-Meat-Portable/
├── boot/              — Ubuntu kernel + initrd
├── chroot/            — Full Ubuntu rootfs
│   ├── /root/nest/   — All business subdirectories
│   ├── /root/voicebox/
│   ├── /root/ollama/ — Local model weights
│   └── /root/agents/ — Charlie, Naledi, Robusca configs
└── data/             — Persistent data (SQLite, logs)
```

---

## 🗂️ Auto-Meat Folder — Already Created ✅

Created 2026-07-03 at `/root/nest/studex-auto-meat/`:

```
studex-auto-meat/
├── operations/         — daily logs, system health
├── finance/          — revenue, supplier payments
├── marketing/        — Naledi content queue
├── sales/            — orders, leads, pipeline
├── engineering/      — deployments, War Room
├── compliance/       — halal certs, import docs
├── executive/
│   ├── ceo-reports/  — morning briefs, board reports
│   └── board/       — board outputs
└── daily-standups/  — all agent standup logs
```

**Rule:** Every agent writes to this vault every day. I read from it at startup.

---

## 📓 NotebookLM Auth — One Step You Need to Do

On your Mac terminal (not the VM — browser-based auth):

```bash
# Clone the skill
git clone https://github.com/claude-world/notebooklm-skill.git ~/notebooklm-skill
cd ~/notebooklm-skill && pip install -r requirements.txt

# Authenticate (opens browser for Google login — do this once)
python3 -m notebooklm login
```

Tell me when you've logged in. Then I can query your notebook `517c7938-3880-4973-9a4d-37a944920980` from the VM via MCP.

---

## ✅ Done Today (2026-07-04)

| Task | Status |
|---|---|
| VM disk cleanup (npm cache) | ✅ ~2.3GB freed |
| Ollama installed + running | ✅ qwen3:4b active |
| Bun installed on VM | ✅ |
| Auto-meat folder structure | ✅ 11 dirs created |
| Voicebox ready to start | 🔶 Need Tailscale first |
| NotebookLM auth | ⏳ Needs you on Mac |

---

## 🗓️ Action Plan — In Order

1. **You:** Auth NotebookLM on Mac (5 min)
2. **Me:** Start voicebox on VM, test voice to Mac
3. **You:** Get Tailscale auth key (free, tailscale.com)
4. **Me:** Set up Tailscale on VM + Mac
5. **Me:** Install more Ollama models (phi4-mini)
6. **You:** Decide on portable server hardware (Pi5 / Rock5B / Beelink)
7. **Me:** Write auto-install script for portable server
8. **Me:** n8n decision (remove or keep for automation workflows)
