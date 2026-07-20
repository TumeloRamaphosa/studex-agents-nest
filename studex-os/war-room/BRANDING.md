# Kanan Band Branding Spec — Rocket.Chat War Room
**Studex Meat OS — Visual Identity Guide**

---

## Brand Colors (Kanan Band)

| Token | Hex | Usage |
|---|---|---|
| `--studex-bg` | `#0a0505` | Page background, sidebar |
| `--studex-red` | `#8B1A1A` | Primary buttons, active states |
| `--studex-gold` | `#d4a017` | Accents, @mention highlights, unread badges |
| `--studex-cream` | `#f5f0e8` | Primary text on dark backgrounds |
| `--studex-surface` | `#1a0f0f` | Cards, panels, elevated surfaces |
| `--studex-border` | `#2d1212` | Dividers, subtle borders |
| `--studex-red-hover` | `#a02020` | Button hover |
| `--studex-online` | `#27ae60` | Online status |

---

## Admin Panel CSS Injection

Navigate to: `http://67.213.119.157:3000/admin/settings/Layout#CustomCSS`

Paste the CSS below into the **Custom CSS** field → **Save Changes**. Theme applies instantly.

```css
/* KANAN BAND — Studex Meat War Room
   Background:#0a0505 | Red:#8B1A1A | Gold:#d4a017 | Cream:#f5f0e8 */

:root {
  --studex-bg: #0a0505;
  --studex-red: #8B1A1A;
  --studex-gold: #d4a017;
  --studex-cream: #f5f0e8;
  --studex-surface: #1a0f0f;
  --studex-border: #2d1212;
  --studex-red-hover: #a02020;
}

body, .rc-layout__main, .app-content { background-color: var(--studex-bg) !important; color: var(--studex-cream) !important; }

.sidebar, .rcx-sidebar, .room-list, [class*="sidebar"] {
  background-color: var(--studex-bg) !important;
  border-right: 1px solid var(--studex-border) !important;
}

.sidebar__header, .rcx-sidebar__header {
  background-color: var(--studex-surface) !important;
  border-bottom: 2px solid var(--studex-red) !important;
}

.sidebar__item, .rc-room-list-item { background: transparent !important; border-left: 3px solid transparent !important; transition: all 0.2s; }
.sidebar__item:hover, .rc-room-list-item:hover { background-color: var(--studex-surface) !important; border-left-color: var(--studex-gold) !important; }
.sidebar__item--active, .rc-room-list-item--active { background-color: var(--studex-surface) !important; border-left-color: var(--studex-red) !important; }

.unread-rooms-indicator, .rcx-badge { background-color: var(--studex-gold) !important; color: var(--studex-bg) !important; font-weight: 700 !important; }
.sidebar__categories-header, .category-stack__header { color: var(--studex-gold) !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; font-size: 11px !important; border-bottom: 1px solid var(--studex-border) !important; }

.rc-header, .chat-header, .message-header { background-color: var(--studex-surface) !important; border-bottom: 1px solid var(--studex-border) !important; }
.rcx-message-header__title { color: var(--studex-cream) !important; }

.rc-message-box, .composer { background-color: var(--studex-surface) !important; border-top: 1px solid var(--studex-border) !important; }
.rc-composer__inner { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; border-radius: 8px !important; }
.rc-composer__inner:focus-within { border-color: var(--studex-gold) !important; box-shadow: 0 0 0 2px rgba(212,160,23,0.2) !important; }

.message--own { background-color: rgba(139,26,26,0.25) !important; }
.message--group { background-color: var(--studex-surface) !important; border-left: 3px solid var(--studex-border) !important; }
.message--system { background-color: rgba(212,160,23,0.1) !important; color: var(--studex-gold) !important; border-left: 3px solid var(--studex-gold) !important; }

.message--mention, .highlight { background-color: rgba(212,160,23,0.3) !important; color: var(--studex-gold) !important; border-radius: 3px !important; font-weight: 600 !important; }
.message[data-username="tummebox"] { background-color: rgba(139,26,26,0.3) !important; }

.rcx-button--primary, .btn-primary { background-color: var(--studex-red) !important; border-color: var(--studex-red) !important; color: var(--studex-cream) !important; font-weight: 600 !important; border-radius: 6px !important; transition: all 0.2s !important; }
.rcx-button--primary:hover { background-color: var(--studex-red-hover) !important; box-shadow: 0 4px 12px rgba(139,26,26,0.4) !important; }
.rcx-button--secondary { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-gold) !important; color: var(--studex-gold) !important; }
.rcx-button--secondary:hover { background-color: rgba(212,160,23,0.15) !important; }

input, textarea, select, .rcx-input { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; color: var(--studex-cream) !important; border-radius: 6px !important; }
input:focus, .rcx-input:focus { border-color: var(--studex-gold) !important; box-shadow: 0 0 0 2px rgba(212,160,23,0.15) !important; outline: none !important; }

.rcx-modal, .modal, .dialog, .popover, .rcx-dropdown { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; border-radius: 12px !important; box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important; }
.modal__title { color: var(--studex-gold) !important; font-weight: 700 !important; }

.rcx-status-bullet--online { background-color: var(--studex-online) !important; box-shadow: 0 0 8px var(--studex-online) !important; }

.rc-emoji-picker { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; }
.rcx-emoji-picker__category-header { color: var(--studex-gold) !important; }

.avatar-suggestion, .autocomplete { background-color: var(--studex-surface) !important; border-bottom: 1px solid var(--studex-border) !important; color: var(--studex-cream) !important; }
.avatar-suggestion:hover { background-color: var(--studex-border) !important; }

.rc-reaction { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; color: var(--studex-cream) !important; border-radius: 4px !important; }
.rc-reaction:hover { border-color: var(--studex-gold) !important; background-color: rgba(212,160,23,0.15) !important; }

.login { background-color: var(--studex-bg) !important; }
.login .content { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; border-radius: 12px !important; border-top: 3px solid var(--studex-red) !important; }

a, .rcx-link { color: var(--studex-gold) !important; }
a:hover { color: #a07810 !important; text-decoration: underline !important; }

.attachment { background-color: var(--studex-surface) !important; border: 1px solid var(--studex-border) !important; border-left: 3px solid var(--studex-red) !important; border-radius: 6px !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--studex-bg) !important; }
::-webkit-scrollbar-thumb { background: var(--studex-border) !important; border-radius: 3px !important; }
::-webkit-scrollbar-thumb:hover { background: var(--studex-red) !important; }
* { scrollbar-width: thin; scrollbar-color: var(--studex-border) var(--studex-bg); }
```

