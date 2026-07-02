# Studex Meat — Delivery Service Level Agreement (SLA)
**Version:** 1.0 | **Date:** 2026-06-29 | **Effective:** 2026-06-29
**Owner:** Robusca (CEO) | **Reviewed by:** Delivery Agent, Charlie (Orchestrator)
**Applies to:** All delivery orders placed via studexmeat.com

---

## 1. Purpose

This SLA defines Studex Meat's commitments to clients and sets operational standards for the internal team and contracted delivery drivers. It is the operating contract between Studex Meat and every party in the delivery chain.

---

## 2. Order-to-Door SLAs

### 2.1 Packing Stage

| Metric | Target | Maximum |
|--------|--------|---------|
| Order to Packed | < 2 hours | 2 hours |
| Late packing trigger | Packed but >2hrs from order time | Escalation flag |

**Definition:** "Packed" means the physical order is sealed, labelled, and ready for driver collection at the warehouse. Not just "being picked."

**Who owns this:** Charlie (Orchestrator) tracks via Kanban. If order sits in `📥 New Order` >2 hours, Charlie alerts the packing team immediately.

**Notes:**
- Fresh cuts (NOT pre-frozen): pack within 90 minutes where possible
- Bulk orders (>R2000): packing team lead must confirm pack time
- Orders placed after 16:00 SAST: pack by next morning (see Section 5)

---

### 2.2 Dispatch Stage

| Metric | Target | Maximum |
|--------|--------|---------|
| Packed to Dispatched | < 1 hour | 1 hour |
| Late dispatch trigger | Driver not assigned within 1hr of packing | Robusca alert |

**Definition:** "Dispatched" means a driver has physically collected the order from the warehouse and the team has moved the Kanban card to `🚚 Dispatched`.

**Who owns this:** Delivery Agent monitors. If dispatch not confirmed within 1 hour of packing, Delivery Agent escalates to Charlie.

---

### 2.3 Delivery Window by Zone

| Zone | Description | Delivery Window | Cutoff for Same-Day |
|------|-------------|-----------------|---------------------|
| Zone A | Within 10km of warehouse | 2–3 hours | Orders before 15:00 |
| Zone B | 10–25km from warehouse | 3–5 hours | Orders before 13:00 |
| Zone C | 25–60km from warehouse | 5–8 hours | Orders before 11:00 |
| Zone D | Outside 60km / Rural SA | Next-day or by arrangement | By arrangement |
| Zone E | National (remote) | Courier lead times apply | By arrangement |

**Warehouse location:** 190 Rooiberg St, N4 Gateway Park, The Willows, Pretoria

**Cutoff rule:** Orders placed *after* the same-day cutoff are automatically scheduled for next-day delivery. Client is notified via WhatsApp.

**Same-day delivery is NOT guaranteed for Zone C+ in peak periods (Fri–Sun, public holidays).**

---

### 2.4 ETA Accuracy

| Condition | Standard |
|-----------|----------|
| ETA stated at dispatch | ±30 minutes acceptable |
| ETA drift > 30 minutes | Delivery Agent must notify client |
| ETA drift > 60 minutes | Full SLA breach — Robusca notified + apology issued |
| Driver unreachable | 2 contact attempts, then switch provider |

---

## 3. Provider Assignment Rules

### Automatic Assignment Logic

```
IF order.value > R2000              → Dinkoko Priority
ELSE IF zone = A OR B AND dist < 15km → My Courier
ELSE                                  → Dinkoko (standard)
ELSE IF zone = C, D, E               → Dinkoko (standard)
```

| Provider | Coverage | Rate | Notes |
|----------|----------|------|-------|
| **Dinkoko Pty** (Derrick, +27 67 681 3076) | All zones, full service | R$$ | Priority flag for >R2000 |
| **My Courier** (Willy, +27 61 362 3448) | Zone A + B only, <15km | R$ | NOT for Zone C+ |

**Override:** If My Courier is unavailable or misses pickup window (>30 min after scheduled), Charlie automatically escalates to Dinkoko.

---

## 4. After-Hours Delivery Policy

### Standard Hours
Monday – Friday: 08:00 – 18:00 SAST
Saturday: 08:00 – 14:00 SAST
Sunday: **Closed** — no dispatch, no delivery

### After-Hours Rules

| Scenario | Rule |
|----------|------|
| Order placed after 16:00 | Next-day delivery confirmed at booking |
| Weekend order | Dispatched Monday morning |
| Client requests after-hours delivery | By written arrangement only — not automatic |
| After-hours surcharge | R150 applied to client's invoice — not disclosed to client unless requested |

**Critical:** All after-hours deliveries must be pre-booked with the driver and confirmed by Robusca before dispatch. No spontaneous after-hours deliveries.

---

## 5. Failed Delivery Protocol

A delivery is classified "failed" if:
1. Driver arrives and client is unreachable / not available (after 15 min wait)
2. Client refuses delivery at door
3. Address is undeliverable (wrong address, gate locked, security block)

### Failed Delivery — Step by Step

