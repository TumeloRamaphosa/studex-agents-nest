import { styles } from './styles'

/**
 * STUDEX — CIIE 2026 BUYER BRIEF (Shanghai, 5–10 Nov 2026)
 *
 * Rebuilt 2026-10-30 (Build Hour) against `coffee-fob-band-card.md`.
 *
 * 🔑 WHAT CHANGED AND WHY — every price string below is now traceable to
 * `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.6 / §2.7 (the band card). Before
 * this rebuild the page carried:
 *   - mangled price strings ("USD 4.20-4.20-4.80/kg", "USD 4.80-3.60-4.00/kg")
 *   - a cupping score of 87-90+ when our OWN registry says 84-87
 *   - "PROWTC (Premium Rwandan Organic Whole Trade Coffee)" listed as a
 *     CERTIFICATION. PROWTC is a Dubai BUYER, not a certifier, and the
 *     expansion was fabricated. "PROWTC" is on our forbidden-strings list.
 *   - "Fully Certified for China Entry" + "All documentation required for
 *     China import already in place" — unsourced certification claims
 *   - "South African registered exporter" — forbidden string
 *   - the forbidden tier price "USD 4.60/kg", and an invented "from USD 4.30/kg"
 *   - MOQ "60kg (1 bag)" against our real 5-10 kg sample / 20 MT / 40 MT / 5 MT
 *   - "FOB Mombasa or Durban" when A1/A2 are FOB Djibouti
 *   - the tariff dated "July 2026" — the tariff is 1 May 2026; 20 Jul 2026 is
 *     the unified phytosanitary regime. Two different things.
 *   - "Rwanda -> China Zero-Tariff · Effective July 2026" + a footer "China
 *     Zero-Tariff Protocol" implying a 30 Apr 2028 window that does not apply
 *     to a Rwandan LDC origin
 *   - "June 2026" (a forbidden string) in the harvest row
 *   - two mailto addresses (tumelo@, coffee@) that are asserted NOWHERE in the
 *     registry, one of which is not a live mailbox we hold
 *   - a duplicated footer sentence
 *
 * The 20-name buyer list is NOT on this page. A buyer-facing page must not
 * publish our target list. It lives in `ciie-buyer-brief/BUYER-LIST.md`.
 */

