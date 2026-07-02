# StudEx Meat — 10KG Wagyu Ribeye Auction Creatives

Polished, high-resolution auction creatives for the StudEx Meat 10kg Wagyu Ribeye auction,
rebuilt from two low-resolution phone exports (242 × 594 px, ~25–30 KB each).

## Approach

No AI upscaler (Real-ESRGAN / Torch) was available in the environment, so per the task's
fallback instruction the posters were **rebuilt from scratch at high resolution** using the
original Wagyu ribeye photography cropped from the source images.

- **Photo subjects preserved:** The actual ribeye scenes were cropped from the source files and
  upscaled ~6× using OpenCV (cubic resize + `detailEnhance` edge-preserving filter + unsharp mask),
  then composited under a vignette and gradient for legibility.
  - Dark theme → marbled ribeye in a black bowl on charcoal slate.
  - Blue theme → ribeye on parchment with rosemary, olive oil and peppercorns on a blue surface.
- **Typography rebuilt** with proper brand fonts (downloaded from Google Fonts):
  Playfair Display (serif display), Cinzel (serif "AUCTION"), Montserrat & Inter (sans body).
- **StudEx crest** recreated cleanly in gold as a circular emblem (stag head + antlers,
  "STUDEX MEAT · PREMIUM WAGYU" arc text) — the source logo was too low-res to extract.
- Residual `www.studexmeat.com` watermark from the source photos is covered by the footer band / CTA.

## Brand style applied

| Element | Value |
|---|---|
| StudEx gold | `#C9A961` |
| Deep matte black | `#0A0A0A` |
| Off-white body text | `#F5F0E6` |
| Blue background | deep navy `#0C1626` |
| Display serif | Playfair Display / Cinzel |
| Body sans | Montserrat / Inter |
| Treatment | Black + gold luxury, double gold frame, vignette photography |

## Copy used (exact)

- **Headline:** 10KG WAGYU RIBEYE AUCTION
- **Sub-headline:** OPENING BID — R 1,050 / kg (StudEx gold)
- **Closing line:** CLOSES SAT 13 JUNE · 12:00 NOON SAST
- **Quality line:** Marble Score 7/8 · CWB Certified Wagyu · Halaal
- **CTA:** BID NOW AT STUDEXMEAT.COM
- **Logo:** StudEx gold crest, retained

## Files produced

| File | Dimensions | Theme | Intended use |
|---|---|---|---|
| `auction_dark_1080x1350.png` | 1080 × 1350 | Dark / charcoal | Instagram portrait feed post |
| `auction_dark_1080x1920.png` | 1080 × 1920 | Dark / charcoal | Instagram / Facebook story |
| `auction_blue_1080x1350.png` | 1080 × 1350 | Blue / herbs | Instagram portrait feed post |
| `auction_blue_1080x1920.png` | 1080 × 1920 | Blue / herbs | Instagram / Facebook story |
| `auction_blue_1200x628.png` | 1200 × 628 | Blue / herbs | Web banner / email hero / Shopify |

## Intermediate working assets (not final deliverables, kept for reference)

| File | Purpose |
|---|---|
| `_dark_scene_hi.png` | Upscaled (~6×) dark ribeye-in-bowl photo |
| `_blue_scene_hi.png` | Upscaled (~6×) blue parchment ribeye scene |
| `_logo_gold.png` | Recreated gold StudEx crest emblem (transparent PNG) |

Generator scripts live at `/home/user/workspace/compose.py` and `/home/user/workspace/make_logo.py`.
Brand fonts are in `/home/user/workspace/fonts/`.

## Notes / suggested tweaks

- All five assets carry the complete, exact copy required; the CTA is a solid gold button with
  black text for maximum contrast.
- For the Shopify product page, the 1080 × 1350 dark version works as the primary gallery image;
  the 1200 × 628 banner suits the collection/hero or email.
- If a true photographic upscale is later desired, re-run with Real-ESRGAN once GPU/Torch is
  available — the `_*_scene_hi.png` crops can be swapped for AI-upscaled versions without changing layout.

---

# Video Reels — Upscale + Cut (added)

Two short vertical reels produced from WhatsApp-compressed source clips for the
10kg Wagyu auction (closes **Saturday 13 June 2026, 12:00 noon SAST**). Built entirely
with ffmpeg + Pillow (no external paid APIs).

