import { useState } from 'react'

const products = [
  {
    name: 'Oscietra Imperial',
    origin: 'Russia · Caspian Sea',
    description: 'Golden-brown grains with a rich, nutty flavor and smooth finish. The crown jewel of Russian caviar.',
    price: 'R 4,200',
    unit: '250g',
    moq: '5 units',
    badge: 'Signature',
    image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80',
  },
  {
    name: 'Sevruga Premium',
    origin: 'Russia · Caspian Sea',
    description: 'Small, dark grains with an intense, bold flavor. Prized for its concentrated taste and silky texture.',
    price: 'R 3,400',
    unit: '250g',
    moq: '5 units',
    badge: 'Popular',
    image: 'https://images.unsplash.com/photo-1585672840563-f2af2ced55c7?w=600&q=80',
  },
  {
    name: 'Siberian Reserve',
    origin: 'Russia · Siberian Lakes',
    description: 'Large, glossy grains with a buttery, refined taste. Excellent value for the discerning buyer.',
    price: 'R 2,600',
    unit: '250g',
    moq: '10 units',
    badge: 'Value',
    image: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
  },
  {
    name: 'Hackback Royal',
    origin: 'Russia · Black Sea',
    description: 'Exceptional large-grain caviar with a sweet, lingering finish. Rare and exquisitely packaged.',
    price: 'R 5,800',
    unit: '250g',
    moq: '3 units',
    badge: 'Rare',
    image: 'https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=600&q=80',
  },
]

const inquiryTopics = [
  'Hotel & Restaurant Supply',
  'Private Event Catering',
  'Corporate Gifting',
  'Retail Partnership',
  'Distribution Enquiry',
]

