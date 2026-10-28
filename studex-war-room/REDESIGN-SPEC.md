# War Room — Design Taste Redesign Spec

**Applied Framework:** design-taste-frontend v2.0
**Dials:** VARIANCE 6 · MOTION 6 · DENSITY 8
**Aesthetic Direction:** Ops Command Center — Bloomberg terminal meets sci-fi bridge

---

## 1. Design Audit — Current State

### What Works
- Orbitron display font is *perfect* for a command center (keep it)
- Amber on dark (#d4a017 on #080c14) is a strong accent system
- The 60px nav + sidebar + main canvas + bottom panels structure is sound
- Status indicators, live dots, glow effects all add atmosphere

### What Needs Fix (Anti-Slop Review)
- ❌ Sidebar "QUICK ACCESS" buttons use marketing copy ("Daily Log", "Brand Bible")
- ❌ Labels mixed case ("GRAPH LEGEND" vs "StudEx OS Hub" — one uppercase, one title case)
- ❌ Border radius inconsistency — some 8px, some not defined
- ❌ No GSAP — all animations are CSS-only, causing jank
- ❌ Spacing is arbitrary px values, not the 8px grid
- ❌ `--text-dim` color is `#7a8099` — too purple, should be warmer dim amber
- ❌ Cards lack `box-shadow` depth — look flat
- ❌ Bottom panels have no visual separation — bleed into each other
- ❌ No motion on data updates (KPIs should flash/pulse when data refreshes)
- ❌ "blocked" state on quick-links is styled with a strikethrough but no visual affordance

---

## 2. Color System Upgrade

**Apply strict semantic color map:**

```css
:root {
  /* Backgrounds — cold blue-black, 3-step temperature */
  --bg-primary:    #070b12;
  --bg-surface:   #0d1422;
  --bg-elevated:  #111927;

  /* Borders — warm-tinted, 2-step */
  --border-subtle:  rgba(212, 160, 23, 0.10);
  --border-active:  rgba(212, 160, 23, 0.30);
  --border-bright:  rgba(212, 160, 23, 0.60);

  /* Text — warm whites, not cold */
  --text-primary:   #f0f0f5;
  --text-secondary: #a0a8c0;
  --text-dim:       #6a7090;

  /* Accent — keep amber */
  --accent:         #d4a017;
  --accent-light:   #ffcc44;
  --accent-dim:     #8b6914;
  --accent-glow:    rgba(212, 160, 23, 0.15);

  /* Semantic status */
  --status-ok:      #22c55e;
  --status-warn:    #f59e0b;
  --status-crit:    #ef4444;
  --status-info:    #3b82f6;
  --status-offline: #4a5568;
}
```

---

## 3. Typography Upgrade

**Keep Orbitron for display. Add IBM Plex Mono for data labels.**

```css
--font-display: 'Orbitron', sans-serif;        /* keep */
--font-mono:    'IBM Plex Mono', monospace;    /* replace Share Tech Mono */
--font-body:    'Inter', sans-serif;           /* keep */
```

**Scale — enforce strictly:**
```
.nav-title:     Orbitron 18px 900 / letter-spacing: 4px / color: --accent
.sidebar-title: IBM Plex Mono 9px 500 / UPPERCASE / letter-spacing: 2px / color: --text-dim
.panel-label:   IBM Plex Mono 10px 500 / UPPERCASE / letter-spacing: 1.5px / color: --text-dim
.kpi-value:      Orbitron 32px 700 / color: --text-primary
.kpi-label:     IBM Plex Mono 9px 400 / UPPERCASE / letter-spacing: 1px / color: --text-dim
.agent-name:    Inter 13px 600 / color: --text-primary
.status-text:   IBM Plex Mono 10px 400 / color: --text-secondary
```

---

## 4. Spacing System (8px Grid)

Audit all padding/margin values and snap to grid:

| Token | Value | Use |
|-------|-------|-----|
| `--space-1` | 4px | Icon padding, tight gaps |
| `--space-2` | 8px | Button padding-x, badge padding |
| `--space-3` | 12px | Compact component padding |
| `--space-4` | 16px | Standard component padding |
| `--space-5` | 24px | Card padding, section gaps |
| `--space-6` | 32px | Panel padding |
| `--space-7` | 48px | Section margins |
| `--space-8` | 64px | Layout gutters |

---

## 5. Component Upgrades

### Card / Panel
```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: var(--space-5);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.5),
    0 1px 0 var(--border-subtle) inset,
    0 -1px 0 rgba(212, 160, 23, 0.05) inset; /* subtle top glow */
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  border-color: var(--border-active);
  box-shadow:
    0 12px 40px rgba(0, 0, 0, 0.6),
    0 0 20px var(--accent-glow),
    0 1px 0 var(--border-active) inset;
}
```

### Sidebar
- Width: 240px (keep)
- Section dividers: 1px `--border-subtle` with `--space-5` margin
- Legend dots: 8px diameter with 2px glow ring on hover
- Quick links: `--space-3` vertical padding, left border accent on hover

### Bottom Panel Strip
- Add top border: `1px solid var(--border-subtle)` with `--accent` left accent on active panel
- Tabs: IBM Plex Mono 9px UPPERCASE, active tab has `--accent` bottom border (2px) + `--accent` text color
- KPI cards: grid layout, `--space-4` gap, `border-radius: 6px`

### Navigation HUD
- Keep height 60px
- Add `backdrop-filter: blur(12px)` for glassmorphism over canvas
- Status indicators in right cluster: 8px pulsing dots (green/amber/red)
- Live clock: IBM Plex Mono 12px, --text-secondary

---

## 6. Motion Design (GSAP)

### Entrance Animation (on mount)
```javascript
const tl = gsap.timeline();
tl.from('.nav-hud',    { opacity: 0, y: -20, duration: 0.4, ease: 'power2.out' })
  .from('.sidebar-left', { opacity: 0, x: -20, duration: 0.4, ease: 'power2.out' }, '-=0.2')
  .from('.app-main',    { opacity: 0, duration: 0.5, ease: 'power2.out' }, '-=0.1')
  .from('.bottom-panel', { opacity: 0, y: 20, duration: 0.4, ease: 'power2.out' }, '-=0.3');
```

### KPI Data Update Flash
```javascript
// When a KPI value changes, flash it amber then settle
const flashKPI = (element) => {
  gsap.to(element, { color: 'var(--accent-light)', duration: 0.1, yoyo: true, repeat: 1 });
};
```

### Node Selection
```javascript
// Selected node: scale up 1.05 + amber glow ring
// Deselect: scale back + remove glow
```

### Agent Cards (NPC Dock)
```javascript
// New activity: slide in from right + brief amber flash
gsap.from('.agent-card.new', {
  opacity: 0, x: 20, duration: 0.3, ease: 'power2.out',
  onComplete: () => gsap.to('.agent-card.new', { opacity: 1, duration: 0.2 })
});
```

---

## 7. Layout Refinements

### Bottom Panel — Split Logic
```
┌─────────────────────┬──────────────────┬─────────────────┐
│  OPS / KPIs         │  COMMS / AGENTS  │  INTEL / FEED   │
│  (DeliveryKPIs)      │  (AgentPanel)   │  (IntelPanel)   │
│  Grid of 6 KPI cards │ Live agent list │ Activity feed   │
└─────────────────────┴──────────────────┴─────────────────┘
```
Each section gets a `--space-3` left border accent when active.

### Sidebar Quick Links — Status Styling
```css
.quick-link {
  font-family: var(--font-mono);
  font-size: 10px;
  text-transform: UPPERCASE;
  letter-spacing: 0.05em;
  padding: var(--space-2) var(--space-3);
  border-left: 2px solid transparent;
  transition: all 0.15s ease;
  color: var(--text-secondary);
}
.quick-link:hover {
  color: var(--text-primary);
  border-left-color: var(--accent);
  background: var(--accent-glow);
}
.quick-link.blocked {
  color: var(--text-dim);
  text-decoration: line-through;
  opacity: 0.6;
}
```

---

## 8. Copy Fixes (Anti-Slop)

| Before | After |
|--------|-------|
| "GRAPH LEGEND" | "GRAPH LEGEND" ✅ (already correct) |
| "CONTROLS" | "CONTROLS" ✅ |
| "QUICK ACCESS" | "QUICK ACCESS" ✅ |
| "Daily Log 2026-06-26" | "DAILY LOG · JUN 26" |
| "Brand Bible" | "BRAND BIBLE" |
| "Youth Day Campaign" | "CAMPAIGNS" |
| "Products (NEEDS DOCS)" | "CATALOGUE · INCOMPLETE" |

---

## 9. New Components to Build

### `<StatusBar />` — Right cluster of nav HUD
- Clock (IBM Plex Mono, updates every second)
- 3 status dots: Discord (green=connected) · Shopify (amber=blocked) · Meta (red=expired)
- Each dot pulses with `--status-*` color

### `<KPIFlash />` — Animated KPI card
- On data refresh: number rolls/ticks up or down
- Brief amber flash on value change
- Subtle ring animation on the card border

### `<AgentStatusBadge />` — States for NPC Dock
- `online`: pulsing green dot
- `busy`: solid amber dot  
- `offline`: dim grey dot
- `error`: pulsing red dot

---

## 10. Implementation Order

1. **CSS variables + typography** — `/src/index.css` (foundations, 30min)
2. **Nav HUD glassmorphism** — `NavigationHUD.tsx` (15min)
3. **Sidebar polish** — `App.tsx` sidebar styles (30min)
4. **Bottom panel tabs** — `OpsDashboard.tsx` + layout (1hr)
5. **GSAP entrance** — `App.tsx` useEffect (30min)
6. **KPI flash animation** — `DeliveryKPIs.tsx` (45min)
7. **StatusBar component** — new + integrate into NavHUD (30min)
8. **Copy cleanup** — all text labels (15min)

**Total estimated: ~4 hours**

---

*Spec by Robusca · Applied framework: design-taste-frontend v2.0 · 2026-07-24*
