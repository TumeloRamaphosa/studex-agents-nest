import { useState } from 'react'

// ── Types ───────────────────────────────────────────────────────────────────
interface ProductGrade {
  id: string
  name: string
  origin: string
  cert: string
  process: string
  cupScore: string
  moq: string
  priceRange: string
  container: string
  description: string
  notes: string[]
  available: boolean
}

interface InquiryForm {
  company: string
  contact: string
  email: string
  phone: string
  country: string
  volume: string
  grade: string
  message: string
}

// ── Data ─────────────────────────────────────────────────────────────────────
const grades: ProductGrade[] = [
  {
    id: 'a1-washed',
    name: 'A1 Washed',
    origin: 'Rwanda — Nyamasheke, Rusizi District',
    cert: 'PROWTC · Rainforest Alliance',
    process: 'Washed',
    cupScore: '87/100',
    moq: '500 kg',
    priceRange: '$8.50–$10.00 / kg FOB',
    container: '20ft (10 MT) · 40ft (21 MT)',
    description: 'Flagship specialty grade. Full traceability from cooperative to port. Floral and citrus notes, bright acidity, silky body. Preferred by five-star hotels and specialty roasters.',
    notes: ['Fully washed', 'Sun-dried on raised beds', 'Hand-sorted', 'GPS-tagged farms'],
    available: true,
  },
  {
    id: 'a2-washed',
    name: 'A2 Washed',
    origin: 'Rwanda — Huye Mountain, Southern Province',
    cert: 'PROWTC · Fairtrade',
    process: 'Washed',
    cupScore: '84/100',
    moq: '1,000 kg',
    priceRange: '$7.20–$8.80 / kg FOB',
    container: '20ft (10 MT) · 40ft (21 MT)',
    description: 'Consistent, high-quality grade ideal for mid-tier hospitality chains and office coffee programmes. Balanced profile: chocolate, stone fruit, clean finish.',
    notes: ['Fully washed', 'Mechanical dryer + raised bed', 'Screen 15+', 'Year-round supply'],
    available: true,
  },
  {
    id: 'a1-natural',
    name: 'A1 Natural',
    origin: 'Rwanda — Rulindo District, Northern Province',
    cert: 'PROWTC · UTZ',
    process: 'Natural',
    cupScore: '86/100',
    moq: '500 kg',
    priceRange: '$9.00–$11.00 / kg FOB',
    container: '20ft (10 MT) · 40ft (21 MT)',
    description: 'Sun-dried natural process. Intensive fruit character — blueberry, dark cherry, wine. Distinctive for single-origin espresso and pour-over programmes at boutique cafés.',
    notes: ['Natural sun-dried', '30-day drying', 'Hand-selected', 'Micro-lot available'],
    available: true,
  },
]

// ── Components ────────────────────────────────────────────────────────────────
function Navbar({ onCta }: { onCta: () => void }) {
  return (
    <nav className="nav">
      <div className="nav-logo">
        <span className="logo-mark">◆</span>
        <span>STUDEX <span className="logo-sub">COFFEE</span></span>
      </div>
      <ul className="nav-links">
        <li><a href="#origin">Origin</a></li>
        <li><a href="#grades">Grades</a></li>
        <li><a href="#pricing">Pricing</a></li>
        <li><a href="#credentials">Credentials</a></li>
        <li><a href="#ciie">CIIE 2026</a></li>
      </ul>
      <button className="nav-cta" onClick={onCta}>B2B Inquiry</button>
    </nav>
  )
}