## Video deliverables

| File | Duration | Dimensions | Codec / fps | Bitrate | Audio | Faststart |
|---|---|---|---|---|---|---|
| `reel_craftsmanship_15s_1080x1920.mp4` | 15.00 s | 1080 × 1920 | H.264 yuv420p / 30 fps | ~8.1 Mbps | AAC (original cleaver/board audio, atempo-matched to 0.75x) | yes |
| `reel_thelot_8s_1080x1920.mp4` | 7.23 s | 1080 × 1920 | H.264 yuv420p / 30 fps | ~7.3 Mbps | none (muted — music to be added in approval pass) | yes |

## Reel A — Craftsmanship Auction Teaser (from video 1)

- Source: `1002097206.mp4` (848×478 landscape, 30 s).
- Center-cropped to vertical 9:16 (cleaver + sliced brisket), scaled to 1080×1920 (Lanczos).
- Playback slowed to **0.75x**; subtle Ken Burns zoom **1.00 → 1.05** via zoompan.
- Color grade: warm/gold tint, deep blacks, lifted reds, soft vignette.
- Original audio retained (mean ~-10 dB, audible board/cleaver content), tempo-corrected with `atempo=0.75`.
- Sequenced gold (`#C9A961`) Noto Serif Display headlines + off-white body, soft drop shadow, with fade in/out:
  - 0–3 s "10kg Wagyu Ribeye"
  - 3–6 s "One lot. One winner."
  - 6–9 s "Opening bid R 1,050/kg"
  - 9–12 s "Closes Sat 12:00 noon"
  - 12–15 s "Bid now at studexmeat.com" + StudEx gold logo

## Reel B — The Lot (from video 2)

- Source: `WhatsApp-Video-2026-06-05-at-03.47.07.mp4` (480×848 portrait, 5.2 s).
- Upscaled 480×848 → 1080×1920 (Lanczos) with light unsharp.
- Light two-pass stabilization (vidstabdetect/vidstabtransform, smoothing=20).
- Color grade: cool deep tones to make the marbling pop.
- Intro card (~1 s): "THE Wagyu Lot" gold serif on black, crossfading into the footage.
- End card (last ~1.5 s): "10kg · Opening R 1,050/kg · Closes Sat 12:00" on black with the white StudEx emblem.
- Muted per brief.

## Asset / working files (kept for reference)

- `assets/studex_logo_white.png`, `assets/studex_logo_gold.png` — recolored StudEx emblem from `Studex-Global-Markets-Logo-5.jpg`.
- `assets/textA_01..05.png` — Reel A text-card overlays (Pillow).
- `assets/reelB_intro.png`, `assets/reelB_endcard.png` — Reel B cards.
- `assets/_reelA_base.mp4`, `assets/_reelB_footage.mp4`, `assets/_introclip.mp4`, `assets/_endclip.mp4` — intermediate clips.
- Generator scripts: `make_text_overlays.py`, `make_reelB_cards.py`, `make_logo_white.py`.

## Verification

Both files confirmed playable via ffprobe: correct duration, 1080×1920 resolution, H.264/yuv420p at 30 fps,
and `moov` atom positioned before `mdat` (faststart enabled).

---

# Brand-Fix v2 — Correct StudEx Meat Seal (added)

**Why:** The previous pass shipped the WRONG brand mark on every auction creative:

- The **5 posters** used a fabricated gold *stag emblem* ("STUDEX MEAT · PREMIUM WAGYU") — not the
  real logo.
- The **2 reels** used the **StudEx GLOBAL MARKETS** logo (circuit-globe with bull + circuit-trail and
  a "STUDEX GLOBAL MARKETS" wordmark) — that is the user's *other* company, not StudEx Meat.
- On several posters the gold "CLOSES SAT 13 JUNE · 12:00 NOON SAST" pill sat on top of the ribeye photo.

This v2 pass replaces every logo with the **correct StudEx Meat seal** and corrects the layout issues.

## ★ Source of truth for the logo