export default function App() {
  return (
    <div style={styles.root}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logoMark}>S</div>
          <div>
            <div style={styles.company}>STUDEX MEAT (PTY) LTD</div>
            <div style={styles.tagline}>Rwanda Green Coffee · Cape Town &amp; Kigali</div>
          </div>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.badge}>CIIE 2026</div>
          <div style={styles.dates}>Shanghai · Nov 5–10</div>
        </div>
      </header>

      {/* Hero */}
      <section style={styles.hero}>
        <div style={styles.heroEyebrow}>🇨🇳 Zero Tariff Since 1 May 2026 · Rwandan LDC Origin, No Expiry</div>
        <h1 style={styles.heroTitle}>
          Rwanda Green Coffee,<br />
          <em>Traced to the Lot</em>
        </h1>
        <p style={styles.heroSub}>
          Rwanda&apos;s exports to China grew from roughly $35m in 2019 to{' '}
          <strong style={styles.heroStrong}>$227m in 2025</strong>. China imported{' '}
          <strong style={styles.heroStrong}>$246m of African coffee</strong> in 2025, up from $157m the
          year before. And the route runs through Kunshan: it handles roughly{' '}
          <strong style={styles.heroStrong}>60% of China&apos;s green-bean imports</strong> and about 60% of
          its roasting capacity, on a customs zone that has already built{' '}
          <strong style={styles.heroStrong}>bespoke clearance protocols for imported coffee</strong>. We
          supply Rwanda A1 and A2 green lots to that corridor — washing station to container.
        </p>
        <div style={styles.heroCta}>
          <a
            href="mailto:info@studexmeat.com?subject=CIIE%202026%20%E2%80%94%20Meeting%20Request"
            style={styles.ctaPrimary}
          >
            Request a Meeting at CIIE →
          </a>
          <a
            href="mailto:info@studexmeat.com?subject=Rwanda%20Coffee%20Sample%20Request"
            style={styles.ctaSecondary}
          >
            Request a Sample Shipment
          </a>
        </div>
      </section>

      {/* Stats Bar */}
      <section style={styles.statsBar}>
        {[
          { val: '$227m', label: 'Rwanda exports to China, 2025', sub: '~$35m in 2019 · $131m in 2023' },
          { val: '$4.20–4.80', label: 'A1 FOB, USD per kg', sub: '17+ screen · 20 MT · FOB Djibouti' },
          { val: '84–87', label: 'SCA cupping score, A1 washed', sub: 'Nyamasheke, Western Province' },
          { val: '0%', label: 'China import tariff', sub: 'Rwandan LDC origin — no expiry' },
        ].map((s) => (
          <div key={s.label} style={styles.statItem}>
            <div style={styles.statVal}>{s.val}</div>
            <div style={styles.statLabel}>{s.label}</div>
            <div style={styles.statSub}>{s.sub}</div>
          </div>
        ))}
      </section>

      {/* Why Rwanda */}
      <section style={styles.section}>
        <div style={styles.sectionLabel}>THE OPPORTUNITY</div>
        <h2 style={styles.sectionTitle}>Why Rwanda, Why Now</h2>
        <div style={styles.grid2}>
          {[
            {
              icon: '🚫',
              title: 'Zero Tariff Since 1 May 2026',
              body: 'China eliminated tariffs on all taxable products from 53 African countries from 1 May 2026. From 20 July 2026 a single continent-wide approval regime lets qualified coffee beans from all 53 countries clear under one framework — no country-by-country negotiation. As a Rwandan least-developed-country origin, our zero-tariff treatment carries no expiry date.',
            },
            {
              icon: '🏔️',
              title: 'Nyamasheke — High-Altitude Volcanic Soils',
              body: 'Western Rwanda at 1,700–2,200 masl produces a clean, bright cup with jasmine and stone-fruit character and a dark-chocolate finish. A1 lots are hand-sorted, fully washed and raised-bed dried, cupping 84–87 on the SCA scale with very low defect counts.',
            },
            {
              icon: '📋',
              title: 'Origin Documentation, Lot by Lot',
              body: 'Every consignment ships with phytosanitary certificate, certificate of origin, certificate of analysis and fumigation records, with lot-level traceability back to the washing station. A copy of the documentation pack is available ahead of any meeting.',
            },
            {
              icon: '🏙️',
              title: 'The Kunshan Corridor — Where the Coffee Actually Is',
              body: 'Kunshan sits beside the Port of Shanghai and handles roughly 60% of China\u2019s green-bean imports and about 60% of its roasting capacity \u2014 and it imported RMB 2.56 billion of green beans in 2025, up 56.4% year on year. Its customs zone has tailored clearance protocols specifically for imported coffee. Meeting in Shanghai puts us inside the corridor rather than at the edge of it.',
            },
            {
              icon: '📦',
              title: 'CIIE 2026 — Shanghai, Nov 5–10',
              body: 'Studex Meat will be at CIIE Shanghai, 5–10 November 2026. Cupping sessions are available for qualified buyers, and we will bring current-crop samples of A1 and A2 to the stand.',
            },
          ].map((item) => (
            <div key={item.title} style={styles.card}>
              <div style={styles.cardIcon}>{item.icon}</div>
              <h3 style={styles.cardTitle}>{item.title}</h3>
              <p style={styles.cardBody}>{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Product Spec */}
      <section style={{ ...styles.section, ...styles.sectionAlt }}>
        <div style={styles.sectionLabel}>PRODUCT SPECIFICATIONS</div>
        <h2 style={styles.sectionTitle}>Rwanda A1 / A2 — Green Coffee</h2>
        <div style={styles.specTable}>
          {[
            ['Origin', 'Nyamasheke District, Western Province, Rwanda'],
            ['Grade', 'A1 Premium (17+ screen) · A2 Commercial (15–16 screen)'],
            ['Altitude', '1,700–2,200 masl'],
            ['SCA Score', '84–87 (A1, washed)'],
            ['Cup Profile', 'Jasmine, stone fruit, dark chocolate finish'],
            ['Processing', 'Fully washed, raised-bed dried'],
            ['Harvest', '2026 main crop, harvested March–June · next crop from March 2027'],
            ['Packaging', 'Hermetic-lined jute bags, 60 kg'],
            ['MOQ', 'Samples 5–10 kg · A1 20 MT · A2 40 MT · Custom blend 5 MT'],
            [
              'FOB Price',
              'A1 USD 4,200–4,800/MT · A2 USD 3,600–4,000/MT · Custom blend USD 3,800/MT — FOB Djibouti',
            ],
            ['CIF Shanghai', 'A1 USD 4,800–5,400/MT · A2 USD 4,200–4,700/MT · from 1 MT'],
            ['Incoterm', 'FOB Djibouti · CIF and DAP on request'],
            ['HS Code', '0901'],
            [
              'Lead Time',
              '5–7 weeks Kigali → Djibouti → Shanghai (origin handling 5–7 days + ~21 days sea)',
            ],
            [
              'Documents',
              'Phytosanitary certificate · certificate of origin (COO) · certificate of analysis (COA) · fumigation record · lot traceability sheet',
            ],
          ].map(([k, v]) => (
            <div key={k} style={styles.specRow}>
              <span style={styles.specKey}>{k}</span>
              <span style={styles.specVal}>{v}</span>
            </div>
          ))}
        </div>
        <div style={styles.sampleNote}>
          📦 <strong>Samples available now.</strong> Sample shipments of 5–10 kg are arranged on request and
          quoted per shipment, covering air freight and courier handling. Cup it against your Brazil base —
          we think you will be surprised.
        </div>
      </section>

      {/* Pricing */}
      <section style={styles.section}>
        <div style={styles.sectionLabel}>COMMERCIAL TERMS</div>
        <h2 style={styles.sectionTitle}>Pricing &amp; Logistics</h2>
        <div style={styles.grid3}>
          {[
            {
              tier: 'Sample',
              price: 'USD 28–45/kg',
              moq: '5–10 kg',
              desc: 'Air freight or courier to Shanghai. Quoted per shipment and confirmed against the current crop before dispatch.',
            },
            {
              tier: 'Pilot Lot',
              price: 'USD 4,200–4,700/MT',
              moq: '1 MT CIF Shanghai',
              desc: 'A2 Commercial (15–16 screen) landed Shanghai, or A1 at USD 4,800–5,400/MT. Sea freight via Djibouti. 5–7 weeks from order to Shanghai.',
            },
            {
              tier: 'Custom Blend',
              price: 'USD 3,800/MT',
              moq: '5 MT FOB Djibouti',
              desc: 'Your blend profile at a 5 MT lot — sized for a roaster who needs differentiation, not a container. Private label packaging available.',
            },
          ].map((p) => (
            <div key={p.tier} style={styles.priceCard}>
              <div style={styles.priceTier}>{p.tier}</div>
              <div style={styles.priceVal}>{p.price}</div>
              <div style={styles.priceMoq}>MOQ {p.moq}</div>
              <p style={styles.priceDesc}>{p.desc}</p>
            </div>
          ))}
        </div>
        <div style={styles.callout}>
          <strong>Annual supply.</strong> Beyond the published lots we can quote a fixed 12-month supply
          agreement with allocated stock, on EXW or FOB terms. Premium natural lots are quoted per lot
          with no published price, from a 500 kg minimum.
        </div>
      </section>

      {/* Customs & Documentation readiness */}
      <section style={{ ...styles.section, ...styles.sectionAlt }}>
        <div style={styles.sectionLabel}>CUSTOMS &amp; DOCUMENTATION READINESS</div>
        <h2 style={styles.sectionTitle}>What Is in Place, and What Is Not</h2>
        <p style={styles.lead}>
          We would rather show you the checklist now than have a broker ask for it in week three. This is
          our current position on the China customs path for a Rwandan green-coffee exporter.
        </p>
        <div style={styles.checklist}>
          {[
            {
              state: 'ready',
              text: 'Phytosanitary certificate, certificate of origin, certificate of analysis and fumigation records — issued per consignment by the certifying bodies in Rwanda.',
            },
            {
              state: 'ready',
              text: 'Tariff position confirmed: zero tariff for a Rwandan least-developed-country origin, with no expiry date attached to our origin.',
            },
            {
              state: 'ready',
              text: 'Unified phytosanitary approval framework covering all 53 African countries, in force since 20 July 2026.',
            },
            {
              state: 'progress',
              text: 'Overseas-establishment registration and certification required of a Rwandan green-coffee exporter to clear Chinese customs — being confirmed with our freight forwarder. We will send the certificate numbers before any contract is signed, not after.',
            },
            {
              state: 'progress',
              text: 'Final Chinese import-registration particulars for the specific consignee entity — confirmed per buyer alongside the forwarder.',
            },
          ].map((row) => (
            <div key={row.text} style={styles.checkRow}>
              <span style={row.state === 'ready' ? styles.checkReady : styles.checkProgress}>
                {row.state === 'ready' ? '✓' : '◐'}
              </span>
              <span style={styles.checkText}>{row.text}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Studex Advantage */}
      <section style={styles.section}>
        <div style={styles.sectionLabel}>WHY STUDEX MEAT</div>
        <h2 style={styles.sectionTitle}>Not Just a Supplier — a Market Entry Partner</h2>
        <div style={styles.grid2}>
          {[
            'Exporting entity Studex Meat (Pty) Ltd — trading from Cape Town, South Africa and Kigali, Rwanda, with freight out of Djibouti, Mombasa and Durban',
            'Green coffee sourced through washing stations in Nyamasheke, Western Province, with lot-level traceability back to the washing station on every shipment',
            'We work the small lot on purpose: a 5 MT custom blend with published cupping and lot traceability is a different product from a container of commodity arabica',
            'Documentation handled end to end — phytosanitary, certificate of origin, certificate of analysis, fumigation record — and released with the consignment, not chased afterwards',
          ].map((t) => (
            <div key={t} style={styles.bulletRow}>
              <span style={styles.bullet}>✓</span>
              <span>{t}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Contact */}
      <section style={styles.contact}>
        <div style={styles.contactCard}>
          <h2 style={styles.contactTitle}>Meet Us at CIIE 2026</h2>
          <p style={styles.contactSub}>November 5–10, Shanghai · Meeting by appointment</p>
          <div style={styles.contactDetails}>
            <div style={styles.contactPerson}>
              <div style={styles.contactName}>Tumelo Ramaphosa</div>
              <div style={styles.contactRole}>Founder &amp; CEO, Studex Meat (Pty) Ltd</div>
              <div style={styles.contactRole}>Cape Town, South Africa &amp; Kigali, Rwanda</div>
            </div>
            <div style={styles.contactLinks}>
              <a href="mailto:info@studexmeat.com" style={styles.contactLink}>
                info@studexmeat.com
              </a>
              <a href="tel:+27844216035" style={styles.contactLink}>
                +27 84 421 6035
              </a>
              <a href="https://wa.me/27794988737" style={styles.contactLink}>
                WhatsApp +27 94 988 8737
              </a>
              <a href="https://studexmeat.com" style={styles.contactLink}>
                studexmeat.com
              </a>
            </div>
          </div>
          <div style={styles.contactCta}>
            <a
              href="mailto:info@studexmeat.com?subject=CIIE%202026%20%E2%80%94%20Meeting%20Request&body=Hi%20Tumelo%2C%0A%0AI%27d%20like%20to%20schedule%20a%20meeting%20with%20the%20Studex%20team%20at%20CIIE%202026.%0A%0ACompany%3A%0AImport%20volume%3A%0APreferred%20meeting%20time%3A%0A%0ABest%2C"
              style={styles.ctaPrimary}
            >
              📅 Book a CIIE Meeting
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <div>
          Studex Meat (Pty) Ltd · Cape Town, South Africa &amp; Kigali, Rwanda · CIIE 2026
        </div>
        <div style={{ marginTop: 4, color: '#6a7090', fontSize: 11 }}>
          Rwanda A1 / A2 green coffee · FOB Djibouti · CIF Shanghai available · HS 0901 · Zero tariff,
          Rwandan LDC origin
        </div>
      </footer>
    </div>
  )
}
