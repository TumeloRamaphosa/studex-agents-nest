import { useState } from 'react'

const b2bProducts = [
  {
    grade: 'A1 Washed',
    process: 'Fully Washed',
    notes: 'Jasmine, stone fruit, clean finish',
    roast: 'Medium-dark roast ideal',
    certifications: ['Rainforest Alliance', 'PROWTC'],
    fobPrice: 'USD 4.80/kg',
    minOrder: '60kg bags',
    color: 'from-amber-900 to-amber-700',
    available: '12 MT in stock',
  },
  {
    grade: 'A2 Natural',
    process: 'Natural',
    notes: 'Blueberry, dark chocolate, full body',
    roast: 'Dark roast preferred',
    certifications: ['Rainforest Alliance', 'PROWTC'],
    fobPrice: 'USD 5.20/kg',
    minOrder: '60kg bags',
    color: 'from-stone-800 to-stone-600',
    available: '6 MT in stock',
  },
]

const painPoints = [
  {
    emoji: '⚡',
    title: 'Load Shedding Risk',
    description: 'SA roasters on generators pass cost premiums to buyers. Rwandan green bean imported and roasted locally in SA eliminates this cost layer — your roasted product lands cheaper.',
  },
  {
    emoji: '📍',
    title: 'Provenance Expectation',
    description: 'Hotel guests increasingly ask "where is this coffee from?" Farm-level traceability on every bag is a guest experience differentiator and a marketing story procurement can own.',
  },
  {
    emoji: '💰',
    title: 'Price Volatility',
    description: 'Arabica futures at $2.50–3.00/lb through 2026. We offer fixed quarterly pricing on contract — no monthly spot exposure for buyers who commit to a supply agreement.',
  },
  {
    emoji: '🚛',
    title: 'Reliability of Supply',
    description: 'Load shedding disrupts SA roasting capacity. We maintain green bean buffer stock in Durban. Monday morning deliveries are guaranteed on contract.',
  },
]

const testimonials = [
  {
    quote: 'The provenance story on the bag — farmer name, farm GPS, harvest date — is something our guests actually ask about. It has become part of the breakfast experience.',
    author: 'GM, Boutique Hotel — Cape Town',
  },
  {
    quote: 'Load shedding used to cost us R12,000/month in generator surcharges on our roasting equipment. Moving to pre-roasted Rwandan green bean solved that overnight.',
    author: 'Owner, Specialty Roastery — Johannesburg',
  },
]

