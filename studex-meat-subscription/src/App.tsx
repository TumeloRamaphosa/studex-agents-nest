import { useState } from 'react'
import './App.css'

const MONTHLY_BOX = [
  {
    icon: '🥩',
    name: '500g Premium Beef Biltong',
    desc: 'Air-cured, grass-fed beef. Heritage recipe.',
    farm: 'Karoo Prime — Strydfontein Farm, Ceres',
  },
  {
    icon: '🥓',
    name: '500g Beef Strips',
    desc: 'Slow-marinated, ready-to-cook premium cuts.',
    farm: 'Highveld Angus — Henneman, Free State',
  },
  {
    icon: '🌭',
    name: '200g Droëwors',
    desc: 'Traditional coriander-spiced beef sausage.',
    farm: 'Karoo Prime — Strydfontein Farm, Ceres',
  },
  {
    icon: '🎁',
    name: 'Seasonal Surprise Cut',
    desc: 'Chef-selected premium cut each month.',
    farm: 'Rotating provenance — ask your agent',
  },
]

const TESTIMONIALS = [
  {
    quote: "Finally a halal meat subscription that actually delivers on provenance. My family won't eat anything else.",
    author: 'Fatima L., Johannesburg',
    role: 'Monthly Subscriber',
  },
  {
    quote: "The biltong quality rivals what I grew up with in Cape Town. Exceptional.",
    author: 'Ibrahim K.',
    role: 'Corporate Gift Buyer — Sunninghill',
  },
]

const FAQS = [
  {
    q: 'Is it halal certified?',
    a: 'Yes. Every product in the Monthly Meat Box carries a valid Halaal certification from an accredited SA certification body. Certificate available on request.',
  },
  {
    q: 'Where do you deliver?',
    a: 'We deliver nationwide across South Africa. Metro areas: next-day delivery. Rural/courier areas: 2–3 days. Free delivery on orders over R599.',
  },
  {
    q: 'Can I pause or cancel?',
    a: 'Pause anytime — up to 48h before your next billing date. Cancel anytime with no cancellation fees. No lock-in contracts.',
  },
  {
    q: 'What if I\'m not happy?',
    a: '100% satisfaction guarantee. If any item doesn\'t meet your expectations, we replace it or credit your next box — no questions asked.',
  },
  {
    q: 'How is the box packaged?',
    a: 'Vacuum-sealed, insulated box with ice packs. Cold-chain maintained from our Johannesmurug to your door. Tracking link sent on dispatch.',
  },
]

