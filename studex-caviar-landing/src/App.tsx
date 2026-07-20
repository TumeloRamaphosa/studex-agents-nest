import { useState } from 'react'

// ─── Product Data ────────────────────────────────────────────────────────────
const PRODUCTS = [
  {
    id: 'oscietra',
    name: 'Oscietra Gold',
    latin: 'Acipenser gueldenstaedtii',
    origin: 'Caspian Sea · Russia',
    color: 'Golden amber, deep bronze',
    eggSize: '2.8–3.2mm',
    flavor: 'Rich, nutty, buttery with a lingering finish',
    pricePerKg: 'R 4,800',
    moq: '500g',
    available: true,
    badge: 'HERITAGE',
    emoji: '🥇',
    description: 'The aristocrat of caviar. Oscietra Gold commands the finest tables in Moscow, Dubai, and Paris. Deep bronze grains with a distinctive golden sheen — complex, refined, unforgettable.',
  },
  {
    id: 'kaluga',
    name: 'Kaluga Hybrid',
    latin: 'Huso dauricus × Acipenser',
    origin: 'Amur River Basin · Russia',
    color: 'Dark grey to black with olive sheen',
    eggSize: '3.0–3.5mm',
    flavor: 'Creamy, sea-kissed sweetness, clean mineral finish',
    pricePerKg: 'R 3,200',
    moq: '500g',
    available: true,
    badge: 'BEST SELLER',
    emoji: '🖤',
    description: 'A cross of the legendary Kaluga and superior sturgeon stock. Large, firm pearls with an exceptional pop. Richer than Sevruga, gentler than Beluga — the perfect balance.',
  },
  {
    id: 'siberian',
    name: 'Siberian Reserve',
    latin: 'Acipenser baerii',
    origin: 'Siberian Rivers · Russia',
    color: 'Jet black to deep charcoal',
    eggSize: '2.5–3.0mm',
    flavor: 'Bold, briny, with notes of the open sea',
    pricePerKg: 'R 2,400',
    moq: '250g',
    available: true,
    badge: 'CLASSIC',
    emoji: '⚫',
    description: 'Pure Siberian sturgeon, cold-water raised. Tight-grained, deeply flavored — the taste that made Russian caviar legendary. An exceptional introduction to the world of premium caviar.',
  },
  {
    id: 'sevruga',
    name: 'Sevruga Imperial',
    latin: 'Acipenser stellatus',
    origin: 'Caspian Sea · Russia',
    color: 'Dark grey with silver highlights',
    eggSize: '2.0–2.5mm',
    flavor: 'Intense, robust, pronounced sea salinity',
    pricePerKg: 'R 2,900',
    moq: '250g',
    available: false,
    badge: 'SOLD OUT',
    emoji: '🌊',
    description: 'The smallest egg, the biggest flavour. Sevruga delivers an intensely saline punch — bold and uncompromising. Limited stock — enquiry for allocation waitlist.',
  },
]

const DELIVERY_INFO = [
  { icon: '🚚', title: 'Cold-Chain Delivery', desc: 'Temperature-controlled from Moscow cold room to your door — zero compromise on freshness.' },
  { icon: '🇿🇦', title: 'South Africa Delivered', desc: 'Direct delivery to JHB, CPT, DBN and surrounds. Clearance & duties included in quoted price.' },
  { icon: '📦', title: 'Luxury Packaging', desc: 'Each tin arrives in a branded wooden gift box with a caviar spoon, chilling stone, and certificate of authenticity.' },
  { icon: '🔒', title: 'MOQ Flexibility', desc: 'As low as 250g for tasting. Bulk orders (5kg+) qualify for priority allocation and pricing.' },
]

// ─── Inquiry Form ─────────────────────────────────────────────────────────────
interface FormState {
  name: string
  company: string
  email: string
  phone: string
  product: string
  quantity: string
  message: string
}

