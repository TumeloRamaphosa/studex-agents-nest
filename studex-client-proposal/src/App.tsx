import { useEffect } from 'react';

const brand = { charcoal: '#0F0F0F', maroon: '#6B0000', gold: '#C9973A', cream: '#F5EDD8', light: '#F9F4EF', white: '#FFFFFF', terracotta: '#8B3A2F' };

const TIMELINE = [
  { y: '2016', e: 'Studex founded — Tumelo building despite SA banks refusing to bank him' },
  { y: '2018', e: 'World Crypto Economic Forum — Top 20 Start-ups #9, Token Design #11 Overall' },
  { y: '2019', e: 'Forbes "Blockchain Africa Rising" — IBM + Cardano IoT partnership live' },
  { y: '2022', e: 'Expanded into premium halal meat — Moutloe Farm partnership, MJC Halal Trust certified' },
  { y: '2024', e: 'AI launched — Charlie, Naledi & Delivery Agent running 24/7. World Youth Festival Sochi.' },
  { y: '2025', e: 'Fosagro Russia partnership — building the Russia-Africa agricultural trade bridge' },
];

const BIZ = [
  { n: 'Studex Meat', s: 'Active', d: 'Premium halal meat — farm to door, SA nationwide', i: '🥩' },
  { n: 'Studex Wildlife', s: 'Building', d: 'Blockchain conservation platform — protecting rare African species', i: '🦏' },
  { n: 'Studex Caviar', s: 'Building', d: 'Russian caviar import — luxury SA market', i: '🐟' },
  { n: 'Dark Factory', s: 'Building', d: 'Open-core development environment for African tech', i: '⚙️' },
];

const PRODS = [
  { n: 'Wagyu Biltong Gold 500g', o: 'Moutloe Farm, SA', p: 'R549', nt: 'A5 Wagyu · Dry-aged 21 days', tg: 'Bestseller', c: brand.maroon },
  { n: 'Wagyu Biltong Gold 1kg', o: 'Moutloe Farm, SA', p: 'R999', nt: 'Whole piece — premium gifting', tg: 'Popular', c: brand.gold },
  { n: 'Premium Beef Short Ribs', o: 'Moutloe Farm, SA', p: 'R499', nt: 'Dry-aged · Full bloodline', tg: '', c: brand.charcoal },
  { n: 'Fresh Farm Lamb Chops', o: 'Moutloe Farm, SA', p: 'R549', nt: 'Spring lamb · Pasture-raised', tg: '', c: brand.charcoal },
  { n: 'Beef Sausage Bulk', o: 'Moutloe Farm, SA', p: 'R399', nt: 'Traditional boerewors', tg: '', c: brand.charcoal },
  { n: 'Ankole Heritage Beef', o: 'Coming Soon', p: 'TBC', nt: 'East African heritage breed', tg: 'New', c: brand.terracotta },
];

const MEDIA = [
  { n: 'Sputnik Africa', q: 'Trade is the cornerstone of Russia-Africa relations. Studex is proud to bridge African agricultural excellence with Russian market opportunity.', a: '— Tumelo Ramaphosa, World Youth Festival Sochi' },
  { n: 'Forbes Africa', q: 'Studex tokenizes African wildlife — allowing global investors to fund conservation while owning fractional shares of rare animals, tracked on-chain via IBM and Cardano.', a: '"Blockchain Africa Rising", 2019' },
];

function SH({ icon, title }: { icon: string; title: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 40 }}>
      <span style={{ fontSize: 28 }}>{icon}</span>
      <h2 style={{ fontFamily: "'Georgia',serif", fontSize: 'clamp(1.5rem,3vw,2.2rem)', color: brand.charcoal, borderBottom: `3px solid ${brand.gold}`, paddingBottom: 8, margin: 0, fontWeight: 700, letterSpacing: '-0.01em' }}>{title}</h2>
    </div>
  );
}

