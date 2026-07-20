# AGENTS.md — StudEx War Room OS Completion

> Drop this file into the root of `studex-content-hub/` and run:
> ```
> claude --dangerously-skip-permissions
> ```
> Claude Code will read this file and execute all tasks autonomously.

---

## 1. PROJECT OVERVIEW

**Repo:** `studex-content-hub/`
**Stack:** Express 5 + Vite 7 + React 18 + Tailwind 3 + shadcn/ui + SQLite (Drizzle ORM)
**Entry points:**
- Server: `server/index.ts` → `server/routes.ts` + `server/storage.ts`
- Client: `client/src/main.tsx` → `client/src/App.tsx`
- Shared types/schema: `shared/schema.ts`
- Build script: `script/build.ts`

**Dev server:** `npm run dev` (port 5000)
**Production build:** `npm run build`
**Type check:** `npm run check`

**War Room color palette (STRICT — never deviate):**
```
BG_DEEP:    #0a0908   (page background, inline style on body/html)
BG_CARD:    #0e0d10   (card backgrounds)
BG_CARD2:   #15140e   (modal/secondary card backgrounds)
GOLD:       #C9A84C   (primary accent, borders, active states)
GOLD_DIM:   #9a8a5a   (secondary text, muted labels)
GOLD_DARK:  #5a4f2e   (tertiary/dim borders)
CREAM:      #f5ecd0   (primary body text)
GREEN:      #4CFFA8   (success, online, fulfilled)
RED:        #c14e3c   (error, critical, rejected)
RED_BRIGHT: #ff4444   (critical order flags)
BLUE_DISC:  #5865F2   (Discord brand)
```

**Typography system (STRICT):**
- Labels/caps: `fontFamily: "'Helvetica Neue', sans-serif"`, `fontSize: "9-10px"`, `letterSpacing: "2-4px"`, `textTransform: "uppercase"`
- Body/captions: `fontFamily: "'Helvetica Neue', sans-serif"`, `fontSize: "12-14px"`
- Headings: `fontFamily: "'Cormorant Garamond', Georgia, serif"`, `fontStyle: "italic"`
- Monospace (numbers/IDs): `fontFamily: "'Menlo', 'Monaco', monospace"`, `className="font-mono"`
- Section headers: `fontFamily: "var(--font-rajdhani, 'Rajdhani', sans-serif)"`, `letterSpacing: "3-8px"`

**Critical rules:**
- NEVER use `localStorage`, `sessionStorage`, `indexedDB`, or cookies for persistent data
- Use React state for transient/UI data, SQLite via backend API for persistent data
- All API calls use `apiRequest` from `@/lib/queryClient` (already handles base URL)
- Privacy context: `usePrivacy()` from `@/contexts/PrivacyContext` — always `mask()` monetary values and PII
- Monetary values ALWAYS use `font-mono` class and `R` prefix (no space: `R29,325`)
- Router uses `useHashLocation` from `wouter/use-hash-location` — do NOT use react-router
- Icons: `lucide-react` only (already installed at `^0.453.0`)
- Component library: shadcn/ui (components in `client/src/components/ui/`)

---

## 2. CURRENT STATE SUMMARY

### What exists and works:
- `ContentQueue.tsx` — full implementation with approve/reject/post mutations
- `ContentCalendar.tsx` — calendar view
- `GenerateContent.tsx` — Higgsfield image/video generation
- `Analytics.tsx` — analytics view
- `ShopifyStore.tsx` — live Shopify data via `/api/shopify/*`
- `AgentNetwork.tsx` — 10 agents + AgentMail inboxes (needs Sync button)
- `FacebookAds.tsx` — mock FB ads data
- `DeliveryTeam.tsx` — static mock orders, no live data, no fulfill button
- `Communications.tsx` — Gmail + AgentMail + Discord + Slack
- `GlobalMarkets.tsx` — Sistine Chapel background
- `SuperAgents.tsx` — SaaS pricing display
- `Payments.tsx` — PayFast integration display
- `RevenueEngine.tsx` — Google Ads table + subscription projections

### What is placeholder/incomplete:
- `Approvals` tab → `ComingSoonPage` in `App.tsx` line 142 — needs full implementation
- `DeliveryTeam.tsx` — uses hardcoded static orders, needs live API + fulfill flow
- `ContentQueue.tsx` — needs platform filter tabs + bulk approve + status pills
- `AgentNetwork.tsx` — needs Sync Messages button + last sync timestamp
- `AnalyticsStrip.tsx` (War Room header) — needs live SAST clock + ROBUSCA status
- `RevenueEngine.tsx` — needs MRR tracker widget with progress bar

### Database tables that exist:
- `content_items` — status field: `draft | approved | rejected | posted`
- `calendar_events`
- `analytics_cache`
- `cached_messages`

### Database tables that need to be created:
- `approvals` — approval log (see Task 1)

---

## 3. ORDERED TASK LIST

Execute tasks in this order. Complete each fully before starting the next.

1. **APPROVALS TAB** (highest priority — currently shows "Coming Soon")
2. **DELIVERY TAB** (live Shopify orders + fulfill flow)
3. **WAR ROOM HEADER** (live SAST clock + ROBUSCA status)
4. **CONTENT QUEUE** (platform filter + bulk approve + status pills)
5. **AGENT NETWORK** (Sync button + last sync timestamp)
6. **REVENUE ENGINE** (MRR tracker widget)

---

## 4. TASK SPECIFICATIONS

---

### TASK 1 — APPROVALS TAB (Highest Priority)

**Goal:** Replace the `ComingSoonPage` placeholder with a full content approval workflow.

#### 4.1.1 — Schema: add `approvals` table

**File:** `shared/schema.ts`

Add after the existing `cachedMessages` table definition:

```typescript
export const approvals = sqliteTable("approvals", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  contentId: integer("content_id").notNull(),
  action: text("action").notNull(), // "approved" | "rejected" | "edited"
  notes: text("notes"),
  timestamp: text("timestamp").notNull(),
});

export const insertApprovalSchema = createInsertSchema(approvals).omit({ id: true });
export type Approval = typeof approvals.$inferSelect;
export type InsertApproval = z.infer<typeof insertApprovalSchema>;
```

#### 4.1.2 — Storage: add approvals CRUD

**File:** `server/storage.ts`

1. Add `CREATE TABLE IF NOT EXISTS approvals` to the `sqlite.exec(...)` block:
```sql
CREATE TABLE IF NOT EXISTS approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  notes TEXT,
  timestamp TEXT NOT NULL
);
```

2. Import `approvals` from `../shared/schema` (add to existing import).

3. Add to the `storage` export object:
```typescript
// Approvals
logApproval: (contentId: number, action: string, notes?: string) =>
  db.insert(approvals).values({ contentId, action, notes: notes || null, timestamp: new Date().toISOString() }).run(),
getApprovals: (contentId?: number) => {
  if (contentId) {
    return db.select().from(approvals).where(eq(approvals.contentId, contentId)).all();
  }
  return db.select().from(approvals).orderBy(desc(approvals.id)).all();
},
```

