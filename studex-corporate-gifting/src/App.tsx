// ✅ CAVIAR-FREE SINCE 2026-10-30 — the 2026 festive proposition is biltong +
// single-origin African coffee + packaging + delivery.
//
// The SA caviar permit stack (DFFE → ITAC frozen-fish notification → DAFF importer
// registration → SARS importer code + duty line → NRCS → CITES export permit +
// registered exporter code) is UNASSEMBLED. Selling caviar into SA without it is
// a seizure risk, and a first shipment could not land inside the 13–15 Nov festive
// window even if the stack moved fast.
//
// The tiers and every compliance claim now come from ./tiers.compliant.tsx — one
// owning source, caviar-free, re-priced against the public SA hamper market
// (R199.95–R720). Do not inline a tier or a claim here: a second copy is a second
// ladder, and a claim with no owning source is not a claim.
//
// The live page (oi28dhtke3yk) still shows the older caviar-free
// R1,299 / R2,499 / R4,999 build — LEAVE IT LIVE until Tumelo signs off on this
// ladder and on the deploy. Building this source publishes nothing: the deploy is
// a separate, deliberate step.
//
// Guards: ops/price-ladder-guard.py (live pages) ·
//         ops/check-caviar-in-retail-source.py (this source)
import { useState } from "react";
import { TIERS_COMPLIANT as TIERS, COMPLIANT_COPY } from "./tiers.compliant";

const INQUIRIES = [
  "Corporate bulk order (10+ boxes)",
  "Custom branded packaging",
  "Quarterly gifting program",
  "One-time event order",
  "B2B coffee supply inquiry",
];

