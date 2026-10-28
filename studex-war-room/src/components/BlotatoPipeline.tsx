import { useState, useEffect } from 'react';

// NO API KEY IN THE BROWSER. The war-room server holds the Blotato key
// and exposes it through /api/blotato/*; this component talks to the
// server, never to Blotato directly.
// The Blotato API key is injected server-side by the /api/blotato proxy.
// NEVER add it to the browser bundle from here.
const API_BASE = '/api/blotato';

interface PlatformAccount {
  id: string;
  platform: string;
  name: string;
  connected: boolean;
  avatar?: string;
}

interface ScheduledPost {
  id: string;
  platform: string;
  content: string;
  scheduledFor: string;
  status: 'queued' | 'published' | 'failed';
  mediaUrl?: string;
}

interface Automation {
  id: string;
  name: string;
  platform: string;
  isActive: boolean;
  trigger: {
    type: string;
    keywords: string[];
  };
  dmMessage: string;
  buttons?: { title: string; type: string; url: string }[];
  updatedAt: string;
}

const PLATFORMS = [
  { id: 'facebook', name: 'Facebook', icon: '📘', color: '#1877F2', connected: false },
  { id: 'instagram', name: 'Instagram', icon: '📷', color: '#E4405F', connected: false },
  { id: 'twitter', name: 'X (Twitter)', icon: '🐦', color: '#1DA1F2', connected: false },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼', color: '#0A66C2', connected: false },
];

const MOCK_SCHEDULED: ScheduledPost[] = [
  { id: 'sp-1', platform: 'facebook', content: '🔥 Karoo Lamb Chops now in stock. Grass-fed, dry-aged 21 days. Order via WhatsApp or DM.', scheduledFor: '2026-07-15 09:00', status: 'queued' },
  { id: 'sp-2', platform: 'instagram', content: 'Your charcuterie board deserves the best. Premium biltong, sliced to order. Link in bio.', scheduledFor: '2026-07-15 12:00', status: 'queued' },
  { id: 'sp-3', platform: 'facebook', content: 'Corporate gifting season is here. Branded Studex boxes for your clients — minimum 20 units.', scheduledFor: '2026-07-16 10:00', status: 'queued' },
  { id: 'sp-4', platform: 'instagram', content: 'Wagyu Ribeye — 450g of pure South African excellence. R780 per pack. WhatsApp orders only.', scheduledFor: '2026-07-14 18:00', status: 'published' },
];

const CONTENT_TEMPLATES = [
  { label: 'Product Drop', text: '🔥 {product} now in stock. Order via WhatsApp or DM. Link in bio.' },
  { label: 'Gifting', text: 'Looking for corporate gifting? Studex premium biltong boxes — minimum 20 units. DM for pricing.' },
  { label: 'Behind the Scenes', text: 'From Karoo farm to your table. Our dry-aging room at work. 🐄🥩' },
  { label: 'Testimonial', text: '"Best biltong I\'ve ever had" — satisfied customer, Sandton. Order now: WhatsApp link in bio.' },
  { label: 'Caviar Launch', text: 'Coming soon: Authentic Russian Caviar, delivered to SA. B2B enquiries open. #StudexCaviar' },
];

// Tonight's 5-Post Diaspora Campaign — Studex Build Hour 2026-10-06
export const CAMPAIGN_POSTS = [
  {
    label: '📖 Origin Story',
    text: 'It started in the Karoo. Dry hills, bold flavours, and a family tradition of perfecting biltong over generations. Studex isn\'t just meat — it\'s a story served on a plate. 🐄🔥 #SouthAfrica #Biltong #Studex',
    platform: 'facebook',
    scheduledFor: '',
  },
  {
    label: '🥩 Wagyu Biltong Gold',
    text: 'Wagyu Biltong Gold — R650. Grade A9+ Japanese Wagyu, dry-cured the traditional Karoo way. 200g of pure excellence. Order via WhatsApp: +27 94 988 8737. #Wagyu #BiltongGold #Studex',
    platform: 'instagram',
    scheduledFor: '',
  },
  {
    label: '🌍 Studex Goes Global',
    text: 'The world is discovering biltong. Studex is ready — exporting premium SA beef to the UK, UAE, and Australia. Diaspora, your taste of home is one WhatsApp away. 🌍✈️ #ExportReady #SouthAfrica #Studex',
    platform: 'facebook',
    scheduledFor: '',
  },
  {
    label: '☕ Biltong + African Coffee — Coming Soon',
    text: 'Biltong and African coffee. Two iconic SA flavours, one natural pairing. Coming soon to Studex — the ultimate taste of home, delivered worldwide. ☕🥩 Stay tuned. #Studex #AfricanCoffee #ComingSoon',
    platform: 'instagram',
    scheduledFor: '',
  },
  {
    label: '⭐ Customer Review Spotlight',
    text: '"I\'ve ordered biltong from three continents. Nothing comes close to Studex. The Wagyu is in a league of its own." — Thandi, Johannesburg ⭐⭐⭐⭐⭐ DM us or click the link to order. #CustomerLove #Studex #5Stars',
    platform: 'facebook',
    scheduledFor: '',
  },
];

