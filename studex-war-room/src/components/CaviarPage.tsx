import { useState } from 'react';
import './CaviarPage.css';

export default function CaviarPage() {
  const [form, setForm] = useState({ name: '', email: '', company: '', message: '', interest: 'tasting-box' });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Leads are routed through the server-side Cloudflare Worker (lead proxy).
  // The AgentMail credential lives in the Worker as a secret — NEVER in the client.
  const LEAD_PROXY_URL = 'https://studex-lead-proxy.tumelor001.workers.dev';

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(LEAD_PROXY_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          company: form.company || 'Individual',
          message: form.message,
          product: 'caviar',
        }),
      });

      const body = await res.json().catch(() => ({}));
      if (!res.ok || body?.ok === false) {
        const detail = body?.error ? `: ${body.error}` : '';
        setError(`Inquiry not sent (HTTP ${res.status})${detail}`);
        return;
      }
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? `Inquiry not sent: ${err.message}` : 'Inquiry not sent: network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="caviar-page">
      {/* HERO */}
      <section className="caviar-hero">
        <div className="caviar-hero__bg-texture" />
        <div className="caviar-hero__content">
          <div className="caviar-badge">Studex Caviar — Direct to You</div>
          <h1 className="caviar-hero__title">
            The World's Rarest<br />
            <span className="gold-text">Delivered to South Africa</span>
          </h1>
          <p className="caviar-hero__subtitle">
            Kaluga · Osetra · Sevruga — sourced from premier farms and re-exported through Dubai.
            The first D2C caviar brand in South Africa.
          </p>
          <div className="caviar-hero__ctas">
            <a href="#tasting-box" className="btn btn--gold">Shop the Tasting Box</a>
            <a href="#inquiry" className="btn btn--outline">Corporate Inquiry</a>
          </div>
          <div className="caviar-hero__trust">
            <span>🇿🇦 First SA D2C Caviar</span>
            <span>·</span>
            <span>🇦🇪 Dubai Sourced</span>
            <span>·</span>
            <span>CITES Compliant</span>
            <span>·</span>
            <span>Cold Chain Verified</span>
          </div>
        </div>
        <div className="caviar-hero__visual">
          <div className="caviar-can__wrapper">
            <div className="caviar-can">
              <div className="caviar-can__lid" />
              <div className="caviar-can__body">
                <div className="caviar-can__label">
                  <span className="caviar-can__brand">STUDEX</span>
                  <span className="caviar-can__type">Kaluga Reserve</span>
                  <span className="caviar-can__weight">30g</span>
                </div>
              </div>
            </div>
            <div className="caviar-can caviar-can--2">
              <div className="caviar-can__lid" />
              <div className="caviar-can__body">
                <div className="caviar-can__label">
                  <span className="caviar-can__brand">STUDEX</span>
                  <span className="caviar-can__type">Osetra Gold</span>
                  <span className="caviar-can__weight">30g</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THE TASTING BOX */}
      <section className="caviar-tasting-box" id="tasting-box">
        <div className="caviar-section-header">
          <div className="caviar-overline">Limited Edition — November 2026</div>
          <h2>The Studex Caviar Tasting Box</h2>
          <p>The gift that opens doors. Curated for the South African palate — pair our farmed Kaluga and French-style Osetra with award-winning Studex biltong and single-origin cold brew.</p>
        </div>

        <div className="caviar-box-contents">
          <div className="caviar-item-card caviar-item-card--featured">
            <div className="caviar-item-card__badge">Box Contents</div>
            <div className="caviar-item-card__title">Caviar Tasting Box</div>
            <div className="caviar-item-card__price">
              <span className="caviar-item-card__price-main">R1,800</span>
              <span className="caviar-item-card__price-sub">per box · excl. delivery</span>
            </div>
            <ul className="caviar-item-card__list">
              <li>
                <strong>Kaluga Reserve 30g</strong>
                <span>R520 value · River sturgeon, farmed · Silky, medium-intensity</span>
              </li>
              <li>
                <strong>Osetra Gold 30g</strong>
                <span>R680 value · French-style farm · Rich, nutty finish</span>
              </li>
              <li>
                <strong>Studex Biltong Selection 50g</strong>
                <span>R120 value · Beef &amp; game · Craft dried</span>
              </li>
              <li>
                <strong>Cold Brew Sample 100ml</strong>
                <span>R80 value · Single-origin Ethiopian</span>
              </li>
            </ul>
            <div className="caviar-item-card__total">
              <span>Total retail value</span>
              <strong>R1,400</strong>
              <em>You save R400 — and it's wrapped.</em>
            </div>
            <button className="btn btn--gold btn--full" onClick={() => document.getElementById('inquiry')?.scrollIntoView({ behavior: 'smooth' })}>
              Reserve Your Box
            </button>
            <p className="caviar-item-card__note">Limited to 50 boxes in November. MOQ for gifting orders: 5 boxes.</p>
          </div>

          <div className="caviar-items-grid">
            <div className="caviar-item-mini">
              <div className="caviar-item-mini__icon">🐟</div>
              <div className="caviar-item-mini__name">Kaluga Reserve</div>
              <div className="caviar-item-mini__desc">River sturgeon from certified farms. Medium-intensity brine, silky texture. Perfect on crème fraîche blinis.</div>
              <div className="caviar-item-mini__price">From R480 / 30g</div>
            </div>
            <div className="caviar-item-mini">
              <div className="caviar-item-mini__icon">🐟</div>
              <div className="caviar-item-mini__name">Osetra Gold</div>
              <div className="caviar-item-mini__desc">Premium farmed Osetra. Rich, nutty with a clean finish. The classic luxury caviar experience.</div>
              <div className="caviar-item-mini__price">From R680 / 30g</div>
            </div>
            <div className="caviar-item-mini">
              <div className="caviar-item-mini__icon">🥩</div>
              <div className="caviar-item-mini__name">Biltong Selection</div>
              <div className="caviar-item-mini__desc">Beef, game &amp; spice-marinated cuts. Craft dried in small batches. The perfect caviar accompaniment.</div>
              <div className="caviar-item-mini__price">From R120 / 50g</div>
            </div>
            <div className="caviar-item-mini">
              <div className="caviar-item-mini__icon">☕</div>
              <div className="caviar-item-mini__name">Cold Brew Sample</div>
              <div className="caviar-item-mini__desc">Single-origin Ethiopian. 18-hour cold steep. Clean, chocolatey, low acidity. Rinses the palate beautifully.</div>
              <div className="caviar-item-mini__price">From R80 / 100ml</div>
            </div>
          </div>
        </div>
      </section>

      {/* PRICING TABLE */}
      <section className="caviar-pricing">
        <div className="caviar-section-header">
          <div className="caviar-overline">Transparent Pricing</div>
          <h2>How It Works</h2>
        </div>
        <div className="caviar-pricing-table">
          <div className="caviar-pricing-row caviar-pricing-row--header">
            <span>Product</span>
            <span>Size</span>
            <span>Per Unit</span>
            <span>5+ Units</span>
            <span>Corporate (10+)</span>
          </div>
          <div className="caviar-pricing-row">
            <span>Kaluga Reserve</span>
            <span>30g</span>
            <span>R480</span>
            <span>R440</span>
            <span>R400</span>
          </div>
          <div className="caviar-pricing-row">
            <span>Osetra Gold</span>
            <span>30g</span>
            <span>R680</span>
            <span>R620</span>
            <span>R560</span>
          </div>
          <div className="caviar-pricing-row">
            <span>Caviar Tasting Box</span>
            <span>Full box</span>
            <span>R1,800</span>
            <span>R1,650</span>
            <span>R1,500</span>
          </div>
          <div className="caviar-pricing-row caviar-pricing-row--muted">
            <span>Custom Corporate Gift</span>
            <span>MOQ 20</span>
            <span>Inquire for bespoke pricing</span>
            <span>—</span>
            <span>—</span>
          </div>
        </div>
        <p className="caviar-pricing__note">
          All prices excl. VAT and delivery. CITES documentation provided with every order. Payment via EFT or BizCheckout.
        </p>
      </section>

      {/* CAVIAR STORY */}
      <section className="caviar-story">
        <div className="caviar-story__text">
          <div className="caviar-overline">Our Sourcing Story</div>
          <h2>From Dubai to Your Table</h2>
          <p>
            Dubai has become the world's undeclared caviar capital — a re-export hub where Russian, Iranian, and Chinese farm caviar flows through trusted intermediaries to buyers across Africa and the Middle East.
          </p>
          <p>
            Studex sources directly from vetted Dubai distributors with verified cold-chain documentation. Every tin is CITES-certified, legally imported, and delivered to your door in temperature-controlled packaging.
          </p>
          <p>
            No grey channels. No customs surprises. Just the world's finest caviar, delivered.
          </p>
          <div className="caviar-story__checks">
            <div className="caviar-check">✓ CITES permits on file</div>
            <div className="caviar-check">✓ DAFF import compliant</div>
            <div className="caviar-check">✓ Cold chain certified</div>
            <div className="caviar-check">✓ EFT & BizCheckout accepted</div>
          </div>
        </div>
        <div className="caviar-story__visual">
          <div className="caviar-map-card">
            <div className="caviar-map-card__route">
              <div className="caviar-route-point">
                <div className="caviar-route-point__dot caviar-route-point__dot--start" />
                <div className="caviar-route-point__label">
                  <strong>Dubai, UAE</strong>
                  <span>Distribution hub</span>
                </div>
              </div>
              <div className="caviar-route-line" />
              <div className="caviar-route-point">
                <div className="caviar-route-point__dot caviar-route-point__dot--end" />
                <div className="caviar-route-point__label">
                  <strong>Cape Town / Johannesburg</strong>
                  <span>Your delivery address</span>
                </div>
              </div>
            </div>
            <div className="caviar-map-card__timeline">
              <div className="caviar-timeline-item">
                <strong>Order placed</strong>
                <span>Day 0</span>
              </div>
              <div className="caviar-timeline-item">
                <strong>Caviar dispatched Dubai</strong>
                <span>Day 1–2</span>
              </div>
              <div className="caviar-timeline-item">
                <strong>Clears SA customs</strong>
                <span>Day 3–5</span>
              </div>
              <div className="caviar-timeline-item">
                <strong>Delivered to you</strong>
                <span>Day 5–7</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* INQUIRY FORM */}
      <section className="caviar-inquiry" id="inquiry">
        <div className="caviar-section-header">
          <div className="caviar-overline">Reserve Now</div>
          <h2>Corporate &amp; Gift Inquiries</h2>
          <p>
            November boxes are limited to 50 units. Fill in your details and our team will confirm availability and arrange delivery.
          </p>
        </div>

        {submitted ? (
          <div className="caviar-success">
            <div className="caviar-success__icon">✅</div>
            <h3> Inquiry received!</h3>
            <p>We'll be in touch within 2 business hours. Check <strong>sales@studex-group.com</strong> for a confirmation.</p>
          </div>
        ) : (
          <form className="caviar-form" onSubmit={handleSubmit}>
            {error && (
              <div role="alert" style={{ color: '#ff4444', marginBottom: '1rem', fontSize: '0.9rem' }}>
                ⚠️ {error}
              </div>
            )}
            <div className="caviar-form__row">
              <div className="caviar-form__field">
                <label>Full Name *</label>
                <input type="text" name="name" required value={form.name} onChange={handleChange} placeholder="Thabo Mkhize" />
              </div>
              <div className="caviar-form__field">
                <label>Email Address *</label>
                <input type="email" name="email" required value={form.email} onChange={handleChange} placeholder="thabo@company.co.za" />
              </div>
            </div>
            <div className="caviar-form__row">
              <div className="caviar-form__field">
                <label>Company / Event Name</label>
                <input type="text" name="company" value={form.company} onChange={handleChange} placeholder="Cape Grace Hotel" />
              </div>
              <div className="caviar-form__field">
                <label>Interested In</label>
                <select name="interest" onChange={(e) => setForm(p => ({ ...p, interest: e.target.value }))}>
                  <option value="tasting-box">Caviar Tasting Box (R1,800)</option>
                  <option value="kaluga">Kaluga Reserve (bulk)</option>
                  <option value="osetra">Osetra Gold (bulk)</option>
                  <option value="corporate">Corporate Gift (MOQ 20)</option>
                  <option value="partnership">Distribution Partnership</option>
                </select>
              </div>
            </div>
            <div className="caviar-form__field">
              <label>Message</label>
              <textarea name="message" value={form.message} onChange={handleChange} rows={4} placeholder="Tell us about your event, order quantity, or any special requirements..." />
            </div>
            <button type="submit" className="btn btn--gold btn--full" disabled={loading}>
              {loading ? 'Sending...' : 'Submit Inquiry →'}
            </button>
            <p className="caviar-form__disclaimer">
              By submitting you agree to be contacted by Studex. We don't spam. Your data is never shared with third parties.
            </p>
          </form>
        )}
      </section>

      {/* FOOTER */}
      <footer className="caviar-footer">
        <div className="caviar-footer__brand">
          <strong>Studex Global Markets</strong>
          <span>Premium South African Exports</span>
        </div>
        <div className="caviar-footer__links">
          <a href="https://studexgroup.com">Main Site</a>
          <a href="https://shop.studexgroup.com">Shop</a>
          <span>info@studexmeat.com</span>
        </div>
        <p className="caviar-footer__copy">© 2026 Studex Global Markets (Pty) Ltd. CITES-compliant imports.</p>
      </footer>
    </div>
  );
}
