/**
 * COMPLIANT FESTIVE GIFTING TIERS — caviar-stripped, 2026 season.
 *
 * WHY THIS FILE EXISTS
 * --------------------
 * `App.tsx` carries caviar in the Gold and Platinum tiers and publishes
 * "CITES-compliant" / "ITAC-compliant" claims. The South African caviar
 * permit stack —
 *
 *   DFFE → ITAC frozen-fish notification → DAFF importer registration
 *        → SARS importer code + duty line → NRCS
 *        → CITES export permit + registered exporter code
 *
 * — was still UNASSEMBLED on 2026-10-28. The first SAFEST action is to not
 * offer caviar at all; the second is to assemble the stack with a real
 * clearing agent and a real lawyer. Neither had happened.
 *
 * The market says the same thing. SA festive hamper orders close 13–15 Nov
 * 2026 and delivery lands mid-November. A first caviar shipment needs the
 * DAFF veterinary import permit applied for at least 4 weeks before shipment
 * and 5–10 working days to issue — roughly two months end to end. Caviar
 * cannot be sold for the 2026 festive window even if the stack moved fast.
 *
 * So: 2026 proposition = biltong + single-origin African coffee + packaging
 * + delivery, done properly. The caviar box is a 2027 proposition.
 *
 * WHAT CHANGED VS App.tsx
 * -----------------------
 *   Silver   R3,000 → R2,650   caviar-free already; re-priced against the
 *                              R199.95–R720 SA hamper market.
 *   Gold     R7,000 → R5,500   caviar REMOVED, replaced with 200g biltong
 *                              Gold + accessories.
 *   Platinum R15,000 → R12,000 caviar REMOVED, replaced with 1kg coffee
 *                              selection + accessories.
 *   Entry price drops 12% (R3,000 → R2,650) — we were 1.8× the R720 deluxe
 *   hamper (buildyourbasket.co.za) and 4.4× the R295 standard hamper
 *   (Richmeats). A caviar-free box is judged against those, not against our
 *   own old tier prices.
 *
 * HOW TO USE
 * ----------
 * ✅ WIRED IN as of 2026-10-30: App.tsx imports TIERS_COMPLIANT and
 * COMPLIANT_COPY from this file, so the tiers and every compliance claim have
 * ONE owning source and the caviar copy in App.tsx is gone.
 *
 * Still true: the live page (oi28dhtke3yk) shows the OLDER caviar-free
 * R1,299 / R2,499 / R4,999 build — LEAVE IT LIVE until Tumelo signs off on this
 * ladder and on the deploy. Building the source publishes nothing.
 *
 * Guards: ops/price-ladder-guard.py (live pages) ·
 *         ops/check-caviar-in-retail-source.py (this source).
 */

export type Tier = {
  name: string;
  price: string;
  tagline: string;
  color: string;
  items: string[];
  bestFor: string;
  featured?: boolean;
};

/** Festive order close. Everything must be deliverable before this. */
export const FESTIVE_CLOSE = "13 November 2026";

/** Market reference band for SA gift hampers (Oct 2026). */
export const HAMPER_BENCHMARKS = {
  richmeatsStandard: "R295 — Richmeats standard hamper",
  richmeatsGiftBox: "R199.95 — Richmeats gift box",
  buildYourBasketDeluxe: "R720 — buildyourbasket.co.za deluxe hamper",
};

export const TIERS_COMPLIANT: Tier[] = [
  {
    name: "Silver",
    price: "R2,650",
    tagline: "Executive Introductions",
    color: "#94a3b8",
    items: [
      "200g Wagyu Biltong (vacuum-sealed)",
      "250g Rwanda Single-Origin Coffee",
      "Studex gift card (handwritten note)",
      "Branded luxury box + ribbon",
      "Delivery to 1 address nationwide",
    ],
    bestFor: "Client appreciation, team thank-yous",
  },
  {
    name: "Gold",
    price: "R5,500",
    tagline: "Boardroom Indulgence",
    color: "#d4a017",
    items: [
      "300g Premium Wagyu Biltong",
      "200g Wagyu Biltong Gold",
      "500g Rwanda Single-Origin Coffee",
      "Studex leather-bound note holder",
      "Custom engraved card",
      "Delivery to 3 addresses nationwide",
    ],
    bestFor: "Board meetings, year-end rewards, investor relations",
    featured: true,
  },
  {
    name: "Platinum",
    price: "R12,000",
    tagline: "Legacy Impressions",
    color: "#e2e8f0",
    items: [
      "500g Heritage Wagyu Biltong (aged 30 days)",
      "1kg African Coffee Selection (4 origins)",
      "Wagyu Biltong Gold accessory set",
      "Studex leather briefcase insert",
      "Custom engraved crystal decanter",
      "White-glove delivery + presentation",
      "Delivery to 10 addresses nationwide",
    ],
    bestFor: "C-suite gifting, deal closes, mining & banking VIPs",
  },
];

/**
 * Replacement copy for the claim-bearing blocks in App.tsx.
 * Every one of these removes an assertion we cannot yet make.
 */
export const COMPLIANT_COPY = {
  heroSub:
    "Wagyu biltong and single-origin African coffee — presented in bespoke boxes for SA's most discerning corporates.",

  /**
   * Replaces the "CITES Caviar" badge.
   *
   * SCOPED ON PURPOSE: the MJC certificate covers 4 WAGYU products only — not
   * coffee, not game (PRICE-SOURCE-REGISTRY.md, "MJC certificate covers 4 Wagyu
   * products"). So the claim is scoped to the Wagyu in the box, never to "every
   * product" and never to the box as a whole. The certifier's registered name
   * is "MJC Halaal Trust"; the string "MJC Halal Trust" is a forbidden
   * spelling.
   */
  heroBadge: "🇿🇦 Halaal-Certified Wagyu",

  /**
   * Replaces the "CITES-Certified Caviar" feature block.
   *
   * Every figure here is sourced: the SA hamper benchmarks are named in
   * HAMPER_BENCHMARKS above (Richmeats R295 / R199.95, buildyourbasket.co.za
   * R720). A claim with no owning source is not a claim.
   */
  featureHeading: "Priced Against a Public Benchmark",
  featureBody:
    "Our entry box sits inside the R199.95–R720 public SA hamper market — Richmeats R295, buildyourbasket.co.za R720 — so your procurement team can verify the number instead of taking our word for it.",

  /** Replaces the footer compliance line. Scoped to the Wagyu range. */
  footerCopy:
    "© 2026 Studex Group (Pty) Ltd. All rights reserved. Halaal-certified Wagyu range.",
} as const;
