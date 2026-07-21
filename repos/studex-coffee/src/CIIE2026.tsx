import { useState } from 'react'

const chinaProducts = [
  {
    grade: 'Rwanda A1',
    process: 'Washed',
    screen: 'Screen 15+',
    score: '85+ pts SCA',
    notes: 'Jasmine, stone fruit, clean black tea finish',
    certifications: ['Rainforest Alliance', 'PROWTC'],
    fobUsd: 'USD 4.80/kg',
    moq: '60kg bags',
    stock: '12 MT available',
    color: 'from-red-900 to-amber-800',
    flag: '🇷🇼',
  },
  {
    grade: 'Rwanda A2',
    process: 'Natural',
    screen: 'Screen 14+',
    score: '84+ pts SCA',
    notes: 'Blueberry, dark chocolate, full body, winey',
    certifications: ['Rainforest Alliance', 'PROWTC'],
    fobUsd: 'USD 5.20/kg',
    moq: '60kg bags',
    stock: '6 MT available',
    color: 'from-amber-950 to-orange-900',
    flag: '🇷🇼',
  },
]

const buyerTypes = [
  {
    emoji: '🏭',
    title: 'Roasteries & Coffee Chains',
    description: 'Import green bean for in-house roasting. Fixed quarterly pricing eliminates spot-market exposure. We handle logistics to your roastery.',
    cta: 'Request FOB Quote',
  },
  {
    emoji: '🏨',
    title: 'Hotels & Hospitality Groups',
    description: 'Premium African origin story for menus and branding. Custom private-label packaging available for orders above 2 MT.',
    cta: 'Inquire About Private Label',
  },
  {
    emoji: '🛒',
    title: 'Importers & Distributors',
    description: 'Exclusive distribution partnerships available for China provinces. First-year partners get priority allocation and dedicated account management.',
    cta: 'Apply for Distribution',
  },
  {
    emoji: '📦',
    title: 'E-Commerce & Retail',
    description: 'Whole bean, ground, or private-label packs for online channels. Shelf-ready with Chinese labeling compliance documentation included.',
    cta: 'Get Retail Pricing',
  },
]

const timeline = [
  { month: 'Aug 2026', event: 'CIIE Booth Confirmed · Sample packs dispatched to China buyers', done: false },
  { month: 'Sep 2026', event: 'Pre-meetings with Luckin, Tim Hortons China procurement teams', done: false },
  { month: 'Oct 2026', event: 'First container loaded — Kigali to Shanghai (approx. 21 days)', done: false },
  { month: 'Nov 5–10', event: 'CIIE Shanghai — Booth 7.2A-06, Robusca Group (Studex Meat)', done: false },
  { month: 'Dec 2026', event: 'First SA green coffee landed in China under bilateral protocol', done: false },
]

