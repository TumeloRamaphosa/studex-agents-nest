# 05 — INTEGRATION STATUS (connect existing Higgsfield + Blotato)

**Verified live:** 2026-10-25 12:10–12:40 UTC · **Coordinator:** Katia
**Rule applied:** *connect what exists, report blockers honestly, generate nothing.*

---

## BLOTATO — ✅ CONNECTED (publish path live, destination gap remains)

**MCP server:** `blotato` — **35 tools, healthy (0.3s)** via `mcporter`.

**Auth check (live call, `blotato_get_user`):**
```
id: 375375ff-e880-42c8-8e14-eec889f83a25
subscriptionStatus: active
subscriptionPlan: starter
statusCode: 200
```
🔑 Header form: `blotato-api-key: <key>` (also accepts `Authorization: Bearer <key>`).
**`Authorization: <raw key>` returns 401 — that is a request-shape error, not a dead key.**

**Account roster (live, `blotato_list_accounts`):**
| Platform | Account ID | Account | Username | Brand/Page accessible? |
|---|---|---|---|---|
| facebook | `38744` | Tumelo Ramaphosa | — | ⚠️ `subaccounts: []` — **no Page** |
| instagram | `76978` | — | `ramaphosatumelo` | ⚠️ personal handle only |
| instagram | `55765` | — | `laisa_aesthetics` | ⚠️ lifestyle account, not brand |
| linkedin | `26628` | Tumelo Ramaphosa | — | ✅ 1 subaccount |
| threads | `7701` | — | `ramaphosatumelo` | ⚠️ personal handle only |
| youtube | `41593` | Studex Wildlife | — | ✅ 23 subaccounts (channels) |
| tiktok | `48423` | — | `studexwildlife` | ⚠️ personal handle only |

### 🚫 Destination-access blocker (unchanged, owner action)
- **Facebook Page "Studex Meat" (`108934711902801`)** — the account is connected but
  `subaccounts` is **empty**, so there is **no Page to post to**. Root cause: the Meta Page
  token expired 27-Jun-2026 (Meta error 190/463).
- **Instagram `studex.meat`** — not connected at all.
- **Every account we can publish to is a personal or lifestyle account. The buyers are on the
  brand accounts.** Posting this package to `ramaphosatumelo` or `laisa_aesthetics` would put
  trade content in front of the wrong audience — so the package is delivered **unpublished**.
- **Fix (owner, in Meta Business Suite → Page Settings → Page Access Tokens):** re-authorise
  the Studex Meat Page with ADVERTISE, CREATE_CONTENT, MESSAGING, MODERATE, MANAGE → then
  connect `studex.meat` on Blotato → Settings → Connected Accounts.

**Nothing was posted, scheduled, queued or advertised.** No Blotato write endpoint was called.

---

## HIGGSFIELD — 🚫 AUTHENTICATION BLOCKER (no credits spent)

**Key location (the key is NOT in `/workspace/.env`):**
`/workspace/studex-os/.vscode/studex.env` → `HIGGSFIELD_API_KEY` (64 chars) +
`HIGGSFIELD_WORKSPACE_ID`.
⚠️ `.env` contains **no** Higgsfield variable — anyone wiring Higgsfield from `.env` alone gets
nothing. Worth moving into the canonical `.env`.

**Documented integration (from the repo, not guessed):**
`/workspace/n8n-workflows/studex-content-pipeline.json` → node "Generate Product Image
(Higgsfield)": `POST https://api.higgsfield.ai/v1/generate/image`,
`Authorization: Bearer <key>`, body `{prompt, workspace_id}`.

**Live probe (single canonical request, empty body — no generation, no credits):**
```
POST https://api.higgsfield.ai/v1/generate/image
→ HTTP 401 {"detail":"Invalid credentials"}
```
**Control:** `POST https://api.higgsfield.ai/v1/models` (a path that does not exist) → **also
HTTP 401 "Invalid credentials"** — so the **auth check happens before routing**, which proves the
401 is a **credential rejection, not a wrong-endpoint artifact**. `GET` on every path returns
`405 Method Not Allowed`, so no endpoint shape can be resolved by GET either.

**Verdict:** the stored Higgsfield credential is **rejected by the API**. The host is reachable;
the key is not accepted. No client or SDK exists in the repo to attempt an alternative auth
path (the only other reference, `studex-agents-nest/agents/content-pipeline/index.js`, reads
`process.env.HIGGSFIELD_API_KEY` and has an unimplemented `TODO: dispatch to Higgsfield`).

**Action (owner):** issue/verify the Higgsfield API key in the Higgsfield dashboard and confirm
the correct endpoint + auth header with them. Until then Higgsfield is **unavailable**, and any
shot in the video brief that depends on it is marked *pending approval* rather than generated.

---

## SUMMARY
| Integration | State | Blocker | Who fixes it |
|---|---|---|---|
| Blotato | ✅ connected, 35 tools, subscription active | ❌ **brand Facebook Page + `studex.meat` IG not connected** → wrong-audience risk | Owner: re-authorise Meta Page token → connect in Blotato |
| Higgsfield | 🚫 not usable | ❌ **stored key rejected (401)**; key not in `.env` | Owner: re-issue key, confirm endpoint + header |
| n8n content pipeline | ⚠️ workflow file exists | Higgsfield node points at the failing credential | Blocked by Higgsfield |
| War Room approvals API | ⚠️ lives on the unreachable hub | host `100.95.66.29` down since 27 Sep | Host owner |

**Credits spent this task: 0. Posts published: 0. Scheduled: 0. Ads launched: 0.**