Also import `desc` from `drizzle-orm` if not already imported (it's already used — check the existing import line).

#### 4.1.3 — API routes: add approvals endpoints

**File:** `server/routes.ts`

Add these two routes BEFORE the `return httpServer` line:

```typescript
// GET approvals log
app.get("/api/approvals", (_req, res) => {
  try {
    const log = storage.getApprovals();
    res.json(log);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// POST log an approval action
app.post("/api/approvals", (req, res) => {
  try {
    const { contentId, action, notes } = req.body as { contentId: number; action: string; notes?: string };
    if (!contentId || !action) return res.status(400).json({ error: "contentId and action are required" });
    // Log the approval
    storage.logApproval(contentId, action, notes);
    // Also update the content item status
    storage.updateContentStatus(contentId, action, notes);
    const updated = storage.getContentById(contentId);
    res.json({ ok: true, item: updated });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/content/pending-approval — items needing approval
app.get("/api/content/pending-approval", (_req, res) => {
  try {
    const items = storage.getAllContent().filter((i: any) =>
      i.status === "draft" || i.status === "pending_approval"
    );
    res.json(items);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});
```

#### 4.1.4 — Create the Approvals page component

**File:** `client/src/pages/Approvals.tsx` (CREATE NEW FILE)

Full implementation requirements:

```
Component: ApprovalsCenter (default export)

State:
- selectedIds: Set<number>  — for bulk selection
- rejectModal: { open: boolean; itemId: number | null; note: string }
- editModal: { open: boolean; item: ContentItem | null; caption: string }

Data fetching:
- useQuery<ContentItem[]>({ queryKey: ["/api/content"] }) — all items
- Filter client-side: items where status === "draft" OR status === "pending_approval"
- useQuery<Approval[]>({ queryKey: ["/api/approvals"] }) — approval log

Mutations:
- approveMutation: POST /api/approvals with { contentId, action: "approved" }
  onSuccess: invalidate ["/api/content"] and ["/api/approvals"]
- rejectMutation: POST /api/approvals with { contentId, action: "rejected", notes }
  onSuccess: same invalidation
- bulkApproveMutation: iterate selectedIds, call approveMutation for each

Layout (from top to bottom):

1. PAGE HEADER
   - Title: "APPROVALS CENTRE" in Rajdhani 36px bold gold #C9A84C letterSpacing 8px uppercase
   - Subtitle: italic Cormorant 12px muted "Content review · Approve · Edit · Reject"
   - Right side: count badge "N PENDING" in monospace

2. STATS BAR (horizontal row of 3 KPI cards)
   - "Pending Review" count (items with status draft/pending_approval)
   - "Approved This Session" count (from local state tracking successful approvals)
   - "Rejected This Session" count
   Each card: gold accent, monospace number, label in 8px caps

3. BULK ACTIONS BAR (shows only when selectedIds.size > 0)
   - "N SELECTED" label
   - "APPROVE ALL" button: green border, onClick calls bulkApproveMutation
   - "DESELECT ALL" button: gold_dark border

4. PLATFORM FILTER TABS
   - Pills: All | Instagram | Facebook | Both
   - Filter the pending items by platform

5. CONTENT CARDS (one per pending item, sorted by scheduledDate ascending)
   Each card layout:
   
   Card container:
   - background: #0e0d10
   - border-left: 3px solid #C9A84C
   - border: 1px solid rgba(201,168,76,0.2)
   - Has a checkbox in top-left for bulk selection
   
   Card top row (flex row, space-between):
   - Left: checkbox + order number (#1 of N) in 9px mono gold_dim
   - Center: platform badge (INSTAGRAM | FACEBOOK | IG+FB) colored appropriately
   - Right: scheduled date in mono font
   
   Card body (grid: image thumbnail | content info):
   LEFT COLUMN — Thumbnail (160px wide, square aspect ratio):
   - Image from assetMap (same mapping used in ContentQueue.tsx)
   - Platform icons overlaid bottom-left (Instagram gradient circle, Facebook blue circle)
   
   RIGHT COLUMN — Content info:
   - Title in Cormorant italic 20px cream
   - Caption label in 8px gold_dim caps
   - Caption text: if isPrivate → show blurred "••••••••••••" overlay with css filter blur(4px) + user-select none; else show full caption truncated to 3 lines with line-clamp-3 style
   - Hashtags in 10px mono gold_dim
   - Scheduled: "SCHEDULED FOR: [date]" in 9px caps gold_dim
   - Campaign badge if present
   
   Card action bar (border-top gold 0.15 opacity):
   - ✅ APPROVE button: green border, Check icon from lucide-react
     onClick → approveMutation.mutate({ contentId: item.id, action: "approved" })
   - ✏️ EDIT button: gold border, Pencil icon
     onClick → open editModal with item
   - ❌ REJECT button: red border, X icon
     onClick → open rejectModal with itemId
   - Loading spinner (Loader2 from lucide) when mutation isPending

6. EMPTY STATE (when no pending items):
   - Cormorant italic 36px cream: "All content reviewed"
   - 9px gold_dim caps: "No items pending approval"
   - CheckCircle2 icon from lucide in green #4CFFA8 at 48px

7. APPROVAL LOG SECTION (below cards, collapsed by default, expandable):
   - "APPROVAL LOG" header with ChevronDown/Up toggle
   - Shows last 20 approvals from /api/approvals in a table:
     columns: Timestamp | Content ID | Action | Notes
   - Timestamps formatted with toLocaleString("en-ZA")
   - Action colored: approved=green, rejected=red, edited=gold

8. EDIT MODAL (Dialog from shadcn/ui):
   - Title: "Edit Caption"
   - Textarea with current caption
   - On save: PATCH /api/content/:id/caption with new caption, then log action "edited" via POST /api/approvals, then invalidate queries
   - Cancel button, Save Changes button (gold)

9. REJECT MODAL (Dialog from shadcn/ui):
   - Title: "Reject Content"
   - Textarea for rejection note (optional)
   - Cancel button, Confirm Reject button (red)
   - On confirm: rejectMutation.mutate({ contentId, action: "rejected", notes })

Privacy integration:
- Import usePrivacy from "@/contexts/PrivacyContext"
- Mask caption text: when isPrivate, replace caption with "••••••••••••••••••••" with style filter: blur(4px), userSelect: "none"
- Do NOT mask platform names, titles, dates, or action buttons
```

**Asset import map** (copy from ContentQueue.tsx exactly):
```typescript
import tomahawkHero from "@assets/tomahawk-hero.jpg";
import hwendeBox from "@assets/hwende-box.png";
import braaiLifestyle from "@assets/braai-lifestyle.png";
import youthDay from "@assets/youth-day.png";
import wagyuPatties from "@assets/wagyu-patties.png";
import hwendeCelebration from "@assets/hwende-celebration.png";
import ankoleScarcity from "@assets/ankole-scarcity.png";

const assetMap: Record<string, string> = {
  "/assets/tomahawk-hero.jpg": tomahawkHero,
  "/assets/hwende-box.png": hwendeBox,
  "/assets/braai-lifestyle.png": braaiLifestyle,
  "/assets/youth-day.png": youthDay,
  "/assets/wagyu-patties.png": wagyuPatties,
  "/assets/hwende-celebration.png": hwendeCelebration,
  "/assets/ankole-scarcity.png": ankoleScarcity,
};
```

#### 4.1.5 — Wire Approvals into App.tsx

**File:** `client/src/App.tsx`

1. Add import at top (with other page imports):
```typescript
import Approvals from "@/pages/Approvals";
```

2. Replace line 142:
```typescript
// BEFORE:
{activeTab === "approvals" && <ComingSoonPage title="Approvals Centre" />}
// AFTER:
{activeTab === "approvals" && <Approvals />}
```

---

### TASK 2 — DELIVERY TAB (Live Shopify Data + Fulfill Flow)

**Goal:** Replace the static `ORDERS` hardcoded array with live Shopify API data and add a "Mark Fulfilled" button per order.

#### 4.2.1 — Add Shopify live orders API route

**File:** `server/routes.ts`

Add this route BEFORE `return httpServer`:

```typescript
// GET /api/shopify/orders — live unfulfilled paid orders from Shopify
app.get("/api/shopify/orders", async (req, res) => {
  const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN; // e.g. "studexmeat.myshopify.com"
  const SHOPIFY_TOKEN = process.env.SHOPIFY_ADMIN_TOKEN;

  if (!SHOPIFY_DOMAIN || !SHOPIFY_TOKEN) {
    // Return the existing mock data when credentials are missing
    return res.json({
      orders: [
        { id: "1947", orderNumber: "#1947", customer: { firstName: "R", lastName: "I" }, totalPrice: "5865.00", lineItemsCount: 4, createdAt: new Date(Date.now() - 2 * 86400000).toISOString(), fulfillmentStatus: "unfulfilled", financialStatus: "paid" },
        { id: "1946", orderNumber: "#1946", customer: { firstName: "C", lastName: "G" }, totalPrice: "1610.00", lineItemsCount: 4, createdAt: new Date(Date.now() - 4 * 86400000).toISOString(), fulfillmentStatus: "unfulfilled", financialStatus: "paid" },
        { id: "1945", orderNumber: "#1945", customer: { firstName: "C", lastName: "G" }, totalPrice: "7245.00", lineItemsCount: 6, createdAt: new Date(Date.now() - 4 * 86400000).toISOString(), fulfillmentStatus: "unfulfilled", financialStatus: "paid" },
        { id: "1944", orderNumber: "#1944", customer: { firstName: "R", lastName: "G" }, totalPrice: "29325.00", lineItemsCount: 3, createdAt: new Date(Date.now() - 4 * 86400000).toISOString(), fulfillmentStatus: "unfulfilled", financialStatus: "paid" },
        { id: "1943", orderNumber: "#1943", customer: { firstName: "D", lastName: "O" }, totalPrice: "5405.00", lineItemsCount: 6, createdAt: new Date(Date.now() - 4 * 86400000).toISOString(), fulfillmentStatus: "unfulfilled", financialStatus: "paid" },
      ],
      totalValue: 49550,
      isMock: true,
    });
  }

  try {
    const url = `https://${SHOPIFY_DOMAIN}/admin/api/2024-01/orders.json?fulfillment_status=unfulfilled&financial_status=paid&limit=50&status=open`;
    const r = await fetch(url, {
      headers: {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
      },
    });
    if (!r.ok) {
      const err = await r.text();
      return res.status(500).json({ error: `Shopify error: ${err}` });
    }
    const data = await r.json();
    const orders = (data.orders || []).map((o: any) => ({
      id: String(o.id),
      orderNumber: `#${o.order_number}`,
      customer: {
        firstName: o.customer?.first_name?.charAt(0) || "?",
        lastName: o.customer?.last_name?.charAt(0) || "?",
      },
      totalPrice: o.total_price,
      lineItemsCount: (o.line_items || []).length,
      createdAt: o.created_at,
      fulfillmentStatus: o.fulfillment_status || "unfulfilled",
      financialStatus: o.financial_status,
    }));
    // Sort oldest first
    orders.sort((a: any, b: any) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
    const totalValue = orders.reduce((sum: number, o: any) => sum + parseFloat(o.totalPrice), 0);
    res.json({ orders, totalValue, isMock: false });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/shopify/orders/:id/fulfill — mark order as fulfilled
app.post("/api/shopify/orders/:id/fulfill", async (req, res) => {
  const SHOPIFY_DOMAIN = process.env.SHOPIFY_DOMAIN;
  const SHOPIFY_TOKEN = process.env.SHOPIFY_ADMIN_TOKEN;
  const orderId = req.params.id;

  if (!SHOPIFY_DOMAIN || !SHOPIFY_TOKEN) {
    // Mock: pretend it worked
    return res.json({ ok: true, message: "Mock fulfilled", isMock: true });
  }

  try {
    // First get the order to find fulfillment_orders
    const orderRes = await fetch(
      `https://${SHOPIFY_DOMAIN}/admin/api/2024-01/orders/${orderId}/fulfillment_orders.json`,
      { headers: { "X-Shopify-Access-Token": SHOPIFY_TOKEN } }
    );
    const orderData = await orderRes.json();
    const fulfillmentOrderId = orderData.fulfillment_orders?.[0]?.id;

    if (!fulfillmentOrderId) {
      return res.status(404).json({ error: "No fulfillment order found" });
    }

    const fulfillRes = await fetch(
      `https://${SHOPIFY_DOMAIN}/admin/api/2024-01/fulfillments.json`,
      {
        method: "POST",
        headers: {
          "X-Shopify-Access-Token": SHOPIFY_TOKEN,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          fulfillment: {
            line_items_by_fulfillment_order: [{ fulfillment_order_id: fulfillmentOrderId }],
            notify_customer: true,
          },
        }),
      }
    );

    if (!fulfillRes.ok) {
      const err = await fulfillRes.text();
      return res.status(500).json({ error: `Shopify fulfill error: ${err}` });
    }
    res.json({ ok: true, message: "Order fulfilled" });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});
```

#### 4.2.2 — Rewrite DeliveryTeam.tsx

**File:** `client/src/pages/DeliveryTeam.tsx`

**REPLACE the entire file** with this new implementation:

```
Component: DeliveryTeam (default export)

Imports needed:
- useQuery, useMutation from "@tanstack/react-query"
- queryClient, apiRequest from "@/lib/queryClient"
- usePrivacy from "@/contexts/PrivacyContext"
- useToast from "@/hooks/use-toast"
- Dialog, DialogContent, DialogHeader, DialogTitle from "@/components/ui/dialog"
- useState from "react"
- lucide-react: Truck, CheckCircle2, AlertTriangle, Clock, Package, DollarSign, Loader2, RefreshCw

Interface ShopifyOrder:
  id: string
  orderNumber: string
  customer: { firstName: string; lastName: string }
  totalPrice: string
  lineItemsCount: number
  createdAt: string
  fulfillmentStatus: string
  financialStatus: string

Interface ApiResponse:
  orders: ShopifyOrder[]
  totalValue: number
  isMock: boolean

State:
- fulfillModal: { open: boolean; orderId: string | null; orderNumber: string }

Data:
- useQuery<ApiResponse>({
    queryKey: ["/api/shopify/orders"],
    refetchInterval: 60000, // refresh every 60s
  })

Helper functions:
- getDaysWaiting(createdAt: string): number
  return Math.floor((Date.now() - new Date(createdAt).getTime()) / 86400000)

- getAgeBadgeStyle(days: number): { color, background, border }
  0-2 days → green #4CFFA8 + rgba(76,255,168,0.08) border
  3-5 days → gold #C9A84C + rgba(201,168,76,0.08) border
  6+ days → red #ff4444 + rgba(255,68,68,0.12) border

- getCardBorderLeft(days: number): string
  0-2 → #4CFFA8
  3-5 → #C9A84C
  6+ → #ff4444

- formatCurrency(val: string | number): string
  return "R" + parseFloat(String(val)).toLocaleString("en-ZA", { minimumFractionDigits: 0, maximumFractionDigits: 0 })

Fulfill mutation:
  mutationFn: (orderId: string) =>
    apiRequest("POST", `/api/shopify/orders/${orderId}/fulfill`, {}).then(r => r.json())
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["/api/shopify/orders"] })
    toast({ title: "Order fulfilled ✅", description: "Shopify updated" })
    setFulfillModal({ open: false, orderId: null, orderNumber: "" })
  }
  onError: () => toast({ title: "Failed to fulfill", variant: "destructive" })