function CIIE2026() {
  const [form, setForm] = useState({
    name: '', company: '', role: '', email: '', wechat: '',
    volume: '', grade: '', city: '', message: ''
  })
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 font-sans">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-red-900/50 bg-stone-950/95 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-red-700 flex items-center justify-center text-white font-bold text-sm">S</div>
          <span className="text-lg font-semibold tracking-wide">Studex Meat — China Export</span>
        </div>
        <div className="flex gap-5 text-sm text-stone-400">
          <a href="#products" className="hover:text-red-400 transition">产品 Products</a>
          <a href="#buyers" className="hover:text-red-400 transition">合作用于 Buyer Types</a>
          <a href="#timeline" className="hover:text-red-400 transition">Timeline</a>
          <a href="#contact" className="px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg transition text-sm font-semibold">报名 Register</a>
        </div>
      </nav>

      {/* Hero — China Export Focus */}
      <section className="relative overflow-hidden px-8 py-28 text-center">
        <div className="absolute inset-0 bg-gradient-to-br from-red-950 via-stone-950 to-stone-950" />
        <div className="absolute inset-0 opacity-5"
          style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'40\' height=\'40\' viewBox=\'0 0 40 40\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23dc2626\' fill-opacity=\'1\'%3E%3Cpath d=\'M20 0v40M0 20h40\'/%3E%3C/g%3E%3C/svg%3E")' }}
        />
        <div className="relative max-w-4xl mx-auto">
          {/* China announcement badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-red-500/50 bg-red-950/60 text-red-300 text-xs font-bold tracking-widest uppercase mb-6">
            <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
            🇨🇳 中国市场开放 · July 20, 2026 — Zero Tariff Access Granted
          </div>

          <h1 className="text-4xl md:text-7xl font-bold leading-tight mb-6">
            Rwanda Green Coffee<br />
            <span className="text-red-500">Now Accessible to China</span>
          </h1>
          <p className="text-xl text-stone-400 max-w-2xl mx-auto mb-4 leading-relaxed">
            First-mover window is open. South African green coffee — zero tariff under FOCAC bilateral protocol. Farm-traceable. Rainforest Alliance certified. CIIE Shanghai, Booth 7.2A-06.
          </p>
          <p className="text-lg text-amber-400 font-semibold mb-10">
            Booth applications close August 31, 2026 · CIIE Shanghai · Nov 5–10, 2026
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#contact" className="px-8 py-4 bg-red-700 hover:bg-red-600 text-white font-bold rounded-lg transition text-center text-lg">
              🇨🇳 Register China Interest
            </a>
            <a href="#products" className="px-8 py-4 border border-stone-600 hover:border-red-600 text-stone-300 hover:text-red-400 font-semibold rounded-lg transition text-center">
              View Products & Pricing
            </a>
          </div>

          {/* Quick stats */}
          <div className="flex flex-wrap items-center justify-center gap-6 mt-14 text-sm text-stone-500">
            <span className="flex items-center gap-2">☕ Rwanda #1 Africa's coffee growth story</span>
            <span className="text-stone-700">|</span>
            <span className="flex items-center gap-2">🌿 Rainforest Alliance + PROWTC Certified</span>
            <span className="text-stone-700">|</span>
            <span className="flex items-center gap-2">📍 FOB Kigali · Sea freight to Shanghai ~21 days</span>
          </div>
        </div>
      </section>

      {/* WHY CHINA NOW bar */}
      <section className="bg-gradient-to-r from-red-950/60 via-stone-950 to-red-950/60 border-y border-red-900/40 px-8 py-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-red-400 mb-2">为什么是现在？Why China, Why Now?</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: '🗡️',
                title: 'Zero Tariff — TODAY',
                en: 'July 20, 2026: South African green coffee admitted under FOCAC bilateral agricultural protocol. Zero import tariff. First-mover advantage goes to who moves first.',
                zh: '2026年7月20日：南非绿色咖啡获FOCAC双边农业协议批准，零关税。',
              },
              {
                icon: '🏆',
                title: 'CIIE Shanghai — Nov 5–10',
                en: 'China International Import Expo is the premier platform for B2B agricultural deals. Deadline: August 31. We have the booth. We need the buyers.',
                zh: '中国国际进口博览会是B2B农业交易的首选平台。报名截止：8月31日。',
              },
              {
                icon: '📈',
                title: 'Demand Is Ready',
                en: 'Luckin Coffee (9,000+ stores), Tim Hortons China (600+ stores), Pacific Coffee — all actively seeking diversified African origin suppliers beyond Ethiopia and Kenya.',
                zh: '瑞幸咖啡（9000+门店）、Tim Hortons中国（600+门店）— 均在寻求非洲货源。',
              },
            ].map(item => (
              <div key={item.title} className="bg-stone-900/80 border border-red-900/30 rounded-xl p-6">
                <div className="text-2xl mb-3">{item.icon}</div>
                <h3 className="font-bold text-red-300 mb-2">{item.title}</h3>
                <p className="text-stone-400 text-sm leading-relaxed mb-3">{item.en}</p>
                <p className="text-stone-600 text-xs leading-relaxed">{item.zh}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Products */}
      <section id="products" className="px-8 py-24 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Current Export Offerings<br /><span className="text-red-400"> Rwanda · South Africa · China</span></h2>
          <p className="text-stone-400 max-w-xl mx-auto">Prices FOB Kigali, Rwanda. Sea freight to Shanghai: ~USD 0.90/kg. All prices in USD. Minimum order: 60kg bags.</p>
        </div>
        <div className="grid md:grid-cols-2 gap-8 mb-10">
          {chinaProducts.map((p) => (
            <div key={p.grade} className={`rounded-2xl bg-gradient-to-br ${p.color} p-8 flex flex-col`}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm">{p.flag}</span>
                <span className="text-xs text-white/50 uppercase tracking-widest">{p.process} · {p.screen} · {p.score}</span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-2">{p.grade}</h3>
              <div className="text-white/70 italic mb-4">{p.notes}</div>
              <div className="flex flex-wrap gap-2 mb-6">
                {p.certifications.map(c => (
                  <span key={c} className="px-3 py-1 bg-white/15 rounded-full text-xs text-white/90">{c}</span>
                ))}
              </div>
              <div className="mt-auto space-y-3 border-t border-white/20 pt-4">
                <div className="flex justify-between">
                  <span className="text-white/60 text-sm">FOB Price</span>
                  <span className="font-bold text-white text-lg">{p.fobUsd}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60 text-sm">Minimum Order</span>
                  <span className="text-white/80">{p.moq}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60 text-sm">Available Stock</span>
                  <span className="text-amber-300 font-semibold">{p.stock}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Landed cost calculator hint */}
        <div className="bg-stone-900 border border-stone-800 rounded-xl p-6">
          <h4 className="font-semibold text-stone-200 mb-3">📊 Landed Cost Estimate — Shanghai</h4>
          <div className="grid md:grid-cols-4 gap-4 text-sm">
            {[
              ['FOB Kigali', 'USD 4.80/kg'],
              ['Freight Kigali → Shanghai', '~USD 0.90/kg'],
              ['Import duty (0% FOCAC)', 'USD 0.00/kg'],
              ['Landed Cost ≈', 'USD 5.70/kg'],
            ].map(([label, val]) => (
              <div key={label} className="text-center p-3 bg-stone-800 rounded-lg">
                <div className="text-stone-500 text-xs mb-1">{label}</div>
                <div className="font-semibold text-white">{val}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-stone-500 mt-3">Indicative only. Final freight quotes confirmed at time of booking. Payment: Letter of Credit or TT 30 days.</p>
        </div>
      </section>

      {/* Buyer Types */}
      <section id="buyers" className="px-8 py-20 bg-stone-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold mb-3">Who We're Looking For<br /><span className="text-stone-500 text-xl font-normal">我们寻找的合作伙伴</span></h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {buyerTypes.map((b) => (
              <div key={b.title} className="bg-stone-800 border border-stone-700 rounded-2xl p-8 flex flex-col">
                <div className="text-3xl mb-4">{b.emoji}</div>
                <h3 className="text-xl font-bold text-white mb-2">{b.title}</h3>
                <p className="text-stone-400 text-sm leading-relaxed mb-6 flex-1">{b.description}</p>
                <a href="#contact" className="inline-block text-center px-5 py-3 bg-red-800/60 hover:bg-red-700/60 border border-red-700/50 text-red-300 font-semibold rounded-lg transition text-sm">
                  {b.cta}
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CIIE Timeline */}
      <section id="timeline" className="px-8 py-20 max-w-4xl mx-auto">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold mb-3">Roadmap to CIIE 2026<br /><span className="text-red-400 text-lg font-normal">进博会展出路线图</span></h2>
          <p className="text-stone-500 text-sm">从现在到上海的一切</p>
        </div>
        <div className="space-y-0">
          {timeline.map((t, i) => (
            <div key={t.month} className="flex gap-6">
              <div className="flex flex-col items-center">
                <div className={`w-4 h-4 rounded-full mt-2 ${i === 0 ? 'bg-red-500 ring-4 ring-red-500/30' : 'bg-stone-700'}`} />
                {i < timeline.length - 1 && <div className="w-0.5 flex-1 bg-stone-800 mt-1" />}
              </div>
              <div className={`pb-8 ${i < timeline.length - 1 ? '' : 'pb-0'}`}>
                <div className="text-xs font-bold text-red-400 uppercase tracking-widest mb-1">{t.month}</div>
                <div className="text-stone-300 text-sm leading-relaxed">{t.event}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-8 p-4 bg-red-950/30 border border-red-900/40 rounded-xl text-center">
          <p className="text-sm text-red-300">
            🚨 <strong>CIIE Booth Application Deadline: August 31, 2026</strong> — 联系我们在上海的展位预约。
          </p>
        </div>
      </section>

      {/* Contact Form */}
      <section id="contact" className="px-8 py-24 bg-stone-900">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Register Your Interest<br /><span className="text-red-400 text-2xl font-normal">报名</span></h2>
            <p className="text-stone-400">
              Charlie, our B2B coordinator, handles all China inquiries personally.<br />
              <span className="text-stone-500 text-sm">查理会亲自处理所有中国买家的询问。</span>
            </p>
          </div>

          {submitted ? (
            <div className="text-center py-16 bg-stone-800 rounded-2xl border border-red-700/30">
              <div className="text-4xl mb-4">✅</div>
              <h3 className="text-xl font-bold mb-2">报名已收到！</h3>
              <p className="text-stone-400">Charlie will contact you within 24 hours.请注意查收邮件或微信。</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Full Name 姓名 *</label>
                  <input required type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition" placeholder="Your name" />
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Company 公司 *</label>
                  <input required type="text" value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition" placeholder="Company / 酒店 / 烘焙厂" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Role / Title 职位</label>
                  <input type="text" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition" placeholder="Procurement Manager / 采购经理" />
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Email *</label>
                  <input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition" placeholder="buyer@company.com" />
                </div>
              </div>
              <div>
                <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">WeChat ID 微信</label>
                <input type="text" value={form.wechat} onChange={e => setForm({ ...form, wechat: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition" placeholder="WeChat ID for direct contact" />
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Monthly Volume 月需求量</label>
                  <select value={form.volume} onChange={e => setForm({ ...form, volume: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-red-600 transition">
                    <option value="">Select volume</option>
                    <option value="300-1mt">300 kg – 1 MT</option>
                    <option value="1-5mt">1 – 5 MT</option>
                    <option value="5-20mt">5 – 20 MT</option>
                    <option value="20mt+">20+ MT (annual contract)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Grade Interest 感兴趣的等级</label>
                  <select value={form.grade} onChange={e => setForm({ ...form, grade: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-red-600 transition">
                    <option value="">Select grade</option>
                    <option>Rwanda A1 Washed</option>
                    <option>Rwanda A2 Natural</option>
                    <option>A1 + A2 Mix</option>
                    <option>Sample Pack (all grades)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">City / Province 城市</label>
                <input type="text" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition" placeholder="Shanghai / Beijing / Guangzhou..." />
              </div>
              <div>
                <label className="block text-xs text-stone-400 uppercase tracking-wider mb-2">Message 留言</label>
                <textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} rows={4} className="w-full bg-stone-800 border border-stone-700 rounded-lg px-4 py-3 text-white placeholder-stone-500 focus:outline-none focus:border-red-600 transition resize-none" placeholder="Tell us about your roastery, current suppliers, and what you're looking for... / 告诉我们您的烘焙厂和需求..." />
              </div>
              <button type="submit" className="w-full py-4 bg-red-700 hover:bg-red-600 text-white font-bold rounded-lg transition text-lg">
                🇨🇳 Submit China Interest — 24小时内回复
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
              <span className="text-lg">🏨</span>
              <span>CIIE Booth 7.2A-06 · Nov 5–10, 2026</span>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-stone-800 px-8 py-8 text-center text-stone-600 text-sm">
        © 2026 Robusca Group (Pty) Ltd · Studex Meat — China Coffee Export Division · charlie@agent.studexmeat.com
      </footer>
    </div>
  )
}

export default CIIE2026
