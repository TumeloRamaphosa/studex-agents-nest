# Kanan Band — Delivery OS Visual Identity
**Version:** 1.0 | **Date:** 2026-06-29 | **Author:** Naledi CMO (Studex Meat)

> "Cattle ranch meets Bloomberg terminal." — This is not generic dark mode. This is Kanan Band: premium dark-ops for a South African premium meat brand.

---

## 1. Design Philosophy

Kanan Band draws from two visual worlds colliding:
- **Ranch:** leather textures, warm wood tones, rawhide, iron rivets, amber lantern light
- **Terminal:** data density, monospace precision, status glows, live counters

The result: an ops board that feels like Studex is running a serious machine — not a hobby butchery.

---

## 2. Color Palette

### Core Palette

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Primary Background | **Biltong Black** | `#0a0505` | Board/app background |
| Card Background | **Charred Oak** | `#14100e` | Kanban card fill |
| Card Hover | **Burnished Bark** | `#1c1512` | Card hover state |
| Elevated Surface | **Aged Leather** | `#221810` | Modals, dropdowns |
| Subtle Border | **Iron Seam** | `#2d2018` | Card outline, dividers |
| Active Border | **Saddle Stitch** | `#4a3520` | Active/focused borders |

### Accent Colors

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Primary Accent | **Ranch Gold** | `#d4a017` | CTAs, badges, highlights |
| Secondary Accent | **Amber Flame** | `#f59e0b` | Hover states, glows |
| Warm Highlight | **Honey Glow** | `#fbbf24` | Critical alerts, live data |
| Text Primary | **Cream Linen** | `#f5f0e8` | Headings, primary text |
| Text Secondary | **Dusty Hide** | `#b8a898` | Body text, descriptions |
| Text Muted | **Ash** | `#7a6a5a` | Timestamps, metadata |

### Status Colors (Delivery Stages)

| Stage | Name | Hex | Emoji | Usage |
|-------|------|-----|-------|-------|
| `NEW_ORDER` | Rust Red | `#8b2500` | 📥 | New Order column |
| `PACKED` | Amber Gold | `#92400e` | 📦 | Packed column |
| `DISPATCHED` | Forge Orange | `#c2410c` | 🚚 | Dispatched column |
| `IN_TRANSIT` | Ember | `#dc2626` | 🔥 | Active delivery |
| `ARRIVED` | Signal Green | `#16a34a` | 🏁 | Arrived at address |
| `DELIVERED` | Done Green | `#15803d` | ✅ | Delivered column |
| `CANCELLED` | Ash Red | `#57534e` | 🚫 | Cancelled column |
| `DELAYED` | Alert Amber | `#d97706` | ⚠️ | Delayed flag |

### Urgency Colors (ETA Badges)

| Urgency | Condition | Hex | Indicator |
|---------|-----------|-----|-----------|
| 🟢 Low | ETA > 2 hours | `#22c55e` | Green dot |
| 🟡 Medium | ETA 1–2 hours | `#f59e0b` | Amber dot |
| 🔴 High | ETA < 1 hour | `#ef4444` | Red dot + pulse |

### Company Border Colors

| Company | Border Color | Hex |
|---------|-------------|-----|
| **Dinkoko Pty** | Deep Rust Red | `#7f1d1d` |
| **My Courier** | Steel Blue | `#1e3a5f` |
| **Unassigned** | Iron Gray | `#374151` |

---

## 3. Typography

### Font Stack

**Headings (display):** `Bebas Neue` — Google Fonts
- All-caps, ultra-condensed, maximum impact
- Used for: column headers, card titles, section labels
- Fallback: `'Oswald', 'Impact', sans-serif`

**Sub-headings / Labels:** `Barlow Condensed` — Google Fonts
- Bold, industrial feel, highly legible at small sizes
- Weight: 600–700
- Used for: badge labels, category tags, button text
- Fallback: `'Arial Narrow', 'Impact', sans-serif`

**Body / Data:** `Source Sans 3` — Google Fonts
- Clean, readable, professional
- Weight: 400 (body), 600 (emphasis)
- Used for: descriptions, addresses, item lists
- Fallback: `'Helvetica Neue', Arial, sans-serif`

