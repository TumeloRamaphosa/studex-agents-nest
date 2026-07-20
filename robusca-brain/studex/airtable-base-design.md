# 📊 Airtable Base Design — StudEx Content & Operations
_For studexmeat.com | Naledi Influencer Pipeline_

## Base Name: "StudEx HQ"

---

## Table 1: Content Calendar 🗓️

| Field | Type | Notes |
|-------|------|-------|
| Post Title | Single line text | Short descriptor |
| Status | Single select | Brief → Generating → Ready → Scheduled → Published |
| Platform | Multiple select | TikTok, Instagram, Facebook, X |
| Post Format | Single select | Image, Carousel, Reel, Story |
| Campaign | Link to Table 3 | e.g. "Easter 2026" |
| Product Featured | Link to Table 2 | Links to product SKU |
| Publish Date | Date | With time |
| Caption (TikTok) | Long text | Auto-generated |
| Caption (Instagram) | Long text | Auto-generated |
| Caption (Facebook) | Long text | Auto-generated |
| Hashtags | Long text | Platform-specific |
| Image URL | URL | Google Drive link |
| Video URL | URL | Google Drive link |
| Blotato Post ID | Single line text | For tracking scheduled posts |
| Reach | Number | Filled after publishing |
| Likes | Number | |
| Comments | Number | |
| Shares | Number | |
| Link Clicks | Number | |
| Engagement Rate | Formula | (Likes+Comments+Shares)/Reach |
| Notes | Long text | |

---

## Table 2: Products 🛒

| Field | Type | Notes |
|-------|------|-------|
| Product Name | Single line text | e.g. "Sliced Biltong 250g" |
| SKU | Single line text | |
| Category | Single select | Biltong, Droëwors, Gift Box, Bundle |
| Price | Currency | |
| Stock Level | Number | Synced from store |
| Units Sold (7 days) | Number | Synced from store |
| Units Sold (30 days) | Number | |
| Revenue (30 days) | Currency | |
| Store URL | URL | |
| Product Image | Attachment | |
| Priority | Single select | High, Medium, Low |
| Notes | Long text | |

---

## Table 3: Campaigns 📣

| Field | Type | Notes |
|-------|------|-------|
| Campaign Name | Single line text | e.g. "Easter 2026" |
| Theme | Single line text | |
| Start Date | Date | |
| End Date | Date | |
| Status | Single select | Planning, Active, Complete |
| Content Posts | Link to Table 1 | All posts in this campaign |
| Total Reach | Rollup | Sum of Reach from linked posts |
| Total Clicks | Rollup | Sum of Link Clicks |
| Budget | Currency | |
| Revenue Attributed | Currency | |
| ROI | Formula | Revenue/Budget |
| Notes | Long text | |

---

## Table 4: Store Sales (Daily) 📈

| Field | Type | Notes |
|-------|------|-------|
| Date | Date | |
| Orders | Number | |
| Revenue | Currency | |
| New Customers | Number | |
| Returning Customers | Number | |
| Top Product | Link to Table 2 | |
| Traffic Source | Single select | Social, Email, Direct, Paid |
| Cart Abandonment Rate | Percent | |
| Notes | Long text | |

---

## Table 5: Naledi Asset Library 🖼️

| Field | Type | Notes |
|-------|------|-------|
| Asset Name | Single line text | |
| Type | Single select | Reference Photo, Generated Image, Video, Composite |
| Campaign | Link to Table 3 | |
| Product | Link to Table 2 | |
| Drive URL | URL | Google Drive link |
| Status | Single select | Draft, Approved, In Use, Archived |
| Created Date | Date | |
| Notes | Long text | |

---

## Automation Ideas (N8n → Airtable)

1. **New content trigger:** When image generated in Drive → create record in Table 1 + Table 5
2. **Daily sales sync:** Every morning pull store data → add row to Table 4
3. **Post published:** When Blotato confirms post live → update Table 1 status to "Published"
4. **Performance check:** Every 24hrs after publish → pull engagement stats → update Table 1
5. **Low stock alert:** When Table 2 stock < threshold → notify on Discord
6. **Weekly report:** Every Friday → aggregate Tables 1, 2, 4 → send summary to Discord

---

## To Get Started
1. Share your Airtable Personal Access Token
   - Go to: https://airtable.com/create/tokens
   - Scopes needed: data.records:read, data.records:write, schema.bases:read, schema.bases:write
2. I'll create the base + all tables programmatically
3. Connect N8n to Airtable using the token