---

## Logo & Asset Upload

### Admin Upload Path
Navigate: `http://67.213.119.157:3000/admin/settings/Layout#Assets`

Upload:
- **Company Logo:** `logo.png` (256×256px, transparent, cream/white logo)
- **Login Background:** `login-bg.png` (1920×1080px, #0a0505 background, Studex emblem)
- **Favicon:** `favicon.ico` (red/gold icon, 32×32px)

### Generate Placeholder Assets (if no designer)

```bash
# SSH into VM:
apt-get install -y imagemagick 2>/dev/null || true

# Create placeholder logo
cat > /root/studex-os/war-room/assets/logo.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect width="200" height="200" fill="#0a0505"/>
  <circle cx="100" cy="100" r="70" fill="none" stroke="#d4a017" stroke-width="4"/>
  <circle cx="100" cy="100" r="50" fill="none" stroke="#8B1A1A" stroke-width="3"/>
  <text x="100" y="115" font-family="Arial Black" font-size="48"
        fill="#f5f0e8" text-anchor="middle" font-weight="900">SM</text>
</svg>
EOF

convert /root/studex-os/war-room/assets/logo.svg \
  -resize 256x256 /root/studex-os/war-room/assets/logo.png

# Create login background
convert -size 1920x1080 xc:"#0a0505" \
  -fill "#d4a017" -draw "circle 960,540 960,420" \
  -fill "#8B1A1A" -draw "circle 960,540 960,480" \
  -font "DejaVu-Sans-Bold" -pointsize 100 \
  -fill "#f5f0e8" -gravity center \
  -annotate +0+0 "STUDEX MEAT" \
  -font "DejaVu-Sans" -pointsize 40 \
  -fill "#d4a017" -annotate +0+120 "Premium Halal Meat • South Africa" \
  /root/studex-os/war-room/assets/login-bg.png
```

---

## Admin Settings Reference

```
Admin → Layout → Site Name: "Studex Meat War Room"
Admin → Layout → Tagline: "Premium Halal Meat Operations Hub"
Admin → Layout → Site Logo: [Upload logo.png]
Admin → Layout → Favicon: [Upload favicon.ico]
Admin → Layout → Login Background: [Upload login-bg.png]
Admin → Layout → Custom CSS: [Paste Kanan Band CSS above]
Admin → Layout → Legal: "© 2025 Studex Meat (Pty) Ltd."
Admin → General → Force SSL: true (after Caddy setup)
Admin → General → Allow New User Registration: DISABLED
```

---

## Bot Avatars

| Bot | Visual |
|---|---|
| Charlie | 🤖 Robot, red/gold |
| Naledi | 🎙️ Mic + star, purple |
| Delivery Agent | 🚚 Truck, green/gold |
| Robusca | 🦎 Gecko/sun, gold/red |
| Meat B@ye | 👑 Crown + meat, gold |

Upload: Admin → Users → [Bot Name] → Edit → Avatar Upload
