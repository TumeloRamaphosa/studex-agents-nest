import { useState } from 'react'

const products = {
  biltong: {
    title: 'Biltong',
    tagline: 'Wind-dried. Heritage-crafted. Unapologetically South African.',
    description: 'Premium biltong from grass-fed beef, cured with coriander, salt, and time. Zero preservatives. Zero sugar. 40g protein per 100g. This is the original — not jerky.',
    cta: 'Partner With Us',
    color: '#dc2626',
    emoji: '🥩',
  },
  coffee: {
    title: 'Ngagi Coffee',
    tagline: 'From Rwanda\'s women farmers, direct to your cup.',
    description: 'Single-origin Rwandan Arabica sourced from women-led cooperatives. 86+ SCA score. $2 per bag funds farmer cooperatives directly. Roasted to order.',
    cta: 'Invest in the Supply Chain',
    color: '#92400e',
    emoji: '☕',
  },
}

type Product = keyof typeof products

function App() {
  const [active, setActive] = useState<Product>('coffee')
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [tab, setTab] = useState<'influencer' | 'wholesale' | 'investor'>('influencer')

  const p = products[active]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (email) setSubmitted(true)
  }

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', color: '#f5f5f5', fontFamily: 'system-ui, sans-serif' }}>
      {/* NAV */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '24px 48px', borderBottom: '1px solid #1a1a1a', position: 'sticky', top: 0, background: '#0a0a0a', zIndex: 100 }}>
        <div style={{ fontSize: '22px', fontWeight: 800, letterSpacing: '-0.5px' }}>
          <span style={{ color: '#dc2626' }}>STUD</span>EX<span style={{ color: '#333' }}>.</span><span style={{ color: '#dc2626' }}>MEAT</span>
        </div>
        <div style={{ display: 'flex', gap: '32px', fontSize: '14px' }}>
          <a href="#products" style={{ color: '#888', textDecoration: 'none' }}>Products</a>
          <a href="#mission" style={{ color: '#888', textDecoration: 'none' }}>Mission</a>
          <a href="#contact" style={{ color: '#888', textDecoration: 'none' }}>Contact</a>
        </div>
      </nav>

      {/* HERO — COFFEE FOCUS */}
      <section style={{ textAlign: 'center', padding: '100px 48px 80px', background: 'radial-gradient(ellipse at top, #1c0f00 0%, #0a0a0a 70%)' }}>
        <div style={{ maxWidth: '760px', margin: '0 auto' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#1c1000', border: '1px solid #3d2a00', borderRadius: '99px', padding: '6px 16px', fontSize: '12px', color: '#d97706', marginBottom: '24px', fontWeight: 600, letterSpacing: '1px' }}>
            <span>🌱</span> NEW — RWANDAN SINGLE-ORIGIN NOW SHIPPING
          </div>
          <h1 style={{ fontSize: 'clamp(40px, 6vw, 72px)', fontWeight: 900, lineHeight: 1.05, marginBottom: '24px', letterSpacing: '-2px' }}>
            Two Products.<br />
            <span style={{ color: '#dc2626' }}>One Supply Chain.</span>
          </h1>
          <p style={{ fontSize: '18px', color: '#888', maxWidth: '560px', margin: '0 auto 40px', lineHeight: 1.6 }}>
            Premium South African biltong and Rwandan specialty coffee — sourced with purpose, roasted to order, shipped worldwide.
          </p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="#products" style={{ background: '#dc2626', color: '#fff', padding: '14px 32px', borderRadius: '4px', textDecoration: 'none', fontWeight: 700, fontSize: '15px' }}>
              Explore Our Products
            </a>
            <a href="#contact" style={{ border: '1px solid #333', color: '#f5f5f5', padding: '14px 32px', borderRadius: '4px', textDecoration: 'none', fontWeight: 700, fontSize: '15px' }}>
              Become a Partner
            </a>
          </div>
        </div>
      </section>

      {/* PRODUCT TOGGLER */}
      <section id="products" style={{ padding: '80px 48px' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ display: 'flex', gap: '4px', background: '#111', borderRadius: '8px', padding: '4px', width: 'fit-content', margin: '0 auto 64px' }}>
            {(['coffee', 'biltong'] as Product[]).map(k => (
              <button
                key={k}
                onClick={() => setActive(k)}
                style={{
                  background: active === k ? (k === 'coffee' ? '#92400e' : '#dc2626') : 'transparent',
                  color: active === k ? '#fff' : '#666',
                  border: 'none',
                  padding: '12px 36px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 700,
                  fontSize: '15px',
                  transition: 'all 0.2s',
                }}
              >
                {products[k].title}
              </button>
            ))}
          </div>

          <div style={{
            background: '#111',
            border: `1px solid ${p.color}22`,
            borderRadius: '16px',
            overflow: 'hidden',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
          }}>
            <div style={{ padding: '64px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <p style={{ color: p.color, fontSize: '11px', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: '12px', fontWeight: 600 }}>StudEx Meat — {p.title}</p>
              <h2 style={{ fontSize: '48px', fontWeight: 900, marginBottom: '8px', letterSpacing: '-1px' }}>{p.title}</h2>
              <p style={{ color: p.color, fontSize: '15px', fontStyle: 'italic', marginBottom: '24px' }}>{p.tagline}</p>
              <p style={{ color: '#888', fontSize: '16px', lineHeight: 1.7, marginBottom: '40px' }}>{p.description}</p>
              <a href="#contact" style={{ background: p.color, color: '#fff', padding: '14px 32px', borderRadius: '4px', textDecoration: 'none', fontWeight: 700, width: 'fit-content' }}>
                {p.cta} →
              </a>
            </div>
            <div style={{
              background: `radial-gradient(ellipse at center, ${p.color}18 0%, transparent 70%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '400px',
            }}>
              <div style={{
                width: '220px',
                height: '220px',
                borderRadius: '50%',
                background: `conic-gradient(from 0deg, ${p.color}00, ${p.color}55, ${p.color}00)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <div style={{
                  width: '180px',
                  height: '180px',
                  borderRadius: '50%',
                  background: '#0a0a0a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '72px',
                }}>
                  {p.emoji}
                </div>
              </div>
            </div>
          </div>

          {/* Stats row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1px', background: '#1a1a1a', borderRadius: '12px', overflow: 'hidden', marginTop: '24px' }}>
            {(active === 'coffee'
              ? [
                  { stat: '86+', label: 'SCA Score' },
                  { stat: '$2/bag', label: 'To Farmer Cooperative' },
                  { stat: '56,000+', label: 'Women Farmers' },
                  { stat: '0', label: 'Middlemen' },
                ]
              : [
                  { stat: '40g', label: 'Protein per 100g' },
                  { stat: '0g', label: 'Sugar' },
                  { stat: '0', label: 'Preservatives' },
                  { stat: '100%', label: 'Grass-Fed Beef' },
                ]
            ).map(s => (
              <div key={s.label} style={{ background: '#111', padding: '32px 24px', textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: 900, color: p.color, marginBottom: '8px' }}>{s.stat}</div>
                <div style={{ fontSize: '12px', color: '#555', textTransform: 'uppercase', letterSpacing: '1px' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* COFFEE FARMERS STORY */}
      {active === 'coffee' && (
        <section style={{ padding: '80px 48px', background: '#0d0d0d', borderTop: '1px solid #1a1a1a', borderBottom: '1px solid #1a1a1a' }}>
          <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
            <p style={{ color: '#d97706', fontSize: '12px', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: '16px', fontWeight: 600 }}>The Ngagi Story</p>
            <h2 style={{ fontSize: 'clamp(26px, 4vw, 44px)', fontWeight: 900, marginBottom: '24px', letterSpacing: '-1px' }}>
              Your morning cup has a name behind it.
            </h2>
            <p style={{ color: '#888', fontSize: '17px', lineHeight: 1.7, marginBottom: '48px' }}>
              Rwanda exported $148.6M in coffee last year. Most of that value never reached the women who grew it. Ngagi Coffee is the direct trade pipeline — from a Rwandan cooperative to your French press, with $2 per bag going directly to the women who grew it. No trading houses. No intermediaries.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
              {[
                { emoji: '🏔️', title: 'Rwanda', sub: 'Kigali Hills, 1,800m altitude' },
                { emoji: '👩‍🌾', title: '56,000 Women', sub: 'In Rwanda\'s coffee cooperatives' },
                { emoji: '☕', title: '86+ Points', sub: 'Specialty grade, SCA scored' },
              ].map(item => (
                <div key={item.title} style={{ background: '#1a1a1a', borderRadius: '12px', padding: '28px', textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', marginBottom: '12px' }}>{item.emoji}</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, marginBottom: '6px' }}>{item.title}</div>
                  <div style={{ fontSize: '13px', color: '#555' }}>{item.sub}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* MISSION */}
      <section id="mission" style={{ padding: '80px 48px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
          <p style={{ color: '#dc2626', fontSize: '12px', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: '16px', fontWeight: 600 }}>Our Mission</p>
          <h2 style={{ fontSize: 'clamp(26px, 4vw, 44px)', fontWeight: 900, marginBottom: '24px', letterSpacing: '-1px' }}>
            Africa's best products. The world's buying power. The farmers' pockets.
          </h2>
          <p style={{ color: '#888', fontSize: '17px', lineHeight: 1.7, marginBottom: '48px' }}>
            We don't run a charity. We run a supply chain. Biltong supports South African cattle farmers. Rwanda coffee funds women cooperatives directly. Every transaction is designed to get more money to the people who grow, cure, and process our products.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
            {[
              { stat: '$2/bag', label: 'Direct to Rwanda women\'s cooperative, every time' },
              { stat: '40g/100g', label: 'Protein in our biltong — no preservatives, no sugar' },
              { stat: '86+', label: 'SCA score on every Rwandan single-origin batch' },
            ].map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '36px', fontWeight: 900, color: '#dc2626', marginBottom: '8px' }}>{s.stat}</div>
                <div style={{ fontSize: '13px', color: '#666', lineHeight: 1.4 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PARTNERSHIP TABS */}
      <section id="contact" style={{ padding: '80px 48px', background: '#0d0d0d', borderTop: '1px solid #1a1a1a' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <p style={{ color: '#dc2626', fontSize: '12px', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: '16px', fontWeight: 600 }}>Partner With Us</p>
            <h2 style={{ fontSize: 'clamp(24px, 4vw, 40px)', fontWeight: 900 }}>Let's Build Together</h2>
          </div>

          <div style={{ display: 'flex', gap: '4px', background: '#111', borderRadius: '8px', padding: '4px', marginBottom: '32px' }}>
            {(['influencer', 'wholesale', 'investor'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                style={{
                  flex: 1,
                  background: tab === t ? '#dc2626' : 'transparent',
                  color: tab === t ? '#fff' : '#555',
                  border: 'none',
                  padding: '10px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 700,
                  fontSize: '13px',
                  textTransform: 'capitalize',
                }}
              >
                {t === 'influencer' ? '🎥 Influencer' : t === 'wholesale' ? '🏪 Wholesale' : '💼 Investor'}
              </button>
            ))}
          </div>

          {tab === 'influencer' && (
            <div style={{ background: '#111', border: '1px solid #1a1a1a', borderRadius: '12px', padding: '40px' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 800, marginBottom: '8px' }}>Creator Program — South Africa</h3>
              <p style={{ color: '#888', marginBottom: '32px', fontSize: '15px' }}>Fitness, food, and lifestyle creators. We pay per post + free product + affiliate commission.</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
                {[
                  { tier: 'Micro', range: '1K–10K followers', pay: 'R500–R1,500/post' },
                  { tier: 'Mid', range: '10K–100K followers', pay: 'R1,500–R5,000/post' },
                  { tier: 'Macro', range: '100K+ followers', pay: 'R5,000+/post' },
                ].map(t => (
                  <div key={t.tier} style={{ background: '#0a0a0a', borderRadius: '8px', padding: '20px' }}>
                    <div style={{ color: '#dc2626', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>{t.tier}</div>
                    <div style={{ fontSize: '11px', color: '#555', marginBottom: '8px' }}>{t.range}</div>
                    <div style={{ fontSize: '16px', fontWeight: 800 }}>{t.pay}</div>
                  </div>
                ))}
              </div>
              <p style={{ color: '#555', fontSize: '13px', marginBottom: '24px' }}>Free product + affiliate link + volume bonuses for real engagement.</p>
              {submitted ? (
                <p style={{ color: '#22c55e', fontWeight: 700 }}>✅ Application received. We'll reach out within 48h.</p>
              ) : (
                <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
                  <input type="email" placeholder="your@email.com" value={email} onChange={e => setEmail(e.target.value)} required style={{ flex: 1, padding: '14px 18px', borderRadius: '6px', border: 'none', background: '#1a1a1a', color: '#fff', fontSize: '15px', outline: 'none' }} />
                  <button type="submit" style={{ background: '#dc2626', color: '#fff', border: 'none', padding: '14px 24px', borderRadius: '6px', fontWeight: 800, cursor: 'pointer' }}>Apply Now</button>
                </form>
              )}
            </div>
          )}

          {tab === 'wholesale' && (
            <div style={{ background: '#111', border: '1px solid #1a1a1a', borderRadius: '12px', padding: '40px' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 800, marginBottom: '8px' }}>Wholesale & Distribution</h3>
              <p style={{ color: '#888', marginBottom: '24px', fontSize: '15px' }}>Hotels, restaurants, butchers, coffee shops, and retailers. We supply Cape Town and can ship nationally.</p>
              <div style={{ background: '#0a0a0a', borderRadius: '8px', padding: '24px', marginBottom: '24px' }}>
                <div style={{ fontSize: '13px', color: '#555', marginBottom: '8px' }}>BILTONG</div>
                <div style={{ fontSize: '15px', marginBottom: '16px' }}>Minimum order: 5kg | Supply: weekly | Packaging: branded or white-label</div>
                <div style={{ fontSize: '13px', color: '#555', marginBottom: '8px' }}>COFFEE</div>
                <div style={{ fontSize: '15px' }}>Minimum order: 10 bags | Supply: fortnightly | Green bean or roasted available</div>
              </div>
              <a href="mailto:info@studexmeat.com" style={{ display: 'inline-block', background: '#dc2626', color: '#fff', padding: '14px 32px', borderRadius: '4px', textDecoration: 'none', fontWeight: 700 }}>Contact for Pricing →</a>
            </div>
          )}

          {tab === 'investor' && (
            <div style={{ background: '#111', border: '1px solid #1a1a1a', borderRadius: '12px', padding: '40px' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 800, marginBottom: '8px' }}>Invest in the Supply Chain</h3>
              <p style={{ color: '#888', marginBottom: '24px', fontSize: '15px' }}>We're raising capital for: Rwanda origin facility, Cape Town AI café, and export infrastructure.</p>
              <div style={{ display: 'grid', gap: '16px', marginBottom: '32px' }}>
                {[
                  { title: 'Phase 1', amount: 'R2.4M', use: 'Rwanda green bean sourcing + export license' },
                  { title: 'Phase 2', amount: 'R1.8M', use: 'Cape Town AI robotic café build-out' },
                  { title: 'Phase 3', amount: 'R3.0M', use: 'Cold-chain export to Middle East + EU' },
                ].map(p => (
                  <div key={p.title} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#0a0a0a', padding: '20px', borderRadius: '8px' }}>
                    <div>
                      <div style={{ fontSize: '13px', color: '#dc2626', fontWeight: 700 }}>{p.title}</div>
                      <div style={{ fontSize: '13px', color: '#555' }}>{p.use}</div>
                    </div>
                    <div style={{ fontSize: '22px', fontWeight: 900 }}>{p.amount}</div>
                  </div>
                ))}
              </div>
              <a href="mailto:robusca.romanov@studex-group.com" style={{ display: 'inline-block', background: '#dc2626', color: '#fff', padding: '14px 32px', borderRadius: '4px', textDecoration: 'none', fontWeight: 700 }}>Request Investor Deck →</a>
            </div>
          )}
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ padding: '32px 48px', borderTop: '1px solid #111', textAlign: 'center', color: '#333', fontSize: '13px' }}>
        <span style={{ color: '#dc2626', fontWeight: 800 }}>STUD</span>EX<span style={{ color: '#333' }}>.</span><span style={{ color: '#dc2626' }}>MEAT</span>
        <span style={{ margin: '0 12px', color: '#1a1a1a' }}>|</span>
        Cape Town, South Africa & Kigali, Rwanda
        <span style={{ margin: '0 12px', color: '#1a1a1a' }}>|</span>
        © 2026 — All rights reserved
      </footer>
    </div>
  )
}

export default App
