# War Room Messaging Platform — Studex Meat OS

## Platform Recommendation: Rocket.Chat

**Verdict: Rocket.Chat** — chosen over Mattermost, Zulip, Element/Matrix, and Chatwoot.

---

## Platform Comparison

### 1. Mattermost
| Criteria | Detail |
|---|---|
| Language | Go |
| Database | PostgreSQL |
| GitHub Stars | ~33,000 |
| Active Development | Yes (Mattermost Inc.) |
| Install Methods | Docker, deb/rpm, Kubernetes |
| RAM on 8GB VM | ~1.5–2GB (light), 3–4GB (moderate traffic) |
| Web UI | Professional, Slack-like, good customizability |
| Mobile Apps | iOS/Android (native, paid features in free tier) |
| @mentions | ✅ Full support |
| Channels | ✅ Public + private + direct messages |
| File Sharing | ✅ With storage backend (S3, MinIO, local) |
| Theming | ✅ CSS customization, custom themes via Marketplace |
| Bot/API | ✅ REST API + WebSocket (Real-Time API), Hubot-compatible |
| Open Source | ⚠️ Open Core (MIT, but Enterprise features behind paywall) |
| Docker Compose | ✅ Official `docker-compose.yml` provided |

**Verdict:** Solid, but open-core means key features (like advanced analytics, SSO with SAML) require paid license. Theming is more restrictive than Rocket.Chat.

---

### 2. Rocket.Chat ✅ RECOMMENDED
| Criteria | Detail |
|---|---|
| Language | Node.js (TypeScript) |
| Database | MongoDB |
| GitHub Stars | ~38,000 |
| Active Development | Very active (Rocket.Chat Inc.) |
| Install Methods | Docker, snap, Ansible, source |
| RAM on 8GB VM | ~1–1.5GB (light), 2–3GB (moderate traffic) |
| Web UI | Modern, feature-rich, excellent customizability |
| Mobile Apps | iOS/Android (native, open source, full-featured in free tier) |
| @mentions | ✅ Full support + user groups |
| Channels | ✅ Public, private, direct, discussion threads |
| File Sharing | ✅ Built-in file upload, supports S3/MinIO/GridFS |
| Theming | ✅ Live CSS injection, full sidebar + theme customization, logo replacement |
| Bot/API | ✅ Best-in-class REST API + Real-Time API (WebSocket), native bot SDK, Hubot adapter, Apps Framework |
| Open Source | ✅ Fully open source (MIT) — ALL features free |
| Docker Compose | ✅ Official docker-compose, single-file |

**Verdict:** 🏆 BEST FIT. Fully open source, exceptional bot/API support (critical for agent integration), easy theming, Docker-native, mobile apps. MongoDB is included in the Docker image. No paid gatekeeping of features.

---

### 3. Zulip
| Criteria | Detail |
|---|---|
| Language | Python (Django) |
| Database | PostgreSQL |
| GitHub Stars | ~19,000 |
| Active Development | Yes (Kandra Labs) |
| Install Methods | Docker, Ubuntu/Debian apt, source |
| RAM on 8GB VM | ~2–3GB |
| Web UI | Clean, unique threaded-topic model |
| Mobile Apps | iOS/Android (native, open source) |
| @mentions | ✅ Full support |
| Channels | ❌ Uses "streams" + "topics" instead of channels — different mental model |
| File Sharing | ✅ Built-in |
| Theming | ⚠️ Limited — theming via custom CSS only, no live theme editor |
| Bot/API | ✅ Good API, bots via Python SDK |
| Open Source | ✅ Fully open source (Apache 2) |
| Docker Compose | ✅ Official Docker image |

**Verdict:** Excellent platform but the stream/topic model is different from standard channel-based War Room workflows. Less intuitive for non-technical users (Tumelo). Theming is limited. Bot API is good but less mature than Rocket.Chat's.

---

