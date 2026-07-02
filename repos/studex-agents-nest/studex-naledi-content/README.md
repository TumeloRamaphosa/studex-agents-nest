# studex-naledi-content

> ✨ **Naledi** AI content agent — Studex Meats' intelligent social media content pipeline.

**Naledi** (meaning "star" in Sesotho) is the creative AI agent responsible for generating, scheduling, and managing all social media content for Studex Meat across Instagram, Facebook, TikTok, and WhatsApp Channels.

## Overview

Naledi replaces manual content creation with an automated pipeline:

1. **Brief** → Brand manager or staff submits a content brief (product launch, promotion, season)
2. **Generate** → Naledi creates captions, hashtags, image prompts, video scripts, and posting schedules
3. **Review** → Content goes to approval workflow (Airtable / WhatsApp approval chain)
4. **Schedule** → Approved content is scheduled via Meta Graph API / Later.com
5. **Report** → Post-performance metrics fed back into Naledi for learning

## Brand Voice

Naledi operates within strict brand guidelines defined in `brand/voice.md`.

**Core Tone**: Proudly South African. Warm. Generous. Family-oriented. Mouthwatering.
**Avoid**: Cold corporate tone, overly formal language, generic food descriptions.

## What Naledi Generates

- 📸 Instagram captions & image prompts (food photography, lifestyle)
- 🎵 TikTok video scripts (behind-the-scenes, recipe reels, unboxing)
- 📌 Pinterest pins (recipes, cuts guide, party platter ideas)
- 📱 WhatsApp Status/Channel posts
- 📰 Facebook posts with engagement hooks
- 🏷️ Hashtag sets per platform and per campaign
- 📅 Monthly content calendars

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Runtime | OpenClaw (Node.js) |
| Content Calendar | Airtable / Supabase |
| Image Generation | DALL-E / Stable Diffusion via API |
| Scheduling | Meta Graph API + Later.com |
| Approval Workflow | N8n + WhatsApp Business API |
| Storage | Google Drive (assets) |

## Quick Start

```bash
git clone https://github.com/TumeloRamaphosa/studex-naledi-content.git
cd studex-naledi-content
npm install
cp .env.example .env
# Set OPENAI_API_KEY, AIRTABLE_API_KEY, META_PAGE_ACCESS_TOKEN, etc.
npm run generate:today   # Generate today's content
npm run schedule:week    # Generate and queue a week's worth
```

## Project Structure

```
studex-naledi-content/
├── agents/
│   └── naledi/
│       ├── naledi-agent.md       # Core content agent prompt
│       ├── caption-generator.md  # Caption writing sub-agent
│       ├── image-prompt-gen.md   # Image prompt sub-agent
│       └── scheduler.md          # Scheduling logic
├── brand/
│   ├── voice.md                  # Brand voice guidelines
│   ├── banned-topics.md          # Content guardrails
│   └── approved-hashtags.md      # Curated hashtag library
├── content/
│   ├── captions/                 # Generated captions archive
│   ├── calendars/                # Monthly content calendars
│   └── media-prompts/            # Image/video generation prompts
├── campaigns/
│   └── [campaign-name]/           # Per-campaign content packs
├── scripts/
│   ├── approve-content.js        # Approval workflow trigger
│   └── post-scheduler.js          # Push approved content to Meta API
├── src/
│   ├── image-generator.js         # DALL-E / SD API wrapper
│   ├── caption-generator.js      # GPT-powered caption writer
│   └── hashtag-selector.js       # Platform-specific hashtag picker
├── configs/
│   └── .env.example
├── protocols/
│   └── content-approval-protocol.md
├── tests/
│   └── caption-quality.test.js
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## Naledi Content Pillars

1. **Product Showcasing** — Premium cuts, fresh produce, value packs
2. **Lifestyle & Recipes** — Cooking inspiration, meal ideas, braai culture
3. **Brand Story** — Farm-to-table, South African heritage, quality assurance
4. **Seasonal Campaigns** — Heritage Day, December holidays, Easter, etc.
5. **Behind the Scenes** — Butchery craft, team spotlights, supplier stories

## Approval Workflow

```
Naledi generates → Saved to Airtable "Pending Approval" → Manager reviews on WhatsApp
    → Approved → Scheduled automatically
    → Rejected → Naledi regenerates with feedback
```

## Status

🟡 **In Development** — Caption and image prompt generation active; full pipeline under construction.

---

_⭐ "Naledi" — shining a light on Studex Meat, one post at a time._
_Built by the **Studex CTO Department**._