**Monospace (IDs + Timestamps):** `JetBrains Mono` — Google Fonts
- Sharp, technical, unmistakable
- Used for: order numbers, tracking IDs, memory log timestamps
- Weight: 400
- Fallback: `'Courier New', monospace`

### Type Scale

```
Display:    48px / Bebas Neue / line-height: 1.0   — Board title
H1:         32px / Bebas Neue / line-height: 1.1   — Column headers
H2:         20px / Barlow Condensed 600 / lh: 1.2 — Card title
H3:         14px / Barlow Condensed 600 / lh: 1.3 — Badge labels
Body:       14px / Source Sans 3 400 / lh: 1.5    — Description text
Caption:    12px / Source Sans 3 400 / lh: 1.4    — Metadata, timestamps
Mono:       12px / JetBrains Mono / lh: 1.4       — Order #, timestamps
```

---

## 4. Icon Strategy

### Emoji Status Icons (Primary — Kanban Columns)

These emoji are the PRIMARY status markers. They are large (24px), positioned in column headers and card top-corners.

| Stage | Emoji | Unicode | Usage |
|-------|-------|---------|-------|
| New Order | 📥 | INBOX TRAY | Column + card badge |
| Packed | 📦 | PACKAGE | Column + card badge |
| Dispatched | 🚚 | DELIVERY TRUCK | Column + card badge |
| In Transit | 🔥 | FIRE | Live card indicator |
| Arrived | 🏁 | CHECKERED FLAG | Driver arrived |
| Delivered | ✅ | WHITE HEAVY CHECK MARK | Done column |
| Cancelled | 🚫 | NO ENTRY | Cancelled column |
| Delayed | ⚠️ | WARNING | Alert badge |

### Custom SVG Icons (Delivery Board — Required Set)

All SVG icons use `currentColor` so they inherit text color. Stroke-based, 24×24 viewBox, 1.5px stroke weight.

| Icon Name | Description | When Used |
|-----------|-------------|-----------|
| `icon-meat.svg` | Stylized chop/steak silhouette | Brand mark on cards |
| `icon-clock.svg` | Analog clock face | ETA display |
| `icon-phone.svg` | Mobile phone | Driver phone field |
| `icon-map-pin.svg` | Location pin | Customer address |
| `icon-thermometer.svg` | Thermometer | Cold chain indicator |
| `icon-truck.svg` | Delivery truck (sharp/geometric) | Dispatched column |
| `icon-location.svg` | GPS crosshairs | Tracking location |
| `icon-bell.svg` | Alert bell | Escalation flag |
| `icon-dinkoko.svg` | "D" lettermark | Dinkoko company badge |
| `icon-my-courier.svg` | "MC" lettermark | My Courier company badge |
| `icon-expand.svg` | Down chevron | Memory log expand |
| `icon-collapse.svg` | Up chevron | Memory log collapse |
| `icon-agent.svg` | Robot head | Agent-actor tag in memory log |
| `icon-human.svg` | Person silhouette | Human-actor tag in memory log |

---

## 5. Card Design — Exact Layout Spec

### Card Anatomy (top → bottom)

```
┌─────────────────────────────────────────────────────────┐
│ [COMPANY BADGE]  [STATUS EMOJI]  [ETA BADGE]   [PRIORITY]│  ← Card Header (40px)
│─────────────────────────────────────────────────────────│
│ ORDER #STUD-{{number}}                                   │  ← Order ID (JetBrains Mono, 12px)
│ {{customer_name}}                                       │  ← Customer Name (Barlow Condensed 600, 18px)
│ {{address_line_1}}                                      │  ← Address (Source Sans 3, 13px)
│ {{address_city}}                                        │  ← City (Source Sans 3, 13px, muted)
│─────────────────────────────────────────────────────────│
│ 🛒 {{item_count}} items · {{weight_kg}}kg               │  ← Items summary (12px, muted)
│────────────────────                                     │
│ ▼ Memory Log (collapsed — click to expand)              │  ← Collapsed state
│                                                         │
│ [Driver: {{driver_name}} · {{driver_phone}}]            │  ← Footer (driver info, click-to-call)
└─────────────────────────────────────────────────────────┘
```