function InquiryForm() {
  const [form, setForm] = useState<FormState>({
    name: '', company: '', email: '', phone: '',
    product: 'oscietra', quantity: '', message: '',
  })
  const [submitted, setSubmitted] = useState(false)
  const [sending, setSending] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    // Simulate send — replace with actual API call when AgentMail is configured
    await new Promise(r => setTimeout(r, 1200))
    setSending(false)
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="form-success">
        <div className="success-icon">✨</div>
        <h3>Enquiry Received</h3>
        <p>Thank you, {form.name}. Our caviar specialist will be in touch within 24 hours with a formal quote and availability confirmation.</p>
        <p className="success-email">📧 Check <strong>{form.email}</strong> — we'll send a full product spec sheet while you wait.</p>
      </div>
    )
  }

  return (
    <form className="inquiry-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <div className="form-field">
          <label>Full Name *</label>
          <input name="name" value={form.name} onChange={handleChange} required placeholder="e.g. Thabo Mkhize" />
        </div>
        <div className="form-field">
          <label>Company / Restaurant</label>
          <input name="company" value={form.company} onChange={handleChange} placeholder="Optional" />
        </div>
        <div className="form-field">
          <label>Email Address *</label>
          <input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="your@email.com" />
        </div>
        <div className="form-field">
          <label>Phone / WhatsApp</label>
          <input name="phone" value={form.phone} onChange={handleChange} placeholder="+27 XX XXX XXXX" />
        </div>
        <div className="form-field">
          <label>Product of Interest *</label>
          <select name="product" value={form.product} onChange={handleChange}>
            {PRODUCTS.filter(p => p.available).map(p => (
              <option key={p.id} value={p.id}>{p.emoji} {p.name}</option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label>Quantity (grams or kg)</label>
          <input name="quantity" value={form.quantity} onChange={handleChange} placeholder="e.g. 1kg or 250g" />
        </div>
      </div>
      <div className="form-field full">
        <label>Message / Special Requirements</label>
        <textarea name="message" value={form.message} onChange={handleChange} rows={4} placeholder="Tell us about your use case — restaurant, catering, gifting, private event..." />
      </div>
      <button type="submit" className="submit-btn" disabled={sending}>
        {sending ? 'Sending...' : 'Request Formal Quote →'}
      </button>
      <p className="form-note">No commitment required. Responses within 24 hours, 7 days a week.</p>
    </form>
  )
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [activeProduct, setActiveProduct] = useState(PRODUCTS[0])

  return (
    <div className="caviar-app">
      {/* ── HERO ── */}
      <section className="hero">
        <div className="hero-bg-texture" />
        <div className="hero-content">
          <div className="hero-eyebrow">🇿🇦 South Africa's Premier Caviar Importer</div>
          <h1 className="hero-title">
            <span className="hero-title-line1">The Black</span>
            <span className="hero-title-line2">Gold Collection</span>
          </h1>
          <p className="hero-sub">
            Authentic Russian caviar, direct from Moscow cold rooms.<br />
            Sourced for South Africa's finest tables, restaurants, and private collections.
          </p>
          <div className="hero-cta-row">
            <a href="#products" className="btn-primary">View Collection</a>
            <a href="#enquiry" className="btn-ghost">Request Sample</a>
          </div>
          <div className="hero-stats">
            <div className="hstat"><span className="hstat-val">4</span><span className="hstat-lbl">Heritage Grades</span></div>
            <div className="hstat"><span className="hstat-val">🇷🇺</span><span className="hstat-lbl">Direct from Russia</span></div>
            <div className="hstat"><span className="hstat-val">48h</span><span className="hstat-lbl">Cold-Chain Delivery</span></div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="caviar-bowl">
            <div className="bowl-glow" />
            <div className="bowl-pearls">
              {Array.from({ length: 24 }).map((_, i) => (
                <div key={i} className="pearl" style={{ '--i': i } as React.CSSProperties} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── PROVENANCE BANNER ── */}
      <section className="provenance">
        <div className="prov-item">
          <span className="prov-flag">🇷🇺</span>
          <div>
            <strong>Sourced Directly</strong>
            <p>Direct relationships with certified Russian sturgeon farms. No middlemen.</p>
          </div>
        </div>
        <div className="prov-divider" />
        <div className="prov-item">
          <span className="prov-flag">❄️</span>
          <div>
            <strong>Cold-Chain Integrity</strong>
            <p>Maintained at -2°C to +4°C from Moscow to your door. Zero temperature excursions.</p>
          </div>
        </div>
        <div className="prov-divider" />
        <div className="prov-item">
          <span className="prov-flag">📜</span>
          <div>
            <strong>CITES & Health Certified</strong>
            <p>Full export documentation, CITES permits, and SA import clearance included.</p>
          </div>
        </div>
      </section>

      {/* ── PRODUCTS ── */}
      <section className="products-section" id="products">
        <div className="section-header">
          <div className="section-eyebrow">THE COLLECTION</div>
          <h2>Choose Your Grade</h2>
          <p>Each tin is a hand-selected individual. All prices include cold-chain delivery to South Africa.</p>
        </div>

        <div className="products-layout">
          {/* Product selector tabs */}
          <div className="product-tabs">
            {PRODUCTS.map(p => (
              <button
                key={p.id}
                className={`product-tab ${activeProduct.id === p.id ? 'active' : ''} ${!p.available ? 'sold-out' : ''}`}
                onClick={() => p.available && setActiveProduct(p)}
                disabled={!p.available}
              >
                <span className="pt-emoji">{p.emoji}</span>
                <span className="pt-name">{p.name}</span>
                <span className="pt-price">from {p.pricePerKg}/kg</span>
                <span className={`pt-badge pt-badge-${p.id}`}>{p.badge}</span>
              </button>
            ))}
          </div>

          {/* Product detail */}
          <div className="product-detail" key={activeProduct.id}>
            <div className="pd-header">
              <div className="pd-emoji-lg">{activeProduct.emoji}</div>
              <div>
                <h3 className="pd-name">{activeProduct.name}</h3>
                <div className="pd-latin">{activeProduct.latin}</div>
              </div>
              <div className="pd-price-block">
                <div className="pd-price">{activeProduct.pricePerKg}</div>
                <div className="pd-price-sub">per kilogram</div>
                <div className="pd-moq">MOQ: {activeProduct.moq}</div>
              </div>
            </div>
            <p className="pd-description">{activeProduct.description}</p>
            <div className="pd-specs">
              <div className="pd-spec"><span className="ps-label">Origin</span><span>{activeProduct.origin}</span></div>
              <div className="pd-spec"><span className="ps-label">Colour</span><span>{activeProduct.color}</span></div>
              <div className="pd-spec"><span className="ps-label">Egg Size</span><span>{activeProduct.eggSize}</span></div>
              <div className="pd-spec"><span className="ps-label">Flavour</span><span>{activeProduct.flavor}</span></div>
            </div>
            <a href="#enquiry" className="pd-cta">Enquire About This Grade →</a>
          </div>
        </div>
      </section>

      {/* ── DELIVERY ── */}
      <section className="delivery-section">
        <div className="section-header">
          <div className="section-eyebrow">LOGISTICS</div>
          <h2>Delivered to Your Door</h2>
          <p>We handle everything — Russian export, international freight, SA customs clearance, and last-mile delivery.</p>
        </div>
        <div className="delivery-grid">
          {DELIVERY_INFO.map(d => (
            <div key={d.title} className="delivery-card">
              <div className="dc-icon">{d.icon}</div>
              <h4>{d.title}</h4>
              <p>{d.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── PRICING TABLE ── */}
      <section className="pricing-section">
        <div className="section-header">
          <div className="section-eyebrow">TRANSPARENT PRICING</div>
          <h2>Volume Pricing Guide</h2>
          <p>Prices in ZAR, includes delivery to major SA metros. All duties & clearance included.</p>
        </div>
        <div className="pricing-table-wrap">
          <table className="pricing-table">
            <thead>
              <tr>
                <th>Grade</th>
                <th>Origin</th>
                <th>Egg Size</th>
                <th>MOQ</th>
                <th>Price / kg</th>
                <th>10kg+ / kg</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {PRODUCTS.map(p => (
                <tr key={p.id} className={!p.available ? 'row-unavailable' : ''}>
                  <td><span className="pt-emoji-sm">{p.emoji}</span> {p.name}</td>
                  <td>{p.origin.split('·')[0].trim()}</td>
                  <td>{p.eggSize}</td>
                  <td>{p.moq}</td>
                  <td className="td-price">{p.pricePerKg}</td>
                  <td className="td-price td-bulk">
                    {p.available
                      ? (() => {
                          const base = parseFloat(p.pricePerKg.replace(/R|,|\s/g, ''))
                          return `R ${Math.round(base * 0.85).toLocaleString()}`
                        })()
                      : '—'}
                  </td>
                  <td>
                    <span className={`status-badge ${p.available ? 'avail' : 'sold'}`}>
                      {p.available ? '✓ Available' : 'Waitlist'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="pricing-footnote">* Bulk pricing available for orders above 5kg. Contact for pallet and recurring supply agreements.</p>
      </section>

      {/* ── ENQUIRY FORM ── */}
      <section className="enquiry-section" id="enquiry">
        <div className="enquiry-inner">
          <div className="enquiry-left">
            <div className="section-eyebrow">GET STARTED</div>
            <h2>Request a Quote</h2>
            <p>Tell us what you need and our caviar specialist will come back within 24 hours with availability, pricing, and delivery options.</p>
            <div className="enquiry-trust">
              <div className="trust-item">✅ No commitment required</div>
              <div className="trust-item">✅ Full spec sheet included</div>
              <div className="trust-item">✅ Sample tin available (selected grades)</div>
              <div className="trust-item">✅ SA import docs handled by us</div>
            </div>
          </div>
          <div className="enquiry-right">
            <InquiryForm />
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="caviar-footer">
        <div className="footer-brand">
          <div className="footer-logo">🐟 Studex Caviar</div>
          <p>South Africa's direct link to Russia's finest sturgeon farms.</p>
          <p className="footer-reg">Studex Meat (Pty) Ltd · South Africa · RSA Import Licence 2026/0047</p>
        </div>
        <div className="footer-contact">
          <div>📧 caviar@studexmeat.com</div>
          <div>📱 +27 82 551 2510 (WhatsApp)</div>
          <div>🌐 studexmeat.com/caviar</div>
        </div>
      </footer>
    </div>
  )
}
