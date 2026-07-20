# 🎬 NotebookLM Integration — 2-Minute Agent Video Summaries

> **Status:** NEEDS_KEY — NotebookLM API key not yet configured  
> **API setup:** https://notebooklm.google.com/ → Settings → API  
> **Goal:** Each agent generates a personal 2-minute stand-up video after the board meeting

---

## Overview

After every board meeting (11:05 PM SAST), each agent generates a short video summary of their day using Google NotebookLM. This creates a personal, AI-curated "day in review" video that:

1. Gets posted to #board-meeting for the team to watch
2. Gets linked in the Obsidian meeting log
3. Gives Tumelo a quick personal update from each agent

**Timeline:**
- 11:05 PM SAST — Each agent generates their video
- 11:10 PM SAST — All video links posted to #board-meeting
- 11:15 PM SAST — Robusca adds links to the Obsidian meeting log

---

## How It Works — Step by Step

### Flow Diagram

```
Meeting ends (11:00 PM SAST)
       │
       ▼
Each agent writes their stand-up text
(Already done during the meeting)
       │
       ▼
NotebookLM API → Generate audio/video summary
(input: stand-up text, duration: 2 minutes)
       │
       ▼
Video link returned → Agent posts to #board-meeting
       │
       ▼
Robusca collects all links → Adds to Obsidian meeting log
```

---

## Step 1 — Set Up NotebookLM API

> ⚠️ **NEEDS_KEY** — You must obtain a NotebookLM API key before using this integration.

1. Go to https://notebooklm.google.com/
2. Sign in with your Google account
3. Navigate to Settings → API
4. Generate an API key
5. Add to TOOLS.md:
   ```
   NotebookLM:
     API Key: [your key]
     Base URL: https://notebooklm.googleapis.com/v2
   ```
6. Add to `/workspace/studex-os/board-meeting/NOTEBOOKLM-CONFIG.json`:
   ```json
   {
     "notebooklm_api_key": "YOUR_KEY_HERE",
     "base_url": "https://notebooklm.googleapis.com/v2"
   }
   ```

---

## Step 2 — Create a Notebook Per Agent

Each agent needs their own NotebookLM notebook. This keeps video summaries organized and tied to each agent's voice and context.

| Agent | Notebook Name | Notebook ID |
|---|---|---|
| Robusca | `Robusca — CEO Agent` | `NOTEBOOK_ID_ROBUSCA` |
| Charlie | `Charlie — Operations` | `NOTEBOOK_ID_CHARLIE` |
| Naledi | `Naledi — Marketing` | `NOTEBOOK_ID_NALEDI` |
| Delivery Agent | `Delivery Agent` | `NOTEBOOK_ID_DELIVERY` |

**How to create notebooks (via NotebookLM API):**
```bash
curl -X POST "https://notebooklm.googleapis.com/v2/notebooks" \
  -H "Authorization: Bearer $NOTEBOOKLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Robusca — CEO Agent",
    "description": "Daily stand-up summaries for Robusca, CEO Agent of Studex Meat"
  }'
```

Save the returned `notebook.id` for each agent.

---

## Step 3 — Add Stand-Up Content to Notebook

After each stand-up, the agent's text is automatically added as a source to their notebook.

```bash
# Example: Add Charlie's stand-up to Charlie's notebook
curl -X POST "https://notebooklm.googleapis.com/v2/notebooks/${NOTEBOOK_ID_CHARLIE}/sources" \
  -H "Authorization: Bearer $NOTEBOOKLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": {
      "type": "TEXT",
      "content": {
        "title": "Charlie Stand-Up — 2026-06-29",
        "text": "1. WHAT I DID: Processed 67 orders. Cleared inventory discrepancy. Kicked off order pipeline.\n2. BUILDING NEXT: Ops monitoring dashboard. Live by Wednesday.\n3. BLOCKERS: Waiting on wholesale pricing tiers from Robusca.\n4. WIN: Order processing time dropped 57% — from 4.2 to 1.8 minutes."
      }
    }
  }'
```

---

## Step 4 — Generate the Audio Summary

NotebookLM's Audio Overview feature creates a natural-sounding two-agent discussion of the content. We use this as the audio track.

