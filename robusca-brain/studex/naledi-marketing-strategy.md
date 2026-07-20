# Naledi × Larry: Marketing Strategy
# StudEx Meat — 1-Page Playbook
# Prepared by Robusca (CMO Support) | 2026-03-13

---

## STRATEGY A: ORGANIC-ONLY (R0 Budget)

**Goal:** 500+ visits/month to studexmeat.com from social within 90 days

### Week 1-2: Foundation
- Post 1x/day on Instagram + TikTok (Naledi content)
- Every post ends: "🛒 Link in bio → studexmeat.com"
- Reply to EVERY comment within 1 hour (algorithm gold)
- Use 8-12 targeted hashtags: #WagyuSA #HalaalMeat #StudExMeat #BraaiBoss #SouthAfricanFood

### Content Mix (Larry schedules automatically)
| Day | Content Type | Platform |
|-----|-------------|---------|
| Mon | Product showcase (image) | Instagram + Facebook |
| Tue | Educational reel | TikTok |
| Wed | Behind-the-scenes | Instagram Stories |
| Thu | Recipe/cooking video | TikTok + Instagram |
| Fri | Customer UGC repost | All |
| Sat | Weekend braai content | Instagram |
| Sun | "Shop now" post + promo | All platforms |

### Call-to-Action Formula (Every Post)
```
[Hook] + [Product benefit] + [Social proof] + [CTA]
"Premium Wagyu biltong that sells out every week 🥩
Halaal certified | Handcrafted | SA-made
👉 studexmeat.com | Free delivery R999+"
```

### Larry Automation (Once Active)
- Auto-schedule from Naledi approval queue
- Cross-post same content to all platforms simultaneously
- Auto-reply to comments using pre-built response templates
- Track which posts drive traffic via UTM → Airtable

**Expected Results (90 days):**
- Instagram: 500-2k followers
- TikTok: 1k-5k (fastest growth platform)
- Monthly store visits from social: 300-800
- Zero ad spend

---

## STRATEGY B: SMALL PAID BUDGET (R500-2000/month)

**Goal:** 5x organic reach, 20+ conversions/month from paid

### Budget Allocation
| Platform | Budget/month | Focus |
|----------|------------|-------|
| Instagram Boost | R800 | Best organic posts → boost to lookalike audiences |
| Facebook Ads | R700 | Retargeting website visitors |
| TikTok Promote | R500 | Best-performing reels |

### Targeting
- South Africa only
- Age: 25-55
- Interests: Premium food, Halaal, BBQ, Wagyu, Gourmet
- Lookalike: Website visitors (Facebook Pixel on Shopify)

### Paid + Organic Combo
1. Naledi creates content organically (via Larry)
2. Monitor 48hrs — if post gets 3%+ engagement → boost it
3. R200 boost per post × 4 posts/month = R800
4. Retarget website visitors with "You left something in your cart" Facebook ads
5. TikTok promote best reel to broader SA audience

### ROI Target
- Average order: R850
- Cost per acquisition target: R80-150
- Break-even: 8 paid orders/month covers ad spend
- Goal: 20+ orders/month from paid = R17,000 GMV

### Naledi + Larry Workflow for Paid
```
Naledi generates content
→ Larry posts organically
→ Robusca monitors engagement (cron job)
→ If engagement > threshold → flag for Agent Lord
→ Agent Lord approves boost
→ Larry/Facebook API boosts the post
→ Sales tracked in Airtable → Shopify
```

---

## TOOLS REQUIRED

| Tool | Purpose | Status |
|------|---------|--------|
| Larry (Postiz) | Auto-scheduling | ⏳ Pending API key |
| Blotato | Cross-posting | ⏳ Pending API key |
| Airtable | Analytics tracking | ⏳ Pending token |
| Facebook Pixel | Retargeting | ⏳ Add to Shopify |
| Google Analytics | UTM tracking | ⏳ Setup on Shopify |
| N8n | Automation flows | ⏳ Pending setup |

---

*The organic strategy can start TODAY once Larry is installed.*
*Paid strategy activates once Facebook Pixel is on Shopify.*
