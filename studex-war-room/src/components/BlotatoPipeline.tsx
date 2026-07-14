import { useState, useEffect } from 'react';

const BLOTATO_KEY = 'blt_y5mVD6oMJrgFb8UsfWN3T4GSYN2ZvCeGsVWWwdaf8Og=';
const API_BASE = 'https://backend.blotato.com/v2';

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

async function fetchAccounts(): Promise<PlatformAccount[]> {
  try {
    const res = await fetch(`${API_BASE}/users/me/accounts`, {
      headers: { 'blotato-api-key': BLOTATO_KEY },
    });
    if (!res.ok) throw new Error('API error ' + res.status);
    const data = await res.json();
    // Expected: { accounts: [{ id, platform, name, connected }] }
    return (data.accounts || []).map((a: any) => ({
      id: a.id,
      platform: a.platform?.toLowerCase() || 'unknown',
      name: a.name || a.platform || 'Unknown',
      connected: a.status === 'active' || a.connected,
    }));
  } catch {
    return [];
  }
}

async function fetchPosts(): Promise<ScheduledPost[]> {
  try {
    const res = await fetch(`${API_BASE}/posts?status=scheduled`, {
      headers: { 'blotato-api-key': BLOTATO_KEY },
    });
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

async function createPost(payload: { platform: string; content: string; scheduledFor?: string }): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(`${API_BASE}/posts`, {
      method: 'POST',
      headers: {
        'blotato-api-key': BLOTATO_KEY,
        'Content-Type': 'application/json',
      },
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
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [showNewPost, setShowNewPost] = useState(false);
  const [postForm, setPostForm] = useState({ platform: 'facebook', content: '', scheduledFor: '' });
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'queue' | 'compose'>('queue');

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

  return (
    <div className="blotato-pipeline">
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
        <button className={`bp-tab ${activeTab === 'queue' ? 'active' : ''}`} onClick={() => setActiveTab('queue')}>
          📋 QUEUE ({queuedPosts.length})
        </button>
        <button className={`bp-tab ${activeTab === 'compose' ? 'active' : ''}`} onClick={() => setActiveTab('compose')}>
          ✍️ COMPOSE
        </button>
      </div>

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
        <div className="bp-stat">
          <div className="bp-stat-val" style={{ color: '#ffaa44' }}>~0</div>
          <div className="bp-stat-lbl">POSTS THIS WEEK</div>
        </div>
      </div>
    </div>
  );
}
