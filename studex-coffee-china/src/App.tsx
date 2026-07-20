import { useState } from 'react'

const PRODUCTS = [
  { grade: 'Rwanda A1', process: 'Washed', altitude: '1,800–2,200m', score: '85+', price: '$5,800', cert: 'Rainforest Alliance', moq: '1 MT', featured: false,
    highlights: ['Full RA certification', 'Traceable lot system', 'SGS pre-shipment cupping', 'MOQ 1 MT'] },
  { grade: 'Rwanda A2', process: 'Washed', altitude: '1,600–2,000m', score: '82–84', price: '$5,200', cert: 'Rainforest Alliance', moq: '1 MT', featured: true,
    highlights: ['Best value-to-quality ratio', 'Ideal for mid-scale roasters', 'Dedicated lot reservation', '5–7 week lead time'] },
  { grade: 'Rwanda Premium', process: 'Natural', altitude: '1,900–2,200m', score: '87+', price: '$6,400', cert: 'RA + Direct Trade', moq: '500 kg', featured: false,
    highlights: ['Bourbon varietal', 'Floral & fruit notes', 'Single washing station', 'Limited availability'] },
]

const CHANNELS = [
  { title: 'Alibaba.com', desc: 'List now. 40M+ buyers. AI search surfaces Africa origin queries. First-movers own the category.', badge: 'Apply Listing' },
  { title: 'CIIE Shanghai Nov 2026', desc: 'Government-subsidized Africa booth. Meet Luckin Coffee, Tim Hortons, Pacific Coffee buyers. Deadline: this week.', badge: 'Booth Enquiry' },
  { title: 'Direct Buyer Outreach', desc: 'Targeted email to C-suite at Luckin Coffee and Tim Hortons China. Rwanda cup profile + zero tariff = immediate interest.', badge: 'Get Sequence' },
]

const LOGISTICS = [
  { step: 1, title: 'Order Confirmed', desc: 'MOQ 1 MT. Lot reserved. Proforma invoice within 24h.' },
  { step: 2, title: 'Quality Approval', desc: 'SGS pre-shipment cupping. Sample approval before loading.' },
  { step: 3, title: 'Kigali → Djibouti', desc: 'Ground freight to Djibouti port. 5–7 days.' },
  { step: 4, title: 'Djibouti → Shanghai', desc: 'Sea freight ~21 days. Zero tariff. CIF delivery included.' },
]