function SaB2BOnePager() {
  const [form, setForm] = useState({
    name: '', company: '', email: '', phone: '',
    volume: '', grade: '', deliveryPort: '', message: ''
  })
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 font-sans">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-stone-800 bg-stone-950/95 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold text-sm">S</div>
          <span className="text-lg font-semibold tracking-wide">Studex Meat — B2B Coffee</span>
        </div>
        <div className="flex gap-6 text-sm text-stone-400">
          <a href="#products" className="hover:text-emerald-400 transition">Products</a>
          <a href="#why" className="hover:text-emerald-400 transition">Why Studex</a>
          <a href="#pricing" className="hover:text-emerald-400 transition">Pricing</a>
          <a href="#contact" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition text-sm">Get a Quote</a>
        </div>
      </nav>

      {/* Hero — B2B Context */}
      <section className="relative overflow-hidden px-8 py-24 text-center">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-950 via-stone-950 to-stone-950" />
        <div className="relative max-w-3xl mx-auto">
          <div className="inline-block px-3 py-1 rounded-full border border-emerald-600 text-emerald-400 text-xs font-medium tracking-widest uppercase mb-6">
            B2B Wholesale · South Africa & UAE
          </div>
          <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
            Rwanda Green Coffee.<br />
            <span className="text-emerald-500">Roasted in SA.</span><br />
            Delivered to Your Door.
          </h1>
          <p className="text-xl text-stone-400 max-w-2xl mx-auto mb-8 leading-relaxed">
            Premium A1/A2 Rwandan green coffee for SA roasters, hotel groups, and wholesale distributors.
            Farm-traceable. Rainforest Alliance certified. Supply resilience guaranteed.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#contact" className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition text-center">
              Request a Quote
            </a>
            <a href="#products" className="px-8 py-4 border border-stone-600 hover:border-emerald-600 text-stone-300 hover:text-emerald-400 font-semibold rounded-lg transition text-center">
              View Products
            </a>
          </div>
        </div>
      </section>

      {/* Value Prop Bar */}
      <section className="bg-emerald-950/40 border-y border-emerald-900/50">
        <div className="max-w-6xl mx-auto px-8 py-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            ['⚡', 'Load Shedding Resilient', 'SA-roasted green bean supply'],
            ['📍', 'Farm Traceability', 'GPS + farmer name on every bag'],
            ['📄', 'Fixed Price Contracts', 'Quarterly pricing, no spot exposure'],
            ['🚛', 'Durban Buffer Stock', 'Monday deliveries guaranteed'],
          ].map(([icon, val, sub]) => (
            <div key={val} className="flex flex-col items-center gap-1">
              <div className="text-2xl">{icon}</div>
              <div className="text-sm font-semibold text-stone-200">{val}</div>
              <div className="text-xs text-stone-500">{sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* The Pain Points We Solve */}
      <section id="why" className="px-8 py-24 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-3">Why SA Roasters Choose Studex</h2>
          <p className="text-stone-400">Four problems in the SA coffee supply chain — and how we solve each one.</p>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {painPoints.map((p) => (
            <div key={p.title} className="bg-stone-900 border border-stone-800 rounded-2xl p-8">
              <div className="text-3xl mb-4">{p.emoji}</div>
              <h3 className="text-lg font-bold text-stone-100 mb-2">{p.title}</h3>
              <p className="text-stone-400 leading-relaxed text-sm">{p.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="bg-stone-900 px-8 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center text-xs text-emerald-400 font-bold tracking-widest uppercase mb-8">What SA Buyers Say</div>
          <div className="grid md:grid-cols-2 gap-6">
            {testimonials.map((t) => (
              <div key={t.author} className="bg-stone-800 border border-stone-700 rounded-2xl p-8">
                <div className="text-amber-400 text-2xl mb-4">"</div>
                <p className="text-stone-300 italic mb-4 leading-relaxed">{t.quote}</p>
                <div className="text-xs text-stone-500 font-medium">{t.author}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Products */}
      <section id="products" className="px-8 py-24 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-3">Current B2B Offerings</h2>
          <p className="text-stone-400">Available now. Dispatch from Durban within 5 working days of order confirmation.</p>
        </div>
        <div className="grid md:grid-cols-2 gap-8">
          {b2bProducts.map((p) => (
            <div key={p.grade} className={`rounded-2xl bg-gradient-to-br ${p.color} p-8 flex flex-col`}>
              <div className="text-xs text-white/60 uppercase tracking-widest mb-2">{p.process} · {p.available}</div>
              <h3 className="text-2xl font-bold text-white mb-2">{p.grade}</h3>
              <div className="text-sm text-white/70 mb-4">{p.notes}</div>
              <div className="flex flex-wrap gap-2 mb-4">
                {p.certifications.map(c => (
                  <span key={c} className="px-3 py-1 bg-white/15 rounded-full text-xs text-white/90">{c}</span>
                ))}
              </div>
              <div className="mt-auto border-t border-white/20 pt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-white/60 text-sm">FOB Price</span>
                  <span className="font-bold text-white">{p.fobPrice}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60 text-sm">Minimum Order</span>
                  <span className="text-white/80 text-sm">{p.minOrder}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60 text-sm">Best For</span>
                  <span className="text-white/80 text-sm">{p.roast}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-8 p-6 bg-stone-900 rounded-xl border border-stone-800">
          <h4 className="font-semibold text-stone-200 mb-2">Supply Chain Note for SA Buyers</h4>
          <p className="text-sm text-stone-400 leading-relaxed">
            All prices FOB Kigali. Sea freight Kigali → Durban: ~USD 0.60/kg. Clearance, import duty (±5%), and last-mile delivery to your roastery in SA additional. For UAE buyers: freight Kigali → Jebel Ali ~USD 0.80/kg. We handle all logistics — you receive the coffee, you pay the landed cost.
          </p>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="px-8 py-16 bg-stone-900">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-3">B2B Pricing — FOB Kigali</h2>
            <p className="text-stone-400">Indicative. Landed cost (SA) = FOB + freight ± USD 0.70/kg. Prices in USD per kg.</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-stone-700">
                  <th className="py-4 px-6 text-stone-400 font-medium text-sm">Grade</th>
                  <th className="py-4 px-6 text-stone-400 font-medium text-sm">Process</th>
                  <th className="py-4 px-6 text-stone-400 font-medium text-sm">FOB / kg</th>
                  <th className="py-4 px-6 text-stone-400 font-medium text-sm">Certifications</th>
                  <th className="py-4 px-6 text-stone-400 font-medium text-sm">Stock</th>
                </tr>
              </thead>
              <tbody>
                {b2bProducts.map((row, i) => (
                  <tr key={row.grade} className={`border-b border-stone-800 ${i % 2 === 0 ? 'bg-stone-800/40' : ''}`}>
                    <td className="py-4 px-6 font-semibold text-emerald-400">{row.grade}</td>
                    <td className="py-4 px-6 text-stone-300">{row.process}</td>
                    <td className="py-4 px-6 text-white font-medium">{row.fobPrice}</td>
                    <td className="py-4 px-6">
                      <div className="flex flex-wrap gap-1">
                        {row.certifications.map(c => (
                          <span key={c} className="px-2 py-0.5 bg-stone-700 rounded text-xs text-stone-300">{c}</span>
                        ))}
                      </div>
                    </td>
                    <td className="py-4 px-6 text-stone-400 text-sm">{row.available}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-6 p-4 bg-emerald-950/30 border border-emerald-800/30 rounded-xl text-center">
            <p className="text-sm text-emerald-300">
              💼 <strong>Contract pricing available:</strong> Commit to 6-month supply agreement → locked quarterly price, priority stock allocation, dedicated account manager.
            </p>
          </div>
        </div>
      </section>

      {/* CIIE Callout */}
      <section className="px-8 py-12 max-w-4xl mx-auto">
        <div className="bg-gradient-to-r from-amber-900/50 to-stone-900/50 border border-amber-700/40 rounded-2xl p-10 text-center">
          <div className="text-xs text-amber-400 font-bold tracking-widest uppercase mb-3">China Market · Coming Soon</div>
          <h3 className="text-2xl font-bold mb-3">CIIE Shanghai — November 2026</h3>
          <p className="text-stone-400 mb-4 max-w-xl mx-auto">
            July 20, 2026: South African green coffee gains access to China under the SA-China bilateral protocol. We're applying for the CIIE booth now. Roasters and importers in China: connect with us in Shanghai.
          </p>
          <a href="#contact" className="inline-block px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg transition">
            Register Interest — China Inquiries
          </a>
        </div>
      </section>

      {/* Contact Form */}
      <section id="contact" className="px-8 py-24 bg-stone-900">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Get a B2B Quote</h2>
            <p className="text-stone-400">We reply within 24 hours. Charlie, our B2B coordinator, handles all wholesale inquiries.</p>
          </div>
          {submitted ? (
            <div className="text-center py-16 bg-stone-800 rounded-2xl border border-emerald-700/30">
              <div className="text-4xl mb-4">✅</div>
              <h3 className="text-xl font-bold mb-2">Inquiry Received</h3>
              <p className="text-stone-400">Charlie will respond within 24 hours with a tailored quote based on your volume and delivery requirements.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Full Name *</label>
                  <input required type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-emerald-600 transition" placeholder="Your name" />
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Company *</label>
                  <input required type="text" value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-emerald-600 transition" placeholder="Hotel / Roastery / Distributor" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Email *</label>
                  <input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-emerald-600 transition" placeholder="buyer@company.com" />
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Phone / WhatsApp</label>
                  <input type="tel" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-emerald-600 transition" placeholder="+27 XX XXX XXXX" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Volume / Month</label>
                  <select value={form.volume} onChange={e => setForm({ ...form, volume: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-600 transition">
                    <option value="">Select volume</option>
                    <option value="60-300kg">60 – 300 kg</option>
                    <option value="300kg-1mt">300 kg – 1 MT</option>
                    <option value="1-5mt">1 – 5 MT</option>
                    <option value="5mt+">5+ MT (contract)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Grade</label>
                  <select value={form.grade} onChange={e => setForm({ ...form, grade: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-600 transition">
                    <option value="">Select grade</option>
                    <option>A1 Washed</option>
                    <option>A2 Natural</option>
                    <option>A1 + A2 Mix</option>
                    <option>Sample Pack (all grades)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Delivery Location</label>
                <select value={form.deliveryPort} onChange={e => setForm({ ...form, deliveryPort: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-600 transition">
                  <option value="">Select delivery location</option>
                  <option value="johannesburg">Johannesburg / Gauteng</option>
                  <option value="cape-town">Cape Town</option>
                  <option value="durban">Durban</option>
                  <option value="jebel-ali">Jebel Ali, UAE</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Message</label>
                <textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} rows={4} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-emerald-600 transition resize-none" placeholder="Tell us about your roastery, current supplier, delivery timeline..." />
              </div>
              <button type="submit" className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg transition text-lg">
                Send B2B Inquiry — Reply Within 24h
              </button>
            </form>
          )}
          <div className="mt-10 flex flex-col md:flex-row items-center justify-center gap-8 text-sm text-stone-500">
            <div className="flex items-center gap-2">
              <span className="text-lg">📧</span>
              <span>charlie@agent.studexmeat.com</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg">💬</span>
              <span>+27 82 555 0194</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg">🏢</span>
              <span>Studex Meat — B2B Coffee Division</span>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-stone-800 px-8 py-8 text-center text-stone-600 text-sm">
        © 2026 Studex Meat — B2B Coffee Division · Robusca Group (Pty) Ltd · charlie@agent.studexmeat.com
      </footer>
    </div>
  )
}

export default SaB2BOnePager