async function fetchAccounts(): Promise<PlatformAccount[]> {
  try {
    const res = await fetch(`${API_BASE}/users/me/accounts`);
    if (!res.ok) throw new Error('API error ' + res.status);
    const data = await res.json();
    // Blotato v2 returns { items: [{ id, platform, username, fullname }] }
    return (data.items || []).map((a: any) => ({
      id: String(a.id),
      platform: a.platform?.toLowerCase() || 'unknown',
      name: a.fullname || a.username || a.platform || 'Unknown',
      connected: true, // if it's in the items list, it's connected
    }));
  } catch {
    return [];
  }
}

async function fetchPosts(): Promise<ScheduledPost[]> {
  try {
    const res = await fetch(`${API_BASE}/posts?status=scheduled`);
    if (!res.ok) throw new Error('API error ' + res.status);
    const data = await res.json();
    return (data.posts || []).map((p: any) => ({
      id: p.id,
      platform: p.platform?.toLowerCase() || 'unknown',
      content: p.content || p.text || '',
      scheduledFor: p.scheduled_for || p.scheduledAt || '',
      status: p.status === 'published' ? 'published' : p.status === 'failed' ? 'failed' : 'queued',
      mediaUrl: p.media_url || p.mediaUrl,
    }));
  } catch {
    return [];
  }
}

async function fetchAutomations(): Promise<Automation[]> {
  try {
    const res = await fetch(`${API_BASE}/automations`);
    if (!res.ok) throw new Error('API error ' + res.status);
    const data = await res.json();
    return (data.automations || []).map((a: any) => ({
      id: a.id,
      name: a.name,
      platform: a.platform,
      isActive: a.isActive,
      trigger: a.trigger || {},
      dmMessage: a.dmMessage || '',
      buttons: a.buttons,
      updatedAt: a.updatedAt,
    }));
  } catch {
    return [];
  }
}

