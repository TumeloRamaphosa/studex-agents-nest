# Studex Meat HQ — Notion Integration Plan
### Kanan Band × Studex OS · Powered by Naledi · Maintained by Robusca

> **Theme:** Kanan Band — `#0a0505` background · `#8B1A1A` dark red · `#d4a017` gold · `#f5f0e8` cream
> **Last updated:** 2026-06-29

---

## A. Notion Workspace Structure

### Workspace Name
```
Studex Meat HQ
```

### Page Hierarchy

```
Studex Meat HQ                    ← Root (workspace icon: 🐄)
│
├── 📊 Dashboard                  ← Metrics overview (metrics database + summary blocks)
├── 📦 Delivery Pipeline           ← Kanban: New → Dispatched → In Transit → Delivered
├── 📋 Orders                      ← List/Table: all orders with filters by status/customer/driver
├── 🐄 Products                    ← Catalog with provenance, cut types, Moutloe Farm data
├── 🏭 Suppliers                    ← Contact cards for Silent Valley, Noags Butchery, Moutloe Farm
├── 🚚 Delivery Partners            ← Dinkoko Pty Ltd + My Courier details + SLA matrix
├── 📅 Content Calendar             ← Naledi's weekly posting schedule (Mon–Sun blocks)
├── 📣 Marketing                    ← Campaigns, Ad账户 links, social post drafts, analytics
├── 💰 Finance                      ← Revenue tracking, COGS, margins, payout calendar
├── 🧠 Agent Memory                 ← Daily logs: Charlie · Naledi · Delivery Agent · Robusca
└── 📄 Pitch Deck                   ← Links to PDF, Loom walkthrough, investor one-pager
```

---

### 📊 Dashboard — Blocks & Metrics

| Block | Source | Refresh |
|---|---|---|
| Today's Orders (count) | Notion Orders DB filter `Date = today` | Real-time |
| Revenue Today | Notion Orders DB sum `Total` | Real-time |
| Active Deliveries | Delivery Pipeline filter `Status = In Transit` | Real-time |
| Naledi Posts This Week | Content Calendar filter `Week = current` | Daily |
| Top Products (best sellers) | Products DB sort by `Units Sold` | Weekly |
| Supplier Stock Alerts | Products DB filter `Stock < 5kg` | Daily |

**Dashboard Layout:** 3-column grid — *Orders / Finance / Marketing* side-by-side.

---

### 📦 Delivery Pipeline — Kanban Columns

| Column | Emoji | Trigger |
|---|---|---|
| New Orders | 📥 | Charlie receives Shopify order → auto-creates DB row |
| Dispatched | 📦 | Delivery Agent assigns driver |
| In Transit | 🚚 | Driver confirmed pickup |
| Delivered | 🏁 | Driver marks complete or webhook fires |
| Issue | ⚠️ | Delivery Agent flags problem |

**Sync:** Delivery Agent watches OS `delivery_board` and mirrors card moves to Notion.

---

### 📋 Orders — Database Properties

| Property | Type | Notes |
|---|---|---|
| Order ID | Text | e.g. `STX-2024-0001` |
| Customer Name | Text | |
| WhatsApp | Phone | |
| Address | Text | Full delivery address |
| Products | Relation → Products DB | Multi-select |
| Quantity (kg) | Number | Total weight |
| Total (ZAR) | Currency | ZAR |
| Status | Select | New / Dispatched / In Transit / Delivered / Cancelled |
| Driver | Relation → Delivery Partners DB | |
| ETA | Date | |
| Shop Name | Text | |
| Notes | Text | |
| Created | Date | Auto |
| Updated | Date | Auto |

---

### 🐄 Products — Database Properties