**`studex_meat_seal_gold.png`** (1200 × 1200, RGBA, transparent background) is now the single canonical
StudEx Meat brand mark. **All five posters and both reels use this identical file.** The seal is a solid
gold (`#C9A961`, measured avg RGB 201/169/97) circular emblem containing: a double gold ring, "STUDEX MEAT"
top arc, "WWW.STUDEXMEAT.COM" bottom arc, bead separators, a front-facing horned bull/antelope head with
bold sweeping horns, a digital-trail hand reaching toward the bull, and a "WAGYU" nameplate.

### How the seal was produced

The real seal lives only as a small, noisy mark in the bottom-right of the packaging photo
`brand_extract/img_03.jpeg` (chilli biltong). Per the task's fallback guidance — *"prioritise CLEAN
silhouette over photographic fidelity — a clean gold vector-like version is better than a noisy raster lift"* —
the seal was **rebuilt as a clean gold vector-style emblem** (`build_seal_vector.py`) rather than lifted as a
noisy raster. OpenCV raster-extraction attempts were tried first and produced the intermediate references
`_seal_raw.png` (124 × 124 tight crop) and `_seal_hi.png` (4× upscaled), which are kept per spec.

## Posters rebuilt (overwritten)

All five posters were regenerated with `build_posters.py` using the correct seal:

- `auction_dark_1080x1350.png`, `auction_dark_1080x1920.png`,
  `auction_blue_1080x1350.png`, `auction_blue_1080x1920.png`, `auction_blue_1200x628.png`.
- Logo at top (~180 px tall, centred); identical seal file on every poster.
- The **"CLOSES SAT 13 JUNE · 12:00 NOON SAST" line was moved OFF the photo** into the dark/navy area
  directly under the price, with **no gold pill** — rendered as bold bright-gold text on the dark background.
- All other copy unchanged and used verbatim (no new copy invented).

## Reels fixed (overwritten)

- **Reel A — `reel_craftsmanship_15s_1080x1920.mp4`:** only the end-card window (~12.2–15.0 s) was
  re-rendered. The wrong GLOBAL MARKETS globe + its "STUDEX GLOBAL MARKETS" wordmark (which overlapped the
  correct "BID NOW AT" text) were covered with a soft dark scrim, and the correct seal plus the original
  "BID NOW AT" / "studexmeat.com" copy were redrawn in the matching serif. All other frames and the original
  AAC audio are untouched. Overlay builder: `build_reelA_fix.py` → `assets/reelA_endfix_overlay.png`.
- **Reel B — `reel_thelot_8s_1080x1920.mp4`:** the end card (~6.0–7.2 s) showed the wrong WHITE GLOBAL
  MARKETS logo on a solid-black card. The logo region was painted black and the correct seal placed in its
  spot; the "10kg / Opening R 1,050/kg / Closes Sat 12:00" copy is untouched. A frame-by-frame scan confirmed
  the **intro card ("THE Wagyu Lot") contains no logo**, so it was left unchanged. Overlay builder:
  `build_reelB_fix.py` → `assets/reelB_endfix_overlay.png`. Reel B has no audio (as before).

## v2 verification (ffprobe)

| File | Duration | Frames | Resolution | Codec / fps | Audio | Faststart |
|---|---|---|---|---|---|---|
| `reel_craftsmanship_15s_1080x1920.mp4` | 15.000 s | 450 | 1080 × 1920 | H.264 / 30 fps | AAC (unchanged) | yes (moov before mdat) |
| `reel_thelot_8s_1080x1920.mp4` | 7.233 s | 217 | 1080 × 1920 | H.264 / 30 fps | none | yes (moov before mdat) |

Both reels match their original durations/frame counts exactly; only the logo on the relevant cards changed.

## v2 working / reference files

- `studex_meat_seal_gold.png` — **canonical correct logo (source of truth).**
- `build_seal_vector.py` — builds the seal; `make_seal.py` — OpenCV raster attempts (kept for `_seal_raw.png`,
  `_seal_hi.png`).
- `build_posters.py` — builds all five posters.
- `build_reelA_fix.py`, `build_reelB_fix.py` — end-card correction overlay builders.
- `assets/reelA_endfix_overlay.png`, `assets/reelB_endfix_overlay.png` — correction overlays.
- **Deprecated / do NOT use:** `_logo_gold.png` (old fabricated stag emblem),
  `assets/studex_logo_gold.png`, `assets/studex_logo_white.png` (the wrong GLOBAL MARKETS logos).