export default function App() {
  const [form, setForm] = useState({
    name: '',
    company: '',
    email: '',
    phone: '',
    topic: inquiryTopics[0],
    message: '',
    volume: '',
  })
  const [submitted, setSubmitted] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-[#f5f0e8] font-sans">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-6 border-b border-[#2a2520]">
        <div className="text-xl font-serif tracking-widest text-[#c9a84c]">STUDEX CAVIAR</div>
        <div className="hidden md:flex gap-8 text-sm tracking-wider text-[#a09080]">
          <a href="#collection" className="hover:text-[#c9a84c] transition-colors">COLLECTION</a>
          <a href="#pricing" className="hover:text-[#c9a84c] transition-colors">PRICING</a>
          <a href="#sourcing" className="hover:text-[#c9a84c] transition-colors">SOURCING</a>
          <a href="#inquiry" className="hover:text-[#c9a84c] transition-colors">INQUIRY</a>
        </div>
        <a href="#inquiry" className="bg-[#c9a84c] text-[#0a0a0f] px-5 py-2 text-sm font-bold tracking-widest hover:bg-[#e0be6a] transition-colors">
          B2B INQUIRY
        </a>
      </nav>

      {/* Hero */}
      <section className="relative px-8 py-32 text-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-[#12100a] to-[#0a0a0f]" />
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: 'url("https://images.unsplash.com/photo-1544025162-d76694265947?w=1600&q=60")',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'blur(2px)',
          }}
        />
        <div className="relative z-10 max-w-4xl mx-auto">
          <p className="text-[#c9a84c] tracking-[0.4em] text-sm mb-6">IMPORTED FROM RUSSIA · DELIVERED TO SOUTH AFRICA</p>
          <h1 className="text-5xl md:text-7xl font-serif font-light mb-6 leading-tight">
            The Finest Russian<br />
            <span className="text-[#c9a84c]">Caviar</span> for SA Tables
          </h1>
          <p className="text-[#a09080] text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
            Authentic Caspian Sea caviar, ethically sourced and professionally imported.
            For hotels, restaurants, and luxury purveyors who accept nothing less.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#collection" className="border border-[#c9a84c] text-[#c9a84c] px-8 py-3 tracking-widest text-sm hover:bg-[#c9a84c] hover:text-[#0a0a0f] transition-all">
              VIEW COLLECTION
            </a>
            <a href="#inquiry" className="bg-[#c9a84c] text-[#0a0a0f] px-8 py-3 tracking-widest text-sm font-bold hover:bg-[#e0be6a] transition-colors">
              SPEAK TO US
            </a>
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#c9a84c40] to-transparent" />
      </section>

      {/* Trust bar */}
      <section className="border-y border-[#2a2520] bg-[#0f0e0b]">
        <div className="max-w-5xl mx-auto px-8 py-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            ['Caspian Sea Origin', 'Direct from Russian suppliers'],
            ['Cold Chain Certified', 'Temperature-controlled delivery'],
            ['SA Customs Cleared', 'Full import documentation'],
            ['B2B Only', 'Trade & hospitality accounts'],
          ].map(([title, sub]) => (
            <div key={title}>
              <div className="text-[#c9a84c] text-xs tracking-widest mb-1">{title}</div>
              <div className="text-[#706050] text-xs">{sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Collection */}
      <section id="collection" className="px-8 py-24 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-[#c9a84c] tracking-[0.3em] text-xs mb-3">THE COLLECTION</p>
          <h2 className="text-4xl font-serif font-light">Choose Your Caviar</h2>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {products.map(p => (
            <div key={p.name} className="border border-[#2a2520] hover:border-[#c9a84c60] transition-colors group">
              <div className="h-48 overflow-hidden">
                <img src={p.image} alt={p.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              </div>
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="inline-block bg-[#c9a84c20] text-[#c9a84c] text-xs px-2 py-0.5 tracking-wider mb-2">{p.badge}</span>
                    <h3 className="text-xl font-serif">{p.name}</h3>
                    <p className="text-[#706050] text-xs tracking-wider mt-0.5">{p.origin}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-[#c9a84c] text-xl font-serif">{p.price}</div>
                    <div className="text-[#706050] text-xs">per {p.unit}</div>
                  </div>
                </div>
                <p className="text-[#a09080] text-sm leading-relaxed mb-4">{p.description}</p>
                <div className="flex items-center justify-between pt-4 border-t border-[#2a2520]">
                  <span className="text-[#706050] text-xs">MOQ: <span className="text-[#c9a84c]">{p.moq}</span></span>
                  <a href="#inquiry" className="text-xs tracking-widest text-[#c9a84c] hover:underline">REQUEST QUOTE →</a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Sourcing */}
      <section id="sourcing" className="bg-[#0f0e0b] border-y border-[#2a2520] px-8 py-24">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-16 items-center">
          <div>
            <p className="text-[#c9a84c] tracking-[0.3em] text-xs mb-3">OUR SOURCING</p>
            <h2 className="text-4xl font-serif font-light mb-6">Direct from the<br />Caspian Sea</h2>
            <p className="text-[#a09080] leading-relaxed mb-6">
              We work directly with certified Russian caviar houses — producers who have operated for generations 
              in the Astrakhan region. Every tin is traceable to its source waters.
            </p>
            <div className="space-y-4">
              {[
                'CITES-certified import permits for all species',
                'Cold-chain logistics from Moscow to Johannesburg',
                'Full FDA-equivalent SA health certifications',
                'Customs clearance and duty handled by us',
              ].map(item => (
                <div key={item} className="flex items-start gap-3">
                  <span className="text-[#c9a84c] mt-0.5">◆</span>
                  <span className="text-[#a09080] text-sm">{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="relative">
            <img 
              src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80" 
              alt="Caviar presentation" 
              className="w-full h-80 object-cover border border-[#2a2520]"
            />
            <div className="absolute -bottom-4 -left-4 bg-[#0a0a0f] border border-[#2a2520] p-4 w-48">
              <div className="text-[#c9a84c] text-2xl font-serif">100%</div>
              <div className="text-[#706050] text-xs">Authentic Russian Origin Guaranteed</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing table */}
      <section id="pricing" className="px-8 py-24 max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-[#c9a84c] tracking-[0.3em] text-xs mb-3">TRADE PRICING</p>
          <h2 className="text-4xl font-serif font-light">Volume & MOQ Structure</h2>
        </div>
        <div className="border border-[#2a2520]">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#2a2520] bg-[#0f0e0b]">
                <th className="text-left p-4 text-[#c9a84c] font-normal tracking-wider">PRODUCT</th>
                <th className="text-center p-4 text-[#c9a84c] font-normal tracking-wider">250g</th>
                <th className="text-center p-4 text-[#c9a84c] font-normal tracking-wider">500g</th>
                <th className="text-center p-4 text-[#c9a84c] font-normal tracking-wider">1kg</th>
                <th className="text-center p-4 text-[#c9a84c] font-normal tracking-wider">MOQ</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p, i) => (
                <tr key={p.name} className={`border-b border-[#2a2520] ${i % 2 === 0 ? '' : 'bg-[#0f0e0b]'}`}>
                  <td className="p-4 font-serif">{p.name}</td>
                  <td className="p-4 text-center text-[#a09080]">{p.price}</td>
                  <td className="p-4 text-center text-[#a09080]">Enquire</td>
                  <td className="p-4 text-center text-[#a09080]">Enquire</td>
                  <td className="p-4 text-center text-[#c9a84c]">{p.moq}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-center text-[#706050] text-xs mt-4 tracking-wider">
          PRICES IN ZAR · SUBJECT TO ZAR/USD EXCHANGE RATE AT TIME OF ORDER · DELIVERY TO JHB, CPT, DBN AVAILABLE
        </p>
      </section>

      {/* Inquiry form */}
      <section id="inquiry" className="px-8 py-24 bg-[#0f0e0b] border-t border-[#2a2520]">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-[#c9a84c] tracking-[0.3em] text-xs mb-3">B2B INQUIRY</p>
            <h2 className="text-4xl font-serif font-light mb-3">Start Your Order</h2>
            <p className="text-[#706050] text-sm">We respond within 24 hours. All enquiries are handled discretionally.</p>
          </div>

          {submitted ? (
            <div className="text-center py-16 border border-[#c9a84c40]">
              <div className="text-[#c9a84c] text-4xl mb-4">◆</div>
              <h3 className="text-2xl font-serif mb-3">Enquiry Received</h3>
              <p className="text-[#706050] text-sm">Thank you, {form.name.split(' ')[0]}. We will be in touch within 24 hours<br />with a formal quote and availability confirmation.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-[#706050] text-xs tracking-wider mb-2">FULL NAME *</label>
                  <input required name="name" value={form.name} onChange={handleChange} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors" placeholder="Jane Smith" />
                </div>
                <div>
                  <label className="block text-[#706050] text-xs tracking-wider mb-2">COMPANY / establishment *</label>
                  <input required name="company" value={form.company} onChange={handleChange} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors" placeholder="The Table Bay Hotel" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-[#706050] text-xs tracking-wider mb-2">EMAIL *</label>
                  <input required name="email" type="email" value={form.email} onChange={handleChange} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors" placeholder="jane@tablebay.co.za" />
                </div>
                <div>
                  <label className="block text-[#706050] text-xs tracking-wider mb-2">PHONE / WhatsApp</label>
                  <input name="phone" value={form.phone} onChange={handleChange} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors" placeholder="+27 82 000 0000" />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-[#706050] text-xs tracking-wider mb-2">ENQUIRY TYPE *</label>
                  <select required name="topic" value={form.topic} onChange={handleChange} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors">
                    {inquiryTopics.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[#706050] text-xs tracking-wider mb-2">APPROX. VOLUME (units/month)</label>
                  <input name="volume" value={form.volume} onChange={handleChange} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors" placeholder="e.g. 20 × 250g" />
                </div>
              </div>
              <div>
                <label className="block text-[#706050] text-xs tracking-wider mb-2">MESSAGE</label>
                <textarea name="message" value={form.message} onChange={handleChange} rows={4} className="w-full bg-[#0a0a0f] border border-[#2a2520] text-[#f5f0e8] px-4 py-3 text-sm focus:border-[#c9a84c] outline-none transition-colors resize-none" placeholder="Tell us about your requirements, event date, delivery address..." />
              </div>
              <button type="submit" className="w-full bg-[#c9a84c] text-[#0a0a0f] py-4 font-bold tracking-widest text-sm hover:bg-[#e0be6a] transition-colors">
                SUBMIT TRADE ENQUIRY
              </button>
              <p className="text-center text-[#504040] text-xs">We respect your privacy. Enquiries are not shared with third parties.</p>
            </form>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#2a2520] px-8 py-8">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-[#c9a84c] tracking-widest text-sm">STUDEX CAVIAR</div>
          <div className="text-[#504040] text-xs tracking-wider">
            © 2026 Studex (Pty) Ltd · Johannesburg, South Africa · VAT 4920183721
          </div>
          <div className="text-[#504040] text-xs">trade@studexmeat.com</div>
        </div>
      </footer>
    </div>
  )
}