| Property | Type | Notes |
|---|---|---|
| Product Name | Text | e.g. "Moutloe Farm Lamb Ribs" |
| SKU | Text | Internal code |
| Category | Select | Beef · Lamb · Poultry · Processed |
| Supplier | Relation → Suppliers DB | |
| Farm | Text | Moutloe Farm, Silent Valley, etc. |
| Provenance | Text | Kill date, abattoir, cert number |
| Stock (kg) | Number | Current stock |
| Price (ZAR/kg) | Number | |
| Units Sold | Number | Auto-tally from Orders |
| Halal Certified | Checkbox | |
| Image | Files | Product photo |
| Status | Select | Available · Low Stock · Out of Stock |

---

### 🏭 Suppliers — Database Properties

| Property | Type | Notes |
|---|---|---|
| Supplier Name | Text | |
| Contact Person | Text | |
| Phone | Phone | |
| Email | Email | |
| Address | Text | |
| Category | Select | Abattoir · Farm · Butchery |
| Products Supplied | Text | |
| Payment Terms | Text | e.g. "Net 30" |
| Rating | Select | ⭐⭐⭐⭐⭐ |
| Notes | Text | |

**Known Suppliers:**

| Supplier | Contact | Address |
|---|---|---|
| Silent Valley | 083 254 6777 | PO Box 215, Philadelphia, 7460 |
| Noags Butchery | 021 001 2345 / 074 580 0815 | Shop 5, Noagas Kraal, Main Road |
| Moutloe Farm | 079 609 8911 | Moutloe Farm, Rawsonville |

---

### 🚚 Delivery Partners — Database Properties

| Property | Type | Notes |
|---|---|---|
| Partner Name | Text | |
| Contact | Phone | |
| WhatsApp | Text | |
| Areas | Multi-select | Cape Town · Southern Suburbs · Northern Suburbs etc. |
| Rate (ZAR/km) | Number | |
| Min Charge (ZAR) | Number | |
| SLA | Text | e.g. "2-hour window" |
| Status | Select | Active · On Hold |
| Notes | Text | |

**Known Partners:**

| Partner | Contact | Areas | Rate |
|---|---|---|---|
| Dinkoko Pty Ltd | 078 161 0332 | Cape Town wide | R9/km |
| My Courier | 081 555 0198 | Cape Town metro | R8/km |

---

### 📅 Content Calendar — Database Properties

| Property | Type | Notes |
|---|---|---|
| Post Title | Text | |
| Platform | Multi-select | Facebook · Instagram · WhatsApp Status |
| Content Type | Select | Reel · Static · Story · Carousel |
| Publish Date | Date | |
| Caption | Text | |
| Media | Files | Image/video draft |
| Status | Select | Idea · Draft · Scheduled · Posted |
| Link | URL | |
| Posted By | Text | Naledi |
| Notes | Text | |

---

### 📣 Marketing — Database Properties

| Property | Type | Notes |
|---|---|---|
| Campaign Name | Text | |
| Platform | Multi-select | |
| Objective | Select | Awareness · Sales · Engagement |
| Start Date | Date | |
| End Date | Date | |
| Budget (ZAR) | Number | |
| Impressions | Number | |
| Clicks | Number | |
| Conversions | Number | |
| Revenue | Currency | |
| Notes | Text | |

---

### 💰 Finance — Page with Embedded Databases

**Database: Revenue**

| Property | Type |
|---|---|
| Date | Date |
| Source | Select (Orders · Bulk · Other) |
| Amount (ZAR) | Currency |
| Order ID | Relation → Orders DB |
| Notes | Text |

**Database: Costs**

| Property | Type |
|---|---|
| Date | Date |
| Category | Select (COGS · Delivery · Marketing · Admin · Other) |
| Supplier | Relation → Suppliers DB |
| Amount (ZAR) | Currency |
| Notes | Text |

**Finance Page Blocks:** Summary table — Revenue · COGS · Gross Profit · Gross Margin % · Net Profit.

---

### 🧠 Agent Memory — Daily Log Templates

Each agent has a sub-page. Format per day:

```markdown
# 2026-06-29 — Charlie Daily Log

## Actions Taken
- [list]

## Decisions Made
- [list]

## Flags / Blockers
- [list]

## Tomorrow
- [list]
```