```bash
# Generate an Audio Overview (2-agent discussion) for a notebook
curl -X POST "https://notebooklm.googleapis.com/v2/notebooks/${NOTEBOOK_ID_CHARLIE}/audio-overviews" \
  -H "Authorization: Bearer $NOTEBOOKLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

This starts the generation job. Poll for completion:

```bash
# Poll for audio overview status
curl -X GET "https://notebooklm.googleapis.com/v2/notebooks/${NOTEBOOK_ID_CHARLIE}/audio-overviews" \
  -H "Authorization: Bearer $NOTEBOOKLM_API_KEY"
```

Response:
```json
{
  "audioOverviews": [
    {
      "status": "COMPLETE",
      "audioUri": "gs://notebooklm-user-oa.../audio.mp3",
      "transcript": "Charlie here with your daily stand-up recap..."
    }
  ]
}
```

---

## Step 5 — Convert to Video

Combine NotebookLM's audio with a branded agent poster image to create a video.

**Recommended approach:**
1. Generate a branded poster image for each agent using `image_synthesize` MCP tool
2. Combine poster + audio into video using ffmpeg or the video MCP tool

```bash
# Example: ffmpeg video generation from poster + audio
ffmpeg -loop 1 -i poster-charlie.png -i charlie-audio.mp3 \
  -c:v libx264 -tune stillimage \
  -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest \
  charlie-2026-06-29.mp4
```

**Agent poster prompt for image_synthesize:**
```
Studex Meat agent video poster. Clean, professional. [Agent name] stand-up summary. South African meat delivery company. Dark background, green and gold accent. Minimalist corporate design.
```

---

## Step 6 — Post Video Link to #board-meeting

Once the video is hosted (use MCP `upload_to_cdn` for public URL):

```
📹 CHARLIE — STAND-UP VIDEO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: 2026-06-29
Duration: 2:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
https://cdn.studexmeat.com/videos/charlie-2026-06-29.mp4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Full Agent Video Script

Save as `/workspace/studex-os/board-meeting/scripts/generate-agent-video.sh`:

```bash
#!/bin/bash
# /workspace/studex-os/board-meeting/scripts/generate-agent-video.sh
# Generates a 2-minute stand-up video for an agent after the board meeting

AGENT="$1"
DATE="$2"
STANDUP_TEXT="$3"
NOTEBOOKLM_API_KEY="${NOTEBOOKLM_API_KEY}"
NOTEBOOK_ID_VAR="NOTEBOOK_ID_${AGENT^^}"
NOTEBOOK_ID="${!NOTEBOOK_ID_VAR}"
VIDEO_OUTPUT_DIR="/workspace/studex-os/board-meeting/videos"

mkdir -p "$VIDEO_OUTPUT_DIR"

# Step 1: Add stand-up as source to notebook
curl -s -X POST \
  "https://notebooklm.googleapis.com/v2/notebooks/${NOTEBOOK_ID}/sources" \
  -H "Authorization: Bearer ${NOTEBOOKLM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"source\":{\"type\":\"TEXT\",\"content\":{\"title\":\"${AGENT} Stand-Up — ${DATE}\",\"text\":\"${STANDUP_TEXT}\"}}}"

# Step 2: Generate audio overview
AUDIO_JOB=$(curl -s -X POST \
  "https://notebooklm.googleapis.com/v2/notebooks/${NOTEBOOK_ID}/audio-overviews" \
  -H "Authorization: Bearer ${NOTEBOOKLM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{}')

# Step 3: Poll for completion (max 60 seconds)
for i in $(seq 1 12); do
  sleep 5
  STATUS=$(curl -s \
    "https://notebooklm.googleapis.com/v2/notebooks/${NOTEBOOK_ID}/audio-overviews" \
    -H "Authorization: Bearer ${NOTEBOOKLM_API_KEY}" \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['audioOverviews'][0]['status'])")
  
  if [ "$STATUS" == "COMPLETE" ]; then
    echo "AUDIO_READY"
    exit 0
  fi
done

echo "ERROR: Audio generation timed out"
exit 1
```

**Usage:**
```bash
./generate-agent-video.sh charlie "2026-06-29" "1. WHAT I DID: Processed 67 orders..."
```