### 4. Element/Matrix (Synapse + Element)
| Criteria | Detail |
|---|---|
| Language | Python (Synapse), TypeScript (Element web) |
| Database | PostgreSQL (recommended) |
| GitHub Stars | Synapse ~12K, Element ~11K |
| Active Development | Active (New Vector Ltd.) |
| Install Methods | Docker, matrix-docker-ansible, source |
| RAM on 8GB VM | ~1.5–2GB (Synapse), plus Element hosting or reverse-proxy |
| Web UI | Element web — clean, modern |
| Mobile Apps | iOS/Android (Element, open source) |
| @mentions | ✅ Full support |
| Channels | ✅ Rooms (public/private), DMs |
| File Sharing | ✅ Matrix protocol (mxc:// URIs) |
| Theming | ⚠️ Partial — Element supports custom CSS, Synapse is minimal |
| Bot/API | ✅ Client-Server API, Application Services (AS) API, many bot libs |
| Open Source | ✅ Fully open source (Apache 2) |
| Docker Compose | ✅ matrix-docker-ansible or docker-compose |

**Verdict:** Powerful decentralized protocol but more complex to operate. Requires managing Synapse + a reverse proxy + Element hosting separately. No unified Docker Compose out of the box. Better for federation/open networks; overkill for a closed private War Room.

---

### 5. Chatwoot
| Criteria | Detail |
|---|---|
| Language | Ruby (Rails) |
| Database | PostgreSQL + Redis |
| GitHub Stars | ~23,000 |
| Active Development | Yes |
| Install Methods | Docker, Cloudron, source |
| RAM on 8GB VM | ~2–3GB (Ruby/Rails stack) |
| Web UI | Clean, customer support-focused |
| Mobile Apps | iOS/Android (native) |
| @mentions | ⚠️ Limited — designed for customer support, not team chat |
| Channels | ⚠️ Not designed as team chat — integrates inbound channels (email, chat, social) |
| File Sharing | ✅ In conversations |
| Theming | ⚠️ Very limited — no CSS injection, white-label only in Enterprise |
| Bot/API | ⚠️ API designed for customer-facing bots, not internal agent integration |
| Open Source | ⚠️ Open Core (free tier limited) |

**Verdict:** Not a team chat platform. Built for customer support inboxes. Wrong tool for internal War Room.

---

## Final Comparison Matrix

| Criteria | Mattermost | Rocket.Chat ✅ | Zulip | Element/Matrix | Chatwoot |
|---|---|---|---|---|---|
| Open Source (full) | ⚠️ Core only | ✅ Full | ✅ Full | ✅ Full | ⚠️ Core only |
| RAM on 8GB VM | ~2–3GB | ~1.5–2.5GB | ~2–3GB | ~2–3GB | ~2–3GB |
| Docker install | ✅ | ✅ | ✅ | ✅ (manual) | ✅ |
| Theming ease | Good | **Excellent** | Limited | Moderate | Very limited |
| Bot/API quality | Good | **Excellent** | Good | Moderate | Limited |
| Mobile apps | ✅ | ✅ | ✅ | ✅ | ✅ |
| No paid gatekeeping | ❌ | ✅ | ✅ | ✅ | ❌ |
| Best for War Room | 3rd | **1st** | 2nd | 4th | ❌ |

---

## Why Rocket.Chat for Studex Meat OS War Room

1. **Fully open source** — no license fees, no feature paywalls
2. **Industry-leading bot/API** — critical for Robusca, Charlie, Naledi, Delivery Agent integration
3. **CSS theme injection** — Kanan Band branding can be applied via live CSS editor in admin panel
4. **Live Chat widget** — can double as customer-facing chat
5. **Rocket.Chat Apps** — can build custom plugins for Shopify webhook → channel routing
6. **Rocket.Chat Push** — mobile push notifications with @mention alerts
7. **Single Docker Compose** — everything in one file, MongoDB included
8. **Webhook support** — can connect OpenClaw via incoming webhooks

---

## Channels / Rooms to Create

| Room Name | Purpose | Auto-join |
|---|---|---|
| `war-room` | Main ops hub — all agents + Tumelo | All |
| `orders` | Charlie → Shopify order alerts | Charlie, Robusca, Tumelo |
| `delivery` | Delivery Agent → status updates | Delivery Agent, Robusca, Tumelo |
| `marketing` | Naledi → content published alerts | Naledi, Robusca, Tumelo |
| `ceo` | Robusca → daily briefings to Tumelo | Robusca, Tumelo |
| `alerts` | Critical escalations only (DMs to Tumelo too) | All |

## Agent Bot Accounts

| Username | Display Name | Role | Primary Channel |
|---|---|---|---|
| `charlie` | Charlie Orchestrator | Bot | `orders` |
| `naledi` | Naledi CMO | Bot | `marketing` |
| `delivery-agent` | Delivery Agent | Bot | `delivery` |
| `robusca` | Robusca AI | Bot | `ceo` |
| `tummebox` | Meat B@ye (Tumelo) | Admin | All |

---

## Installation Order

See `INSTALL.md` for full step-by-step installation on the VM.

Quick start sequence:
1. SSH into VM
2. Clone/update `studex-os` repo
3. `cd war-room && docker-compose up -d`
4. Run initial admin setup wizard
5. Apply Kanan Band branding (see `BRANDING.md`)
6. Create rooms and bot accounts (see `INSTALL.md`)
7. Configure OpenClaw webhook integration (see `bot-integration.md`)
8. Set up mobile apps (see `INSTALL.md`)
9. Configure firewall (see `INSTALL.md`)