### Left Border Color Coding

4px left border, full card height. Color determined by `assignedCompany`:
- **Dinkoko Pty:** `#7f1d1d` (deep rust red)
- **My Courier:** `#1e3a5f` (steel blue)
- **Unassigned:** `#374151` (iron gray, dashed border)

### Card Dimensions

| Property | Value |
|----------|-------|
| Width | 280px (fixed) |
| Min Height | 160px |
| Border Radius | 6px (top-right, bottom-right) |
| Border Radius (left) | 4px |
| Background | `#14100e` |
| Box Shadow (default) | `0 2px 8px rgba(0,0,0,0.4)` |
| Box Shadow (hover) | `0 4px 16px rgba(212,160,23,0.15)` |
| Box Shadow (dragging) | `0 8px 32px rgba(212,160,23,0.25), 0 0 0 2px #d4a017` |

### Memory Log — Collapsed State

Collapsed (default):
```
▼ Memory (3)
```
- Font: Source Sans 3, 12px, muted color
- Chevron icon (expand SVG) pointing down
- Count of log entries shown in parentheses

Expanded (on click):
```
▲ Memory (3)
────────────────────────────────
[08:42] 🤖 Charlie: Order assigned to Dinkoko
[08:45] 👤 Tumelo: Updated driver phone number
[09:10] 🤖 Delivery Agent: Client notified via WhatsApp
```
- Full log visible, max-height 200px, scrollable
- Each entry: `[HH:MM] [ACTOR_ICON] [Actor]: [Message]`
- Actor icons: 🤖 for agents, 👤 for humans
- Newest entries at top
- Background: `#1c1512`, inset shadow
- Collapse on second click or outside click

### ETA Badge Placement

Positioned top-right of card header:
- 🟢 `14:30` — green dot prefix, `#22c55e` text
- 🟡 `13:45` — amber dot prefix, `#f59e0b` text
- 🔴 `12:50` — red dot prefix, `#ef4444` text, subtle pulse animation
- Gray fallback: `ETA: --` when no ETA set

---

## 6. Column Header Design

Each column header bar:

```
┌──────────────────────────────────────────────────┐
│  [EMOJI]  COLUMN TITLE              [COUNT BADGE]│  ← Header bar, 48px tall
│  ═══════════════════════════════════════════════ │  ← Glow underline (4px)
└──────────────────────────────────────────────────┘
```

### Column Header Properties

| Column | Emoji | Background | Underline Glow | Count Badge Color |
|--------|-------|------------|----------------|-------------------|
| 📥 New Order | `#8b2500` | Rust red | `rgba(139,37,0,0.6)` | `#8b2500` |
| 📦 Packed | `#92400e` | Amber gold | `rgba(146,64,14,0.6)` | `#92400e` |
| 🚚 Dispatched | `#c2410c` | Forge orange | `rgba(194,65,12,0.6)` | `#c2410c` |
| 🏁 Delivered | `#16a34a` | Done green | `rgba(22,163,74,0.6)` | `#16a34a` |
| ✅ Done | `#15803d` | Settled green | `rgba(21,128,61,0.4)` | `#15803d` |
| 🚫 Cancelled | `#57534e` | Ash gray | none | `#57534e` |

**Count Badge:** Circular, 28px diameter, background matches column color, text `#f5f0e8`. Shows number of cards in column. Pulses briefly when count changes.

**Glow Underline:** 4px bar at bottom of header, color = column color, with `box-shadow: 0 0 12px [column-color-alpha]`.

---

## 7. Motion & Animation

### Card Drag Feedback

- **On grab:** Scale to `1.03`, box-shadow expands with gold tint, cursor becomes `grabbing`
- **While dragging:** Opacity `0.9`, slight rotation `±2deg` (random), ghost outline left behind in original position
- **On drop:** Scale back to `1.0`, brief gold border flash (`200ms`), shadow settles

### New Card Entrance Animation

