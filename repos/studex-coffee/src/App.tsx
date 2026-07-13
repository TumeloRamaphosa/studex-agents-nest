import { useState } from 'react'

const products = [
  {
    grade: 'A1 Washed',
    screen: 'Screen 15+',
    score: 'Cup Score 85+',
    process: 'Washed',
    notes: 'Floral, citrus, black tea',
    certifications: ['Rainforest Alliance'],
    fobPrice: '$3,800–$4,200/MT',
    minOrder: '1 MT',
    color: 'from-amber-900 to-amber-700',
    badge: 'Most Popular',
  },
  {
    grade: 'A2 Washed',
    screen: 'Screen 14+',
    score: 'Cup Score 83+',
    process: 'Double Washed',
    notes: 'Caramel, stone fruit, full body',
    certifications: ['Rainforest Alliance'],
    fobPrice: '$3,200–$3,600/MT',
    minOrder: '1 MT',
    color: 'from-stone-800 to-stone-600',
    badge: null,
  },
  {
    grade: 'A1 Natural',
    screen: 'Screen 15+',
    score: 'Cup Score 86+',
    process: 'Natural',
    notes: 'Blueberry, dark chocolate, winey',
    certifications: ['UTZ'],
    fobPrice: '$4,000–$4,500/MT',
    minOrder: '500 kg',
    color: 'from-yellow-900 to-yellow-700',
    badge: 'Limited',
  },
  {
    grade: 'A2 Natural',
    screen: 'Screen 14+',
    score: 'Cup Score 82+',
    process: 'Natural',
    notes: 'Stone fruit, cocoa, smooth',
    certifications: ['Fair Trade'],
    fobPrice: '$3,400–$3,800/MT',
    minOrder: '500 kg',
    color: 'from-orange-900 to-orange-700',
    badge: null,
  },
]

const pricingRows = [
  { grade: 'A1 Washed', minOrder: '1 MT', fobPrice: '$3,800–$4,200', cert: 'Rainforest Alliance' },
  { grade: 'A2 Washed', minOrder: '1 MT', fobPrice: '$3,200–$3,600', cert: 'Rainforest Alliance' },
  { grade: 'A1 Natural', minOrder: '500 kg', fobPrice: '$4,000–$4,500', cert: 'UTZ' },
  { grade: 'A2 Natural', minOrder: '500 kg', fobPrice: '$3,400–$3,800', cert: 'Fair Trade' },
]