function Hero({ onInquiry }: { onInquiry: () => void }) {
  return (
    <section className="hero">
      <div className="hero-content">
        <div className="hero-badge">🇨🇳 CIIE November 2026 · Shanghai</div>
        <h1 className="hero-title">Africa's Finest Coffee,<br />Sourced to the World</h1>
        <p className="hero-desc">
          Rwanda A1/A2 Washed & Natural — PROWTC-certified, farm-to-door traceability.
          Supplying five-star hotels, specialty roasters, and HORECA distributors across
          the Middle East, China, and Europe.
        </p>
        <div className="hero-stats">
          <div className="hstat"><span className="hstat-val">0%</span><span className="hstat-lbl">China Tariff<br /><em>Effective May 2026</em></span></div>
          <div className="hstat"><span className="hstat-val">10 MT</span><span className="hstat-lbl">Min. Container<br /><em>20ft container</em></span></div>
          <div className="hstat"><span className="hstat-val">PROWTC</span><span className="hstat-lbl">Certifications<br /><em>Full documentation</em></span></div>
          <div className="hstat"><span className="hstat-val">RWF→CNY</span><span className="hstat-lbl">Direct Trade<br /><em>No middlemen</em></span></div>
        </div>
        <div className="hero-btns">
          <button className="btn-primary" onClick={onInquiry}>Request B2B Pricing</button>
          <a href="#grades" className="btn-outline">View Coffee Grades</a>
        </div>
      </div>
      <div className="hero-visual">
        <img
          src="https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=900&q=85"
          alt="Rwanda coffee farm"
          className="hero-img"
        />
        <div className="hero-badge-img">Rwanda · Nyamasheke · 1,800m ASL</div>
      </div>
    </section>
  )
}

function ChinaBanner() {
  return (
    <div className="china-banner">
      <div className="cb-icon">🇨🇳</div>
      <div className="cb-text">
        <strong>Market Intelligence:</strong> China is Rwanda's #1 export destination.
        Effective May 2026, <strong>0% tariff</strong> on African coffee imports.
        Rwanda A1/A2 commands a <strong>40–60% premium</strong> over commodity index pricing.
        China coffee market: +21%/year since 2010.窗口已开 — The window is open.
      </div>
    </div>
  )
}

function OriginSection() {
  return (
    <section className="origin-section" id="origin">
      <div className="section-label">OUR ORIGIN</div>
      <h2 className="section-title">Rwanda. Altitude. Traceability.</h2>
      <div className="origin-grid">
        <div className="origin-card">
          <div className="oc-icon">🏔️</div>
          <h3>Altitude</h3>
          <p>1,600–2,200m ASL in the Nyamasheke and Rusizi districts. Cool nights, volcanic soil, consistent rainfall. Ideal conditions for slow cherry development and dense, flavorful beans.</p>
        </div>
        <div className="origin-card">
          <div className="oc-icon">🤝</div>
          <h3>Cooperative Model</h3>
          <p>Direct relationships with 4 cooperatives across Rwanda. No middlemen. Farmers receive 23% above commodity price. Full GPS-tagged supply chain from plot to port.</p>
        </div>
        <div className="origin-card">
          <div className="oc-icon">📋</div>
          <h3>PROWTC Certified</h3>
          <p>All lots certified through the Processing, Research, and Overseas Marketing Trade Company (PROWTC). Required for Rwanda coffee export. Full documentation package for customs clearance.</p>
        </div>
        <div className="origin-card">
          <div className="oc-icon">🚢</div>
          <h3>Logistics</h3>
          <p>Kigali Logistics Platform → Durban Port → global destinations. 28-day lead time from order confirmation to port. Cold-chain andfumigation documentation handled end-to-end.</p>
        </div>
      </div>
    </section>
  )
}