const T = {
  en: {
    heroTitle: 'Rwanda Premium Coffee', heroSub: 'A1 & A2 grade Arabica. Zero tariff into China from July 20, 2026. Rainforest Alliance certified. CIF Shanghai delivery.',
    statTariff: '0%', statTariffL: 'China Import Tariff', statCountries: '53', statCountriesL: 'African Countries Eligible',
    statDate: 'Jul 20', statDateL: 'Policy Effective', statMoq: '1 MT', statMoqL: 'Minimum Order (CIF)',
    oppHeadline: 'Historic Market Opening',
    oppBody: 'From July 20, 2026, China opens coffee imports to all 53 African countries. Rwanda qualifies immediately. Competitors are locking supply agreements — act now.',
    whyTitle: 'Why Rwanda Coffee', whySub: "The World's Most Story-Rich Arabica Origin",
    channelTitle: 'Market Access Channels',
    prodTitle: 'Product Specifications',
    pricingTitle: 'Pricing — CIF Shanghai', pricingSub: 'All-in delivered cost per MT',
    logisticsTitle: 'Supply Chain', logisticsSub: 'From Rwanda Hills to Shanghai Port in 5–7 Weeks',
    formTitle: 'Get a Quote Now', formSub: 'We supply roasters, importers, and distributors across Asia.',
    formCompany: 'Company Name', formName: 'Contact Person', formEmail: 'Email Address',
    formPhone: 'Phone / WeChat', formProduct: 'Product Interest', formQuantity: 'Quantity Needed',
    formMessage: 'Message', formSubmit: 'Send Enquiry', formSuccess: '✓ Enquiry sent! We respond within 24 hours.',
    formError: 'Please fill in all required fields.',
    ctaTitle: 'Ready to Source Rwanda?', ctaBody: 'Get a formal quote, request samples, or discuss a supply agreement.',
    footerBrand: 'Studex Wildlife', footerLocs: 'Kigali · Dubai · Shanghai · Cape Town',
    whyCards: [
      { icon: '🛡', title: 'Rainforest Alliance', body: 'Full RA certification. The #1 credential for EU and China premium buyers.' },
      { icon: '🌍', title: 'Geographic Identity', body: "Rwanda's volcanic soils produce bright acidity, floral aromatics, clean finish — prized by specialty roasters." },
      { icon: '📋', title: 'Traceable Supply Chain', body: 'End-to-end lot traceability. Phytosanitary, COO, bill of lading, insurance included.' },
    ],
  },
  zh: {
    heroTitle: '卢旺达顶级咖啡', heroSub: 'A1/A2级阿拉比卡。2026年7月20日起零关税进入中国。雨林联盟认证。CIF上海交货。',
    statTariff: '0%', statTariffL: '中国进口关税', statCountries: '53个', statCountriesL: '符合条件的非洲国家',
    statDate: '7月20日', statDateL: '政策生效日期', statMoq: '1吨', statMoqL: '最低起订量(CIF)',
    oppHeadline: '历史性市场开放',
    oppBody: '2026年7月20日起，中国对全部53个非洲国家开放咖啡进口。卢旺达立即符合条件。竞争对手正在锁定供应协议——现在行动。',
    whyTitle: '为什么选择卢旺达', whySub: '全球故事最丰富的阿拉比卡产地',
    channelTitle: '进入渠道',
    prodTitle: '产品规格',
    pricingTitle: '价格 — CIF上海', pricingSub: '含税到门价，每公吨',
    logisticsTitle: '供应链', logisticsSub: '从卢旺达到上海港，5–7周',
    formTitle: '立即获取报价', formSub: '我们供应烘焙商、进口商和亚洲分销商。',
    formCompany: '公司名称', formName: '联系人', formEmail: '邮箱',
    formPhone: '电话/微信', formProduct: '意向产品', formQuantity: '意向数量',
    formMessage: '留言', formSubmit: '发送询价', formSuccess: '✓ 询价已发送！我们将在24小时内回复。',
    formError: '请填写必填项后重试。',
    ctaTitle: '准备好采购卢旺达咖啡了吗？', ctaBody: '获取正式报价、样品申请或供应协议。',
    footerBrand: 'Studex Wildlife', footerLocs: '基加利·迪拜·上海·开普敦',
    whyCards: [
      { icon: '🛡', title: '雨林联盟认证', body: '全供应链雨林联盟认证。是欧盟和中国买家最重要的资质证明。' },
      { icon: '🌍', title: '地理身份标识', body: '卢旺达火山土壤产出独特风味——明亮酸质、花香、干净余韵。' },
      { icon: '📋', title: '可追溯供应链', body: '从水洗站到港口全程批次追溯。植物检疫证、产地证、提单全包。' },
    ],
  }
}

type Lang = 'en' | 'zh'
type FormState = { company: string; name: string; email: string; phone: string; product: string; quantity: string; message: string }

