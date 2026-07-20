import { useState } from 'react'

const GREEN = '#2E5E3A'
const GOLD = '#C9A84C'
const DARK = '#1A1208'
const CREAM = '#F5F0E8'
const CREAM_DARK = '#EDE5D8'
const TEXT = '#2C2416'
const TEXT_MUTED = '#6B5E4A'
const WHITE = '#FFFFFF'

function App() {
  const [form, setForm] = useState({
    name: '', company: '', email: '', phone: '', whatsapp: '', wechat: '',
    quantity: '', origin: 'Rwanda A2 Washed', message: ''
  })
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    const payload = {
      source: 'China Coffee LP — Rwanda Export',
      timestamp: new Date().toISOString(),
      ...form
    }

    try {
      // Try AgentMail webhook first
      await fetch('https://api.agentmail.to/v0/webhook/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${import.meta.env.VITE_AGENTMAIL_KEY || ''}` },
        body: JSON.stringify(payload)
      })
    } catch {
      // Fallback: mailto
    }

    // Also open mailto as backup
    const subject = encodeURIComponent(`China Coffee Enquiry — ${form.company || form.name}`)
    const body = encodeURIComponent(
      `Name: ${form.name}\nCompany: ${form.company}\nEmail: ${form.email}\nPhone: ${form.phone}\nWhatsApp: ${form.whatsapp}\nWeChat: ${form.wechat}\nQuantity: ${form.quantity}\nOrigin: ${form.origin}\nMessage: ${form.message}`
    )
    window.location.href = `mailto:ceo@agent.studexmeat.com?subject=${subject}&body=${body}`

    setSubmitted(true)
    setSubmitting(false)
  }

  return (
    <div style={{ fontFamily: "'Inter', sans-serif", background: CREAM, color: TEXT, lineHeight: 1.6 }}>

    {/* HERO */}
    <section style={{ background: DARK, color: WHITE, padding: '80px 40px 100px', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 80% 20%, rgba(46,94,58,0.6) 0%, transparent 60%), radial-gradient(ellipse at 20% 80%, rgba(201,168,76,0.15) 0%, transparent 50%)`, pointerEvents: 'none' }} />
      <div style={{ maxWidth: 1100, margin: '0 auto', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'inline-block', fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, border: '1px solid rgba(201,168,76,0.4)', padding: '6px 16px', borderRadius: 2, marginBottom: 32 }}>
          🇨🇳 China Market · Effective July 20, 2026
        </div>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(42px, 6vw, 80px)', fontWeight: 900, lineHeight: 1.05, marginBottom: 12, color: WHITE }}>
          Rwanda <span style={{ color: GOLD }}>Premium Coffee</span><br />Export to China
        </h1>
        <p style={{ fontSize: 18, color: 'rgba(255,255,255,0.65)', fontWeight: 300, maxWidth: 540, marginBottom: 48 }}>
          Premium Rwanda A1 &amp; A2 grade Arabica coffee. Tariff-free entry into China from July 20, 2026. Rainforest Alliance certified. CIF Shanghai pricing.
        </p>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          {[
            '✓ Rainforest Alliance Certified',
            '✓ Direct Trade Origin',
            '✓ Zero Tariff — China 2026',
            '✓ Min. Order 1 MT'
          ].map(b => (
            <div key={b} style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.12)', padding: '10px 18px', borderRadius: 4, fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.85)' }}>
              <span style={{ color: GOLD }}>✓</span> {b.replace('✓ ', '')}
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* STATS BAR */}
    <div style={{ background: GREEN, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
      {[
        { v: '0%', l: 'China Import Tariff' },
        { v: '53', l: 'African Countries Eligible' },
        { v: 'Jul 20', l: 'Policy Effective Date' },
        { v: '1 MT', l: 'Minimum Order (CIF)' },
      ].map(s => (
        <div key={s.l} style={{ padding: '32px 28px', textAlign: 'center', borderRight: '1px solid rgba(255,255,255,0.15)' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: GOLD }}>{s.v}</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: 4 }}>{s.l}</div>
        </div>
      ))}
    </div>

    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '80px 40px' }}>

      {/* WHY RWANDA */}
      <div style={{ marginBottom: 80 }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          Why Rwanda Coffee
          <span style={{ flex: 1, maxWidth: 40, height: 1, background: GOLD, display: 'inline-block' }} />
        </div>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 700, marginBottom: 32, lineHeight: 1.2 }}>
          The World's Most Story-Rich<br />Arabica Origin
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 28 }}>
          {[
            { title: 'Rainforest Alliance', desc: 'Full RA certification across all supply chain stages. The single most important credential for EU and now China premium buyers.', accent: false },
            { title: 'Geographic Identity', desc: "Rwanda's high-altitude volcanic soils produce a distinct Arabica profile — bright acidity, floral aromatics, clean finish — prized by specialty roasters globally.", accent: true },
            { title: 'Traceable Supply Chain', desc: 'End-to-end lot traceability from washing station to port. Full documentation: phytosanitary certificates, COO, bill of lading, insurance.', accent: false },
          ].map(c => (
            <div key={c.title} style={{ background: WHITE, border: `1px solid ${CREAM_DARK}`, borderRadius: 6, padding: '32px 28px', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: c.accent ? GOLD : GREEN }} />
              <div style={{ width: 44, height: 44, background: c.accent ? 'rgba(201,168,76,0.12)' : 'rgba(46,94,58,0.1)', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 18, color: c.accent ? GOLD : GREEN, fontSize: 20 }}>☐</div>
              <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, marginBottom: 10 }}>{c.title}</h3>
              <p style={{ fontSize: 14, color: TEXT_MUTED, lineHeight: 1.65 }}>{c.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* OPPORTUNITY BANNER */}
      <div style={{ background: DARK, borderRadius: 8, padding: '48px 52px', marginBottom: 80, display: 'grid', gridTemplateColumns: '1fr auto', gap: 40, alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
            China-Africa Trade Policy
            <span style={{ flex: 1, maxWidth: 40, height: 1, background: GOLD, display: 'inline-block' }} />
          </div>
          <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 700, marginBottom: 16, color: WHITE }}>Historic Market Opening</h2>
          <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: 15, maxWidth: 560 }}>
            From July 20, 2026, China opens coffee imports to all 53 African countries under a unified phytosanitary system. Rwanda qualifies immediately. This is the window — act before competitors lock in supply agreements.
          </p>
        </div>
        <div style={{ background: 'rgba(201,168,76,0.15)', border: `1px solid ${GOLD}`, color: GOLD, fontSize: 13, fontWeight: 600, padding: '10px 20px', borderRadius: 100, whiteSpace: 'nowrap', textAlign: 'center' }}>
          <strong style={{ display: 'block', fontSize: 22, fontFamily: "'Playfair Display', serif", marginBottom: 2 }}>0%</strong>
          Import Tariff<br />
          <span style={{ fontSize: 11, opacity: 0.7 }}>May 2026 onward</span>
        </div>
      </div>

      {/* PRODUCT TABLE */}
      <div style={{ marginBottom: 80 }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          Product Specifications
          <span style={{ flex: 1, maxWidth: 40, height: 1, background: GOLD, display: 'inline-block' }} />
        </div>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 700, marginBottom: 24 }}>Available Lots</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', background: WHITE, borderRadius: 6, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
          <thead style={{ background: GREEN }}>
            <tr>
              {['Grade', 'Process', 'Altitude', 'Score', 'MOQ', 'Certification'].map(h => (
                <th key={h} style={{ padding: '16px 20px', textAlign: 'left', fontSize: 12, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.85)' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              { grade: 'Rwanda A1', process: 'Washed', alt: '1,800–2,200m', score: '85+', moq: '1 MT', cert: ['Rainforest Alliance'] },
              { grade: 'Rwanda A2', process: 'Washed', alt: '1,600–2,000m', score: '82–84', moq: '1 MT', cert: ['Rainforest Alliance'] },
              { grade: 'Rwanda Premium\nBourbon varietal, single washing station', process: 'Natural', alt: '1,900–2,200m', score: '87+', moq: '500 kg', cert: ['Rainforest Alliance', 'Direct Trade'] },
            ].map(r => (
              <tr key={r.grade} style={{ borderBottom: `1px solid ${CREAM_DARK}` }}>
                <td style={{ padding: '16px 20px', fontSize: 14, fontWeight: 600, color: GREEN, whiteSpace: 'pre-line' }}>{r.grade}</td>
                <td style={{ padding: '16px 20px', fontSize: 14 }}>{r.process}</td>
                <td style={{ padding: '16px 20px', fontSize: 13, fontFamily: 'monospace' }}>{r.alt}</td>
                <td style={{ padding: '16px 20px', fontSize: 13, fontFamily: 'monospace' }}>{r.score}</td>
                <td style={{ padding: '16px 20px', fontSize: 13, fontFamily: 'monospace' }}>{r.moq}</td>
                <td style={{ padding: '16px 20px' }}>
                  {r.cert.map(c => (
                    <span key={c} style={{ display: 'inline-block', background: c === 'Direct Trade' ? 'rgba(201,168,76,0.15)' : 'rgba(46,94,58,0.1)', color: c === 'Direct Trade' ? '#8A6A2A' : GREEN, fontSize: 11, fontWeight: 600, padding: '3px 10px', borderRadius: 100, marginRight: 4 }}>{c}</span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* PRICING */}
      <div style={{ marginBottom: 80 }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          Pricing &amp; Incoterms
          <span style={{ flex: 1, maxWidth: 40, height: 1, background: GOLD, display: 'inline-block' }} />
        </div>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 700, marginBottom: 32 }}>CIF Shanghai — All-In Delivered Cost</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }}>
          {[
            {
              title: 'Rwanda A1 — Washed', featured: false,
              price: '$4,800 – $5,400', note: 'Price varies by lot, season, and volume. FOB Djibouti reference.',
              items: ['Marine freight Kigali → Djibouti (port)', 'Sea freight Djibouti → Shanghai', 'Port handling & clearance at Shanghai', 'Phytosanitary certificate included', 'COO (Certificate of Origin) included', 'Marine cargo insurance included']
            },
            {
              title: 'Rwanda A2 — Washed', featured: true,
              price: '$4,200 – $4,700', note: 'Strong value-to-quality ratio. Ideal for mid-scale roasters & café chains.',
              items: ['All-inclusive CIF Shanghai pricing', 'Full Rainforest Alliance documentation', 'Dedicated lot reservation', 'Quality inspection on request', 'SGS pre-shipment cupping available', 'Lead time: 5–7 weeks from order confirmation']
            },
          ].map(p => (
            <div key={p.title} style={{ background: WHITE, border: `1px solid ${p.featured ? GOLD : CREAM_DARK}`, borderRadius: 6, padding: '36px 32px', boxShadow: p.featured ? `0 0 0 1px ${GOLD}` : 'none' }}>
              {p.featured && <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: GOLD, marginBottom: 8 }}>Most Popular for China Importers</div>}
              <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, marginBottom: 6 }}>{p.title}</h3>
              <div style={{ fontSize: 12, color: TEXT_MUTED, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 24 }}>CIF Shanghai · per MT</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 38, fontWeight: 700, color: GREEN }}>{p.price}</div>
              <div style={{ fontSize: 12, color: TEXT_MUTED, marginTop: 6 }}>{p.note}</div>
              <ul style={{ marginTop: 20, listStyle: 'none', padding: 0 }}>
                {p.items.map(i => (
                  <li key={i} style={{ fontSize: 13, padding: '6px 0', display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                    <span style={{ color: GREEN, fontWeight: 700, flexShrink: 0 }}>✓</span>
                    <span style={{ color: TEXT_MUTED }}>{i}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* LOGISTICS */}
      <div style={{ background: WHITE, borderRadius: 6, padding: 48, marginBottom: 80, border: `1px solid ${CREAM_DARK}` }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          Supply Chain
          <span style={{ flex: 1, maxWidth: 40, height: 1, background: GOLD, display: 'inline-block' }} />
        </div>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 700, marginBottom: 36 }}>From Rwanda Hills to Shanghai Port<br />in 5–7 Weeks</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 32 }}>
          {[
            { n: 1, title: 'Order Confirmed', desc: 'MOQ 1 MT. Order confirmed and lot reserved. Proforma invoice issued.' },
            { n: 2, title: 'Quality Check', desc: 'SGS or local agent pre-shipment cupping. Sample approval before loading.' },
            { n: 3, title: 'Kigali → Djibouti', desc: 'Ground freight from washing station to Djibouti port. Typically 5–7 days.' },
            { n: 4, title: 'Djibouti → Shanghai', desc: 'Sea freight approx. 21 days. Port clearance, duty (0%), delivery to buyer warehouse.' },
          ].map(s => (
            <div key={s.n} style={{ textAlign: 'center' }}>
              <div style={{ width: 36, height: 36, background: GREEN, color: WHITE, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 14, margin: '0 auto 12px' }}>{s.n}</div>
              <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 6 }}>{s.title}</h4>
              <p style={{ fontSize: 12, color: TEXT_MUTED, lineHeight: 1.5 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* INQUIRY FORM */}
      <div id="enquire" style={{ background: `linear-gradient(135deg, ${GREEN} 0%, #1C3A2A 100%)`, borderRadius: 8, padding: '64px 60px', marginBottom: 40 }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: GOLD, marginBottom: 16 }}>🇨🇳 Limited Window — Act Before July 20</div>
          <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(28px, 4vw, 42px)', fontWeight: 700, color: WHITE, marginBottom: 16 }}>Inquire About Rwanda Coffee</h2>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: 16, maxWidth: 520, margin: '0 auto' }}>
            We supply roasters, importers, and distributors across Asia. Complete the form and our team will respond within 24 hours with a formal quote or sample details.
          </p>
        </div>

        {submitted ? (
          <div style={{ textAlign: 'center', padding: '48px 32px', background: 'rgba(255,255,255,0.08)', borderRadius: 8, border: `1px solid rgba(201,168,76,0.4)` }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>✅</div>
            <h3 style={{ fontFamily: "'Playfair Display', serif", color: WHITE, fontSize: 24, marginBottom: 12 }}>Enquiry Received</h3>
            <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: 15 }}>
              Thank you, {form.name || 'valued buyer'}. Our team will contact you within 24 hours.<br />
              For urgent enquiries, message us directly on <strong style={{ color: GOLD }}>WhatsApp</strong>.
            </p>
            <div style={{ marginTop: 24 }}>
              <a href="https://wa.me/27698881094" target="_blank" rel="noopener" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: '#25D366', color: WHITE, fontWeight: 700, fontSize: 14, padding: '12px 28px', borderRadius: 4, textDecoration: 'none' }}>
                💬 Chat on WhatsApp
              </a>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ maxWidth: 720, margin: '0 auto' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20, marginBottom: 20 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Full Name *</label>
                <input required name="name" value={form.name} onChange={handleChange} placeholder="e.g. Li Wei" style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Company *</label>
                <input required name="company" value={form.company} onChange={handleChange} placeholder="Company /  公司名称" style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Business Email *</label>
                <input required type="email" name="email" value={form.email} onChange={handleChange} placeholder="you@company.com" style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Phone / WhatsApp</label>
                <input name="phone" value={form.phone} onChange={handleChange} placeholder="+86 / +65 / +971..." style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>WeChat ID</label>
                <input name="wechat" value={form.wechat} onChange={handleChange} placeholder="WeChat ID / 微信" style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Quantity Needed</label>
                <select name="quantity" value={form.quantity} onChange={handleChange} style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }}>
                  <option value="" style={{ background: GREEN }}>Select quantity</option>
                  <option value="500 kg" style={{ background: GREEN }}>500 kg (trial)</option>
                  <option value="1 MT" style={{ background: GREEN }}>1 MT</option>
                  <option value="5 MT" style={{ background: GREEN }}>5 MT</option>
                  <option value="10+ MT" style={{ background: GREEN }}>10+ MT</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Preferred Origin / Grade</label>
              <select name="origin" value={form.origin} onChange={handleChange} style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', boxSizing: 'border-box' }}>
                <option value="Rwanda A1 Washed" style={{ background: GREEN }}>Rwanda A1 — Washed (85+ pts)</option>
                <option value="Rwanda A2 Washed" style={{ background: GREEN }}>Rwanda A2 — Washed (82-84 pts)</option>
                <option value="Rwanda Premium Natural" style={{ background: GREEN }}>Rwanda Premium — Natural (87+ pts)</option>
                <option value="Any Rwanda" style={{ background: GREEN }}>Open to recommendations</option>
              </select>
            </div>

            <div style={{ marginBottom: 32 }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Message</label>
              <textarea name="message" value={form.message} onChange={handleChange} rows={4} placeholder="Tell us about your roastery, current sourcing, or any specific requirements... / 介绍您的烘焙厂和采购需求" style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 4, color: WHITE, fontSize: 14, outline: 'none', resize: 'vertical', boxSizing: 'border-box' }} />
            </div>

            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button type="submit" disabled={submitting} style={{ background: submitting ? 'rgba(201,168,76,0.5)' : GOLD, color: DARK, fontWeight: 700, fontSize: 14, padding: '14px 40px', borderRadius: 4, border: 'none', cursor: submitting ? 'not-allowed' : 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8, transition: 'all 0.2s' }}>
                {submitting ? '⏳ Submitting...' : '📩 Submit Enquiry'}
              </button>
              <a href="https://wa.me/27698881094" target="_blank" rel="noopener" style={{ background: '#25D366', color: WHITE, fontWeight: 700, fontSize: 14, padding: '14px 32px', borderRadius: 4, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                💬 WhatsApp Us Direct
              </a>
            </div>

            <p style={{ textAlign: 'center', marginTop: 20, fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
              Or email <a href="mailto:ceo@agent.studexmeat.com" style={{ color: GOLD }}>ceo@agent.studexmeat.com</a> directly · Response within 24 hours
            </p>
          </form>
        )}
      </div>

    </div>

    {/* FOOTER */}
    <footer style={{ textAlign: 'center', padding: '32px 40px', fontSize: 12, color: TEXT_MUTED, borderTop: `1px solid ${CREAM_DARK}` }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, color: TEXT, fontSize: 14 }}>Studex Wildlife</div>
      <p style={{ marginTop: 6 }}>Kigali · Dubai · Shanghai · Cape Town</p>
      <p style={{ marginTop: 10 }}>
        <a href="mailto:ceo@agent.studexmeat.com" style={{ color: GREEN, textDecoration: 'none' }}>ceo@agent.studexmeat.com</a> ·
        Rwanda A1/A2 Coffee Export · Effective July 2026
      </p>
    </footer>

    </div>
  )
}

export default App