function App() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [form, setForm] = useState({ name: '', email: '', whatsapp: '', city: '', interest: 'monthly' })
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  return (
    <div className="app">
      {/* NAV */}
      <nav className="nav">
        <div className="nav-inner">
          <div className="logo">
            <span className="logo-icon">🥩</span>
            <span className="logo-text">Studex <span className="logo-sub">Meat</span></span>
          </div>
          <div className="nav-links">
            <a href="#whats-inside">What's Inside</a>
            <a href="#provenance">Provenance</a>
            <a href="#pricing">Pricing</a>
            <a href="#faq">FAQ</a>
            <a href="#subscribe" className="nav-cta">Subscribe</a>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-badge">🇿🇦 South Africa's First Halal Premium Meat Subscription</div>
          <h1 className="hero-title">
            Premium Meat,<br />
            <span className="hero-accent">Delivered Monthly.</span>
          </h1>
          <p className="hero-desc">
            Curated biltong, beef cuts & droëwors — halaal certified, farm-traceable,
            delivered to your door every month. No compromise on faith, quality, or provenance.
          </p>
          <div className="hero-actions">
            <a href="#subscribe" className="btn btn-primary">Start Your Subscription</a>
            <a href="#whats-inside" className="btn btn-ghost">See What's Inside</a>
          </div>
          <div className="hero-proof">
            <span>✓ Halaal Certified</span>
            <span>✓ Farm Traceable</span>
            <span>✓ Nationwide Delivery</span>
            <span>✓ Cancel Anytime</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-box-mock">
            <div className="mock-label">MONTHLY MEAT BOX</div>
            <div className="mock-items">
              {MONTHLY_BOX.map((item, i) => (
                <div key={i} className="mock-item">
                  <span className="mock-icon">{item.icon}</span>
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
            <div className="mock-footer">
              <span>📦 Fresh · Vacuüm-sealed · Ice-packed</span>
            </div>
          </div>
        </div>
      </section>

      {/* STATS BAR */}
      <section className="stats-bar">
        <div className="stats-inner">
          <div className="stat">
            <div className="stat-num">R499</div>
            <div className="stat-label">per month</div>
          </div>
          <div className="stat-div" />
          <div className="stat">
            <div className="stat-num">1.2kg+</div>
            <div className="stat-label">premium meat per box</div>
          </div>
          <div className="stat-div" />
          <div className="stat">
            <div className="stat-num">100%</div>
            <div className="stat-label">halaal certified</div>
          </div>
          <div className="stat-div" />
          <div className="stat">
            <div className="stat-num">Next-day</div>
            <div className="stat-label">metro delivery</div>
          </div>
        </div>
      </section>

      {/* WHAT'S INSIDE */}
      <section className="section" id="whats-inside">
        <div className="section-inner">
          <div className="section-label">What's Inside</div>
          <h2 className="section-title">Every Month, A New Box of Excellence</h2>
          <p className="section-desc">
            Each box is assembled the day before delivery. Every item carries full farm provenance.
            You know exactly where your meat comes from — because you deserve to know.
          </p>
          <div className="product-grid">
            {MONTHLY_BOX.map((item, i) => (
              <div key={i} className="product-card">
                <div className="product-icon">{item.icon}</div>
                <h3 className="product-name">{item.name}</h3>
                <p className="product-desc">{item.desc}</p>
                <div className="product-farm">
                  <span className="farm-label">📍 Farm</span>
                  <span className="farm-name">{item.farm}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROVENANCE */}
      <section className="section provenance-section" id="provenance">
        <div className="section-inner provenance-inner">
          <div className="prov-content">
            <div className="section-label">Farm Provenance</div>
            <h2 className="section-title">We Name Every Farm.<br />Because Transparency Sells.</h2>
            <p className="section-desc">
              Unlike Woolworths or Food Lover's Market, we don't hide provenance behind
              "sourced from RSA." Every item in your box carries the farm name, location,
              and date of processing.
            </p>
            <ul className="prov-list">
              <li>✓ Full abattoir & Halaal certificate per batch</li>
              <li>✓ Cold-chain temperature log from slaughter to door</li>
              <li>✓ Monthly farm rotation to ensure seasonal peak quality</li>
              <li>✓ WhatsApp your agent — ask for your specific batch</li>
            </ul>
            <a href="#subscribe" className="btn btn-primary">Reserve Your Box</a>
          </div>
          <div className="prov-visual">
            <div className="trace-card">
              <div className="trace-header">SAMPLE TRACE — JUNE BOX</div>
              <div className="trace-row"><span>Product</span><span>500g Beef Biltong</span></div>
              <div className="trace-row"><span>Farm</span><span>Strydfontein Farm, Ceres</span></div>
              <div className="trace-row"><span>Cut</span><span>Silverside, grass-fed</span></div>
              <div className="trace-row"><span>Slaughtered</span><span>2026-06-24</span></div>
              <div className="trace-row"><span>Certified</span><span>Halaal #HF-28471</span></div>
              <div className="trace-row"><span>Dispatched</span><span>2026-06-28</span></div>
              <div className="trace-row"><span>Tracking</span><span>RAMSA-008241</span></div>
            </div>
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section className="section" id="pricing">
        <div className="section-inner">
          <div className="section-label">Pricing</div>
          <h2 className="section-title">Simple, Honest Pricing</h2>
          <p className="section-desc">
            No joining fee. No delivery surcharge (metro). Cancel whenever you want.
          </p>
          <div className="pricing-grid">
            <div className="pricing-card">
              <div className="pricing-tier">Starter</div>
              <div className="pricing-price">R349<span>/mo</span></div>
              <div className="pricing-note"> проб</div>
              <ul className="pricing-features">
                <li>✓ 750g biltong + beef strips</li>
                <li>✓ Halaal certified</li>
                <li>✓ Farm provenance card</li>
                <li>✓ Courier delivery (2–3 days)</li>
                <li>✓ Cancel anytime</li>
              </ul>
              <a href="#subscribe" className="btn btn-outline">Get Started</a>
            </div>
            <div className="pricing-card pricing-featured">
              <div className="pricing-badge">MOST POPULAR</div>
              <div className="pricing-tier">Classic Box</div>
              <div className="pricing-price">R499<span>/mo</span></div>
              <div className="pricing-note">1.2kg+ premium meat</div>
              <ul className="pricing-features">
                <li>✓ 500g biltong + 500g strips + 200g droëwors</li>
                <li>✓ Seasonal surprise cut</li>
                <li>✓ Full farm traceability</li>
                <li>✓ Free metro delivery</li>
                <li>✓ Pause or cancel anytime</li>
              </ul>
              <a href="#subscribe" className="btn btn-primary">Subscribe Now</a>
            </div>
            <div className="pricing-card">
              <div className="pricing-tier">Corporate</div>
              <div className="pricing-price">R799<span>/mo</span></div>
              <div className="pricing-note">For teams & client gifting</div>
              <ul className="pricing-features">
                <li>✓ 2kg mixed premium cuts</li>
                <li>✓ Custom branded box + message</li>
                <li>✓ Dedicated account agent</li>
                <li>✓ Invoice billing (net-30)</li>
                <li>✓ Monthly or quarterly</li>
              </ul>
              <a href="#subscribe" className="btn btn-outline">Contact Us</a>
            </div>
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="section testimonials-section">
        <div className="section-inner">
          <div className="section-label">Subscribers Say</div>
          <h2 className="section-title">Trusted by Families Across SA</h2>
          <div className="testimonial-grid">
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="testimonial-card">
                <div className="testimonial-stars">★★★★★</div>
                <p className="testimonial-quote">"{t.quote}"</p>
                <div className="testimonial-author">
                  <div className="testimonial-avatar">{t.author[0]}</div>
                  <div>
                    <div className="testimonial-name">{t.author}</div>
                    <div className="testimonial-role">{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="section faq-section" id="faq">
        <div className="section-inner">
          <div className="section-label">FAQ</div>
          <h2 className="section-title">Questions? We've Got Answers.</h2>
          <div className="faq-list">
            {FAQS.map((faq, i) => (
              <div key={i} className={`faq-item ${openFaq === i ? 'open' : ''}`}>
                <button className="faq-q" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
                  {faq.q}
                  <span className="faq-icon">{openFaq === i ? '−' : '+'}</span>
                </button>
                {openFaq === i && <div className="faq-a">{faq.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SUBSCRIBE / CTA */}
      <section className="section subscribe-section" id="subscribe">
        <div className="section-inner">
          <div className="subscribe-inner">
            <div className="subscribe-copy">
              <div className="section-label">Get Started</div>
              <h2 className="section-title">Reserve Your Monthly Meat Box</h2>
              <p className="section-desc">
                Fill in your details below. We'll send you a confirmation WhatsApp within 2 hours
                with next steps and your first box delivery date.
              </p>
              <div className="subscribe-trust">
                <span>🔒 No payment today</span>
                <span>✓ Halaal guaranteed</span>
                <span>📦 First box ships within 7 days</span>
              </div>
            </div>
            <div className="subscribe-form-wrap">
              {submitted ? (
                <div className="form-success">
                  <div className="success-icon">✓</div>
                  <h3>You're on the list!</h3>
                  <p>We'll WhatsApp you within 2 hours to confirm your subscription details.</p>
                  <p className="success-note">Questions? Message us on<br /><a href="https://wa.me/27712345678" target="_blank" rel="noopener">WhatsApp +27 71 234 5678</a></p>
                </div>
              ) : (
                <form className="subscribe-form" onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label>Your Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Fatima L."
                      value={form.name}
                      onChange={e => setForm({ ...form, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Email Address</label>
                    <input
                      type="email"
                      placeholder="you@example.com"
                      value={form.email}
                      onChange={e => setForm({ ...form, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>WhatsApp Number</label>
                    <input
                      type="tel"
                      placeholder="+27 71 234 5678"
                      value={form.whatsapp}
                      onChange={e => setForm({ ...form, whatsapp: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>City / Area</label>
                    <input
                      type="text"
                      placeholder="e.g. Sandton, JHB"
                      value={form.city}
                      onChange={e => setForm({ ...form, city: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Interested In</label>
                    <select
                      value={form.interest}
                      onChange={e => setForm({ ...form, interest: e.target.value })}
                    >
                      <option value="monthly">Monthly Subscription — R499/mo</option>
                      <option value="corporate">Corporate / Gift Boxes — R799/mo</option>
                      <option value="starter">Starter Box — R349/mo</option>
                    </select>
                  </div>
                  <button type="submit" className="btn btn-primary btn-full">Reserve My Box</button>
                  <p className="form-disclaimer">
                    No payment required now. We'll contact you to confirm before charging.
                  </p>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <div className="logo">
              <span className="logo-icon">🥩</span>
              <span className="logo-text">Studex <span className="logo-sub">Meat</span></span>
            </div>
            <p>Premium halaal meat, farm-to-door.</p>
            <p>Johannesburg · Cape Town · Nationwide</p>
          </div>
          <div className="footer-links">
            <div className="footer-col">
              <h4>Shop</h4>
              <a href="#whats-inside">What's Inside</a>
              <a href="#pricing">Pricing</a>
              <a href="#faq">FAQ</a>
            </div>
            <div className="footer-col">
              <h4>Contact</h4>
              <a href="mailto:ceo@agent.studexmeat.com">ceo@agent.studexmeat.com</a>
              <a href="https://wa.me/27712345678" target="_blank" rel="noopener">WhatsApp</a>
              <a href="https://studexmeat.com" target="_blank" rel="noopener">studexmeat.com</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 Studex Wildlife (Pty) Ltd. All rights reserved. Halaal certified.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