---

## Agent Video Poster Templates

Create branded poster images for each agent. Store at:
- `/workspace/studex-os/board-meeting/assets/poster-robusca.png`
- `/workspace/studex-os/board-meeting/assets/poster-charlie.png`
- `/workspace/studex-os/board-meeting/assets/poster-naledi.png`
- `/workspace/studex-os/board-meeting/assets/poster-delivery.png`

```
┌──────────────────────────────────────┐
│  📹 [AGENT NAME]                     │
│     Stand-Up Summary                 │
│                                      │
│  Studex Meat Agent Board Meeting    │
│  Date: [DATE]                        │
│  Duration: 2:00                      │
│                                      │
│  🤖 [Agent Role]                     │
│  studexmeat.com                      │
└──────────────────────────────────────┘
```

---

## Video Hosting

| Option | Cost | Notes |
|---|---|---|
| MCP upload_to_cdn | ✅ Available | Use directly — public URL returned |
| Cloudflare R2 | Free tier | AgentMail/Orgo VM storage |
| Google Drive | Free | Share links publicly |
| Self-hosted (VM) | Free | `/workspace/studex-os/board-meeting/videos/` |

**Recommended:** Use MCP `upload_to_cdn` tool — files publicly accessible immediately.

---

## Post-Meeting Video Checklist

| Step | Agent | Status | Video Link |
|---|---|---|---|
| 1 | Robusca | ❌ Pending | |
| 2 | Charlie | ❌ Pending | |
| 3 | Naledi | ❌ Pending | |
| 4 | Delivery Agent | ❌ Pending | |

**Deadline:** All videos posted to #board-meeting by 11:10 PM SAST

---

## Configuration File

Save as `/workspace/studex-os/board-meeting/NOTEBOOKLM-CONFIG.json`:

```json
{
  "notebooklm_api_key": "NEEDS_KEY",
  "base_url": "https://notebooklm.googleapis.com/v2",
  "notebooks": {
    "robusca": {
      "name": "Robusca — CEO Agent",
      "notebook_id": null,
      "poster_asset": "assets/poster-robusca.png"
    },
    "charlie": {
      "name": "Charlie — Operations",
      "notebook_id": null,
      "poster_asset": "assets/poster-charlie.png"
    },
    "naledi": {
      "name": "Naledi — Marketing",
      "notebook_id": null,
      "poster_asset": "assets/poster-naledi.png"
    },
    "delivery": {
      "name": "Delivery Agent",
      "notebook_id": null,
      "poster_asset": "assets/poster-delivery.png"
    }
  },
  "video": {
    "duration_seconds": 120,
    "output_dir": "/workspace/studex-os/board-meeting/videos",
    "cdn_upload": true
  },
  "timeline": {
    "generation_start": "23:05 SAST",
    "links_due": "23:10 SAST",
    "vault_links_due": "23:15 SAST"
  }
}
```

---

## ⚠️ Current Status

| Item | Status | Notes |
|---|---|---|
| NotebookLM API Key | ❌ NEEDS_KEY | Get from notebooklm.google.com |
| Agent notebooks created | ❌ Pending | Create one per agent |
| Poster images | ❌ Pending | Generate with image_synthesize |
| Video generation script | ✅ Written | `scripts/generate-agent-video.sh` |
| CDN upload integration | ✅ Available | Use MCP `upload_to_cdn` |
| Video hosting | 🔄 Pending | Set up storage location |

---

## First-Time Setup Checklist

Before the first board meeting with videos:

- [ ] Get NotebookLM API key → add to TOOLS.md
- [ ] Create 4 notebooks (one per agent) → save IDs to NOTEBOOKLM-CONFIG.json
- [ ] Generate agent poster images → save to `/workspace/studex-os/board-meeting/assets/`
- [ ] Test video generation for one agent (Charlie) → verify output
- [ ] Test CDN upload → verify public link works
- [ ] Test Rocket.Chat post → verify video link renders
- [ ] Test Obsidian link → verify link added to meeting log
- [ ] Run full pipeline end-to-end before first live meeting

---

*Last updated: 2026-06-29 | Version: 1.0.0*