function App() {
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [inquiryType, setInquiryType] = useState("");
  const [company, setCompany] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      // NO API KEY IN THE BROWSER. See studex-lead-proxy/src/worker.js.
      const res = await fetch(import.meta.env.VITE_LEAD_PROXY_URL || "https://studex-lead-proxy.tumelor001.workers.dev", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "Corporate Gifting Landing",
          name,
          company,
          email,
          phone,
          message,
          tierInterest: selectedTier,
          inquiryType,
        }),
      });
      if (!res.ok) throw new Error("lead proxy rejected the request");
      setSubmitted(true);
    } catch (_) {
      // Do NOT fake success - that hides a lost lead.
      setError("Could not send your enquiry. Please email info@studexmeat.com and we will pick it up.");
    }
    setSubmitting(false);
  };

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-logo">
          <span className="logo-mark">&#9670;</span>
          <span className="logo-text">STUDEX</span>
          <span className="logo-sub">CORPORATE</span>
        </div>
        <div className="nav-links">
          <a href="#tiers">Gift Boxes</a>
          <a href="#story">Our Story</a>
          <a href="#contact">Inquire</a>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-eyebrow">South Africa&#39;s Premier Corporate Gifting House</div>
        <h1 className="hero-title">Gift the <span className="accent">African Story</span></h1>
        <p className="hero-sub">{COMPLIANT_COPY.heroSub}</p>
        <div className="hero-badges">
          <span>&#x1F98C; Heritage Wagyu Biltong</span>
          <span>{COMPLIANT_COPY.heroBadge}</span>
          <span>&#x1F30D; African Coffee</span>
          <span>&#x1F4E6; Nationwide Delivery</span>
        </div>
        <a href="#contact" className="btn-primary">Request a Custom Quote</a>
      </section>

      <section className="proof-bar">
        <div className="proof-item"><div className="proof-num">R12B+</div><div className="proof-label">SA corporate gifting market (annual)</div></div>
        <div className="proof-divider" />
        <div className="proof-item"><div className="proof-num">22%</div><div className="proof-label">YoY growth in food &amp; drink corporate gifting</div></div>
        <div className="proof-divider" />
        <div className="proof-item"><div className="proof-num">{TIERS[0].price}&ndash;{TIERS[TIERS.length - 1].price}</div><div className="proof-label">Per-box price range across {TIERS.length} tiers</div></div>
        <div className="proof-divider" />
        <div className="proof-item"><div className="proof-num">0</div><div className="proof-label">SA competitors in this white space</div></div>
      </section>

      <section className="social-strip">
        <p className="social-label">Trusted by SA&#39;s leading firms:</p>
        <div className="social-names">
          <span>Standard Bank</span>
          <span>&#xb7;</span>
          <span>Anglo American</span>
          <span>&#xb7;</span>
          <span>Webber Wentzel</span>
          <span>&#xb7;</span>
          <span>Mount Grace Country House</span>
          <span>&#xb7;</span>
          <span>SA Wine Partners</span>
        </div>
      </section>

      <section className="problem">
        <h2 className="section-title">Generic Hampers Don&#39;t Close Deals</h2>
        <div className="problem-grid">
          <div className="problem-card">
            <div className="problem-icon">&#x1F615;</div>
            <h3>Same Old, Same Old</h3>
            <p>Every law firm and bank sends the same branded hampers. Your gift disappears into a pile of identical ones. Zero lasting impression.</p>
          </div>
          <div className="problem-card">
            <div className="problem-icon">&#x1F69A;</div>
            <h3>Logistics Nightmares</h3>
            <p>Coordinating delivery to multiple offices, executives&#39; homes, or event venues is a coordination nightmare for your PA team.</p>
          </div>
          <div className="problem-card">
            <div className="problem-icon">&#x1F3FA;</div>
            <h3>No Story to Tell</h3>
            <p>Imported chocolates and wine have no provenance. Your clients don&#39;t remember who sent it. Studex gifts tell the African story.</p>
          </div>
        </div>
      </section>

      <section className="tiers" id="tiers">
        <h2 className="section-title">Choose Your Tier</h2>
        <p className="section-sub">Each box crafted to impress. Prices exclude VAT. Custom branding available from Gold tier.</p>
        <div className="tiers-grid">
          {TIERS.map((tier) => (
            <div
              key={tier.name}
              className={"tier-card " + (tier.featured ? "featured" : "")}
              style={{ "--tier-color": tier.color } as React.CSSProperties}
            >
              {tier.featured && <div className="tier-badge">Most Popular</div>}
              <div className="tier-name" style={{ color: tier.color }}>{tier.name}</div>
              <div className="tier-price">{tier.price}</div>
              <div className="tier-tagline">{tier.tagline}</div>
              <ul className="tier-items">
                {tier.items.map((item) => <li key={item}>+ {item}</li>)}
              </ul>
              <div className="tier-best-for">Best for: {tier.bestFor}</div>
              <button
                className="tier-cta"
                style={{ borderColor: tier.color, color: tier.color }}
                onClick={() => { setSelectedTier(tier.name); document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" }); }}
              >
                Select {tier.name}
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="difference" id="story">
        <h2 className="section-title">Why Studex?</h2>
        <div className="diff-grid">
          <div className="diff-item">
            <div className="diff-icon">&#x1F98C;</div>
            <h3>Heritage Wagyu Biltong</h3>
            <p>Slow-dried for 30 days. No shortcuts. Our biltong is hung, not baked &#8212; the way biltong was meant to be made.</p>
          </div>
          <div className="diff-item">
            <div className="diff-icon">&#x1F4CA;</div>
            <h3>{COMPLIANT_COPY.featureHeading}</h3>
            <p>{COMPLIANT_COPY.featureBody}</p>
          </div>
          <div className="diff-item">
            <div className="diff-icon">&#x1F30D;</div>
            <h3>Pan-African Coffee</h3>
            <p>Ethiopia, Rwanda, Kenya, South Africa &#8212; we source direct from small-holder farmers with a story to tell.</p>
          </div>
          <div className="diff-item">
            <div className="diff-icon">&#x1F4E6;</div>
            <h3>White-Glove Logistics</h3>
            <p>Temperature-controlled delivery, same-day dispatch, tracking on every box. 1 address or 100 &#8212; same care, zero headache.</p>
          </div>
        </div>
      </section>

      <section className="process">
        <h2 className="section-title">How It Works</h2>
        <div className="process-steps">
          <div className="step"><div className="step-num">01</div><div className="step-content"><h3>Inquire</h3><p>Tell us your budget, quantity, and delivery addresses. We respond within 2 business hours.</p></div></div>
          <div className="step-arrow">-&gt;</div>
          <div className="step"><div className="step-num">02</div><div className="step-content"><h3>Curate</h3><p>We build your custom quote with box configuration, branding options, and delivery schedule.</p></div></div>
          <div className="step-arrow">-&gt;</div>
          <div className="step"><div className="step-num">03</div><div className="step-content"><h3>Present</h3><p>We craft, gift-wrap, and deliver. You receive a tracking dashboard and photographic proof of delivery.</p></div></div>
        </div>
      </section>

      <section className="contact" id="contact">
        <div className="contact-inner">
          <div className="contact-left">
            <h2 className="section-title" style={{textAlign:"left"}}>Let&#39;s Build Your Gift Program</h2>
            <p>Average response time: <strong>2 business hours</strong>. We work with procurement teams, EAs, and direct executives.</p>
            <div className="contact-features">
              <div>+ Net 30 payment terms available (Gold + Platinum)</div>
              <div>+ Custom branding from 10+ units</div>
              <div>+ Quarterly retainer programs available</div>
              <div>+ NDA available on request</div>
            </div>
            <div className="contact-email">Or email directly: <a href="mailto:info@studexmeat.com">info@studexmeat.com</a></div>
          </div>
          <div className="contact-right">
            {submitted ? (
              <div className="success-card">
                <div className="success-icon">OK</div>
                <h3>Inquiry Received</h3>
                <p>Thank you, {name}. We&#39;ll be in touch within 2 business hours.</p>
                <p className="success-email">A confirmation has been sent to {email}</p>
              </div>
            ) : (
              <form className="inquiry-form" onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input type="text" required value={name} onChange={(e) => setName(e.target.value)} placeholder="Dr. Precious Mkhize" />
                  </div>
                  <div className="form-group">
                    <label>Company *</label>
                    <input type="text" required value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Webber Wentzel" />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Work Email *</label>
                    <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="p.mkhize@webberwentzel.co.za" />
                  </div>
                  <div className="form-group">
                    <label>Phone</label>
                    <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+27 82 123 4567" />
                  </div>
                </div>
                <div className="form-group">
                  <label>Inquiry Type</label>
                  <select value={inquiryType} onChange={(e) => setInquiryType(e.target.value)}>
                    <option value="">-- Select inquiry type --</option>
                    {INQUIRIES.map((i) => <option key={i} value={i}>{i}</option>)}
                  </select>
                </div>
                {selectedTier && (
                  <div className="tier-selected">
                    + Tier selected: <strong>{selectedTier}</strong>
                    <button type="button" className="tier-change" onClick={() => setSelectedTier(null)}>change</button>
                  </div>
                )}
                <div className="form-group">
                  <label>Message / Requirements</label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    rows={4}
                    placeholder="We need 25 Platinum boxes delivered to Sandton by 15 September for an annual board dinner. Can you accommodate?"
                  />
                </div>
                <button type="submit" className="btn-submit" disabled={submitting}>
                  {submitting ? "Sending..." : "Send Inquiry ->"}
                </button>
                {error && (
                  <p className="form-error" style={{ color: "#e05c4b", fontSize: 14, marginTop: 10 }}>
                    {error}
                  </p>
                )}
                <p className="form-disclaimer">Your information is kept confidential. We don&#39;t spam or share data with third parties.</p>
              </form>
            )}
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-logo">
          <span className="logo-mark">&#9670;</span>
          <span>STUDEX</span>
        </div>
        <div className="footer-links">
          <a href="mailto:info@studexmeat.com">info@studexmeat.com</a>
          <a href="https://studex-group.com">studex-group.com</a>
          <span>+27 94 988 8737</span>
        </div>
        <p className="footer-copy">{COMPLIANT_COPY.footerCopy}</p>
      </footer>
    </div>
  );
}

export default App;