function App() {
  const [form, setForm] = useState({ name: '', company: '', email: '', phone: '', volume: '', grade: '', message: '' })
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 font-sans">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-stone-800 bg-stone-950/90 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-amber-600 flex items-center justify-center text-white font-bold text-sm">S</div>
          <span className="text-lg font-semibold tracking-wide">Studex Wildlife Coffee</span>
        </div>
        <div className="flex gap-6 text-sm text-stone-400">
          <a href="#products" className="hover:text-amber-400 transition">Products</a>
          <a href="#pricing" className="hover:text-amber-400 transition">Pricing</a>
          <a href="#traceability" className="hover:text-amber-400 transition">Traceability</a>
          <a href="#contact" className="hover:text-amber-400 transition">Contact</a>
          <a href="/b2b" className="px-3 py-1 bg-emerald-700 hover:bg-emerald-600 text-emerald-300 rounded-md transition text-xs font-medium">B2B SA</a>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden px-8 py-28 text-center">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-950 via-stone-950 to-stone-950" />
        <div className="absolute inset-0 opacity-10"
          style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23d97706\' fill-opacity=\'0.4\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }}
        />
        <div className="relative max-w-4xl mx-auto">
          <div className="inline-block px-3 py-1 rounded-full border border-amber-600 text-amber-400 text-xs font-medium tracking-widest uppercase mb-6">
            Direct Trade · Rwanda to the World
          </div>
          <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
            African Coffee,<br />
            <span className="text-amber-500">Wildlife Verified</span>
          </h1>
          <p className="text-xl text-stone-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Premium Rwandan A1/A2 green coffee sourced from Rainforest Alliance certified farms.
            Traceable to the plot. Delivered to your roastery.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#contact" className="px-8 py-4 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg transition text-center">
              Request a Sample
            </a>
            <a href="#pricing" className="px-8 py-4 border border-stone-600 hover:border-amber-600 text-stone-300 hover:text-amber-400 font-semibold rounded-lg transition text-center">
              View B2B Pricing
            </a>
          </div>
          <div className="flex items-center justify-center gap-8 mt-12 text-sm text-stone-500">
            <span className="flex items-center gap-2">☕ 180M+ cups/year UAE market</span>
            <span className="flex items-center gap-2">🌍 GPS-traced farms</span>
            <span className="flex items-center gap-2">📦 FOB Kigali delivery</span>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-stone-900 border-y border-stone-800">
        <div className="max-w-6xl mx-auto px-8 py-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            ['$3,200–$4,500', 'FOB Price Range / MT'],
            ['4–6 Weeks', 'Port of Discharge'],
            ['250g', 'Sample Available $25'],
            ['UTZ · RA · FT', 'Certifications'],
          ].map(([val, label]) => (
            <div key={label}>
              <div className="text-2xl font-bold text-amber-400">{val}</div>
              <div className="text-stone-500 text-sm mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Products */}
      <section id="products" className="px-8 py-24 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Our Green Coffee Offerings</h2>
          <p className="text-stone-400 max-w-xl mx-auto">Every batch traceable to farms in Nyamasheke & Rusizi districts, Western Rwanda. GPS-verified. Quality assured.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((p) => (
            <div key={p.grade} className={`relative rounded-2xl bg-gradient-to-br ${p.color} p-6 flex flex-col`}>
              {p.badge && (
                <div className="absolute -top-3 left-4 px-3 py-1 bg-amber-500 text-stone-950 text-xs font-bold rounded-full">
                  {p.badge}
                </div>
              )}
              <div className="text-xs text-white/60 uppercase tracking-widest mb-2">{p.process}</div>
              <h3 className="text-xl font-bold text-white mb-1">{p.grade}</h3>
              <div className="text-sm text-white/70 mb-4">{p.screen} · {p.score}</div>
              <div className="flex-1">
                <div className="text-xs text-white/50 mb-2">Cup Profile</div>
                <div className="text-sm text-white/90 italic mb-4">{p.notes}</div>
                <div className="flex flex-wrap gap-1 mb-4">
                  {p.certifications.map(c => (
                    <span key={c} className="px-2 py-0.5 bg-white/15 rounded text-xs text-white/80">{c}</span>
                  ))}
                </div>
              </div>
              <div className="border-t border-white/20 pt-4">
                <div className="text-xs text-white/50">FOB Price</div>
                <div className="text-lg font-bold text-white">{p.fobPrice}</div>
                <div className="text-xs text-white/60 mt-1">Min. {p.minOrder}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-8 p-4 bg-stone-900 rounded-xl border border-stone-800 text-center text-stone-500 text-sm">
          🌍 Prices are EXW Kigali. Sea freight to Jebel Ali ~$800/MT · To Durban ~$600/MT · Samples: 250g for $25 (credited to first order)
        </div>
      </section>

      {/* UAE + SA Market */}
      <section id="traceability" className="bg-stone-900 py-24 px-8">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16">
          <div>
            <div className="text-amber-400 text-xs font-bold tracking-widest uppercase mb-3">UAE Market</div>
            <h3 className="text-3xl font-bold mb-4">Why Dubai Buys Rwandan</h3>
            <p className="text-stone-400 leading-relaxed mb-4">
              Dubai's hospitality sector consumes 180M+ cups annually. Hotel groups (Marriott, Hilton, Jumeirah) now mandate traceable, ethically-sourced coffee in procurement policies. Rwanda's Rainforest Alliance certification is a direct entry ticket.
            </p>
            <div className="p-4 bg-amber-950/40 border border-amber-800/30 rounded-xl">
              <div className="text-xs text-amber-400 font-semibold mb-2">Margin Opportunity</div>
              <p className="text-sm text-stone-300">UAE buyers pay <strong>$4,800–$7,200/MT</strong> for Rwanda A1. We source at <strong>$3,200–$4,000/MT</strong> FOB Kigali. That's <strong>$1,600–$3,000/MT</strong> for the right distributor.</p>
            </div>
          </div>
          <div>
            <div className="text-amber-400 text-xs font-bold tracking-widest uppercase mb-3">South Africa Market</div>
            <h3 className="text-3xl font-bold mb-4">The Boutique Hotel Opportunity</h3>
            <p className="text-stone-400 leading-relaxed mb-4">
              SA's specialty coffee market is growing 15% YoY. Independent boutique hotels in Sandton, Cape Town, and the Winelands are actively seeking direct-trade suppliers with authentic African origin stories.
            </p>
            <div className="p-4 bg-amber-950/40 border border-amber-800/30 rounded-xl">
              <div className="text-xs text-amber-400 font-semibold mb-2">Boutique Buyer Pricing</div>
              <p className="text-sm text-stone-300">SA boutique buyers pay <strong>R85–R140/kg</strong> for premium green. Landed cost: <strong>R52–R68/kg</strong>. The margin window for direct-trade specialty roasters is strong.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Table */}
      <section id="pricing" className="px-8 py-24 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">B2B Pricing — FOB Kigali</h2>
          <p className="text-stone-400">Indicative pricing. EXW Kigali. Sea freight additional.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-stone-700">
                <th className="py-4 px-6 text-stone-400 font-medium text-sm">Grade</th>
                <th className="py-4 px-6 text-stone-400 font-medium text-sm">Min Order</th>
                <th className="py-4 px-6 text-stone-400 font-medium text-sm">FOB Price (USD/MT)</th>
                <th className="py-4 px-6 text-stone-400 font-medium text-sm">Certifications</th>
              </tr>
            </thead>
            <tbody>
              {pricingRows.map((row, i) => (
                <tr key={row.grade} className={`border-b border-stone-800 ${i % 2 === 0 ? 'bg-stone-900/50' : ''}`}>
                  <td className="py-4 px-6 font-semibold text-amber-400">{row.grade}</td>
                  <td className="py-4 px-6 text-stone-300">{row.minOrder}</td>
                  <td className="py-4 px-6 text-white font-medium">{row.fobPrice}</td>
                  <td className="py-4 px-6">
                    <span className="px-3 py-1 bg-stone-800 rounded-full text-xs text-stone-300">{row.cert}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-6 grid md:grid-cols-3 gap-4 text-center text-sm text-stone-500">
          <div className="p-3 bg-stone-900 rounded-lg border border-stone-800">📄 Bill of Lading included</div>
          <div className="p-3 bg-stone-900 rounded-lg border border-stone-800">🌿 Phytosanitary certificate</div>
          <div className="p-3 bg-stone-900 rounded-lg border border-stone-800">🧾 Certificate of origin + cupping report</div>
        </div>
      </section>

      {/* PROWTC Callout */}
      <section className="px-8 py-16 max-w-4xl mx-auto">
        <div className="bg-gradient-to-r from-amber-900/60 to-stone-900/60 border border-amber-700/40 rounded-2xl p-10 text-center">
          <div className="text-xs text-amber-400 font-bold tracking-widest uppercase mb-3">New Buyers</div>
          <h3 className="text-2xl font-bold mb-3">PROWTC Dubai Pilot Programme</h3>
          <p className="text-stone-400 mb-6 max-w-xl mx-auto">Structured pricing, dedicated account manager, and priority shipping slots for inaugural buyers. Let us prove the supply chain.</p>
          <a href="#contact" className="inline-block px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg transition">
            Apply for PROWTC
          </a>
        </div>
      </section>

      {/* Contact Form */}
      <section id="contact" className="px-8 py-24 bg-stone-900">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Let's Talk</h2>
            <p className="text-stone-400">We're building long-term supply relationships — not one-off transactions. Tell us about your requirements.</p>
          </div>

          {submitted ? (
            <div className="text-center py-16 bg-stone-800 rounded-2xl border border-amber-700/30">
              <div className="text-4xl mb-4">✅</div>
              <h3 className="text-xl font-bold mb-2">Request Received</h3>
              <p className="text-stone-400">Charlie at Studex will reach out within 24 hours. Check your inbox or WhatsApp.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Full Name *</label>
                  <input required type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-amber-600 transition" placeholder="Your name" />
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Company *</label>
                  <input required type="text" value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-amber-600 transition" placeholder="Hotel / Roastery / Distributor" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Email *</label>
                  <input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-amber-600 transition" placeholder="buyer@company.com" />
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Phone / WhatsApp</label>
                  <input type="tel" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-amber-600 transition" placeholder="+27 XX XXX XXXX" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Volume Required</label>
                  <select value={form.volume} onChange={e => setForm({ ...form, volume: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-600 transition">
                    <option value="">Select volume</option>
                    <option value="500kg">500 kg – 1 MT</option>
                    <option value="1-5mt">1 – 5 MT</option>
                    <option value="5-20mt">5 – 20 MT</option>
                    <option value="20mt+">20+ MT (annual)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Grade Interest</label>
                  <select value={form.grade} onChange={e => setForm({ ...form, grade: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-600 transition">
                    <option value="">Select grade</option>
                    <option>A1 Washed</option>
                    <option>A2 Washed</option>
                    <option>A1 Natural</option>
                    <option>A2 Natural</option>
                    <option>Multiple / Sample Pack</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Message</label>
                <textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} rows={4} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-amber-600 transition resize-none" placeholder="Tell us about your requirements, timeline, delivery port..." />
              </div>
              <button type="submit" className="w-full py-4 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-lg transition text-lg">
                Send Inquiry — We'll Reply Within 24h
              </button>
            </form>
          )}

          <div className="mt-10 grid md:grid-cols-3 gap-4 text-center text-sm text-stone-500">
            <div>
              <div className="text-lg mb-1">📧</div>
              <div className="font-medium text-stone-300">charlie@agent.studexmeat.com</div>
            </div>
            <div>
              <div className="text-lg mb-1">💬</div>
              <div className="font-medium text-stone-300">+27 82 555 0194</div>
            </div>
            <div>
              <div className="text-lg mb-1">🏢</div>
              <div className="font-medium text-stone-300">Robusca Group · Studex Wildlife</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-stone-800 px-8 py-8 text-center text-stone-600 text-sm">
        © 2026 Robusca Group (Pty) Ltd · Studex Wildlife Coffee · charlie@agent.studexmeat.com
      </footer>
    </div>
  )
}

export default App