| Agent | Sub-page | Tag colour |
|---|---|---|
| Robusca | HQ / Agent Memory / Robusca | 🔴 |
| Charlie | HQ / Agent Memory / Charlie | 🟡 |
| Naledi | HQ / Agent Memory / Naledi | 🟢 |
| Delivery Agent | HQ / Agent Memory / Delivery Agent | 🔵 |

---

## B. Notion API Integration

### Step 1 — Create the Integration

1. Go to **[https://www.notion.so/profile/integrations](https://www.notion.so/profile/integrations)**
2. Click **"New integration"**
3. Fill in:
   - **Name:** `Studex OS`
   - **Associated workspace:** `Studex Meat HQ`
   - **Type:** Internal
   - **Token:** Copy and store securely (shown ONCE)
4. Required **Scopes** (minimum set):

| Scope | Why |
|---|---|
| `Read content` | Read orders, products, dashboards |
| `Update content` | Write order status, update blocks |
| `Insert content` | Create new DB rows on new orders |
| `Read database content` | Pull metrics for dashboards |
| `Write database content` | Write pipeline updates |

### Step 2 — Share the Workspace with the Integration

1. Open the `Studex Meat HQ` workspace
2. Click **···** (top-right menu) → **"Add connections"**
3. Search for `Studex OS` integration → **Confirm**

### Step 3 — Store the API Key

```bash
# In your .env or OpenClaw environment
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_WORKSPACE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4 — How Robusca Uses It

| Use Case | Flow |
|---|---|
| **Morning briefing** | Robusca opens Dashboard → sees orders, revenue, active deliveries |
| **Track an order** | Opens Orders DB → filters by `Status = In Transit` → checks ETA |
| **Plan content** | Opens Content Calendar → Naledi pre-fills next week's posts |
| **Resolve delivery issue** | Opens Delivery Pipeline → moves card to `Issue` → Charlie is notified |
| **Review finances** | Opens Finance page → sees gross margin calculated live |

---

## C. Notion Sync Protocol

### Architecture Overview

```
Shopify (order.created webhook)
    │
    ▼
Charlie (OpenClaw agent — webhook receiver)
    │
    ├─→ creates Notion Orders DB row (via @notionhq/client)
    │
    ├─→ Delivery Agent (assigns driver, updates Status = Dispatched)
    │
    └─→ Notion Orders DB ← Status column updated by Delivery Agent
```

### Detailed Sync Flows

#### Flow 1 — New Order (Shopify → Notion)

```
1. Customer places order on Shopify
2. Shopify fires order.created webhook → Charlie
3. Charlie parses order (customer, items, address, total)
4. Charlie calls notion.databases.create:
   {
     parent: { database_id: ORDERS_DB_ID },
     properties: {
       "Order ID":   { title: [{ text: { content: "STX-2024-XXXX" }}] },
       "Customer":  { rich_text: [{ text: { content: "..." }}] },
       "WhatsApp":  { phone_number: "+27..." },
       "Address":   { rich_text: [{ text: { content: "..." }}] },
       "Products":  { relation: [...] },
       "Total":     { number: { amount: 49900, currency: "ZAR" }},
       "Status":    { select: { name: "New" }},
       "Shop Name": { rich_text: [{ text: { content: "..." }}] },
     }
   }
5. Charlie stores new page ID in session context
6. Delivery Agent picks up → assigns driver → updates "Status" to "Dispatched"
```

#### Flow 2 — Delivery Status Update

```
1. Driver sends WhatsApp update to Delivery Agent (or Charlie intercepts webhook)
2. Delivery Agent calls notion.pages.update:
   {
     page_id: ORDER_PAGE_ID,
     properties: {
       "Status": { select: { name: "In Transit" }},
       "ETA":    { date: { start: "2026-06-29T14:00:00" }}
     }
   }
3. Notion Kanban card auto-moves to "In Transit" column
4. Robusca sees real-time status on Dashboard
```

#### Flow 3 — Naledi's Content Calendar

```
1. Naledi reviews week's content plan in Notion
2. Creates Content Calendar entries for each post (Caption, Platform, Publish Date)
3. Charlie reads upcoming "Scheduled" entries each morning
4. Naledi's weekly stats (Impressions, Clicks, Conversions) are written back by Naledi
5. Finance page pulls revenue attributed to social posts
```

#### Flow 4 — Daily Revenue to Finance

```
1. End of day — Charlie tallies Orders DB filtered by today
2. Charlie calls notion.pages.update on Finance page block or writes Revenue DB entry
3. Gross margin auto-calculates via Notion formula: Revenue - COGS
4. Robusca reviews Finance page next morning
```

---

## D. Kanan Band Notion Branding

### Cover Image Specification

| Element | Value |
|---|---|
| Background | `#0a0505` near-black |
| Primary accent | `#8B1A1A` dark red |
| Secondary accent | `#d4a017` gold |
| Text | `#f5f0e8` cream |
| Icon style | Line art, warm red tones |

Create a branded cover in Canva or Figma using:
- Dark background (`#0A0505`)
- Subtle grain texture overlay (10% opacity)
- Gold (`#d4a017`) geometric border
- Company logo in dark red

Upload as workspace banner: **1500 × 600 px, PNG/JPG, < 5 MB**

### Icon Colour Strategy

| Element | Colour |
|---|---|
| Page icons | `#8B1A1A` |
| Database icons | `#d4a017` |
| Agent Memory icons | `#f5f0e8` (cream) |
| Status — New | `#8B1A1A` (red) |
| Status — In Transit | `#d4a017` (gold) |
| Status — Delivered | `#4CAF50` (green) |
| Status — Issue | `#FF5722` (orange) |

### Database Property Naming Convention

Use OS-aligned names so Robusca's mental model is consistent:

```
Orders DB     → Order ID, Customer, WhatsApp, Address, Products, Quantity (kg),
                Total (ZAR), Status, Driver, ETA, Shop Name, Notes
Products DB   → Product Name, SKU, Category, Supplier, Farm, Provenance,
                Stock (kg), Price (ZAR/kg), Halal Certified, Status
Finance DB    → Date, Source, Amount (ZAR), Order ID, Notes
```

### Custom Emoji Set (Status)

| Meaning | Emoji |
|---|---|
| New order received | 📥 |
| Dispatched to driver | 📦 |
| En route | 🚚 |
| Delivered | 🏁 |
| Issue / Problem | ⚠️ |
| Confirmed / Paid | ✅ |
| Cancelled | ❌ |
| Low stock | 🔴 |
| Bulk order | 🐄 |
| Premium product | ⭐ |

---

## E. Notion → OS Push (Notifications)

### Webhook-Based Push

> Notion's official API does **not** yet support outbound webhooks natively.
> Until Notion releases them, use **polling + delta detection** as the primary mechanism.

#### Primary: OpenClaw Gateway Polling (Heartbeat)

```
OpenClaw gateway heartbeat (every 15 minutes):
    │
    ├─→ Charlie checks Notion Orders DB (updated_after: last_checked_at)
    │       └─→ New entries found?
    │           └─→ Yes: create internal event → notify Robusca
    │
    └─→ Naledi checks Content Calendar DB (Status = Scheduled, Date = tomorrow)
            └─→ Upcoming posts found?
                └─→ Yes: add to daily brief for Robusca
```

#### Fallback: Robusca Manual Check

- Robusca opens Notion Dashboard (always live, no refresh needed)
- OpenClaw **does not need to poll** for dashboard — Robusca reads directly

#### Future: Notion Webhooks (when available)

```
When Notion releases page/database webhooks:
  1. Register webhook: POST https://api.notion.com/v1/webhooks
     { url: "https://your-gateway/notion-webhook", filter: { object: "page" }}
  2. OpenClaw gateway receives POST at /notion-webhook
  3. Parse payload → route to correct agent by page/database type
  4. Agent processes update → responds to Robusca
```

### Routing Rules

| What changed in Notion | Route to |
|---|---|
| Orders DB — new row | Charlie → Delivery Agent |
| Orders DB — Status change | Charlie → Robusca (if Issue) |
| Content Calendar — new Scheduled post | Naledi |
| Products DB — Stock drops below 5kg | Charlie → Robusca (alert) |
| Finance DB — new Revenue entry | Charlie → Robusca (daily summary) |
| Agent Memory — new daily log | Robusca reads directly |

---

## F. Implementation Steps

### Phase 1 — Manual Setup (Tumelo)

- [ ] **Step 1:** Tumelo signs up at [notion.so](https://www.notion.so) (or logs in if existing)
- [ ] **Step 2:** Create workspace named **`Studex Meat HQ`**
- [ ] **Step 3:** Create all pages per [Section A](#a-notion-workspace-structure):
  - Create sub-pages under root using the emoji names
  - For Orders, Products, Delivery Partners — click **"Table"** to make a database
- [ ] **Step 4:** Create the Notion integration:
  - Go to [https://www.notion.so/profile/integrations](https://www.notion.so/profile/integrations) → **New integration**
  - Name: `Studex OS` · Workspace: `Studex Meat HQ`
  - Enable scopes: Read content, Update content, Insert content, Read database content, Write database content
  - **Copy the API token** (displayed once only)
- [ ] **Step 5:** Share the workspace with the integration:
  - Open `Studex Meat HQ` root page → **···** → **Add connections** → select `Studex OS`
- [ ] **Step 6:** Share the API token with Robusca (via AgentMail, not in plaintext in code):
  - `NOTION_API_KEY=secret_xxx` in Robusca's environment
  - `NOTION_WORKSPACE_ID=xxx` (workspace URL: `notion.so/workspace/XXXXXXXX`)

### Phase 2 — Automated Setup (Robusca runs the script)

- [ ] **Step 7:** Robusca clones / updates the `studex-os/notion/` directory
- [ ] **Step 8:** Robusca sets env vars:
  ```bash
  export NOTION_API_KEY="secret_xxx"
  export NOTION_WORKSPACE_ID="xxx"
  ```
- [ ] **Step 9:** Robusca runs:
  ```bash
  node notion/notion-api-setup.js
  ```
  This creates all databases with correct properties and seeds known data.
- [ ] **Step 10:** Robusca verifies databases were created correctly in Notion

### Phase 3 — OS Integration

- [ ] **Step 11:** Robusca configures OpenClaw gateway with Notion credentials
- [ ] **Step 12:** Charlie's webhook receiver is updated to call Notion on new orders
- [ ] **Step 13:** Delivery Agent is configured to write to Notion Orders DB
- [ ] **Step 14:** Naledi's content calendar is linked to Facebook/Instagram posting pipeline
- [ ] **Step 15:** End-to-end test: place test order on Shopify → verify it appears in Notion within 30s

---

## G. Environment Variables Reference

```bash
# Required
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_WORKSPACE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — IDs of created databases (set by notion-api-setup.js)
STUDEX_NOTION_ORDERS_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STUDEX_NOTION_PRODUCTS_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STUDEX_NOTION_DELIVERY_PARTNERS_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STUDEX_NOTION_CONTENT_CALENDAR_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## H. Troubleshooting

| Problem | Fix |
|---|---|
| "Could not connect to Notion" | Check NOTION_API_KEY is correct and workspace is shared with integration |
| "Insufficient permissions" | Re-share workspace: Open workspace → ··· → Add connections → Studex OS |
| "Database not found" | Run `notion-api-setup.js` first — it creates DBs and prints their IDs |
| "Polling not working" | Check heartbeat interval; ensure OpenClaw gateway is running |
| "Orders not syncing" | Verify Shopify webhook is pointing to Charlie's endpoint |

---

*Built with ❤️ for Studex Meat HQ · Kanan Band · Studex OS · 2026*