LAYOUT:

1. PAGE HEADER
   Title: "DELIVERY PIPELINE" — Rajdhani 36px bold gold #C9A84C letterSpacing 8px uppercase
   Subtitle: italic Cormorant 12px muted "Live Shopify orders · Unfulfilled & Paid · Sorted by urgency"
   Right side: RefreshCw button that calls queryClient.invalidateQueries({ queryKey: ["/api/shopify/orders"] })
   Below: if isMock → amber banner "MOCK DATA — Set SHOPIFY_DOMAIN + SHOPIFY_ADMIN_TOKEN env vars"

2. PIPELINE VALUE BAR (full-width card)
   Three stats in a row:
   - "TOTAL PIPELINE VALUE" → mask(formatCurrency(totalValue)) in Menlo 28px gold
   - "UNFULFILLED ORDERS" → mask(String(orders.length)) in Menlo 28px red #ff4444
   - "DAYS OLDEST ORDER" → mask(String(getDaysWaiting(orders[0]?.createdAt || new Date().toISOString()))) in Menlo 28px dynamic color via getAgeBadgeStyle

3. ORDER CARDS (one per order, sorted oldest first — already sorted by API)
   Each card:
   
   Container:
   - background: #0e0d10
   - border: 1px solid rgba(201,168,76,0.12)
   - border-left: 3px solid [getCardBorderLeft(daysWaiting)]
   - marginBottom: 12px
   - hover: translateY(-2px) transition
   
   Card top row:
   - Left: order number in Menlo 14px bold gold (#C9A84C)
   - Right: age badge "[N] days" styled via getAgeBadgeStyle
   
   Card middle row:
   - Customer initials: "[F].[L]." in Cormorant italic 18px cream (masked when isPrivate → "•.•.")
   - Items count: "[N] items" in 9px Rajdhani caps gold_dim
   - Total price: formatCurrency(totalPrice) in Menlo 16px bold cream (masked when isPrivate)
   - Date ordered: toLocaleDateString("en-ZA") in 9px mono gold_dim
   
   Card action row (border-top gold 0.1 opacity):
   - "MARK FULFILLED" button:
     - background: rgba(76,255,168,0.06)
     - border: 1px solid rgba(76,255,168,0.4)
     - color: #4CFFA8
     - fontSize: 9px, letterSpacing: 3px, uppercase, Helvetica Neue
     - CheckCircle2 icon left
     - onClick → setFulfillModal({ open: true, orderId: order.id, orderNumber: order.orderNumber })

4. EMPTY STATE (when orders.length === 0 after loading):
   Cormorant italic 32px cream: "All orders fulfilled"
   9px gold_dim caps: "Pipeline is clear"
   CheckCircle2 icon in green #4CFFA8 at 48px

5. CONFIRM FULFILL MODAL (Dialog from shadcn/ui):
   - Title: "Confirm Fulfilment"
   - Body: "Mark order [orderNumber] as fulfilled in Shopify? This action cannot be undone."
   - Two buttons: Cancel (gold_dark border) | CONFIRM FULFILL (green border, CheckCircle2 icon)
   - On confirm: fulfillMutation.mutate(fulfillModal.orderId)
   - Show Loader2 spinner when fulfillMutation.isPending

6. KEEP the existing TEAM CHAT (Discord iframe section) and WHATSAPP NOTIFICATIONS section
   These are already implemented in the file — do not remove them. Keep them below the order pipeline.
   The DISCORD_SERVER_ID const stays at the top of the file as is.
```

---

### TASK 3 — WAR ROOM HEADER (Live SAST Clock + ROBUSCA Status)

**Goal:** Add live SAST time, today's date, and "ROBUSCA ONLINE" status indicator to the AnalyticsStrip.

**File:** `client/src/components/AnalyticsStrip.tsx`

**Changes:**

1. Add `useEffect` and `useState` to imports from "react".

2. Add live clock state before the component's return:
```typescript
const [now, setNow] = useState(new Date());

useEffect(() => {
  const timer = setInterval(() => setNow(new Date()), 1000);
  return () => clearInterval(timer);
}, []);

const sastTime = now.toLocaleTimeString("en-ZA", {
  timeZone: "Africa/Johannesburg",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

const sastDate = now.toLocaleDateString("en-ZA", {
  timeZone: "Africa/Johannesburg",
  weekday: "short",
  day: "numeric",
  month: "short",
  year: "numeric",
}).toUpperCase();
```

3. Insert a new center-right section BETWEEN the stats section and the privacy toggle button. Add it inside the outer flex container (the `div.flex.items-center.gap-5.flex-1.justify-center.flex-wrap` already has the stats). After the stats div, add a new sibling `div` with `className="hidden lg:flex items-center gap-4 shrink-0"`:

```tsx
{/* Live clock + status */}
<div className="hidden lg:flex items-center gap-4 shrink-0">
  {/* ROBUSCA ONLINE status */}
  <div className="flex items-center gap-1.5">
    <span
      style={{
        width: "7px",
        height: "7px",
        borderRadius: "50%",
        background: "#4CFFA8",
        display: "inline-block",
        boxShadow: "0 0 6px rgba(76,255,168,0.8)",
        animation: "pulse 2s ease-in-out infinite",
      }}
    />
    <span
      style={{
        fontFamily: "'Helvetica Neue', sans-serif",
        fontSize: "9px",
        letterSpacing: "2.5px",
        textTransform: "uppercase",
        color: "#4CFFA8",
      }}
    >
      ROBUSCA ONLINE
    </span>
  </div>

  {/* Divider */}
  <div style={{ width: "1px", height: "20px", background: "rgba(201,168,76,0.2)" }} />

  {/* SAST clock */}
  <div className="flex flex-col items-end leading-tight">
    <span
      style={{
        fontFamily: "'Menlo', 'Monaco', monospace",
        fontSize: "13px",
        fontWeight: 600,
        color: "#C9A84C",
        letterSpacing: "1px",
      }}
    >
      {sastTime}
    </span>
    <span
      style={{
        fontFamily: "'Helvetica Neue', sans-serif",
        fontSize: "8px",
        letterSpacing: "2px",
        color: "#9a8a5a",
        textTransform: "uppercase",
      }}
    >
      {sastDate} · SAST
    </span>
  </div>
</div>
```

4. Add the pulse keyframe animation to `client/src/index.css` (append at the bottom):
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
```

---

### TASK 4 — CONTENT QUEUE IMPROVEMENTS

**Goal:** Add platform filter tabs, bulk approve, and proper status pills.

**File:** `client/src/pages/ContentQueue.tsx`

#### 4.4.1 — Platform filter tabs

Add a new second filter row (below the existing campaign/status filter) for platform:

```typescript
const PLATFORM_FILTERS = ["All", "Instagram", "Facebook", "TikTok", "LinkedIn", "Both"];
const [platformFilter, setPlatformFilter] = useState("All");
```

Apply platform filter in the `filtered` computation:
```typescript
const filtered = items.filter((item) => {
  // Existing status/campaign filter
  const statusMatch = (() => {
    if (activeFilter === "All") return true;
    const lower = activeFilter.toLowerCase();
    if (["draft", "approved", "posted", "rejected", "pending_approval"].includes(lower)) return item.status === lower;
    return item.campaign === activeFilter;
  })();
  // Platform filter
  const platformMatch = (() => {
    if (platformFilter === "All") return true;
    if (platformFilter === "Both") return item.platform === "both";
    return item.platform === platformFilter.toLowerCase() || item.platform === "both";
  })();
  return statusMatch && platformMatch;
});
```

Add the platform filter row UI below the existing campaign filter row (after the `hairline divider`):
```tsx
{/* Platform filter row */}
<div className="flex flex-wrap items-center gap-2" style={{ marginBottom: "8px" }}>
  <span style={{ fontSize: "9px", letterSpacing: "3px", textTransform: "uppercase", color: GOLD_DIM, fontFamily: "'Helvetica Neue', sans-serif", marginRight: "4px" }}>
    Platform
  </span>
  {PLATFORM_FILTERS.map((p) => (
    <button
      key={p}
      onClick={() => setPlatformFilter(p)}
      style={{
        background: platformFilter === p ? "rgba(201,168,76,0.12)" : "transparent",
        border: `1px solid ${platformFilter === p ? GOLD : GOLD_DARK}`,
        color: platformFilter === p ? CREAM : GOLD_DIM,
        padding: "5px 11px",
        fontSize: "9px",
        letterSpacing: "2px",
        textTransform: "uppercase",
        cursor: "pointer",
        fontFamily: "'Helvetica Neue', sans-serif",
        transition: "all 0.15s",
      }}
    >
      {p}
    </button>
  ))}
</div>
```

#### 4.4.2 — Status pills on content cards

**In `ContentCard` component**, add a proper status pill (replace or supplement the existing absolute-positioned badge). The pill system:

```typescript
const STATUS_CONFIG = {
  draft:            { label: "DRAFT",           color: "#9a8a5a", bg: "rgba(154,138,90,0.08)",    border: "rgba(154,138,90,0.25)" },
  pending_approval: { label: "PENDING APPROVAL", color: "#C9A84C", bg: "rgba(201,168,76,0.1)",    border: "rgba(201,168,76,0.4)"  },
  approved:         { label: "APPROVED",          color: "#4CFFA8", bg: "rgba(76,255,168,0.08)",   border: "rgba(76,255,168,0.4)"  },
  scheduled:        { label: "SCHEDULED",         color: "#5865F2", bg: "rgba(88,101,242,0.08)",   border: "rgba(88,101,242,0.4)"  },
  posted:           { label: "POSTED",            color: "#C9A84C", bg: "rgba(201,168,76,0.1)",    border: "rgba(201,168,76,0.4)"  },
  rejected:         { label: "REJECTED",          color: "#c14e3c", bg: "rgba(193,78,60,0.08)",    border: "rgba(193,78,60,0.4)"   },
};
```

Replace the three separate `isApproved`, `isRejected`, `isPosted` absolute badges with a single unified status pill using the config above. Keep the absolute positioning (top-right corner).

#### 4.4.3 — Bulk approve button

Add to `ContentQueue` component:

```typescript
const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
const { toast } = useToast();

const bulkApproveMutation = useMutation({
  mutationFn: async (ids: number[]) => {
    for (const id of ids) {
      await apiRequest("PATCH", `/api/content/${id}/status`, { status: "approved" }).then(r => r.json());
    }
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["/api/content"] });
    setSelectedIds(new Set());
    toast({ title: `${selectedIds.size} items approved ✅` });
  },
  onError: () => toast({ title: "Bulk approve failed", variant: "destructive" }),
});
```

Add bulk actions bar between filter rows and content list:
```tsx
{selectedIds.size > 0 && (
  <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px 14px", background: "rgba(201,168,76,0.06)", border: "1px solid rgba(201,168,76,0.2)", marginBottom: "8px" }}>
    <span style={{ fontFamily: "'Menlo', monospace", fontSize: "10px", color: GOLD, letterSpacing: "2px" }}>
      {selectedIds.size} SELECTED
    </span>
    <button
      onClick={() => bulkApproveMutation.mutate([...selectedIds])}
      disabled={bulkApproveMutation.isPending}
      style={{ background: "rgba(76,255,168,0.08)", border: "1px solid rgba(76,255,168,0.4)", color: "#4CFFA8", padding: "7px 14px", fontSize: "9px", letterSpacing: "2px", textTransform: "uppercase", cursor: "pointer", fontFamily: "'Helvetica Neue', sans-serif" }}
    >
      {bulkApproveMutation.isPending ? "Approving..." : "APPROVE ALL"}
    </button>
    <button
      onClick={() => setSelectedIds(new Set())}
      style={{ background: "transparent", border: `1px solid ${GOLD_DARK}`, color: GOLD_DIM, padding: "7px 14px", fontSize: "9px", letterSpacing: "2px", textTransform: "uppercase", cursor: "pointer", fontFamily: "'Helvetica Neue', sans-serif" }}
    >
      DESELECT
    </button>
  </div>
)}
```

Add a checkbox to each `ContentCard`'s top-left corner. Pass `selectedIds`, `onSelect` as props to `ContentCard`:
```typescript
// ContentCard receives additional props:
interface ContentCardProps {
  item: ContentItem;
  isSelected: boolean;
  onToggleSelect: (id: number) => void;
}
```

Add a small checkbox div in the card header top-left (before the platform/schedule metadata):
```tsx
<div
  onClick={() => onToggleSelect(item.id)}
  style={{
    width: "16px",
    height: "16px",
    border: `1px solid ${isSelected ? GOLD : GOLD_DARK}`,
    background: isSelected ? "rgba(201,168,76,0.2)" : "transparent",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  }}
>
  {isSelected && <Check className="w-3 h-3" style={{ color: GOLD }} />}
</div>
```

Update the `ContentQueue` render to pass these props:
```tsx
{filtered.map((item) => (
  <ContentCard
    key={item.id}
    item={item}
    isSelected={selectedIds.has(item.id)}
    onToggleSelect={(id) => setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    })}
  />
))}
```

---

### TASK 5 — AGENT NETWORK (Sync Button + Last Sync Timestamp)

**Goal:** Add a "Sync Messages" button and "Last synced: Nm ago" display.

**File:** `client/src/pages/AgentNetwork.tsx`

1. Add imports:
```typescript
import { useState, useEffect } from "react"; // already has these — check first
import { RefreshCw, Loader2 } from "lucide-react"; // add to existing lucide import
import { useMutation } from "@tanstack/react-query"; // add to existing tanstack import
import { queryClient, apiRequest } from "@/lib/queryClient"; // add if not present
import { useToast } from "@/hooks/use-toast"; // add if not present
```

2. Add to the `AgentNetwork` component function body (near the top, with other state):
```typescript
const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
const [timeAgoLabel, setTimeAgoLabel] = useState<string>("");
const { toast } = useToast();

// Update "X ago" label every 30s
useEffect(() => {
  if (!lastSyncTime) return;
  const update = () => {
    const diffMs = Date.now() - lastSyncTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffSecs = Math.floor(diffMs / 1000);
    if (diffSecs < 60) setTimeAgoLabel(`${diffSecs}s ago`);
    else if (diffMins < 60) setTimeAgoLabel(`${diffMins}m ago`);
    else setTimeAgoLabel(`${Math.floor(diffMins / 60)}h ago`);
  };
  update();
  const interval = setInterval(update, 30000);
  return () => clearInterval(interval);
}, [lastSyncTime]);

const syncMutation = useMutation({
  mutationFn: () => apiRequest("GET", "/api/agentmail/messages").then(r => r.json()),
  onSuccess: (data) => {
    setLastSyncTime(new Date());
    queryClient.invalidateQueries({ queryKey: ["/api/messages"] });
    toast({ title: "AgentMail synced ✅", description: `${Array.isArray(data) ? data.length : 0} messages fetched` });
  },
  onError: () => toast({ title: "Sync failed", variant: "destructive" }),
});
```

3. Find the AgentMail inboxes section header in the JSX (the section that shows the AgentMail inboxes). In that section's header row, add the sync button and timestamp. The section header likely has a title like "AGENTMAIL INBOXES" — add to its right side:

```tsx
{/* Right side of AgentMail section header */}
<div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
  {lastSyncTime && (
    <span style={{
      fontFamily: "'Menlo', monospace",
      fontSize: "9px",
      color: "#9a8a5a",
      letterSpacing: "1px",
    }}>
      Last synced: {timeAgoLabel}
    </span>
  )}
  <button
    onClick={() => syncMutation.mutate()}
    disabled={syncMutation.isPending}
    style={{
      display: "flex",
      alignItems: "center",
      gap: "6px",
      background: "transparent",
      border: "1px solid rgba(201,168,76,0.4)",
      color: "#C9A84C",
      padding: "6px 12px",
      fontSize: "9px",
      letterSpacing: "2px",
      textTransform: "uppercase",
      cursor: syncMutation.isPending ? "not-allowed" : "pointer",
      fontFamily: "'Helvetica Neue', sans-serif",
      opacity: syncMutation.isPending ? 0.6 : 1,
    }}
  >
    {syncMutation.isPending
      ? <Loader2 className="w-3 h-3 animate-spin" />
      : <RefreshCw className="w-3 h-3" />
    }
    {syncMutation.isPending ? "Syncing..." : "Sync Messages"}
  </button>
</div>
```

---

### TASK 6 — REVENUE ENGINE (MRR Tracker Widget)

**Goal:** Add an MRR tracker widget with current/target progress bar to the RevenueEngine tab.

**File:** `client/src/pages/RevenueEngine.tsx`

1. Add MRR state at the top of the `RevenueEngine` component function:
```typescript
const MONTHLY_TARGET = 333333; // R4,000,000/year ÷ 12
const [currentMRR, setCurrentMRR] = useState(0);
const [mrrInputVal, setMrrInputVal] = useState("0");
```

2. Add the MRR tracker widget as a new view tab option. In the view tabs array, add:
```typescript
{ id: "mrr", label: "MRR Tracker" }
```

3. Add the MRR tracker view panel:
```tsx
{view === "mrr" && (
  <div className="space-y-6">
    {/* Shopify month stats */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {[
        { label: "Orders This Month", value: mask("4"), color: "#C9A84C" },
        { label: "Revenue This Month", value: mask("R43,585"), color: "#4CFFA8" },
        { label: "Avg Order Value", value: mask("R10,896"), color: "#C9A84C" },
      ].map(kpi => (
        <div key={kpi.label} style={{ background: `${kpi.color}06`, border: `1px solid ${kpi.color}18`, padding: "16px" }}>
          <p style={{ fontSize: "8px", letterSpacing: "2px", textTransform: "uppercase", color: "#9a8a5a", marginBottom: "6px" }}>{kpi.label}</p>
          <p style={{ fontSize: "24px", fontFamily: "Menlo, monospace", color: kpi.color, fontWeight: 700 }}>{kpi.value}</p>
        </div>
      ))}
    </div>

    {/* MRR input + tracker */}
    <div style={{ background: "rgba(201,168,76,0.04)", border: "1px solid rgba(201,168,76,0.15)", padding: "20px" }}>
      <p style={{ fontSize: "9px", letterSpacing: "4px", textTransform: "uppercase", color: "#9a8a5a", marginBottom: "12px" }}>
        MRR TRACKER — TARGET: R333,333/MONTH (R4M/YEAR)
      </p>

      {/* Input row */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "20px" }}>
        <span style={{ fontFamily: "Menlo, monospace", fontSize: "16px", color: "#C9A84C" }}>R</span>
        <input
          type="number"
          value={mrrInputVal}
          onChange={(e) => {
            setMrrInputVal(e.target.value);
            const parsed = parseInt(e.target.value.replace(/[^0-9]/g, ""), 10);
            if (!isNaN(parsed)) setCurrentMRR(parsed);
          }}
          placeholder="Enter current MRR"
          style={{
            background: "rgba(0,0,0,0.4)",
            border: "1px solid rgba(201,168,76,0.3)",
            color: "#f5ecd0",
            fontFamily: "Menlo, monospace",
            fontSize: "20px",
            padding: "8px 12px",
            width: "200px",
            outline: "none",
          }}
        />
        <span style={{ fontSize: "10px", color: "#9a8a5a" }}>current MRR</span>
      </div>

      {/* Progress bar */}
      <div style={{ marginBottom: "12px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
          <span style={{ fontSize: "10px", fontFamily: "Menlo, monospace", color: "#C9A84C" }}>
            {mask(`R${currentMRR.toLocaleString("en-ZA")}`)}
          </span>
          <span style={{ fontSize: "10px", fontFamily: "Menlo, monospace", color: "#9a8a5a" }}>
            R{MONTHLY_TARGET.toLocaleString("en-ZA")}
          </span>
        </div>
        <div style={{ height: "8px", background: "rgba(201,168,76,0.1)", border: "1px solid rgba(201,168,76,0.2)", position: "relative", overflow: "hidden" }}>
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              height: "100%",
              width: `${Math.min((currentMRR / MONTHLY_TARGET) * 100, 100)}%`,
              background: currentMRR >= MONTHLY_TARGET ? "#4CFFA8" : currentMRR > MONTHLY_TARGET * 0.5 ? "#C9A84C" : "#c14e3c",
              transition: "width 0.4s ease",
            }}
          />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px" }}>
          <span style={{ fontSize: "9px", color: "#9a8a5a" }}>
            {Math.round((currentMRR / MONTHLY_TARGET) * 100)}% of monthly target
          </span>
          <span style={{ fontSize: "9px", color: "#9a8a5a" }}>
            Gap: {mask(`R${Math.max(MONTHLY_TARGET - currentMRR, 0).toLocaleString("en-ZA")}`)}
          </span>
        </div>
      </div>

      {/* Annual projection */}
      <div style={{ borderTop: "1px solid rgba(201,168,76,0.1)", paddingTop: "12px", display: "flex", gap: "32px" }}>
        <div>
          <p style={{ fontSize: "8px", letterSpacing: "2px", color: "#9a8a5a", textTransform: "uppercase" }}>Annual Run Rate</p>
          <p style={{ fontSize: "18px", fontFamily: "Menlo, monospace", color: "#4CFFA8", fontWeight: 700 }}>
            {mask(`R${(currentMRR * 12).toLocaleString("en-ZA")}`)}
          </p>
        </div>
        <div>
          <p style={{ fontSize: "8px", letterSpacing: "2px", color: "#9a8a5a", textTransform: "uppercase" }}>Target ARR</p>
          <p style={{ fontSize: "18px", fontFamily: "Menlo, monospace", color: "#9a8a5a", fontWeight: 700 }}>R4,000,000</p>
        </div>
        <div>
          <p style={{ fontSize: "8px", letterSpacing: "2px", color: "#9a8a5a", textTransform: "uppercase" }}>Status</p>
          <p style={{ fontSize: "18px", fontFamily: "Menlo, monospace", color: currentMRR >= MONTHLY_TARGET ? "#4CFFA8" : "#c14e3c", fontWeight: 700 }}>
            {currentMRR >= MONTHLY_TARGET ? "ON TARGET" : "BELOW TARGET"}
          </p>
        </div>
      </div>
    </div>
  </div>
)}
```

---

## 5. FILE CHANGE SUMMARY

| File | Action | Task |
|------|--------|------|
| `shared/schema.ts` | Add `approvals` table schema | 1 |
| `server/storage.ts` | Add `CREATE TABLE approvals` + `logApproval` + `getApprovals` methods | 1 |
| `server/routes.ts` | Add `/api/approvals` GET+POST, `/api/content/pending-approval` GET, `/api/shopify/orders` GET, `/api/shopify/orders/:id/fulfill` POST | 1, 2 |
| `client/src/pages/Approvals.tsx` | **CREATE NEW FILE** — full approvals workflow | 1 |
| `client/src/App.tsx` | Import Approvals, replace ComingSoonPage for approvals tab | 1 |
| `client/src/pages/DeliveryTeam.tsx` | **REWRITE** — live Shopify orders + fulfill flow (keep Discord + WhatsApp sections) | 2 |
| `client/src/components/AnalyticsStrip.tsx` | Add SAST clock + ROBUSCA status | 3 |
| `client/src/index.css` | Add `@keyframes pulse` | 3 |
| `client/src/pages/ContentQueue.tsx` | Add platform filter + bulk approve + status pill system | 4 |
| `client/src/pages/AgentNetwork.tsx` | Add Sync Messages button + last sync timestamp | 5 |
| `client/src/pages/RevenueEngine.tsx` | Add MRR tracker view tab | 6 |

---

## 6. IMPLEMENTATION NOTES & GOTCHAS

### TypeScript
- Run `npm run check` after all changes — fix any type errors before building
- `ContentItem` type from `@shared/schema` has `status: string` not a union — no casting needed
- `apiRequest` returns `Promise<Response>` — chain `.then(r => r.json())` for JSON body
- When iterating `Set<number>`, spread with `[...selectedIds]` before passing to mutation

### Imports
- `desc` is already imported from `drizzle-orm` in `server/storage.ts` — verify before adding
- `approvals` table must be added to the import in `server/storage.ts`: add to the existing import from `../shared/schema`
- `useToast` is at `@/hooks/use-toast` — this is correct for this repo
- `Dialog` components: `import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"`

### Styling
- DO NOT use Tailwind utility classes for colors — use inline `style={{}}` with the palette constants
- DO use Tailwind for layout (`className="flex items-center gap-2"`, `className="grid grid-cols-3"`, `className="space-y-4"`, `className="overflow-x-auto"`)
- The `font-mono` Tailwind class maps to `fontFamily: 'Menlo', monospace` — either works
- The `animate-spin` Tailwind class works for `Loader2` — keep using it

### Database migration
- The SQLite tables are created with `CREATE TABLE IF NOT EXISTS` in `server/storage.ts`
- Adding the `approvals` table to the `sqlite.exec()` block is sufficient — no migration needed
- The `data.db` file persists between restarts — existing data is safe

### Privacy toggle
- `isPrivate` from `usePrivacy()` — when true, wrap display values in `mask(value)`
- For caption text masking in Approvals: use CSS `filter: isPrivate ? "blur(4px)" : "none"` and `userSelect: isPrivate ? "none" : "auto"` on the caption container
- Customer initials in Delivery: `isPrivate ? "•.•." : `${order.customer.firstName}.${order.customer.lastName}.``

### Route ordering in server/routes.ts
- Express matches routes in order — `/api/content/pending-approval` MUST be defined BEFORE `/api/content/:id/status` to avoid `:id` matching "pending-approval"
- Add the pending-approval route at the TOP of the new routes block, before the fulfill route

### AgentMail sync
- `GET /api/agentmail/messages` already fetches from AgentMail API — the Sync button just calls this endpoint and invalidates the cache
- The existing `AgentNetwork.tsx` already has useQuery for `/api/messages` — after sync, invalidate that query key

---

## 7. RUN COMMANDS

### Development (local testing)
```bash
# Start dev server (port 5000)
npm run dev

# In a separate terminal — type check only
npm run check
```

### Production build + deploy
```bash
# 1. Type check first — fix all errors before building
npm run check

# 2. Build production bundle
npm run build

# 3. Deploy via pplx-tool (from repo root)
pplx-tool deploy_website
```

### Verify the build worked
```bash
# Start production server locally to verify
npm run start
# Then open http://localhost:5000 and check all 6 changed tabs
```

---

## 8. VERIFICATION CHECKLIST

After implementing all tasks, verify each item:

### Approvals Tab
- [ ] Tab shows pending content items (status: draft or pending_approval)
- [ ] Each card shows: image thumbnail, caption (blurred when private), platform badge, scheduled date
- [ ] APPROVE button → status changes to "approved" → item disappears from approvals list → appears in queue as approved
- [ ] REJECT button → modal opens → rejection note saved → item disappears from approvals list
- [ ] EDIT button → modal opens → caption editable → on save, caption updated
- [ ] Bulk select checkboxes work
- [ ] APPROVE ALL button approves all selected items
- [ ] Approval log section shows history
- [ ] Privacy toggle masks caption text

### Delivery Tab
- [ ] Live orders load from `/api/shopify/orders`
- [ ] Orders sorted oldest first (most urgent at top)
- [ ] Color coding: green (0-2d), gold (3-5d), red (6+d) via border-left and age badge
- [ ] Total pipeline value shown at top
- [ ] "MARK FULFILLED" button per order → confirmation modal → on confirm, calls `/api/shopify/orders/:id/fulfill`
- [ ] Privacy toggle masks amounts and customer initials
- [ ] Discord team chat section still present
- [ ] WhatsApp section still present

### War Room Header
- [ ] Live SAST time updates every second (HH:MM:SS format)
- [ ] Today's date shown in SAST timezone
- [ ] "ROBUSCA ONLINE" label with pulsing green dot
- [ ] Elements hidden on mobile (lg:flex), visible on desktop

### Content Queue
- [ ] Platform filter tabs (All/Instagram/Facebook/TikTok/LinkedIn/Both) work
- [ ] Platform filter correctly filters the list
- [ ] Status pills use the new unified STATUS_CONFIG (5 states visible)
- [ ] Bulk select checkboxes work on each card
- [ ] Bulk actions bar appears when items selected
- [ ] APPROVE ALL bulk button works

### Agent Network
- [ ] "Sync Messages" button visible near AgentMail section header
- [ ] Clicking Sync calls GET /api/agentmail/messages
- [ ] Loading spinner shows during sync
- [ ] "Last synced: Xm ago" label appears after first sync
- [ ] Label updates (auto-refreshes the "ago" text)

### Revenue Engine
- [ ] "MRR Tracker" appears as a new view tab
- [ ] Input field for current MRR works
- [ ] Progress bar fills proportionally (current / 333,333)
- [ ] Bar color: red below 50% target, gold above 50%, green at/above 100%
- [ ] Annual run rate calculated correctly (currentMRR × 12)
- [ ] Gap shows remaining to target
- [ ] Privacy toggle masks all monetary values

---

## 9. GIT COMMIT MESSAGE TEMPLATES

Use one commit per task:

```
feat(approvals): build full content approval workflow

- Add approvals SQLite table to schema + storage
- Add /api/approvals GET+POST routes
- Add /api/content/pending-approval route  
- Create Approvals.tsx with card layout, bulk select, approve/reject/edit
- Wire into App.tsx replacing ComingSoonPage placeholder
- Privacy toggle masks caption text
```

```
feat(delivery): live Shopify orders pipeline + fulfill flow

- Add /api/shopify/orders route with Shopify Admin API integration
- Add /api/shopify/orders/:id/fulfill route
- Rewrite DeliveryTeam.tsx with live data, color-coded urgency
- Add Mark Fulfilled button with confirmation modal
- Privacy toggle masks amounts and customer initials
- Keep Discord + WhatsApp sections intact
```

```
feat(header): live SAST clock + ROBUSCA status indicator

- Add useEffect clock state to AnalyticsStrip.tsx
- Show HH:MM:SS in Africa/Johannesburg timezone (updates every second)
- Add ROBUSCA ONLINE status with pulsing green dot animation
- Add @keyframes pulse to index.css
- Hidden on mobile (lg:flex), visible on desktop
```

```
feat(queue): platform filter tabs + bulk approve + status pills

- Add platform filter row (All/Instagram/Facebook/TikTok/LinkedIn/Both)
- Unify status badges using STATUS_CONFIG (5 states: draft/pending/approved/scheduled/posted/rejected)
- Add per-card selection checkboxes
- Add bulk actions bar with APPROVE ALL button
- Bulk mutation iterates selected IDs and updates each
```

```
feat(agents): sync messages button + last sync timestamp

- Add syncMutation calling GET /api/agentmail/messages
- Add lastSyncTime state + timeAgoLabel that updates every 30s
- Add Sync Messages button with Loader2 spinner during pending state
- Show "Last synced: Xm ago" label after first successful sync
```

```
feat(revenue): MRR tracker widget with progress bar

- Add MRR Tracker as 5th view tab in RevenueEngine
- Input field for current MRR (React state, no persistence needed)
- Progress bar: current / R333,333 monthly target
- Color: red <50%, gold 50-99%, green ≥100%
- Shopify month stats KPI cards
- Annual run rate + gap calculations
- Privacy toggle masks all amounts
```

---

## 10. ENVIRONMENT VARIABLES (OPTIONAL — for live integrations)

These are already handled gracefully (fallback to mock data when missing):

```bash
# Shopify (Delivery tab live orders)
SHOPIFY_DOMAIN=studexmeat.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxxx

# Already configured (existing routes use these):
OPENAI_API_KEY=sk-...
HIGGSFIELD_KEY_ID=...
HIGGSFIELD_KEY_SECRET=...
AGENTMAIL_TOKEN=am_us_...
```

All env vars are read server-side only (`server/routes.ts`) — never expose in client code.

---

*End of AGENTS.md — all tasks are fully specified. Execute in order, verify each checklist before committing.*