export default function App() {
  useEffect(() => { window.scrollTo(0, 0); }, []);
  return (
    <div style={{ background: brand.cream, minHeight: '100vh', fontFamily: "'Georgia',serif", color: brand.charcoal }}>

      {/* NAV */}
      <nav style={{ background: 'rgba(15,15,15,0.97)', backdropFilter: 'blur(12px)', padding: '0 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000, boxShadow: '0 2px 24px rgba(0,0,0,0.5)', height: 68 }}>
        <img src="/studex-logo-stamp.png" alt="Studex" style={{ height: 44, objectFit: 'contain' }} />
        <div style={{ display: 'flex', gap: 28 }}>
          {['Our Story','Biltong','Certificate','Products','Conservation','Contact'].map(l => (
            <a key={l} href={`#${l.toLowerCase()}`} style={{ color: '#888', textDecoration: 'none', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.12em', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>{l}</a>
          ))}
        </div>
        <a href="#contact" style={{ background: brand.gold, color: brand.charcoal, padding: '8px 20px', borderRadius: 3, fontWeight: 700, textDecoration: 'none', fontFamily: 'system-ui,sans-serif', fontSize: '0.75rem', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Order Now</a>
      </nav>

      {/* HERO */}
      <section style={{
        background: `radial-gradient(ellipse at 20% 50%, rgba(201,151,58,0.18) 0%, transparent 55%), radial-gradient(ellipse at 80% 20%, rgba(107,0,0,0.12) 0%, transparent 50%), radial-gradient(ellipse at 60% 80%, rgba(201,151,58,0.08) 0%, transparent 45%), #0F0F0F`,
        minHeight: '100vh', paddingTop: 68, display: 'flex', alignItems: 'center', position: 'relative', overflow: 'hidden'
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 48px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center', width: '100%' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(201,151,58,0.12)', border: `1px solid rgba(201,151,58,0.4)`, borderRadius: 40, padding: '7px 18px', marginBottom: 28 }}>
              <span style={{ fontSize: '0.9rem' }}>☪</span>
              <span style={{ color: brand.gold, fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.78rem', letterSpacing: '0.12em', textTransform: 'uppercase' }}>100% Halal Certified · 10 Years Building</span>
            </div>
            <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.82rem', letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(201,151,58,0.7)', marginBottom: 16 }}>
              Studex Group · South Africa
            </div>
            <h1 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(2.8rem,5.5vw,4.8rem)', lineHeight: 1.0, letterSpacing: '-0.03em', color: brand.white, marginBottom: 8 }}>
              Built From the
            </h1>
            <h1 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(2.8rem,5.5vw,4.8rem)', lineHeight: 1.0, letterSpacing: '-0.03em', marginBottom: 8 }}>
              <span style={{ color: brand.gold }}>Ankole's</span>
            </h1>
            <h1 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(2.8rem,5.5vw,4.8rem)', lineHeight: 1.0, letterSpacing: '-0.03em', color: brand.white }}>
              Horns Up.
            </h1>
            <p style={{ color: '#999', fontSize: '1.05rem', lineHeight: 1.85, fontWeight: 300, maxWidth: 520, marginTop: 20, marginBottom: 16, fontFamily: 'system-ui,sans-serif' }}>
              The Ankole — "cow of kings" — majestic horns, enormous stature, the most valuable cattle in Africa. Tumelo Ramaphosa's family bred them. He built Studex to trade that African wealth with the world.
            </p>
            <p style={{ color: '#777', fontSize: '0.9rem', lineHeight: 1.7, fontWeight: 300, maxWidth: 520, marginBottom: 36, fontFamily: 'system-ui,sans-serif', fontStyle: 'italic' }}>
              "They called me a financial nuclear weapon. SA banks wouldn't touch me. So I built with blockchain, AI, and conviction." — Tumelo Ramaphosa
            </p>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              <a href="#biltong" style={{ background: brand.gold, color: brand.charcoal, padding: '14px 32px', borderRadius: 3, fontWeight: 700, textDecoration: 'none', fontFamily: 'system-ui,sans-serif', fontSize: '0.88rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Explore Biltong</a>
              <a href="#conservation" style={{ border: `1px solid rgba(201,151,58,0.5)`, color: brand.gold, padding: '14px 32px', borderRadius: 3, textDecoration: 'none', fontFamily: 'system-ui,sans-serif', fontSize: '0.88rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>See the Vision</a>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', position: 'relative' }}>
            <div style={{ width: '100%', maxWidth: 440, aspectRatio: '3/4', borderRadius: 16, overflow: 'hidden', border: `2px solid rgba(201,151,58,0.4)`, boxShadow: '0 32px 80px rgba(0,0,0,0.6)', position: 'relative' }}>
              <img src="/tumelo-baby.jpg" alt="Tumelo Ramaphosa — Studex Founder" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 55%)' }} />
              <div style={{ position: 'absolute', bottom: 16, left: 16, right: 16 }}>
                <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: '0.95rem', color: brand.gold, marginBottom: 2 }}>Tumelo Ramaphosa</div>
                <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.72rem', color: '#ccc', letterSpacing: '0.06em' }}>Founder & CEO · 10 Years Building Through Every Barrier</div>
              </div>
            </div>
            <div style={{ position: 'absolute', top: -12, right: -12, background: brand.gold, color: brand.charcoal, padding: '10px 16px', borderRadius: 8, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.7rem', letterSpacing: '0.1em', textTransform: 'uppercase', boxShadow: '0 8px 24px rgba(201,151,58,0.4)' }}>
              ☪ Halal Certified
            </div>
          </div>
        </div>
      </section>

      {/* STATS BAR */}
      <section style={{ background: 'rgba(15,15,15,0.95)', borderTop: `1px solid rgba(201,151,58,0.2)`, borderBottom: `1px solid rgba(201,151,58,0.2)`, padding: '28px 48px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 24 }}>
          {[{ n: '10+', l: 'Years Building' }, { n: '100%', l: 'Halal Certified' }, { n: 'Top 20', l: 'SA Stud Breeders' }, { n: '24/7', l: 'AI Agents Live' }, { n: '#9', l: 'WCEF Start-ups 2018' }, { n: 'Fosagro', l: 'Russia Partner' }].map(x => (
            <div key={x.l} style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: "'Georgia',serif", fontSize: 'clamp(1.4rem,2.5vw,2rem)', fontWeight: 700, color: brand.gold }}>{x.n}</div>
              <div style={{ color: '#777', fontSize: '0.72rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300, letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: 4 }}>{x.l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* OUR STORY — ANKOLE BRAND STORY */}
      <section id="our-story" style={{ padding: '100px 48px', maxWidth: 1200, margin: '0 auto', background: brand.white }}>
        <SH icon="📖" title="Our Story — Ankole, Wealth & The Trade Bridge" />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 72, alignItems: 'start' }}>
          <div>
            <p style={{ color: '#333', lineHeight: 1.95, fontSize: '1.05rem', fontWeight: 300, marginBottom: 20 }}>In African heritage, the <strong>Ankole</strong> is not just a cow — it is wealth stored in horns and stature. Known as the "cow of kings," the Ankole carries enormous horns that sweep wide as a gateway and a body built for the harshest African climates. A single Ankole bull can be worth millions. A herd is a treasury.</p>
            <p style={{ color: '#333', lineHeight: 1.95, fontSize: '1.05rem', fontWeight: 300, marginBottom: 20 }}><strong>Stud</strong> — a premium Ankole breeding animal, carefully selected and prized. <strong>Ex</strong> — exchange. Global trade of African heritage and wealth, shared with the world. The name says exactly what Tumelo Ramaphosa built.</p>
            <p style={{ color: '#333', lineHeight: 1.95, fontSize: '1.05rem', fontWeight: 300, marginBottom: 20 }}>His family's farm is ranked among the <strong>top 20 stud game breeding operations in South Africa</strong>. Tumelo took that — the Ankole, the heritage, the wealth stored in African wildlife — and built a company that could trade it globally.</p>
            <p style={{ color: '#333', lineHeight: 1.95, fontSize: '1.05rem', fontWeight: 300, marginBottom: 32 }}>South African banks called him a <strong>"financial nuclear weapon"</strong> and refused to open business accounts. He pivoted to crypto and blockchain as infrastructure. He built anyway. Ten years in, Studex is still standing — and still building.</p>
            <div style={{ background: `rgba(201,151,58,0.08)`, border: `1px solid rgba(201,151,58,0.25)`, borderLeft: `4px solid ${brand.gold}`, padding: '20px 24px', borderRadius: 4 }}>
              <p style={{ fontFamily: "'Georgia',serif", fontStyle: 'italic', color: brand.charcoal, fontSize: '1rem', marginBottom: 10 }}>"With AI anything is fathomable. I persevered because the vision was bigger than the obstacles."</p>
              <p style={{ color: brand.gold, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>— Tumelo Ramaphosa, Founder</p>
            </div>
          </div>
          <div>
            <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.78rem', color: '#888', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 24 }}>The Journey</div>
            {TIMELINE.map((m, i) => {
              const isLast = i === TIMELINE.length - 1;
              return (
                <div key={i} style={{ display: 'flex', gap: 20, alignItems: 'stretch' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 56 }}>
                    <div style={{ background: isLast ? brand.gold : brand.charcoal, color: isLast ? brand.charcoal : brand.gold, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.78rem', padding: '6px 10px', borderRadius: 4, textAlign: 'center', flexShrink: 0, minWidth: 56 }}>{m.y}</div>
                    {i < TIMELINE.length - 1 && <div style={{ width: 1, flex: 1, minHeight: 24, background: `rgba(201,151,58,0.3)`, margin: '4px auto' }} />}
                  </div>
                  <div style={{ paddingBottom: 24, paddingTop: 4 }}>
                    <div style={{ fontFamily: 'system-ui,sans-serif', fontSize: '0.9rem', color: '#333', lineHeight: 1.5, fontWeight: isLast ? 500 : 300 }}>{m.e}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* BILTONG HERO */}
      <section id="biltong" style={{ background: brand.charcoal, padding: '100px 48px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 72, alignItems: 'center' }}>
          <div>
            <div style={{ color: brand.gold, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.78rem', letterSpacing: '0.18em', textTransform: 'uppercase', marginBottom: 16 }}>Flagship Product · ☪ Halal Certified</div>
            <h2 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(2.5rem,4vw,3.8rem)', color: brand.white, lineHeight: 1.05, letterSpacing: '-0.02em', marginBottom: 8 }}>Wagyu Biltong</h2>
            <h2 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(2.5rem,4vw,3.8rem)', color: brand.gold, lineHeight: 1.05, letterSpacing: '-0.02em', marginBottom: 28 }}>Gold</h2>
            <p style={{ color: '#aaa', lineHeight: 1.85, fontSize: '1rem', fontWeight: 300, marginBottom: 32, maxWidth: 480 }}>A5 Wagyu beef. Dry-aged for 21 days. Slow-cured in the traditional South African biltong style. Japanese genetics. South African craft. From the same bloodlines that produced the Ankole — the most valuable cattle on the continent.</p>
            <div style={{ display: 'flex', gap: 16, marginBottom: 36, flexWrap: 'wrap' }}>
              {[{ l: '500g', p: 'R549' }, { l: '1kg', p: 'R999' }].map(x => (
                <div key={x.l} style={{ background: '#1e1e1e', border: `1px solid rgba(201,151,58,0.2)`, borderRadius: 6, padding: '14px 24px' }}>
                  <div style={{ fontFamily: "'Georgia',serif", fontSize: '1.5rem', fontWeight: 700, color: brand.gold }}>{x.l} — {x.p}</div>
                </div>
              ))}
            </div>
            {['A5 Wagyu beef — dry-aged 21 days under controlled conditions','Traditional South African biltong cure — slow, dry, natural','☪ Halal certified — every batch verified','Full farm provenance on every package','Ankole-influenced genetics — African heritage on every plate'].map((f, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                <div style={{ width: 5, height: 5, borderRadius: '50%', background: brand.gold, flexShrink: 0 }} />
                <span style={{ color: '#ccc', fontFamily: 'system-ui,sans-serif', fontSize: '0.9rem', fontWeight: 300 }}>{f}</span>
              </div>
            ))}
          </div>
          <div style={{ borderRadius: 16, overflow: 'hidden', border: `1px solid rgba(201,151,58,0.3)`, boxShadow: '0 24px 64px rgba(0,0,0,0.5)', position: 'relative' }}>
            <img src="/halal-cert.jpg" alt="Studex Halal Certificate" style={{ width: '100%', aspectRatio: '4/3', objectFit: 'cover', display: 'block' }} />
            <div style={{ position: 'absolute', top: 16, left: 16, background: brand.gold, color: brand.charcoal, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.7rem', padding: '5px 14px', borderRadius: 20, textTransform: 'uppercase', letterSpacing: '0.08em' }}>☪ MJC Halal Trust</div>
            <div style={{ position: 'absolute', bottom: 16, right: 16, background: brand.maroon, color: brand.gold, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.68rem', padding: '5px 14px', borderRadius: 20, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Studex Brand · HT 4606</div>
          </div>
        </div>
      </section>

      {/* HALAL CERTIFICATE */}
      <section id="certificate" style={{ padding: '100px 48px', background: `linear-gradient(180deg,${brand.charcoal} 0%,#0a0505 100%)` }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: 28 }}>☪</span>
            <h2 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(1.6rem,3vw,2.4rem)', color: brand.gold, borderBottom: `3px solid ${brand.gold}`, paddingBottom: 8, letterSpacing: '-0.02em' }}>Halal Certification</h2>
          </div>
          <p style={{ color: '#888', fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '1rem', maxWidth: 680, marginBottom: 48, lineHeight: 1.7 }}>All Studex products are certified halal by the <strong style={{ color: brand.gold }}>MJC Halaal Trust</strong> — South Africa's most trusted Islamic certification body, established 1945.</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, alignItems: 'start' }}>
            <div style={{ background: brand.white, borderRadius: 12, overflow: 'hidden', boxShadow: '0 8px 40px rgba(0,0,0,0.4)', border: `2px solid rgba(201,151,58,0.3)` }}>
              <img src="/halal-cert.jpg" alt="Studex MJC Halaal Certificate" style={{ width: '100%', height: 'auto', display: 'block' }} />
              <div style={{ background: brand.charcoal, padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#aaa', fontSize: '0.78rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>MJC Halaal Trust — EST. 1945</span>
                <span style={{ color: brand.gold, fontSize: '0.78rem', fontFamily: 'system-ui,sans-serif', fontWeight: 600 }}>HT 4606 · Studex Brand</span>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div style={{ background: '#1a1a1a', borderRadius: 10, padding: '24px', border: `1px solid rgba(201,151,58,0.2)` }}>
                <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 600, color: brand.gold, marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '0.78rem' }}>Certificate Details</div>
                {[['Issuing Authority','MJC Halaal Trust'],['Certificate No.','HT 4606'],['Company','Cape Deli — Studex Brand'],['Address','34 Shiraz Road, Saxenburg Park 1, Blackheath'],['Valid','Active — Annually Renewed']].map(([k,v]) => (
                  <div key={k} style={{ display: 'flex', gap: 12, marginBottom: 10, borderBottom: '1px solid #2a2a2a', paddingBottom: 10 }}>
                    <span style={{ color: '#666', fontSize: '0.82rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300, minWidth: 150 }}>{k}</span>
                    <span style={{ color: '#eee', fontSize: '0.82rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>{v}</span>
                  </div>
                ))}
              </div>
              <div style={{ background: '#1a1a1a', borderRadius: 10, padding: '24px', border: `1px solid rgba(201,151,58,0.2)` }}>
                <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 600, color: brand.gold, marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '0.78rem' }}>Certified Products</div>
                {['Wagyu Droewors','Wagyu Biltong Original','Wagyu Snapsticks Chilli','Wagyu Snapsticks Original'].map((p,i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <div style={{ width: 5, height: 5, borderRadius: '50%', background: brand.gold }} />
                    <span style={{ color: '#ddd', fontSize: '0.88rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>{p}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PRODUCTS */}
      <section id="products" style={{ padding: '100px 48px', background: brand.light }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <SH icon="🥩" title="Products & Pricing" />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: 24 }}>
            {PRODS.map((p, i) => (
              <div key={i} style={{ background: brand.white, borderRadius: 10, boxShadow: '0 2px 20px rgba(0,0,0,0.08)', overflow: 'hidden', position: 'relative' }}>
                {p.tg && <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 1 }}><span style={{ background: p.tg === 'New' ? brand.terracotta : brand.gold, color: p.tg === 'New' ? brand.white : brand.charcoal, fontSize: '0.65rem', fontWeight: 700, padding: '3px 10px', borderRadius: 20, textTransform: 'uppercase', letterSpacing: '0.05em', fontFamily: 'system-ui,sans-serif' }}>{p.tg}</span></div>}
                <div style={{ height: 5, background: p.c }} />
                <div style={{ padding: '22px 24px' }}>
                  <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: '1.1rem', color: brand.charcoal, marginBottom: 4 }}>{p.n}</div>
                  <div style={{ color: '#888', fontSize: '0.78rem', fontFamily: 'system-ui,sans-serif', marginBottom: 6, fontWeight: 300 }}>{p.o}</div>
                  <div style={{ color: '#666', fontSize: '0.82rem', fontFamily: 'system-ui,sans-serif', marginBottom: 16, fontStyle: 'italic', fontWeight: 300 }}>{p.nt}</div>
                  <div style={{ fontFamily: "'Georgia',serif", fontSize: '1.8rem', fontWeight: 700, color: brand.maroon }}>{p.p}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* STUDEX WILDLIFE — CONSERVATION / BLOCKCHAIN */}
      <section id="conservation" style={{ padding: '100px 48px', background: brand.charcoal }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: 28 }}>🦏</span>
            <h2 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(1.6rem,3vw,2.4rem)', color: brand.gold, borderBottom: `3px solid ${brand.gold}`, paddingBottom: 8, letterSpacing: '-0.02em' }}>Studex Wildlife — Blockchain Conservation</h2>
          </div>
          <p style={{ color: '#888', fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '1rem', maxWidth: 720, marginBottom: 48, lineHeight: 1.7 }}>Conceived as Tumelo Ramaphosa's Master's thesis at <strong style={{ color: brand.gold }}>Hult International Business School</strong> — a blockchain platform to protect Africa's most endangered species by turning conservation into a globally investable asset class.</p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, marginBottom: 48 }}>
            {[
              { t: 'Fractional Ownership', d: 'Each rare animal\'s value is divided into tradable shares. Global investors own a fraction — with IoT-verified proof of the living asset.' },
              { t: 'On-Chain Tracking', d: 'IBM + Cardano blockchain partnership. IoT sensors track location, heart rate, activity — all recorded immutably on-chain.' },
              { t: 'Anti-Poaching Drones', d: 'LoRa network + drone surveillance covers vast land. Real-time alerts. Minimal human contact. Animals live naturally.' },
              { t: 'ERC-721 + ERC-20 Tokens', d: 'Whole animal NFTs or fractional ERC-20 shares. Token holders own the likeness and conservation value of their animal.' },
            ].map((item, i) => (
              <div key={i} style={{ background: '#1a1a1a', border: `1px solid rgba(201,151,58,0.15)`, borderRadius: 10, padding: '24px' }}>
                <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: '1rem', color: brand.gold, marginBottom: 10 }}>{item.t}</div>
                <div style={{ color: '#999', fontSize: '0.88rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300, lineHeight: 1.7 }}>{item.d}</div>
              </div>
            ))}

          </div>

          {/* Forum banner */}
          <div style={{ background: 'linear-gradient(135deg, rgba(201,151,58,0.15) 0%, rgba(107,0,0,0.1) 100%)', border: `1px solid rgba(201,151,58,0.3)`, borderRadius: 10, padding: '28px 36px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 24 }}>
            <div>
              <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.78rem', color: brand.gold, textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 6 }}>2018 World Crypto Economic Forum</div>
              <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(1.2rem,2vw,1.8rem)', color: brand.white, letterSpacing: '-0.02em' }}>Top 20 Start-ups #9 · Token Design #11 Overall</div>
              <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.85rem', color: '#999', marginTop: 6 }}>Forbes "Blockchain Africa Rising" · IBM + Cardano Partnership</div>
            </div>
            <a href="#contact" style={{ background: brand.gold, color: brand.charcoal, padding: '12px 28px', borderRadius: 4, fontWeight: 700, textDecoration: 'none', fontFamily: 'system-ui,sans-serif', fontSize: '0.85rem', letterSpacing: '0.08em', textTransform: 'uppercase', flexShrink: 0 }}>Invest in Conservation</a>
          </div>
        </div>
      </section>

      {/* RUSSIA-AFRICA TRADE */}
      <section style={{ padding: '100px 48px', background: brand.cream }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: 28 }}>🌍</span>
            <h2 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(1.6rem,3vw,2.4rem)', color: brand.charcoal, borderBottom: `3px solid ${brand.gold}`, paddingBottom: 8, letterSpacing: '-0.02em' }}>Russia–Africa Trade Bridge</h2>
          </div>
          <p style={{ color: '#555', fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '1rem', maxWidth: 720, marginBottom: 48, lineHeight: 1.7 }}>At the World Youth Festival in Sochi, Tumelo announced Studex as the official African partner for <strong>Fosagro</strong> — Russia's largest fertilizer company. His uncles sought exile in Russia during the liberation struggle. Now he is building the trade bridge between the two countries.</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40, marginBottom: 40 }}>
            {MEDIA.map((m, i) => (
              <div key={i} style={{ background: brand.white, border: `1px solid rgba(201,151,58,0.2)`, borderRadius: 10, padding: '28px', position: 'relative' }}>
                <div style={{ position: 'absolute', top: -12, left: 24, background: brand.gold, color: brand.charcoal, fontFamily: 'system-ui,sans-serif', fontWeight: 700, fontSize: '0.72rem', padding: '3px 12px', borderRadius: 20, textTransform: 'uppercase', letterSpacing: '0.1em' }}>{m.n}</div>
                <p style={{ fontFamily: "'Georgia',serif", fontStyle: 'italic', color: '#444', fontSize: '0.95rem', lineHeight: 1.7, marginBottom: 14, marginTop: 4 }}>"{m.q}"</p>
                <p style={{ color: brand.gold, fontFamily: 'system-ui,sans-serif', fontWeight: 600, fontSize: '0.75rem', letterSpacing: '0.06em' }}>{m.a}</p>
              </div>
            ))}
          </div>
          <div style={{ background: `rgba(201,151,58,0.08)`, border: `1px solid rgba(201,151,58,0.2)`, borderRadius: 10, padding: '24px 32px', display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: '1.1rem', color: brand.charcoal, marginBottom: 4 }}>Studex × Fosagro Partnership</div>
              <div style={{ fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '0.88rem', color: '#666' }}>Russian fertilizer to African farms · South African biltong to Russian markets</div>
            </div>
          </div>
        </div>
      </section>

      {/* BUSINESS UNITS */}
      <section style={{ padding: '100px 48px', background: brand.white }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <SH icon="🏛️" title="The Studex Group" />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(260px,1fr))', gap: 20 }}>
            {BIZ.map((b, i) => (
              <div key={i} style={{ background: brand.cream, borderRadius: 10, padding: '24px', boxShadow: '0 2px 16px rgba(0,0,0,0.06)', borderTop: `4px solid ${b.s === 'Active' ? brand.gold : '#aaa'}` }}>
                <div style={{ fontSize: '2rem', marginBottom: 12 }}>{b.i}</div>
                <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: '1.05rem', color: brand.charcoal, marginBottom: 4 }}>{b.n}</div>
                <div style={{ fontSize: '0.7rem', fontFamily: 'system-ui,sans-serif', fontWeight: b.s === 'Active' ? 700 : 300, color: b.s === 'Active' ? '#2a7a2a' : '#888', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>{b.s}</div>
                <div style={{ color: '#666', fontSize: '0.85rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>{b.d}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FARMS */}
      <section style={{ padding: '100px 48px', background: brand.light }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <SH icon="🏔️" title="Our Farm Network" />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 24 }}>
            {[
              { n: 'Moutloe Farm', l: 'South Africa', s: 'Wagyu, Lamb, Premium Beef', c: brand.maroon },
              { n: 'Silent Valley', l: 'The Willows, Pretoria', s: 'Fresh Cuts, Ankole Heritage Breeding', c: brand.gold },
              { n: 'Noags Butchery', l: 'Kempton Park', s: 'Bulk Orders', c: brand.charcoal },
            ].map((f, i) => (
              <div key={i} style={{ background: brand.white, borderRadius: 8, padding: '28px 24px', borderTop: `4px solid ${f.c}` }}>
                <div style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: '1.15rem', color: brand.charcoal, marginBottom: 8 }}>{f.n}</div>
                <div style={{ color: brand.gold, fontSize: '0.78rem', fontFamily: 'system-ui,sans-serif', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>{f.l}</div>
                <div style={{ color: '#666', fontSize: '0.9rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>{f.s}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CONTACT */}
      <section id="contact" style={{ background: `linear-gradient(160deg,${brand.maroon} 0%,${brand.charcoal} 100%)`, padding: '100px 48px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -100, right: -100, width: 500, height: 500, borderRadius: '50%', border: `1px solid rgba(201,151,58,0.08)` }} />
        <div style={{ maxWidth: 700, margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <img src="/studex-logo-stamp.png" alt="Studex" style={{ height: 80, objectFit: 'contain', marginBottom: 32, filter: 'brightness(0) invert(1)', borderRadius: '50%' }} />
          <h2 style={{ fontFamily: "'Georgia',serif", fontWeight: 700, fontSize: 'clamp(2rem,4vw,3.2rem)', color: brand.white, marginBottom: 16, letterSpacing: '-0.02em' }}>Ready to Taste the Difference?</h2>
          <p style={{ color: 'rgba(255,200,200,0.7)', fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '1rem', marginBottom: 12 }}>☪ 100% Halal Certified &nbsp;|&nbsp; 10 Years Building &nbsp;|&nbsp; Blockchain Conservation &nbsp;|&nbsp; Russia-Africa Trade</p>
          <p style={{ color: '#bbb', fontFamily: 'system-ui,sans-serif', fontWeight: 300, fontSize: '1rem', marginBottom: 40 }}>studexmeat.com &nbsp;|&nbsp; Nationwide Delivery</p>
          <div style={{ display: 'flex', gap: 20, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="https://studexmeat.com" style={{ background: brand.gold, color: brand.charcoal, padding: '14px 36px', borderRadius: 4, fontWeight: 700, textDecoration: 'none', fontFamily: 'system-ui,sans-serif', fontSize: '0.9rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>studexmeat.com</a>
            <a href="mailto:orders@studexmeat.com" style={{ border: `1px solid rgba(201,151,58,0.5)`, color: brand.gold, padding: '14px 36px', borderRadius: 4, textDecoration: 'none', fontFamily: 'system-ui,sans-serif', fontSize: '0.9rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>orders@studexmeat.com</a>
          </div>
          <div style={{ marginTop: 60, color: 'rgba(255,255,255,0.25)', fontSize: '0.75rem', fontFamily: 'system-ui,sans-serif', fontWeight: 300 }}>© 2026 Studex Meat (Pty) Ltd · All Rights Reserved · ☪ Halal Certified</div>
        </div>
      </section>

    </div>
  );
}