export default function App() {
  const [lang, setLang] = useState<Lang>('en')
  const t = T[lang]
  const [form, setForm] = useState<FormState>({ company: '', name: '', email: '', phone: '', product: '', quantity: '', message: '' })
  const [status, setStatus] = useState<'idle'|'success'|'error'>('idle')

  const upd = (k: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.company || !form.name || !form.email || !form.product) { setStatus('error'); return }
    try {
      await fetch('https://hook.eu-west-1.n8n.robusca.io/webhook/coffee-enquiry', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, source: 'china-coffee-landing', lang, ts: new Date().toISOString() }),
      }).catch(() => {})
    } catch {}
    const s = encodeURIComponent(`[${lang==='zh'?'ZH':'EN'}] Coffee Enquiry — ${form.product} × ${form.quantity}`)
    const b = encodeURIComponent(`Company: ${form.company}\nName: ${form.name}\nEmail: ${form.email}\nPhone: ${form.phone}\nProduct: ${form.product}\nQuantity: ${form.quantity}\n\n${form.message}`)
    window.location.href = `mailto:ceo@agent.studexmeat.com?subject=${s}&body=${b}`
    setStatus('success')
  }

  const secLabel = (txt: string) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
      <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#C9A84C' }}>{txt}</span>
      <span style={{ width: 40, height: 1, background: '#C9A84C', display: 'inline-block' }} />
    </div>
  )

  const inp = (label: string, key: keyof FormState, type = 'text', placeholder = '') => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.65)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>{label}</label>
      <input type={type} placeholder={placeholder} value={form[key]} onChange={upd(key)} required={key !== 'quantity' && key !== 'message' && key !== 'phone'}
        style={{ padding: '12px 16px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.08)', color: '#fff', fontSize: 14, outline: 'none' }} />
    </div>
  )

  return (
    <div style={{ fontFamily: "'Inter', sans-serif", background: '#F5F0E8', color: '#2C2416', minHeight: '100vh' }}>

      {/* LANG TOGGLE */}
      <div style={{ position: 'fixed', top: 16, right: 20, zIndex: 200, display: 'flex', gap: 8 }}>
        {(['en','zh'] as Lang[]).map(l => (
          <button key={l} onClick={() => setLang(l)} style={{ padding: '6px 14px', borderRadius: 4, border: `1px solid ${lang===l?'#2E5E3A':'#ccc'}`, fontSize: 12, fontWeight: 600, cursor: 'pointer', background: lang===l?'#2E5E3A':'transparent', color: lang===l?'#fff':'#555' }}>
            {l === 'en' ? 'EN' : '中文'}
          </button>
        ))}
      </div>

      {/* HERO */}
      <section style={{ background: '#1A1208', padding: '90px 40px 110px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 80% 20%, rgba(46,94,58,0.6) 0%, transparent 60%), radial-gradient(ellipse at 20% 80%, rgba(201,168,76,0.15) 0%, transparent 50%)', pointerEvents: 'none' }} />
        <div style={{ maxWidth: 1100, margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#C9A84C', border: '1px solid rgba(201,168,76,0.4)', padding: '6px 16px', borderRadius: 2, marginBottom: 32, display: 'inline-block' }}>
            🇨🇳 {lang==='zh'?'中国市场·2026年7月生效':'China Market · Effective July 2026'}
          </div>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(40px, 6vw, 76px)', fontWeight: 900, lineHeight: 1.05, marginBottom: 16, color: '#fff' }}>
            {t.heroTitle.split(' ').slice(0,-1).join(' ')} <span style={{ color: '#C9A84C' }}>{t.heroTitle.split(' ').slice(-1)}</span>
          </h1>
          <p style={{ fontSize: 18, color: 'rgba(255,255,255,0.6)', fontWeight: 300, maxWidth: 540, marginBottom: 40 }}>{t.heroSub}</p>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {['🛡 Rainforest Alliance','🌍 Zero Tariff — China 2026','📦 CIF Shanghai','📋 COO + Phytosanitary Included'].map(b => (
              <span key={b} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.12)', padding: '9px 16px', borderRadius: 4, fontSize: 13, color: 'rgba(255,255,255,0.8)' }}>{b}</span>
            ))}
          </div>
        </div>
      </section>

      {/* STATS */}
      <div style={{ background: '#2E5E3A', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
        {[{v:t.statTariff,l:t.statTariffL},{v:t.statCountries,l:t.statCountriesL},{v:t.statDate,l:t.statDateL},{v:t.statMoq,l:t.statMoqL}].map(s => (
          <div key={s.l} style={{ padding: '32px 24px', textAlign: 'center', borderRight: '1px solid rgba(255,255,255,0.15)' }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: '#C9A84C' }}>{s.v}</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: 4 }}>{s.l}</div>
          </div>
        ))}
      </div>

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '80px 40px' }}>

        {/* OPPORTUNITY BANNER */}
        <div style={{ background: '#1A1208', borderRadius: 8, padding: '48px 52px', marginBottom: 72, display: 'grid', gridTemplateColumns: '1fr auto', gap: 40, alignItems: 'center' }}>
          <div>
            {secLabel(lang==='zh'?'中非贸易政策':'China-Africa Trade Policy')}
            <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(24px, 3.5vw, 38px)', fontWeight: 700, color: '#fff', marginBottom: 16 }}>{t.oppHeadline}</h2>
            <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 15, maxWidth: 540 }}>{t.oppBody}</p>
          </div>
          <div style={{ background: 'rgba(201,168,76,0.15)', border: '1px solid #C9A84C', color: '#C9A84C', padding: '14px 20px', borderRadius: 100, textAlign: 'center', minWidth: 140 }}>
            <div style={{ fontSize: 26, fontFamily: "'Playfair Display', serif", fontWeight: 700 }}>0%</div>
            <div style={{ fontSize: 11 }}>{lang==='zh'?'进口关税':'Import Tariff'}</div>
            <div style={{ fontSize: 10, opacity: 0.6 }}>{lang==='zh'?'2026年5月起':'From May 2026'}</div>
          </div>
        </div>

        {/* WHY RWANDA */}
        <div style={{ marginBottom: 72 }}>
          {secLabel(t.whyTitle)}
          <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(26px, 4vw, 42px)', fontWeight: 700, marginBottom: 36, lineHeight: 1.2 }}>{t.whySub}</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
            {t.whyCards.map((c, i) => (
              <div key={i} style={{ background: '#fff', border: '1px solid #EDE5D8', borderRadius: 6, padding: '28px 24px', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: i===1?'#C9A84C':'#2E5E3A' }} />
                <div style={{ fontSize: 24, marginBottom: 14 }}>{c.icon}</div>
                <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, marginBottom: 10 }}>{c.title}</h3>
                <p style={{ fontSize: 13, color: '#6B5E4A', lineHeight: 1.65 }}>{c.body}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CHANNELS */}
        <div style={{ marginBottom: 72 }}>
          {secLabel(t.channelTitle)}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {CHANNELS.map(c => (
              <div key={c.title} style={{ background: '#fff', border: '1px solid #EDE5D8', borderRadius: 6, padding: '24px 22px' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#2E5E3A', marginBottom: 8 }}>{c.title}</div>
                <p style={{ fontSize: 13, color: '#6B5E4A', lineHeight: 1.6, marginBottom: 14 }}>{c.desc}</p>
                <span style={{ display: 'inline-block', background: 'rgba(46,94,58,0.1)', color: '#2E5E3A', fontSize: 11, fontWeight: 600, padding: '4px 12px', borderRadius: 100 }}>{c.badge}</span>
              </div>
            ))}
          </div>
        </div>

        {/* PRODUCTS */}
        <div style={{ marginBottom: 72 }}>
          {secLabel(t.prodTitle)}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
            {PRODUCTS.map(p => (
              <div key={p.grade} style={{ background: '#fff', border: p.featured ? '2px solid #C9A84C' : '1px solid #EDE5D8', borderRadius: 6, padding: '32px 26px', position: 'relative', boxShadow: p.featured ? '0 4px 24px rgba(201,168,76,0.15)' : 'none' }}>
                {p.featured && <div style={{ position: 'absolute', top: -1, left: 20, background: '#C9A84C', color: '#1A1208', fontSize: 10, fontWeight: 700, padding: '3px 10px', borderRadius: '0 0 4px 4px' }}>Most Popular</div>}
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, fontWeight: 700, marginBottom: 2, marginTop: p.featured ? 14 : 0 }}>{p.grade}</div>
                <div style={{ fontSize: 11, color: '#6B5E4A', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>{p.process} · {p.altitude}</div>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, fontWeight: 700, color: '#2E5E3A', marginBottom: 2 }}>{p.price}</div>
                <div style={{ fontSize: 11, color: '#6B5E4A', marginBottom: 16 }}>{t.pricingSub} · {p.moq} MOQ</div>
                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px' }}>
                  {p.highlights.map(h => <li key={h} style={{ fontSize: 12, color: '#6B5E4A', padding: '4px 0', display: 'flex', gap: 8 }}><span style={{ color: '#2E5E3A', fontWeight: 700 }}>✓</span>{h}</li>)}
                </ul>
                <button onClick={() => setForm(f => ({ ...f, product: p.grade }))}
                  style={{ width: '100%', padding: '9px', background: p.featured ? '#2E5E3A' : 'transparent', color: p.featured ? '#fff' : '#2E5E3A', border: '1px solid #2E5E3A', borderRadius: 4, fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>
                  {lang==='zh'?'选择此产品':'Select'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* LOGISTICS */}
        <div style={{ background: '#fff', borderRadius: 6, padding: 48, marginBottom: 72, border: '1px solid #EDE5D8' }}>
          {secLabel(t.logisticsTitle)}
          <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(22px, 3.5vw, 36px)', fontWeight: 700, marginBottom: 36 }}>{t.logisticsSub}</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 32 }}>
            {LOGISTICS.map(l => (
              <div key={l.step} style={{ textAlign: 'center' }}>
                <div style={{ width: 36, height: 36, background: '#2E5E3A', color: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 14, margin: '0 auto 12px' }}>{l.step}</div>
                <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 6 }}>{l.title}</h4>
                <p style={{ fontSize: 12, color: '#6B5E4A', lineHeight: 1.5 }}>{l.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FORM */}
        <div style={{ background: 'linear-gradient(135deg, #2E5E3A 0%, #1C3A2A 100%)', borderRadius: 8, padding: '56px 52px' }}>
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(26px, 4vw, 40px)', fontWeight: 700, color: '#fff', marginBottom: 10 }}>{t.formTitle}</h2>
            <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: 15 }}>{t.formSub}</p>
          </div>

          {status === 'success' ? (
            <div style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.25)', borderRadius: 6, padding: '24px 32px', textAlign: 'center', color: '#fff', fontSize: 16 }}>{t.formSuccess}</div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {inp(t.formCompany, 'company', 'text', 'e.g. Shanghai Roasters Ltd.')}
              {inp(t.formName, 'name', 'text', 'e.g. Wei Chen')}
              {inp(t.formEmail, 'email', 'email', 'wei@shanghairoasters.cn')}
              {inp(t.formPhone, 'phone', 'text', '+86 / WeChat ID')}

              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.65)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>{t.formProduct} *</label>
                <select value={form.product} onChange={upd('product')} required style={{ padding: '12px 16px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.08)', color: '#fff', fontSize: 14, outline: 'none', appearance: 'none' }}>
                  <option value="" disabled style={{ color: '#1A1208' }}>{lang==='zh'?'选择产品':'Select product'}</option>
                  <option value="Rwanda A1" style={{ color: '#1A1208' }}>Rwanda A1 — Washed</option>
                  <option value="Rwanda A2" style={{ color: '#1A1208' }}>Rwanda A2 — Washed (Most Popular)</option>
                  <option value="Rwanda Premium" style={{ color: '#1A1208' }}>Rwanda Premium — Natural</option>
                  <option value="Multiple / Mixed" style={{ color: '#1A1208' }}>Multiple / Mixed</option>
                </select>
              </div>

              {inp(t.formQuantity, 'quantity', 'text', 'e.g. 5 MT / 10 MT')}

              <div style={{ gridColumn: '1 / -1', display: 'flex', flexDirection: 'column', gap: 6 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.65)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>{t.formMessage}</label>
                <textarea placeholder={lang==='zh'?'告诉我您的烘焙需求、目标市场或问题...':'Tell us about your roasting needs, target market, or questions...'}
                  value={form.message} onChange={upd('message')} rows={4}
                  style={{ padding: '12px 16px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.08)', color: '#fff', fontSize: 14, outline: 'none', resize: 'vertical' }} />
              </div>

              {status === 'error' && <div style={{ gridColumn: '1/-1', color: '#ffb4b4', fontSize: 13 }}>{t.formError}</div>}

              <div style={{ gridColumn: '1 / -1', textAlign: 'center', marginTop: 8 }}>
                <button type="submit" style={{ background: '#C9A84C', color: '#1A1208', fontWeight: 700, fontSize: 14, padding: '14px 52px', borderRadius: 4, border: 'none', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                  📩 {t.formSubmit}
                </button>
                <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, marginTop: 12 }}>Or email ceo@agent.studexmeat.com directly</p>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* FOOTER */}
      <footer style={{ textAlign: 'center', padding: '32px 40px', fontSize: 12, color: '#6B5E4A', borderTop: '1px solid #EDE5D8', background: '#fff' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: 15, color: '#2C2416' }}>{t.footerBrand}</div>
        <div style={{ marginTop: 6 }}>{t.footerLocs}</div>
        <div style={{ marginTop: 10 }}>ceo@agent.studexmeat.com · Rwanda A1/A2 Coffee Export · Effective July 2026</div>
      </footer>
    </div>
  )
}
