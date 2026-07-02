# StudEx Meat — Father's Day Send-Now Email
**File:** EMAIL_SENDNOW_2026-06-11.md
**Created:** Thu 11 Jun 2026
**Send window:** Tonight, Thu 11 Jun 2026 — ASAP (evening SAST)
**Campaign ID:** FD26-SENDNOW

---

## TWO SENDS — OVERVIEW

| Send | From | Audience | Version |
|---|---|---|---|
| **Hero send** | info@studexmeat.com | Full list | Version A (hero) |
| **Founder send** | tumelo@studexmeat.com | Top-10% VIPs by LTV | Version B (founder note) |

Both go tonight. The Founder send goes to the top-10% segment only and uses a warmer, personal tone. The Hero send is the primary campaign creative.

---
---

# VERSION A — HERO SEND
**From:** StudEx Meat `<info@studexmeat.com>`
**Reply-to:** info@studexmeat.com
**Audience:** Full list
**Campaign ID:** FD26-SENDNOW-HERO

---

## Subject Lines (A/B)

- **Subject A (urgency-led):** `44 hours left. Father's Day gold awaits.`
- **Subject B (auction-led):** `The 10kg Wagyu auction closes Saturday noon.`

**A/B split recommendation:** Send Subject A to 90% of the list, Subject B to the remaining 10%. Subject A pairs urgency with aspiration and lands under 50 characters. Subject B is more specific — useful for buyers who already know the auction exists. If Subject B outperforms on click-to-open rate, lead with it for Send 2 (reminder blast).

---

## Preview Text

`Gift deadline Friday 11:00 · Auction closes Saturday noon · 10kg Wagyu Ribeye up for bid right now.`

*(94 characters — within 90–110 target)*

---

## Full HTML Body — Version A (Hero Send)