```
Step 1: Driver calls client (attempt 1)
         ↓ no answer within 5 min
Step 2: Driver texts client via WhatsApp with arrival notice
         ↓ no response in 10 min
Step 3: Driver waits 15 min, then returns to warehouse
         → Mark Kanban card: ⚠️ DELAYED — FAILED ATTEMPT
         → Delivery Agent sends Robusca alert immediately
         → Delivery Agent sends client WhatsApp:
           "We tried to deliver your order but couldn't reach you.
            Please reply to reschedule."
         ↓ client responds within 4 hours
Step 4: Re-dispatch same driver same day (if available)
         → Second delivery attempt at no charge
         ↓ no response after 4 hours
Step 5: Charlie contacts client directly by phone
         → If unreachable after 24 hours total: cancel order
         → Refund policy applies (see Section 7)
```

**Second attempt window:** Within 24 hours of original failed attempt. Client must be contacted by phone if WhatsApp fails.

**No second attempt fee** for first failed delivery where client was genuinely unreachable.

---

## 6. Cold Chain Minimum Standards

All Studex Meat products must maintain temperature integrity from warehouse to client door.

| Product Type | Minimum Temp | Maximum Temp | Monitoring |
|-------------|-------------|-------------|-----------|
| Fresh cuts (beef, lamb, poultry) | 0°C | 4°C | Visual + ice gel packs |
| Frozen products | -18°C | -12°C | Ice + insulated box |
| Processed (dried, cured) | Ambient | 25°C | Dry storage |

### Cold Chain Requirements

- **Insulated boxes:** All orders must travel in insulated box with minimum 2 ice gel packs
- **Driver vehicle:** Open bakkies must have canvas/cover. No exposed meat in rain or sun
- **Delivery wait time:** Driver may not leave meat unattended at doorstep >10 minutes in hot weather (>25°C). If client unreachable, driver returns to warehouse following FAILED DELIVERY protocol above
- **Photos:** Driver takes photo of delivered order at doorstep as proof of delivery
- **Refusal right:** Driver may refuse delivery if packaging is compromised (torn, wet, warm) — escalate to Charlie immediately

---

## 7. Refund & Compensation Policy

### SLA Breach Compensation

| Breach Type | Compensation |
|------------|-------------|
| Packing delayed >2hrs (confirmed SLA breach) | 10% off next order |
| Delivery delayed >60 min beyond ETA | 15% off next order + apology |
| Delivery delayed >2hrs | Full refund or 25% credit |
| Failed delivery (Studex error) | Full refund + free re-delivery |
| Cold chain failure (meat spoiled) | Full refund + replacement order |

**Process:** All compensation is applied as a Shopify discount code, emailed to client. Robusca approves all refunds >R500.

---

## 8. Escalation Matrix

| Trigger | Who Gets Alerted | How | Response Time |
|---------|----------------|-----|---------------|
| Packing overdue >2hrs | Charlie | Kanban flag + WhatsApp | 30 min |
| Dispatch overdue >1hr | Charlie + Robusca | WhatsApp alert | 20 min |
| Driver unreachable 20+ min | Robusca | WhatsApp + phone | 15 min |
| ETA missed by >30 min | Robusca | WhatsApp alert | 15 min |
| ETA missed by >60 min | Robusca | WhatsApp + client apology message | 10 min |
| Driver declined job | Robusca | WhatsApp alert | 15 min |
| Failed delivery attempt | Robusca | WhatsApp alert | 30 min |
| Client complaint via WhatsApp | Charlie + Naledi | WhatsApp forward | 1 hour |
| Cold chain failure | Robusca + Charlie | WhatsApp alert + phone | Immediate |

---

## 9. Daily Operating Windows

| Time | Activity | Owner |
|------|----------|-------|
| 06:00 SAST | Delivery Agent morning check — overnight orders | Delivery Agent |
| 07:00 SAST | Morning briefing sent to Robusca | Delivery Agent |
| 08:00 SAST | Warehouse opens — packing begins | Packing Team |
| 13:00 SAST | Zone B same-day cutoff | Charlie |
| 15:00 SAST | Zone A same-day cutoff | Charlie |
| 16:00 SAST | Last same-day dispatch | Packing Team |
| 16:30 SAST | After-hours orders logged for next day | Charlie |
| 17:00 SAST | Daily delivery report to Robusca | Delivery Agent |
| 18:00 SAST | Warehouse closes | Packing Team |

---

## 10. Metrics & Review

These SLAs are reviewed weekly by Robusca + Charlie. Key metrics tracked:

| Metric | Target | Floor (minimum) |
|--------|--------|----------------|
| Same-day dispatch rate | >90% | 80% |
| On-time delivery rate | >85% | 75% |
| First-attempt success rate | >80% | 70% |
| Cold chain compliance | 100% | 95% |
| Client satisfaction (delivery) | >4.5/5 | 4.0/5 |

**Provider review:** Dinkoko and My Courier performance reviewed monthly. Poor performance triggers a formal review conversation with Robusca.

---

*This SLA is the operational backbone of Studex Meat Delivery OS.*
*Robusca owns this. Charlie executes it. Delivery Agent monitors it.*
*Last updated: 2026-06-29*