```
@keyframes cardEntrance {
  0%   { opacity: 0; transform: translateY(-12px) scaleY(0.95); }
  60%  { opacity: 1; transform: translateY(2px) scaleY(1.01); }
  100% { opacity: 1; transform: translateY(0) scaleY(1); }
}
```
- Duration: `350ms`
- Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)` (slight spring)
- New card glows gold briefly on entrance (box-shadow pulse)

### Status Change Pulse

When a card moves between columns:
1. Card briefly scales to `1.02` (`150ms`)
2. Gold border appears (`200ms`, `rgba(212,160,23,0.8)`)
3. Border fades, card settles (`300ms`)
4. Column header count badge pulses (scale `1.2 → 1.0`, `400ms`)

### Memory Log Slide-Down

```
@keyframes memoryExpand {
  0%   { opacity: 0; max-height: 0; transform: translateY(-4px); }
  100% { opacity: 1; max-height: 200px; transform: translateY(0); }
}
```
- Duration: `250ms`
- Easing: `ease-out`
- Chevron rotates 180° during animation
- Scrollbar appears if content exceeds 200px

### Live / In-Transit Card

Cards in `DISPATCHED` or `IN_TRANSIT` stage have a subtle amber pulse on the left border:
```
@keyframes transitPulse {
  0%, 100% { border-left-color: #c2410c; }
  50%       { border-left-color: #f59e0b; }
}
```
- Duration: `2s`, infinite, ease-in-out
- Applied only to cards in active delivery stages

### Delayed Card Alert

Cards flagged as delayed get:
- Red left border (overrides company color)
- `⚠️ DELAYED` badge in header
- Subtle red background tint `rgba(239,68,68,0.08)`
- Gentle shake animation on initial flag: `translateX(±3px)`, 3 oscillations, `400ms`

---

## 8. Background Texture

Board background: `#0a0505` with a subtle noise texture overlay.

**Implementation (CSS):**
```css
/* SVG noise filter as CSS pseudo-element */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
  opacity: 0.3;
}
```

**Column backgrounds:** Slight gradient — darker at top, `5%` lighter at bottom — to give depth.

---

## 9. CSS Custom Properties (Token Reference)

```css
:root {
  /* Backgrounds */
  --kb-bg:           #0a0505;
  --kb-card-bg:      #14100e;
  --kb-card-hover:   #1c1512;
  --kb-elevated:     #221810;
  --kb-border:       #2d2018;
  --kb-border-active:#4a3520;

  /* Accents */
  --kb-gold:         #d4a017;
  --kb-amber:        #f59e0b;
  --kb-honey:        #fbbf24;
  --kb-cream:        #f5f0e8;
  --kb-hide:         #b8a898;
  --kb-ash:          #7a6a5a;

  /* Company colors */
  --kb-dinkoko:      #7f1d1d;
  --kb-my-courier:   #1e3a5f;
  --kb-unassigned:   #374151;

  /* Column stage colors */
  --kb-stage-new:    #8b2500;
  --kb-stage-packed: #92400e;
  --kb-stage-dispatch:#c2410c;
  --kb-stage-transit:#dc2626;
  --kb-stage-arrived:#16a34a;
  --kb-stage-done:   #15803d;
  --kb-stage-cancelled:#57534e;
  --kb-stage-delayed:#d97706;

  /* Urgency */
  --kb-urgency-low:  #22c55e;
  --kb-urgency-med:  #f59e0b;
  --kb-urgency-high: #ef4444;

  /* Typography */
  --font-display:    'Bebas Neue', 'Oswald', Impact, sans-serif;
  --font-label:     'Barlow Condensed', 'Arial Narrow', sans-serif;
  --font-body:      'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
  --font-mono:      'JetBrains Mono', 'Courier New', monospace;
}
```

---

## 10. Figma / Design Tool Export Notes

When handing off to a designer or exporting for web:

- **ViewBox:** All icons 24×24
- **Colors:** Use exact hex values from this document — DO NOT approximate
- **Font loading:** Load Google Fonts in `<head>`:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
  ```
- **Accessibility:** All text must maintain 4.5:1 contrast ratio on card backgrounds
- **Dark mode only:** This design system is purpose-built for dark environments. Light mode not supported.

---

*Compiled by Naledi CMO — Studex Meat Delivery OS — 2026-06-29*