> **PLACEHOLDER NOTE:** The Biltong Gold gift pack URL `https://studexmeat.com/products/biltong-gold` is a placeholder. The R 1,450 / 8 × 70g SKU may not yet exist on Shopify at this price point. Confirm the live product URL and Shopify variant ID before sending. Replace the placeholder href in the HTML below before deployment.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Father's Day Gold — StudEx Meat</title>
  <!--[if mso]>
  <noscript>
    <xml>
      <o:OfficeDocumentSettings>
        <o:PixelsPerInch>96</o:PixelsPerInch>
      </o:OfficeDocumentSettings>
    </xml>
  </noscript>
  <![endif]-->
  <style>
    /* Reset */
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    img { -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }
    /* Client-specific */
    body { margin: 0 !important; padding: 0 !important; background-color: #0A0A0A; }
    /* Responsive */
    @media only screen and (max-width: 620px) {
      .email-container { width: 100% !important; }
      .fluid { max-width: 100% !important; width: 100% !important; }
      .stack-column, .stack-column-center { display: block !important; width: 100% !important; max-width: 100% !important; }
      .center-on-narrow { text-align: center !important; }
      .hero-headline { font-size: 34px !important; line-height: 40px !important; }
      .section-headline { font-size: 24px !important; line-height: 30px !important; }
      .cta-button { padding: 16px 32px !important; font-size: 14px !important; }
      .price-tag { font-size: 28px !important; }
      .padding-mobile { padding: 28px 20px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0A;font-family:'Inter',Arial,sans-serif;">

  <!-- Preheader text (hidden) -->
  <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#0A0A0A;">
    Gift deadline Friday 11:00 &middot; Auction closes Saturday noon &middot; 10kg Wagyu Ribeye up for bid right now.&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
  </div>

  <!-- Email wrapper -->
  <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color:#0A0A0A;">
    <tr>
      <td align="center">

        <!-- Main container -->
        <table class="email-container" role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width:600px;">

          <!-- ============================================================
               TOP BAR — urgency strip
          ============================================================ -->
          <tr>
            <td style="background-color:#C9A961;padding:10px 30px;text-align:center;">
              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#0A0A0A;">
                Auction closes Sat 12:00 &nbsp;&middot;&nbsp; Gift deadline Fri 11:00
              </p>
            </td>
          </tr>

          <!-- ============================================================
               HEADER — seal + brand name
          ============================================================ -->
          <tr>
            <td style="background-color:#0B1B2A;padding:36px 40px 28px;text-align:center;" class="padding-mobile">
              <img src="cid:studex-seal" alt="StudEx Meat" width="90" height="90"
                   style="display:block;margin:0 auto 18px;width:90px;height:90px;border-radius:50%;">
              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C9A961;">
                STUDEX MEAT &nbsp;&middot;&nbsp; CAPE TOWN
              </p>
            </td>
          </tr>

          <!-- ============================================================
               HERO — headline + sub
          ============================================================ -->
          <tr>
            <td style="background-color:#0B1B2A;padding:0 40px 48px;" class="padding-mobile">

              <!-- Gold rule -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                  <td style="height:1px;background-color:#C9A961;opacity:0.4;"></td>
                </tr>
              </table>

              <h1 class="hero-headline"
                  style="margin:40px 0 20px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:42px;font-weight:700;line-height:50px;color:#C9A961;text-align:center;letter-spacing:-0.5px;">
                Father's Day<br>deserves gold.
              </h1>

              <p style="margin:0 0 32px;font-family:'Inter',Arial,sans-serif;font-size:17px;line-height:27px;color:#F4F1EA;text-align:center;">
                Ten days. Two ways to get there. The Wagyu Biltong Gold gift packs are ready to order — and the 10kg Wagyu Ribeye auction is live, with less than 44 hours on the clock.
              </p>

              <!-- Double rule -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                  <td style="height:1px;background-color:#C9A961;opacity:0.4;"></td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- ============================================================
               BLOCK 1 — BILTONG GOLD GIFT PACK (R 1,450)
          ============================================================ -->
          <tr>
            <td style="background-color:#0A0A0A;padding:48px 40px;" class="padding-mobile">

              <p style="margin:0 0 8px;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C9A961;">
                THE GIFT
              </p>

              <h2 class="section-headline"
                  style="margin:0 0 20px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:28px;font-weight:700;line-height:36px;color:#F4F1EA;">
                Wagyu Biltong Gold<br>Gift Pack
              </h2>

              <p style="margin:0 0 16px;font-family:'Inter',Arial,sans-serif;font-size:15px;line-height:25px;color:#C0BAB0;">
                Eight premium 70g packs. Halaal-certified Wagyu, processed and seasoned in Cape Town, vacuum-sealed in gift-ready presentation. For the father who wants nothing — give him something he has never tasted.
              </p>

              <p style="margin:0 0 28px;font-family:'Inter',Arial,sans-serif;font-size:14px;line-height:22px;color:#C0BAB0;">
                Order before <strong style="color:#F4F1EA;">Friday 13 June at 11:00 SAST</strong> for same-day dispatch to major metros — Saturday delivery in Cape Town, Johannesburg, Pretoria and Durban. Outside major metros: 1–3 working days, refrigerated courier.
              </p>

              <!-- Price tag -->
              <p class="price-tag"
                 style="margin:0 0 28px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:32px;font-weight:700;color:#C9A961;">
                R 1,450 &nbsp;<span style="font-size:16px;font-weight:400;color:#C0BAB0;font-family:'Inter',Arial,sans-serif;">· 8 &times; 70g</span>
              </p>

              <!-- CTA button -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="background-color:#C9A961;border-radius:2px;">
                    <a class="cta-button"
                       href="https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold"
                       target="_blank"
                       style="display:inline-block;padding:16px 40px;font-family:'Inter',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#0A0A0A;text-decoration:none;">
                      Order Biltong Gold
                    </a>
                  </td>
                </tr>
              </table>

              <!-- PLACEHOLDER NOTE (remove before send) -->
              <!-- *** EDITOR NOTE: URL above is a placeholder. Confirm live Shopify variant URL before sending. *** -->

            </td>
          </tr>

          <!-- ============================================================
               DIVIDER
          ============================================================ -->
          <tr>
            <td style="background-color:#0A0A0A;padding:0 40px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                  <td style="height:1px;background-color:#C9A961;opacity:0.25;"></td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ============================================================
               BLOCK 2 — 10KG WAGYU RIBEYE AUCTION
          ============================================================ -->
          <tr>
            <td style="background-color:#0A0A0A;padding:48px 40px;" class="padding-mobile">

              <p style="margin:0 0 8px;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C9A961;">
                THE AUCTION
              </p>

              <h2 class="section-headline"
                  style="margin:0 0 20px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:28px;font-weight:700;line-height:36px;color:#F4F1EA;">
                10kg Wagyu Ribeye.<br>One lot. One winner.
              </h2>

              <!-- Auction countdown strip -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
                     style="background-color:#0B1B2A;border-left:3px solid #C9A961;margin-bottom:24px;">
                <tr>
                  <td style="padding:16px 20px;">
                    <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#C9A961;">
                      Closes Saturday 13 June &middot; 12:00 noon SAST
                    </p>
                    <p style="margin:4px 0 0;font-family:'Inter',Arial,sans-serif;font-size:13px;color:#C0BAB0;">
                      Less than 44 hours from now. Bids extend 2 minutes on late entries.
                    </p>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 16px;font-family:'Inter',Arial,sans-serif;font-size:15px;line-height:25px;color:#C0BAB0;">
                Marble score 7/8. CWB Certified Wagyu. Halaal. Dry-aged 21 days. Vacuum-sealed in StudEx Meat branded packaging. Approximately 12–14 steaks at 700–850g each. This is not a retail product — it is a single lot, sold once, to one buyer.
              </p>

              <p style="margin:0 0 28px;font-family:'Inter',Arial,sans-serif;font-size:15px;line-height:25px;color:#C0BAB0;">
                Opening bid <strong style="color:#F4F1EA;">R 1,050/kg</strong>. Bid increments R 50/kg. Winner notified within 15 minutes of close. Payment due within 4 hours. Major centres: refrigerated courier, free.
              </p>

              <!-- Price tag -->
              <p class="price-tag"
                 style="margin:0 0 28px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:32px;font-weight:700;color:#C9A961;">
                Opens at R 10,500 <span style="font-size:16px;font-weight:400;color:#C0BAB0;font-family:'Inter',Arial,sans-serif;">· R 1,050/kg</span>
              </p>

              <!-- CTA button -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="background-color:#C9A961;border-radius:2px;">
                    <a class="cta-button"
                       href="https://studexmeat.com/products/wagyu-10kg-auction?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=auction"
                       target="_blank"
                       style="display:inline-block;padding:16px 40px;font-family:'Inter',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#0A0A0A;text-decoration:none;">
                      Place Your Bid
                    </a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- ============================================================
               DIVIDER
          ============================================================ -->
          <tr>
            <td style="background-color:#0A0A0A;padding:0 40px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                  <td style="height:1px;background-color:#C9A961;opacity:0.25;"></td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ============================================================
               BLOCK 3 — 7KG BILTONG GOLD BOX (for bigger gifts)
          ============================================================ -->
          <tr>
            <td style="background-color:#0A0A0A;padding:48px 40px;" class="padding-mobile">

              <p style="margin:0 0 8px;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C9A961;">
                FOR THE BIGGER GIFT
              </p>

              <h2 class="section-headline"
                  style="margin:0 0 20px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:28px;font-weight:700;line-height:36px;color:#F4F1EA;">
                Wagyu Biltong Gold<br>7kg Box
              </h2>

              <p style="margin:0 0 28px;font-family:'Inter',Arial,sans-serif;font-size:15px;line-height:25px;color:#C0BAB0;">
                For the family that shares, the team that gathers, or the gift that needs to make a statement. Seven kilograms. Same premium Wagyu. Same cold chain.
              </p>

              <p class="price-tag"
                 style="margin:0 0 28px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:32px;font-weight:700;color:#C9A961;">
                R 12,500 &nbsp;<span style="font-size:16px;font-weight:400;color:#C0BAB0;font-family:'Inter',Arial,sans-serif;">· 7kg</span>
              </p>

              <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="background-color:transparent;border:1px solid #C9A961;border-radius:2px;">
                    <a class="cta-button"
                       href="https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold_7kg"
                       target="_blank"
                       style="display:inline-block;padding:14px 36px;font-family:'Inter',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#C9A961;text-decoration:none;">
                      Order the 7kg Box
                    </a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- ============================================================
               TRUST BLOCK
          ============================================================ -->
          <tr>
            <td style="background-color:#0B1B2A;padding:36px 40px;text-align:center;" class="padding-mobile">
              <p style="margin:0 0 8px;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C9A961;">
                Our Promise
              </p>
              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:14px;line-height:24px;color:#C0BAB0;">
                Marble 7/8 &nbsp;&middot;&nbsp; CWB Certified Wagyu &nbsp;&middot;&nbsp; 100% Halaal &nbsp;&middot;&nbsp; Cape Town
              </p>
              <p style="margin:12px 0 0;font-family:'Inter',Arial,sans-serif;font-size:13px;color:#8A8070;">
                Cold chain maintained from production to your door. Refrigerated courier nationwide.
              </p>
            </td>
          </tr>

          <!-- ============================================================
               FOOTER — POPIA compliant
          ============================================================ -->
          <tr>
            <td style="background-color:#0A0A0A;padding:36px 40px;border-top:1px solid #1A1A1A;" class="padding-mobile">

              <p style="margin:0 0 12px;font-family:'Inter',Arial,sans-serif;font-size:12px;line-height:20px;color:#5A5A5A;text-align:center;">
                You are receiving this because you signed up or purchased from StudEx Meat.
              </p>

              <p style="margin:0 0 16px;font-family:'Inter',Arial,sans-serif;font-size:12px;line-height:20px;color:#5A5A5A;text-align:center;">
                <a href="{{unsubscribe_url}}" style="color:#C9A961;text-decoration:underline;">Unsubscribe</a>
                &nbsp;&middot;&nbsp;
                <a href="{{preferences_url}}" style="color:#C9A961;text-decoration:underline;">Manage preferences</a>
                &nbsp;&middot;&nbsp;
                <a href="{{view_in_browser_url}}" style="color:#C9A961;text-decoration:underline;">View in browser</a>
              </p>

              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:11px;line-height:18px;color:#404040;text-align:center;">
                StudEx Meat (Pty) Ltd &nbsp;&middot;&nbsp; Cape Town, South Africa<br>
                <a href="mailto:info@studexmeat.com" style="color:#5A5A5A;text-decoration:none;">info@studexmeat.com</a>
                &nbsp;&middot;&nbsp;
                <a href="https://studexmeat.com" style="color:#5A5A5A;text-decoration:none;">studexmeat.com</a>
              </p>

            </td>
          </tr>

        </table>
        <!-- End main container -->

      </td>
    </tr>
  </table>

</body>
</html>
```

---

## Plain-Text Fallback — Version A (Hero Send)

```
STUDEX MEAT — FATHER'S DAY GOLD
================================================
Auction closes Sat 12:00 · Gift deadline Fri 11:00
================================================

Father's Day deserves gold.

Ten days. Two ways to get there.

------------------------------------------------
THE GIFT — WAGYU BILTONG GOLD GIFT PACK
------------------------------------------------

Eight premium 70g packs. Halaal-certified Wagyu, processed and
seasoned in Cape Town, vacuum-sealed in gift-ready presentation.

R 1,450 · 8 × 70g

Order before Friday 13 June at 11:00 SAST for Saturday delivery
in Cape Town, Johannesburg, Pretoria and Durban.
Outside major metros: 1–3 working days, refrigerated courier.

Order Biltong Gold:
https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold

[NOTE: URL above is a placeholder — confirm live Shopify URL before sending]

------------------------------------------------
THE AUCTION — 10KG WAGYU RIBEYE
------------------------------------------------

One lot. Ten kilograms. One winner.

Marble score 7/8. CWB Certified Wagyu. Halaal. Dry-aged 21 days.
Vacuum-sealed in StudEx Meat branded packaging.
~12–14 steaks at 700–850g each.

Opening bid: R 1,050/kg (R 10,500 for the full lot)
Bid increments: R 50/kg

CLOSES: Saturday 13 June 2026 · 12:00 noon SAST
Less than 44 hours from now.

Anti-snipe rule: bids in the final 2 minutes extend the close
by 2 minutes. Winner notified within 15 minutes. Payment due
within 4 hours of notification.

Place Your Bid:
https://studexmeat.com/products/wagyu-10kg-auction?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=auction

------------------------------------------------
FOR THE BIGGER GIFT — 7KG BILTONG GOLD BOX
------------------------------------------------

R 12,500 · 7kg

For the family that shares or the gift that needs to make a
statement. Same premium Wagyu. Same cold chain.

Order the 7kg Box:
https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold_7kg

------------------------------------------------
OUR PROMISE
Marble 7/8 · CWB Certified Wagyu · 100% Halaal · Cape Town
Cold chain maintained from production to your door.
------------------------------------------------

You are receiving this because you signed up or purchased from
StudEx Meat.

Unsubscribe: {{unsubscribe_url}}
Manage preferences: {{preferences_url}}

StudEx Meat (Pty) Ltd · Cape Town, South Africa
info@studexmeat.com · studexmeat.com
```

---
---

# VERSION B — FOUNDER SEND
**From:** Tumelo `<tumelo@studexmeat.com>`
**Reply-to:** tumelo@studexmeat.com
**Audience:** Top-10% of list by lifetime value (VIP segment)
**Campaign ID:** FD26-SENDNOW-FOUNDER

> This is a shorter, more personal note. It references the auction with intimacy — these customers already know the brand. Tone is direct, warm, and personal. Still luxury. Still no emojis.

---

## Subject Lines (A/B)

- **Subject A (personal-first):** `A personal note from Tumelo — 44 hours left`
- **Subject B (specific-first):** `You get first word on the 10kg Wagyu lot`

**A/B split recommendation:** Send Subject A to 80% of the VIP segment, Subject B to 20%. Subject A signals personal attention — strong for VIPs who respond to founder access. Subject B is a scarcity signal — appropriate for customers who transact on exclusivity. Measure click-to-open; use winner for the Father's Day reminder send on Friday.

---

## Preview Text

`The auction closes Saturday at noon. The gift deadline is Friday. I wanted you to know first — Tumelo`

*(96 characters — within 90–110 target)*

---

## Full HTML Body — Version B (Founder Send)

> **PLACEHOLDER NOTE:** Same Biltong Gold URL caveat as Version A applies. Confirm live Shopify product URL before sending.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>A personal note — StudEx Meat</title>
  <style>
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    img { -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }
    body { margin: 0 !important; padding: 0 !important; background-color: #0A0A0A; }
    @media only screen and (max-width: 620px) {
      .email-container { width: 100% !important; }
      .hero-headline { font-size: 30px !important; line-height: 38px !important; }
      .padding-mobile { padding: 28px 20px !important; }
      .cta-button { padding: 16px 28px !important; font-size: 13px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0A;font-family:'Inter',Arial,sans-serif;">

  <!-- Preheader -->
  <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#0A0A0A;">
    The auction closes Saturday at noon. The gift deadline is Friday. I wanted you to know first — Tumelo&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
  </div>

  <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color:#0A0A0A;">
    <tr>
      <td align="center">

        <table class="email-container" role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width:600px;">

          <!-- TOP BAR -->
          <tr>
            <td style="background-color:#C9A961;padding:10px 30px;text-align:center;">
              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#0A0A0A;">
                Auction closes Sat 12:00 &nbsp;&middot;&nbsp; Gift deadline Fri 11:00
              </p>
            </td>
          </tr>

          <!-- HEADER -->
          <tr>
            <td style="background-color:#0B1B2A;padding:40px 48px 32px;text-align:center;" class="padding-mobile">
              <img src="cid:studex-seal" alt="StudEx Meat" width="80" height="80"
                   style="display:block;margin:0 auto 16px;width:80px;height:80px;border-radius:50%;">
              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C9A961;">
                A personal note from Tumelo
              </p>
            </td>
          </tr>

          <!-- BODY — personal letter format -->
          <tr>
            <td style="background-color:#0A0A0A;padding:48px 48px 40px;" class="padding-mobile">

              <h1 class="hero-headline"
                  style="margin:0 0 28px;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:34px;font-weight:700;line-height:42px;color:#C9A961;">
                Ten days to Father's Day.<br>Less than 44 hours on the auction.
              </h1>

              <p style="margin:0 0 20px;font-family:'Inter',Arial,sans-serif;font-size:16px;line-height:27px;color:#F4F1EA;">
                I wanted to reach you directly before this goes to the broader list.
              </p>

              <p style="margin:0 0 20px;font-family:'Inter',Arial,sans-serif;font-size:16px;line-height:27px;color:#C0BAB0;">
                The 10kg Wagyu Ribeye auction closes <strong style="color:#F4F1EA;">this Saturday at noon</strong>. One lot. Marble 7/8. CWB Certified. Halaal. Twenty-one days dry-aged. Opening at R 1,050 per kilogram — the full lot opens at R 10,500. Bids in the final two minutes extend the close. This will not roll over.
              </p>

              <p style="margin:0 0 20px;font-family:'Inter',Arial,sans-serif;font-size:16px;line-height:27px;color:#C0BAB0;">
                If the auction is not for you, the <strong style="color:#F4F1EA;">Wagyu Biltong Gold gift pack</strong> is ready — R 1,450 for eight premium 70g packs, gift-presented, cold chain dispatched. Order before <strong style="color:#F4F1EA;">Friday at 11:00</strong> and it lands Saturday in CPT, JHB, PTA and DBN.
              </p>

              <p style="margin:0 0 36px;font-family:'Inter',Arial,sans-serif;font-size:16px;line-height:27px;color:#C0BAB0;">
                For a bigger statement, the 7kg Biltong Gold box at R 12,500 is also available — same production, same quality, a different scale.
              </p>

              <!-- CTA row — two side-by-side on desktop, stacked on mobile -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                  <td style="padding-bottom:12px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td style="background-color:#C9A961;border-radius:2px;">
                          <a class="cta-button"
                             href="https://studexmeat.com/products/wagyu-10kg-auction?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=auction"
                             target="_blank"
                             style="display:inline-block;padding:15px 36px;font-family:'Inter',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#0A0A0A;text-decoration:none;">
                            Bid on the Lot
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td style="border:1px solid #C9A961;border-radius:2px;">
                          <a class="cta-button"
                             href="https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold"
                             target="_blank"
                             style="display:inline-block;padding:14px 36px;font-family:'Inter',Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#C9A961;text-decoration:none;">
                            Order Biltong Gold
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <p style="margin:40px 0 0;font-family:'Inter',Arial,sans-serif;font-size:15px;line-height:25px;color:#C0BAB0;">
                Thank you for being part of what we are building here.
              </p>

              <p style="margin:12px 0 0;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:18px;color:#F4F1EA;">
                Tumelo
              </p>

              <p style="margin:4px 0 0;font-family:'Inter',Arial,sans-serif;font-size:13px;color:#5A5A5A;">
                Founder, StudEx Meat
              </p>

            </td>
          </tr>

          <!-- TRUST STRIP -->
          <tr>
            <td style="background-color:#0B1B2A;padding:24px 48px;text-align:center;" class="padding-mobile">
              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:13px;line-height:22px;color:#C0BAB0;">
                Marble 7/8 &nbsp;&middot;&nbsp; CWB Certified Wagyu &nbsp;&middot;&nbsp; 100% Halaal &nbsp;&middot;&nbsp; Cape Town
              </p>
            </td>
          </tr>

          <!-- FOOTER — POPIA compliant -->
          <tr>
            <td style="background-color:#0A0A0A;padding:32px 48px;border-top:1px solid #1A1A1A;" class="padding-mobile">

              <p style="margin:0 0 10px;font-family:'Inter',Arial,sans-serif;font-size:12px;line-height:20px;color:#5A5A5A;text-align:center;">
                You are receiving this as a valued StudEx Meat customer.
              </p>

              <p style="margin:0 0 14px;font-family:'Inter',Arial,sans-serif;font-size:12px;line-height:20px;color:#5A5A5A;text-align:center;">
                <a href="{{unsubscribe_url}}" style="color:#C9A961;text-decoration:underline;">Unsubscribe</a>
                &nbsp;&middot;&nbsp;
                <a href="{{preferences_url}}" style="color:#C9A961;text-decoration:underline;">Manage preferences</a>
                &nbsp;&middot;&nbsp;
                <a href="{{view_in_browser_url}}" style="color:#C9A961;text-decoration:underline;">View in browser</a>
              </p>

              <p style="margin:0;font-family:'Inter',Arial,sans-serif;font-size:11px;line-height:18px;color:#404040;text-align:center;">
                StudEx Meat (Pty) Ltd &nbsp;&middot;&nbsp; Cape Town, South Africa<br>
                <a href="mailto:tumelo@studexmeat.com" style="color:#5A5A5A;text-decoration:none;">tumelo@studexmeat.com</a>
                &nbsp;&middot;&nbsp;
                <a href="https://studexmeat.com" style="color:#5A5A5A;text-decoration:none;">studexmeat.com</a>
              </p>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>
```

---

## Plain-Text Fallback — Version B (Founder Send)

```
STUDEX MEAT — A PERSONAL NOTE FROM TUMELO
================================================
Auction closes Sat 12:00 · Gift deadline Fri 11:00
================================================

Ten days to Father's Day. Less than 44 hours on the auction.

I wanted to reach you directly before this goes to the broader list.

The 10kg Wagyu Ribeye auction closes this Saturday at noon. One lot.
Marble 7/8. CWB Certified. Halaal. Twenty-one days dry-aged. Opening
at R 1,050 per kilogram (R 10,500 for the full lot). Bids in the final
two minutes extend the close. This will not roll over.

Bid on the Lot:
https://studexmeat.com/products/wagyu-10kg-auction?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=auction

If the auction is not for you, the Wagyu Biltong Gold gift pack is
ready — R 1,450 for eight premium 70g packs, gift-presented, cold chain
dispatched. Order before Friday at 11:00 SAST and it lands Saturday
in Cape Town, Johannesburg, Pretoria and Durban.

Order Biltong Gold:
https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold

[NOTE: URL above is a placeholder — confirm live Shopify URL before sending]

For a bigger statement: 7kg Biltong Gold Box, R 12,500.
https://studexmeat.com/products/biltong-gold?utm_source=agentmail&utm_medium=email&utm_campaign=fathersday_send1&utm_content=biltong_gold_7kg

Thank you for being part of what we are building here.

Tumelo
Founder, StudEx Meat

------------------------------------------------
Marble 7/8 · CWB Certified Wagyu · 100% Halaal · Cape Town
------------------------------------------------

You are receiving this as a valued StudEx Meat customer.

Unsubscribe: {{unsubscribe_url}}
Manage preferences: {{preferences_url}}

StudEx Meat (Pty) Ltd · Cape Town, South Africa
tumelo@studexmeat.com · studexmeat.com
```

---
---

# AGENTMAIL — SEND INSTRUCTIONS

## Ready-to-paste curl commands

> Replace `YOUR_LIST_ID_FULL`, `YOUR_LIST_ID_VIP`, `YOUR_TEMPLATE_ID_HERO`, and `YOUR_TEMPLATE_ID_FOUNDER` with your AgentMail list and template IDs. The API key is read from the environment variable `AGENTMAIL_API_KEY`.

### Send A — Hero (info@studexmeat.com → full list)

```bash
curl -X POST "https://api.agentmail.to/v1/sends" \
  -H "Authorization: Bearer ${AGENTMAIL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {
      "name": "StudEx Meat",
      "email": "info@studexmeat.com"
    },
    "reply_to": "info@studexmeat.com",
    "list_id": "YOUR_LIST_ID_FULL",
    "subject": {
      "default": "44 hours left. Father'\''s Day gold awaits.",
      "ab_test": {
        "variants": [
          { "subject": "44 hours left. Father'\''s Day gold awaits.", "weight": 0.9 },
          { "subject": "The 10kg Wagyu auction closes Saturday noon.", "weight": 0.1 }
        ]
      }
    },
    "preview_text": "Gift deadline Friday 11:00 · Auction closes Saturday noon · 10kg Wagyu Ribeye up for bid right now.",
    "html_template_id": "YOUR_TEMPLATE_ID_HERO",
    "text_template_id": "YOUR_TEMPLATE_ID_HERO_TEXT",
    "send_at": "now",
    "utm": {
      "source": "agentmail",
      "medium": "email",
      "campaign": "fathersday_send1"
    },
    "attachments": [
      {
        "cid": "studex-seal",
        "path": "/brand_assets/studex_meat_seal_gold_CANONICAL.png",
        "content_type": "image/png"
      }
    ]
  }'
```

### Send B — Founder (tumelo@studexmeat.com → top-10% VIP segment)

```bash
curl -X POST "https://api.agentmail.to/v1/sends" \
  -H "Authorization: Bearer ${AGENTMAIL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {
      "name": "Tumelo",
      "email": "tumelo@studexmeat.com"
    },
    "reply_to": "tumelo@studexmeat.com",
    "list_id": "YOUR_LIST_ID_VIP",
    "subject": {
      "default": "A personal note from Tumelo — 44 hours left",
      "ab_test": {
        "variants": [
          { "subject": "A personal note from Tumelo — 44 hours left", "weight": 0.8 },
          { "subject": "You get first word on the 10kg Wagyu lot", "weight": 0.2 }
        ]
      }
    },
    "preview_text": "The auction closes Saturday at noon. The gift deadline is Friday. I wanted you to know first — Tumelo",
    "html_template_id": "YOUR_TEMPLATE_ID_FOUNDER",
    "text_template_id": "YOUR_TEMPLATE_ID_FOUNDER_TEXT",
    "send_at": "now",
    "utm": {
      "source": "agentmail",
      "medium": "email",
      "campaign": "fathersday_send1"
    },
    "attachments": [
      {
        "cid": "studex-seal",
        "path": "/brand_assets/studex_meat_seal_gold_CANONICAL.png",
        "content_type": "image/png"
      }
    ]
  }'
```

> **Note on inline image (CID attachment):** AgentMail's exact syntax for inline CID attachments may vary — check their docs for the `attachments` schema. An alternative is to host the seal on AgentMail's CDN and reference it as a standard `<img src="https://cdn.agentmail.to/...">` tag instead.

---
---

# PRE-SEND QA CHECKLIST

Before pressing send on either version, verify the following:

**Subject line and preview:**
- Neither subject line triggers common spam filters (avoid all-caps, excessive punctuation, and words like "FREE", "WIN", "PRIZE" — these subjects are clean).
- Preview text renders correctly in Gmail, Apple Mail, and Outlook test sends.
- Subject line character counts: A (41 chars), B (43 chars) — both under 50.

**Links:**
- Confirm `studexmeat.com/products/biltong-gold` is a live, purchasable URL pointing to the correct R 1,450 / 8 × 70g SKU. This is the single highest-risk item — the SKU may not yet exist on Shopify. If it does not exist, either hold this send or replace the link with a working product URL or a contact/WhatsApp page.
- Confirm `studexmeat.com/products/wagyu-10kg-auction` resolves and the bid widget is live.
- Test all UTM-tagged URLs via a UTM builder preview to confirm parameters pass correctly through to GA4.
- Confirm `{{unsubscribe_url}}`, `{{preferences_url}}`, and `{{view_in_browser_url}}` are populated by AgentMail's template engine — these must not render as raw placeholders.

**Images:**
- Upload `studex_meat_seal_gold_CANONICAL.png` to AgentMail CDN before sending; confirm the `cid:studex-seal` reference (or hosted URL) resolves in a test render across Gmail, Apple Mail, and Outlook.
- Confirm the email renders acceptably even with images disabled (all-text fallback and alt text in place).

**Sender authentication:**
- Verify SPF and DKIM are configured and aligned for both `info@studexmeat.com` and `tumelo@studexmeat.com`. Run a test send to mail-tester.com and target a score of 9/10 or above before the live send.
- Confirm DMARC policy for `studexmeat.com` is in place (`p=quarantine` or `p=reject` preferred).
- Confirm the sending IP/domain is not on major blocklists (MXToolbox blacklist check).

**Mobile rendering:**
- Test on iPhone (Apple Mail and Gmail app) and Android Gmail at minimum.
- Confirm the hero headline does not overflow on a 375px viewport.

**POPIA / legal:**
- Unsubscribe link is live and one-click (no password required to unsubscribe).
- Physical address (`StudEx Meat (Pty) Ltd · Cape Town, South Africa`) is present in the footer.
- Contact email (`info@studexmeat.com` / `tumelo@studexmeat.com`) is present in the footer.
- List was obtained with consent; no purchased or scraped lists were used.

---
---

# POPIA COMPLIANCE NOTE

Both versions of this email comply with the Protection of Personal Information Act (POPIA), Act 4 of 2013 (South Africa). Each email contains: (1) the legal name and physical location of the responsible party — StudEx Meat (Pty) Ltd, Cape Town, South Africa; (2) a direct contact email address for the responsible party (`info@studexmeat.com` in Version A; `tumelo@studexmeat.com` in Version B); (3) a one-click unsubscribe link allowing the data subject to opt out of further direct marketing at any time, in compliance with section 69 of POPIA; and (4) a preference management link enabling subscribers to adjust the frequency or type of communications received. These emails must only be sent to data subjects who provided consent for direct marketing communications, or who are existing customers within the ambit of section 69(2) of POPIA (which permits marketing of similar products to existing customers without fresh consent, subject to the right to opt out). No sensitive personal information is collected in this communication. All data is processed by AgentMail as operator on behalf of StudEx Meat as responsible party — ensure an operator agreement is in place with AgentMail.

---

*Document produced: Thu 11 Jun 2026 — StudEx Meat / FD26-SENDNOW campaign. Both versions are copy-paste-ready pending Shopify URL confirmation and AgentMail list ID substitution.*