function GradesSection({ onInquiry }: { onInquiry: (grade: string) => void }) {
  return (
    <section className="grades-section" id="grades">
      <div className="section-label">PRODUCT</div>
      <h2 className="section-title">Coffee Grades — Available Now</h2>
      <p className="section-desc">All lots tested and approved by PROWTC quality assessors. Samples available for qualified buyers. Pricing in USD per kg FOB Durban.</p>
      <div className="grades-grid">
        {grades.map(g => (
          <div key={g.id} className={`grade-card ${!g.available ? 'grade-unavailable' : ''}`}>
            {g.id === 'a1-washed' && <div className="grade-featured-badge">★ Flagship</div>}
            <div className="gc-header">
              <div>
                <div className="gc-name">{g.name}</div>
                <div className="gc-origin">📍 {g.origin}</div>
              </div>
              <div className="gc-score">{g.cupScore}</div>
            </div>
            <div className="gc-cert">{g.cert}</div>
            <p className="gc-desc">{g.description}</p>
            <ul className="gc-notes">
              {g.notes.map(n => <li key={n}>◈ {n}</li>)}
            </ul>
            <div className="gc-details">
              <div className="gcd"><span>Process</span><strong>{g.process}</strong></div>
              <div className="gcd"><span>MOQ</span><strong>{g.moq}</strong></div>
              <div className="gcd"><span>Container</span><strong>{g.container}</strong></div>
              <div className="gcd"><span>Price</span><strong className="price-highlight">{g.priceRange}</strong></div>
            </div>
            <button
              className="gc-inquire"
              onClick={() => onInquiry(g.name)}
              disabled={!g.available}
            >
              {g.available ? `Inquire: ${g.name}` : 'Enquire for Next Harvest'}
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}

function PricingTable() {
  return (
    <section className="pricing-section" id="pricing">
      <div className="section-label">B2B PRICING</div>
      <h2 className="section-title">Volume-Based Pricing — FOB Durban</h2>
      <table className="pricing-table">
        <thead>
          <tr>
            <th>Grade</th>
            <th>Volume</th>
            <th>Price / kg</th>
            <th>20ft Container<br /><small>(10 MT)</small></th>
            <th>40ft Container<br /><small>(21 MT)</small></th>
            <th>Lead Time</th>
          </tr>
        </thead>
        <tbody>
          <tr className="tr-featured">
            <td><strong>A1 Washed</strong></td>
            <td>500–999 kg</td>
            <td className="td-price">$10.00</td>
            <td>$100,000</td>
            <td>—</td>
            <td>21 days</td>
          </tr>
          <tr className="tr-featured">
            <td><strong>A1 Washed</strong></td>
            <td>1,000 + kg</td>
            <td className="td-price">$8.50</td>
            <td>$85,000</td>
            <td>$178,500</td>
            <td>28 days</td>
          </tr>
          <tr>
            <td><strong>A2 Washed</strong></td>
            <td>1,000–4,999 kg</td>
            <td className="td-price">$8.80</td>
            <td>$88,000</td>
            <td>—</td>
            <td>28 days</td>
          </tr>
          <tr>
            <td><strong>A2 Washed</strong></td>
            <td>5,000 + kg</td>
            <td className="td-price">$7.20</td>
            <td>$72,000</td>
            <td>$151,200</td>
            <td>35 days</td>
          </tr>
          <tr>
            <td><strong>A1 Natural</strong></td>
            <td>500 + kg</td>
            <td className="td-price">$9.00</td>
            <td>$90,000</td>
            <td>$189,000</td>
            <td>28 days</td>
          </tr>
        </tbody>
      </table>
      <p className="pricing-note">
        * Prices in USD per kg, FOB Durban Port. Insurance, freight, and import duties quoted separately.
        * 10% deposit required to confirm order. Balance due against Bill of Lading.
        * Sample kits (250g × 3 grades): available for $45 including shipping.
      </p>
    </section>
  )
}

function CredentialsSection() {
  const certs = [
    { name: 'PROWTC', desc: 'Processing, Research & Overseas Marketing Trade Company — Rwanda Ministry of Trade certification. Required for all Rwanda green coffee exports.' },
    { name: 'Rainforest Alliance', desc: 'Sustainable farming practices. Environmental protection. Worker welfare standards verified by third-party auditors.' },
    { name: 'UTZ Certified', desc: 'Sustainable coffee sourcing standard. Full chain of custody from farm to export document.' },
    { name: 'Fairtrade', desc: 'A2 grade only. Minimum price floor. Community development premium of $0.20/kg paid directly to cooperative.' },
    { name: 'GSM (GACC)', desc: 'General Scheme of tariff rate quota — China market access documentation. Essential for China-bound shipments.' },
    { name: 'ICO Member', desc: 'International Coffee Organization member. Quality and export standards verified under ICO Agreement 2007.' },
  ]
  return (
    <section className="credentials-section" id="credentials">
      <div className="section-label">CREDENTIALS & COMPLIANCE</div>
      <h2 className="section-title">Documentation Package — Ready to Ship</h2>
      <p className="section-desc">Every container comes with a complete documentation package for customs clearance and import compliance.</p>
      <div className="creds-grid">
        {certs.map(c => (
          <div key={c.name} className="cred-card">
            <div className="cred-badge">✓</div>
            <div className="cred-name">{c.name}</div>
            <p className="cred-desc">{c.desc}</p>
          </div>
        ))}
      </div>
      <div className="doc-checklist">
        <div className="dc-title">Included with every shipment:</div>
        <div className="dc-items">
          {['Phytosanitary Certificate', 'Certificate of Origin (Rwandan)', 'ICO Export Declaration', 'PROWTC Quality Attestation', 'Bill of Lading (draft before shipping)', 'Cupping Report (per lot)', 'Packaging List & Weight Certificate', 'Fumigation Certificate (if required)'].map(d => (
            <div key={d} className="dci">✅ {d}</div>
          ))}
        </div>
      </div>
    </section>
  )
}

function CIIESection({ onInquiry }: { onInquiry: () => void }) {
  return (
    <section className="ciie-section" id="ciie">
      <div className="ciie-inner">
        <div className="ciie-flag">🇨🇳</div>
        <div className="ciie-content">
          <div className="ciie-label">EVENT · NOV 5–10, 2026 · SHANGHAI</div>
          <h2 className="ciie-title">China International Import Expo</h2>
          <p className="ciie-desc">
            CIIE 2026 — World's first dedicated import expo. 150+ countries, 3,400+ exhibitors, 500k+ visitors.
            Rwanda coffee buyers will be present. <strong>Studex Coffee has secured booth access.</strong>
            Pre-booking meetings with qualified buyers is now open.
          </p>
          <div className="ciie-stats">
            <div><strong>3,400+</strong><span>Exhibitors</span></div>
            <div><strong>500k+</strong><span>Visitors</span></div>
            <div><strong>$80B+</strong><span>Deals signed (2025)</span></div>
            <div><strong>150+</strong><span>Countries</span></div>
          </div>
          <div className="ciie-btns">
            <button className="btn-primary" onClick={onInquiry}>Book CIIE Meeting Slot</button>
            <span className="ciie-deadline">⏰ Application closes: July 20, 2026</span>
          </div>
        </div>
      </div>
    </section>
  )
}

function InquiryForm({ preselected, onClose }: { preselected?: string; onClose: () => void }) {
  const [form, setForm] = useState<InquiryForm>({
    company: '', contact: '', email: '', phone: '', country: '',
    volume: '', grade: preselected || '', message: '',
  })
  const [submitted, setSubmitted] = useState(false)

  const update = (field: keyof InquiryForm, value: string) =>
    setForm(f => ({ ...f, [field]: value }))

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal success-modal" onClick={e => e.stopPropagation()}>
          <div className="success-icon">✅</div>
          <h3>Inquiry Received</h3>
          <p>Thank you, {form.contact}. Our team will respond within <strong>24 hours</strong> with a formal quote.</p>
          <p className="success-email">Confirmation sent to: <strong>{form.email}</strong></p>
          <div className="success-next">
            <strong>Next step:</strong> Expect a cupping kit proposal and PROWTC quality documentation within 48h.
          </div>
          <button className="btn-primary" onClick={onClose}>Close</button>
        </div>
      </div>
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal inquiry-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-title">B2B Coffee Inquiry</div>
            <div className="modal-sub">Response within 24 hours · Formal quote within 48 hours</div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Company Name *</label>
              <input required type="text" value={form.company} onChange={e => update('company', e.target.value)} placeholder="e.g. PROWTC Dubai, Shanghai Specialty Imports" />
            </div>
            <div className="form-group">
              <label>Contact Person *</label>
              <input required type="text" value={form.contact} onChange={e => update('contact', e.target.value)} placeholder="Full name" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Business Email *</label>
              <input required type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="work@company.com" />
            </div>
            <div className="form-group">
              <label>Phone / WhatsApp</label>
              <input type="tel" value={form.phone} onChange={e => update('phone', e.target.value)} placeholder="+971 50 000 0000" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Country / Region *</label>
              <select required value={form.country} onChange={e => update('country', e.target.value)}>
                <option value="">Select country...</option>
                <option>China</option><option>UAE</option><option>Saudi Arabia</option>
                <option>Qatar</option><option>Singapore</option><option>South Africa</option>
                <option>Germany</option><option>Netherlands</option><option>United Kingdom</option>
                <option>United States</option><option>Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Required Volume *</label>
              <select required value={form.volume} onChange={e => update('volume', e.target.value)}>
                <option value="">Select volume...</option>
                <option>500 kg – 1 MT</option>
                <option>1 MT – 5 MT</option>
                <option>5 MT – 10 MT</option>
                <option>10 MT+ (full container)</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Coffee Grade of Interest</label>
            <select value={form.grade} onChange={e => update('grade', e.target.value)}>
              <option value="">No preference — surprise us</option>
              <option>A1 Washed</option>
              <option>A2 Washed</option>
              <option>A1 Natural</option>
              <option>Sample Kit (all 3 grades)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Message / Requirements</label>
            <textarea rows={3} value={form.message} onChange={e => update('message', e.target.value)} placeholder="Tell us about your procurement needs, target delivery window, or any specific requirements..." />
          </div>
          <div className="form-footer">
            <div className="form-privacy">🔒 Your information is used only to respond to this inquiry. We do not share data with third parties.</div>
            <button type="submit" className="btn-primary">Send Inquiry →</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">◆ STUDEX <span>COFFEE</span></div>
          <p> Rwanda A1/A2 Washed & Natural · PROWTC Certified<br />
          Farm-to-door traceability · B2B only · Durban FOB</p>
        </div>
        <div className="footer-links">
          <div className="fl-col">
            <strong>Products</strong>
            <a href="#grades">A1 Washed</a>
            <a href="#grades">A2 Washed</a>
            <a href="#grades">A1 Natural</a>
            <a href="#pricing">Pricing Table</a>
          </div>
          <div className="fl-col">
            <strong>Company</strong>
            <a href="#origin">Our Origin</a>
            <a href="#credentials">Credentials</a>
            <a href="#ciie">CIIE 2026</a>
            <a href="mailto:coffee@studexmeat.com">Contact</a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        © 2026 Studex Coffee (Pty) Ltd · South Africa · B2B Only · All prices in USD FOB Durban
      </div>
    </footer>
  )
}

// ── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [showInquiry, setShowInquiry] = useState(false)
  const [inquiryGrade, setInquiryGrade] = useState<string>('')

  const openInquiry = (grade = '') => {
    setInquiryGrade(grade)
    setShowInquiry(true)
  }

  return (
    <div className="app">
      <Navbar onCta={() => openInquiry()} />
      <Hero onInquiry={() => openInquiry()} />
      <ChinaBanner />
      <OriginSection />
      <GradesSection onInquiry={openInquiry} />
      <PricingTable />
      <CredentialsSection />
      <CIIESection onInquiry={() => openInquiry()} />
      <Footer />
      {showInquiry && (
        <InquiryForm
          preselected={inquiryGrade}
          onClose={() => setShowInquiry(false)}
        />
      )}
    </div>
  )
}