async function createPost(payload: { platform: string; content: string; scheduledFor?: string }): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(`${API_BASE}/posts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform: payload.platform,
        content: payload.content,
        scheduled_for: payload.scheduledFor,
        status: payload.scheduledFor ? 'scheduled' : 'draft',
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return { ok: false, error: err.message || `HTTP ${res.status}` };
    }
    return { ok: true };
  } catch (e: any) {
    return { ok: false, error: e.message };
  }
}

export default function BlotatoPipeline() {
  const [platforms, setPlatforms] = useState<PlatformAccount[]>([]);
  const [scheduled, setScheduled] = useState<ScheduledPost[]>(MOCK_SCHEDULED);
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [showNewPost, setShowNewPost] = useState(false);
  const [postForm, setPostForm] = useState({ platform: 'facebook', content: '', scheduledFor: '' });
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'queue' | 'compose' | 'automations'>('automations');

  useEffect(() => {
    setLoadingAccounts(true);
    fetchAccounts().then(accounts => {
      if (accounts.length > 0) {
        setPlatforms(accounts);
      } else {
        // Use mock connected state if API returns nothing
        setPlatforms(PLATFORMS.map(p => ({ platform: p.id, name: p.name, connected: p.id === 'facebook' || p.id === 'instagram', id: p.id })));
      }
    }).catch(() => {
      setApiError('Blotato API unreachable — using demo data');
      setPlatforms(PLATFORMS.map(p => ({ platform: p.id, name: p.name, connected: p.id === 'facebook' || p.id === 'instagram', id: p.id })));
    }).finally(() => setLoadingAccounts(false));

    fetchPosts().then(posts => {
      if (posts.length > 0) setScheduled(posts);
    });

    fetchAutomations().then(auts => {
      if (auts.length > 0) setAutomations(auts);
    });
  }, []);

  async function handlePost(e: React.FormEvent) {
    e.preventDefault();
    if (!postForm.content.trim()) return;
    setPosting(true);
    setPostResult(null);
    const result = await createPost({ platform: postForm.platform, content: postForm.content, scheduledFor: postForm.scheduledFor || undefined });
    setPostResult(result.ok ? { ok: true, msg: 'Post created!' } : { ok: false, msg: result.error || 'Unknown error' });
    if (result.ok) {
      setScheduled(prev => [...prev, {
        id: 'local-' + Date.now(),
        platform: postForm.platform,
        content: postForm.content,
        scheduledFor: postForm.scheduledFor || 'Draft (not scheduled)',
        status: postForm.scheduledFor ? 'queued' : 'queued',
      }]);
      setPostForm({ platform: 'facebook', content: '', scheduledFor: '' });
      setShowNewPost(false);
    }
    setPosting(false);
  }

  function applyTemplate(t: typeof CONTENT_TEMPLATES[0]) {
    setPostForm(prev => ({ ...prev, content: t.text }));
  }

  const queuedPosts = scheduled.filter(p => p.status === 'queued');
  const publishedPosts = scheduled.filter(p => p.status === 'published');

  const platformIcon = (id: string) => PLATFORMS.find(p => p.id === id)?.icon || '📣';
  const platformColor = (id: string) => PLATFORMS.find(p => p.id === id)?.color || '#888';

  const metaAccounts = platforms.filter(p => ['facebook', 'instagram'].includes(p.platform));
  const metaConnected = metaAccounts.some(p => p.connected);

  return (
    <div className="blotato-pipeline">
      {/* URGENT Meta Reconnect Banner */}
      {!metaConnected && (
        <div className="bp-meta-alert">
          <div className="bp-meta-alert-icon">🚨</div>
          <div className="bp-meta-alert-body">
            <div className="bp-meta-alert-title">META TOKENS EXPIRED — NALEDI IS BLOCKED</div>
            <div className="bp-meta-alert-desc">
              Facebook + Instagram disconnected since <strong>June 22, 2026</strong>. Naledi cannot post or schedule content.
              Fix: log into <a href="https://app.blotato.com" target="_blank" rel="noopener noreferrer">app.blotato.com</a> → Settings → Connected Accounts → click <strong>Reconnect Facebook</strong> and <strong>Reconnect Instagram</strong> and complete Meta OAuth. This is the #1 priority before CIIE.
            </div>
          </div>
          <a
            href="https://app.blotato.com"
            target="_blank"
            rel="noopener noreferrer"
            className="bp-meta-alert-btn"
          >
            FIX NOW →
          </a>
        </div>
      )}

      <div className="bp-header">
        <div className="bp-title">📡 STUDEX CONTENT PIPELINE</div>
        <div className="bp-subtitle">Blotato-powered social publishing</div>
        {apiError && <div className="bp-api-warn">⚠️ {apiError}</div>}
      </div>

      {/* Platform Connections */}
      <div className="bp-section">
        <div className="bp-section-title">CONNECTED PLATFORMS</div>
        <div className="bp-platforms">
          {platforms.map(p => {
            const meta = PLATFORMS.find(m => m.id === p.platform) || PLATFORMS[0];
            return (
              <div key={p.platform} className="bp-platform-card" style={{ borderColor: p.connected ? platformColor(p.platform) + '60' : '#2a2520' }}>
                <div className="bp-pf-icon">{meta.icon}</div>
                <div className="bp-pf-info">
                  <div className="bp-pf-name">{meta.name}</div>
                  <div className="bp-pf-status" style={{ color: p.connected ? '#4aff88' : '#ff4444' }}>
                    {p.connected ? '● CONNECTED' : '○ NOT CONNECTED'}
                  </div>
                </div>
                {!p.connected && (
                  <a
                    href="https://app.blotato.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bp-connect-btn"
                    style={{ backgroundColor: platformColor(p.platform) }}
                  >
                    CONNECT
                  </a>
                )}
              </div>
            );
          })}
        </div>
        <div className="bp-oauth-hint">
          💡 To connect accounts: log into <a href="https://app.blotato.com" target="_blank" rel="noopener noreferrer">app.blotato.com</a> → Settings → Connected Accounts → OAuth Facebook & Instagram
        </div>
      </div>

      {/* Tab nav */}
      <div className="bp-tabs">
        <button className={`bp-tab ${activeTab === 'automations' ? 'active' : ''}`} onClick={() => setActiveTab('automations')}>
          🤖 DM AUTOMATIONS ({automations.length})
        </button>
        <button className={`bp-tab ${activeTab === 'queue' ? 'active' : ''}`} onClick={() => setActiveTab('queue')}>
          📋 QUEUE ({queuedPosts.length})
        </button>
        <button className={`bp-tab ${activeTab === 'compose' ? 'active' : ''}`} onClick={() => setActiveTab('compose')}>
          ✍️ COMPOSE
        </button>
      </div>

      {activeTab === 'automations' && (
        <div className="bp-section">
          <div className="bp-section-title">LIVE DM AUTO-REPLIES</div>
          {automations.length === 0 ? (
            <div className="bp-empty">
              No automations found. Visit{' '}
              <a href="https://app.blotato.com" target="_blank" rel="noopener noreferrer">app.blotato.com</a>{' '}
              to create keyword-triggered auto-replies.
            </div>
          ) : (
            <div className="bp-post-list">
              {automations.map(aut => {
                const meta = PLATFORMS.find(p => p.id === aut.platform) || PLATFORMS[0];
                const keywords = aut.trigger?.keywords || [];
                return (
                  <div key={aut.id} className="bp-post-card">
                    <div className="bp-post-top">
                      <span className="bp-post-platform" style={{ color: meta.color }}>
                        {meta.icon} {aut.name}
                      </span>
                      <span
                        className="bp-post-status"
                        style={{
                          color: aut.isActive ? '#4aff88' : '#ffaa44',
                          background: aut.isActive ? 'rgba(74,255,136,0.1)' : 'rgba(255,170,68,0.1)',
                          border: `1px solid ${aut.isActive ? '#4aff8840' : '#ffaa4440'}`,
                        }}
                      >
                        {aut.isActive ? '● LIVE' : '○ DRAFT'}
                      </span>
                    </div>
                    <div className="bp-post-content" style={{ fontSize: '11px', color: '#a09080', marginBottom: '6px' }}>
                      🔑 Keywords: {keywords.length > 0 ? keywords.join(', ') : '(all messages)'}
                    </div>
                    <div className="bp-post-content" style={{ fontSize: '12px', whiteSpace: 'pre-wrap' }}>
                      {aut.dmMessage.substring(0, 160)}{aut.dmMessage.length > 160 ? '…' : ''}
                    </div>
                    {aut.buttons && aut.buttons.length > 0 && (
                      <div className="bp-post-meta" style={{ marginTop: '6px' }}>
                        {aut.buttons.map((btn, i) => (
                          <span key={i} style={{ marginRight: '10px', color: '#4a9eff' }}>
                            🔗 {btn.title}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
          <div style={{ marginTop: '12px', padding: '10px', background: 'rgba(74,255,136,0.05)', border: '1px solid #4aff8830', borderRadius: '6px', fontSize: '11px', color: '#8a9080' }}>
            💡 To add more automations or edit existing ones, go to{' '}
            <a href="https://app.blotato.com" target="_blank" rel="noopener noreferrer">app.blotato.com → Automations</a>
            {' '}— or run <code>node /workspace/builds/blotato-dm-automation/setup-automations.sh</code> to add new keyword flows.
          </div>
        </div>
      )}

      {activeTab === 'queue' && (
        <div className="bp-section">
          <div className="bp-section-title">SCHEDULED POSTS</div>
          {scheduled.length === 0 ? (
            <div className="bp-empty">No posts scheduled. Compose one below.</div>
          ) : (
            <div className="bp-post-list">
              {scheduled.map(post => (
                <div key={post.id} className={`bp-post-card ${post.status === 'published' ? 'bp-post-published' : ''}`}>
                  <div className="bp-post-top">
                    <span className="bp-post-platform" style={{ color: platformColor(post.platform) }}>
                      {platformIcon(post.platform)} {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
                    </span>
                    <span className={`bp-post-status bp-status-${post.status}`}>{post.status.toUpperCase()}</span>
                  </div>
                  <div className="bp-post-content">{post.content}</div>
                  <div className="bp-post-meta">
                    {post.scheduledFor && <span>🕐 {post.scheduledFor}</span>}
                    {post.mediaUrl && <span>📎 Media attached</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'compose' && (
        <div className="bp-section">
          <div className="bp-section-title">NEW POST</div>

          {/* Quick templates */}
          <div className="bp-templates">
            <div className="bp-tpl-label">QUICK TEMPLATES:</div>
            <div className="bp-tpl-btns">
              {CONTENT_TEMPLATES.map(t => (
                <button key={t.label} className="bp-tpl-btn" onClick={() => applyTemplate(t)}>{t.label}</button>
              ))}
            </div>
          </div>

          <form className="bp-form" onSubmit={handlePost}>
            <div className="bp-form-row">
              <label className="bp-label">PLATFORM</label>
              <div className="bp-platform-select">
                {PLATFORMS.filter(p => platforms.find(ac => ac.platform === p.id && ac.connected)).map(p => (
                  <button
                    key={p.id}
                    type="button"
                    className={`bp-pf-toggle ${postForm.platform === p.id ? 'selected' : ''}`}
                    style={{ borderColor: postForm.platform === p.id ? p.color : 'transparent', color: postForm.platform === p.id ? p.color : '#a09080' }}
                    onClick={() => setPostForm(f => ({ ...f, platform: p.id }))}
                  >
                    {p.icon} {p.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="bp-form-row">
              <label className="bp-label">CONTENT</label>
              <textarea
                className="bp-textarea"
                placeholder="Write your post... (keep it under 500 chars for Instagram)"
                value={postForm.content}
                onChange={e => setPostForm(f => ({ ...f, content: e.target.value }))}
                rows={4}
                maxLength={2000}
              />
              <div className="bp-char-count">{postForm.content.length}/2000</div>
            </div>

            <div className="bp-form-row">
              <label className="bp-label">SCHEDULE (optional)</label>
              <input
                type="datetime-local"
                className="bp-input"
                value={postForm.scheduledFor}
                onChange={e => setPostForm(f => ({ ...f, scheduledFor: e.target.value }))}
              />
            </div>

            {postResult && (
              <div className={`bp-result ${postResult.ok ? 'bp-result-ok' : 'bp-result-err'}`}>
                {postResult.ok ? '✅ Post created!' : `❌ ${postResult.msg}`}
              </div>
            )}

            <div className="bp-form-actions">
              <button type="submit" className="bp-submit-btn" disabled={posting || !postForm.content.trim()}>
                {posting ? 'POSTING...' : 'PUBLISH VIA BLOTATO →'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Stats footer */}
      <div className="bp-stats">
        <div className="bp-stat">
          <div className="bp-stat-val" style={{ color: '#4aff88' }}>{automations.filter(a => a.isActive).length}</div>
          <div className="bp-stat-lbl">LIVE AUTOS</div>
        </div>
        <div className="bp-stat">
          <div className="bp-stat-val">{queuedPosts.length}</div>
          <div className="bp-stat-lbl">QUEUED</div>
        </div>
        <div className="bp-stat">
          <div className="bp-stat-val">{publishedPosts.length}</div>
          <div className="bp-stat-lbl">PUBLISHED</div>
        </div>
        <div className="bp-stat">
          <div className="bp-stat-val" style={{ color: '#4aff88' }}>{platforms.filter(p => p.connected).length}/{platforms.length}</div>
          <div className="bp-stat-lbl">CONNECTED</div>
        </div>
      </div>
    </div>
  );
}
