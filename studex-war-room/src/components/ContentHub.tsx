import { useState, useEffect } from 'react';

// ─── Types ───────────────────────────────────────────────────────────────────
interface QueuedPost {
  id: string;
  content: string;
  platforms: ('facebook' | 'instagram')[];
  scheduledAt: string;
  status: 'draft' | 'queued' | 'published' | 'failed';
  imageUrl?: string;
  createdBy: string;
  blotsId?: string;
}

interface BlotatoAccount {
  id: string;
  platform: 'facebook' | 'instagram';
  name: string;
  username: string;
  connected: boolean;
}

interface ContentTemplate {
  id: string;
  label: string;
  content: string;
  platforms: ('facebook' | 'instagram')[];
}

// ─── Mock data (Blotato API integration) ──────────────────────────────────────
const CONTENT_TEMPLATES: ContentTemplate[] = [
  {
    id: 't1',
    label: '🐄 StudEx Wild Game biltong drop',
    content: '🔥 NEW DROP — Wild Game Biltong is HERE. Springbok, Kudu, Eland — straight from the bush to your door. Taste the difference wild makes. 🦌\n\n📦 Free delivery on orders over R350.\n🔗 Link in bio.',
    platforms: ['facebook', 'instagram'],
  },
  {
    id: 't2',
    label: '☕ Rwanda A1 Coffee — China window',
    content: '🇨🇳 BIG NEWS: China opens to African coffee July 20. Rwanda A1/A2 commanding 40–60% premium. The window is OPEN.\n\nPROWTC Dubai → China corridor now the hottest route in specialty coffee.',
    platforms: ['facebook'],
  },
  {
    id: 't3',
    label: '🥩 Premium cuts — Father\'s Day lead',
    content: 'Father\'s Day is coming. Don\'t settle for ordinary — give him cuts he\'ll never forget. Wagyu Ribeye. Dry-aged. Grass-fed.\n\n📦 Order by Wed for Fri delivery.',
    platforms: ['facebook', 'instagram'],
  },
  {
    id: 't4',
    label: '📦 Subscription Box promo',
    content: 'Never run out of biltong again. StudEx Meat Subscription Box — monthly delivery of the finest SA biltong, curated seasonal cuts, and exclusive specials.\n\n🔗 First month 15% off — link in bio.',
    platforms: ['instagram'],
  },
];

const MOCK_QUEUE: QueuedPost[] = [
  {
    id: 'q1',
    content: '🐄 Wild Game Biltong Drop 🔥 Springbok, Kudu & Eland — NEW for July. Free delivery R350+ orders.',
    platforms: ['facebook', 'instagram'],
    scheduledAt: '2026-07-06T09:00',
    status: 'queued',
    createdBy: 'Naledi',
  },
  {
    id: 'q2',
    content: '☕ Rwanda A1 Specialty Coffee — hitting the China window July 20. PROWTC Dubai → China corridor active.',
    platforms: ['facebook'],
    scheduledAt: '2026-07-07T11:00',
    status: 'queued',
    createdBy: 'Naledi',
  },
  {
    id: 'q3',
    content: '🥩 Father\'s Day cuts — Wagyu Ribeye, Dry-aged. Order by Wed for Fri delivery.',
    platforms: ['facebook', 'instagram'],
    scheduledAt: '2026-07-08T10:00',
    status: 'draft',
    createdBy: 'Naledi',
  },
  {
    id: 'q4',
    content: '📦 StudEx Subscription Box — first month 15% off. Never run out of biltong.',
    platforms: ['instagram'],
    scheduledAt: '2026-07-09T12:00',
    status: 'draft',
    createdBy: 'Naledi',
  },
];

// ─── Blotato API helpers ───────────────────────────────────────────────────────
const BLOTATO_KEY = 'blt_y5mVD6oMJrgFb8UsfWN3T4GSYN2ZvCeGsVWWwdaf8Og=';
const BLOTATO_BASE = 'https://backend.blotato.com/v2';

async function fetchBlotatoAccounts(): Promise<BlotatoAccount[]> {
  try {
    const res = await fetch(`${BLOTATO_BASE}/users/me/accounts`, {
      headers: { 'blotato-api-key': BLOTATO_KEY },
    });
    if (!res.ok) throw new Error(`Blotato ${res.status}`);
    const data = await res.json();
    return (data.accounts || []).map((acc: any) => ({
      id: acc.id,
      platform: acc.platform || 'facebook',
      name: acc.name || acc.username || 'Unknown Account',
      username: acc.username || '',
      connected: acc.status === 'active' || acc.connected === true,
    }));
  } catch {
    return MOCK_ACCOUNTS;
  }
}

async function postToBlotato(content: string, platforms: string[], scheduledAt?: string): Promise<{ success: boolean; blotId?: string; error?: string }> {
  try {
    const res = await fetch(`${BLOTATO_BASE}/posts`, {
      method: 'POST',
      headers: {
        'blotato-api-key': BLOTATO_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        platforms,
        ...(scheduledAt ? { scheduled_at: scheduledAt } : {}),
        account_ids: [], // let Blotato use all connected
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return { success: false, error: err.message || `HTTP ${res.status}` };
    }
    const data = await res.json();
    return { success: true, blotId: data.id || data.post_id };
  } catch (e: any) {
    return { success: false, error: e.message };
  }
}

// Mock accounts when API is not connected
const MOCK_ACCOUNTS: BlotatoAccount[] = [
  { id: 'fb1', platform: 'facebook', name: 'StudEx Meat', username: 'studexmeat', connected: false },
  { id: 'ig1', platform: 'instagram', name: 'StudEx Meat', username: '@studexmeat', connected: false },
];

// ─── Platform icons ───────────────────────────────────────────────────────────
const PLATFORM_ICONS: Record<string, string> = {
  facebook: '📘',
  instagram: '📷',
};

const PLATFORM_COLORS: Record<string, string> = {
  facebook: '#4a9eff',
  instagram: '#ff6eb4',
};

// ─── Component ────────────────────────────────────────────────────────────────
export default function ContentHub() {
  const [queue, setQueue] = useState<QueuedPost[]>(MOCK_QUEUE);
  const [accounts, setAccounts] = useState<BlotatoAccount[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<{ success: boolean; msg: string } | null>(null);

  // Composer state
  const [composerContent, setComposerContent] = useState('');
  const [composerPlatforms, setComposerPlatforms] = useState<('facebook' | 'instagram')[]>(['facebook']);
  const [composerSchedule, setComposerSchedule] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [view, setView] = useState<'queue' | 'calendar' | 'accounts'>('queue');

  // Load accounts on mount
  useEffect(() => {
    setLoadingAccounts(true);
    fetchBlotatoAccounts().then(accs => {
      setAccounts(accs);
      setLoadingAccounts(false);
    });
  }, []);

  // Apply template to composer
  function applyTemplate(tplId: string) {
    const tpl = CONTENT_TEMPLATES.find(t => t.id === tplId);
    if (!tpl) return;
    setComposerContent(tpl.content);
    setComposerPlatforms(tpl.platforms);
    setSelectedTemplate(tplId);
  }

  function toggleComposerPlatform(p: 'facebook' | 'instagram') {
    setComposerPlatforms(prev =>
      prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]
    );
  }

  async function handlePublish(immediate: boolean) {
    if (!composerContent.trim()) return;
    setPosting(true);
    setPostResult(null);

    const scheduledAt = immediate ? undefined : composerSchedule || undefined;
    const result = await postToBlotato(composerContent, composerPlatforms, scheduledAt);

    if (result.success) {
      const newPost: QueuedPost = {
        id: `q${Date.now()}`,
        content: composerContent,
        platforms: composerPlatforms,
        scheduledAt: scheduledAt || new Date().toISOString(),
        status: immediate ? 'published' : 'queued',
        createdBy: 'Naledi',
        blotsId: result.blotId,
      };
      setQueue(prev => [newPost, ...prev]);
      setComposerContent('');
      setComposerSchedule('');
      setSelectedTemplate('');
      setPostResult({ success: true, msg: immediate ? '✅ Published to Blotato!' : `✅ Queued for ${scheduledAt}` });
    } else {
      setPostResult({ success: false, msg: `❌ Blotato error: ${result.error}` });
    }
    setPosting(false);
    setTimeout(() => setPostResult(null), 5000);
  }

  function moveToQueue(postId: string) {
    setQueue(prev => prev.map(p => p.id === postId ? { ...p, status: 'queued' as const } : p));
  }

  const queuedCount = queue.filter(p => p.status === 'queued').length;
  const draftCount = queue.filter(p => p.status === 'draft').length;
  const publishedCount = queue.filter(p => p.status === 'published').length;

  return (
    <div className="content-hub">
      {/* Top stats strip */}
      <div className="ch-stats">
        <div className="ch-stat">
          <span className="ch-stat-val">{queuedCount}</span>
          <span className="ch-stat-label">QUEUED</span>
        </div>
        <div className="ch-stat">
          <span className="ch-stat-val" style={{ color: '#ffaa44' }}>{draftCount}</span>
          <span className="ch-stat-label">DRAFTS</span>
        </div>
        <div className="ch-stat">
          <span className="ch-stat-val" style={{ color: '#4aff88' }}>{publishedCount}</span>
          <span className="ch-stat-label">PUBLISHED</span>
        </div>
        <div className="ch-stat">
          <span className="ch-stat-val" style={{ color: accounts.filter(a => a.connected).length > 0 ? '#4aff88' : '#ff4444' }}>
            {accounts.filter(a => a.connected).length}/{accounts.length}
          </span>
          <span className="ch-stat-label">BLOTATO CONNECTED</span>
        </div>
        <div className="ch-stat" style={{ marginLeft: 'auto', borderLeft: '1px solid var(--border)', paddingLeft: '16px' }}>
          <span className="ch-stat-label">AGENT</span>
          <span className="ch-stat-val" style={{ color: 'var(--amber)', fontSize: '13px' }}>Naledi CMO</span>
        </div>
      </div>

      {/* Nav tabs */}
      <div className="ch-tabs">
        <button className={`ch-tab ${view === 'queue' ? 'active' : ''}`} onClick={() => setView('queue')}>📋 POST QUEUE</button>
        <button className={`ch-tab ${view === 'calendar' ? 'active' : ''}`} onClick={() => setView('calendar')}>📅 CALENDAR</button>
        <button className={`ch-tab ${view === 'accounts' ? 'active' : ''}`} onClick={() => setView('accounts')}>🔗 ACCOUNTS</button>
      </div>

      <div className="ch-body">
        {/* ── POST QUEUE VIEW ── */}
        {view === 'queue' && (
          <div className="ch-queue-layout">
            {/* Left: Composer */}
            <div className="ch-composer">
              <div className="ch-composer-title">✍️ NEW POST</div>

              {/* Quick templates */}
              <div className="ch-templates-label">QUICK TEMPLATES</div>
              <div className="ch-templates">
                {CONTENT_TEMPLATES.map(tpl => (
                  <button
                    key={tpl.id}
                    className={`ch-template-btn ${selectedTemplate === tpl.id ? 'active' : ''}`}
                    onClick={() => applyTemplate(tpl.id)}
                  >
                    {tpl.label}
                  </button>
                ))}
              </div>

              {/* Platform toggles */}
              <div className="ch-platform-toggles">
                {(['facebook', 'instagram'] as const).map(p => (
                  <button
                    key={p}
                    className={`ch-platform-toggle ${composerPlatforms.includes(p) ? 'active' : ''}`}
                    style={{ '--plat-color': PLATFORM_COLORS[p] } as React.CSSProperties}
                    onClick={() => toggleComposerPlatform(p)}
                  >
                    {PLATFORM_ICONS[p]} {p.charAt(0).toUpperCase() + p.slice(1)}
                  </button>
                ))}
              </div>

              {/* Textarea */}
              <textarea
                className="ch-textarea"
                value={composerContent}
                onChange={e => setComposerContent(e.target.value)}
                placeholder="Write your post... Be authentic. Be bold. Be StudEx."
                rows={6}
              />
              <div className="ch-char-count" style={{ color: composerContent.length > 2000 ? '#ff4444' : 'var(--text-dim)' }}>
                {composerContent.length} / 2000
              </div>

              {/* Schedule */}
              <div className="ch-schedule-row">
                <label className="ch-schedule-label">⏰ SCHEDULE</label>
                <input
                  type="datetime-local"
                  className="ch-datetime"
                  value={composerSchedule}
                  onChange={e => setComposerSchedule(e.target.value)}
                  min={new Date().toISOString().slice(0, 16)}
                />
              </div>

              {/* Actions */}
              <div className="ch-composer-actions">
                <button
                  className="ch-btn secondary"
                  onClick={() => handlePublish(false)}
                  disabled={!composerContent.trim() || composerPlatforms.length === 0 || posting}
                >
                  📅 {posting ? 'PUBLISHING...' : 'QUEUE'}
                </button>
                <button
                  className="ch-btn primary"
                  onClick={() => handlePublish(true)}
                  disabled={!composerContent.trim() || composerPlatforms.length === 0 || posting}
                >
                  {posting ? '⏳...' : '🚀 PUBLISH NOW'}
                </button>
              </div>

              {postResult && (
                <div className={`ch-result ${postResult.success ? 'success' : 'error'}`}>
                  {postResult.msg}
                </div>
              )}

              {/* Blotato status */}
              <div className="ch-blotato-status">
                <div className="ch-blotato-status-label">🔗 BLOTATO STATUS</div>
                {loadingAccounts ? (
                  <div className="ch-blotato-loading">Checking Blotato accounts...</div>
                ) : (
                  accounts.map(acc => (
                    <div key={acc.id} className="ch-account-row">
                      <span>{PLATFORM_ICONS[acc.platform]}</span>
                      <span className="ch-acc-name">{acc.name}</span>
                      <span className={`ch-acc-badge ${acc.connected ? 'connected' : 'disconnected'}`}>
                        {acc.connected ? '● CONNECTED' : '○ DISCONNECTED'}
                      </span>
                    </div>
                  ))
                )}
                <div className="ch-connect-hint">
                  Connect accounts at <strong>app.blotato.com</strong> — then click refresh below
                </div>
                <button className="ch-btn tiny" onClick={() => fetchBlotatoAccounts().then(setAccounts)}>
                  🔄 Refresh accounts
                </button>
              </div>
            </div>

            {/* Right: Queue list */}
            <div className="ch-queue-list">
              <div className="ch-queue-header">
                <span>POST QUEUE</span>
                <span className="ch-queue-count">{queue.length} posts</span>
              </div>
              {queue.map(post => (
                <div key={post.id} className={`ch-queue-item ${post.status}`}>
                  <div className="ch-qi-top">
                    <div className="ch-qi-platforms">
                      {post.platforms.map(p => (
                        <span key={p} style={{ color: PLATFORM_COLORS[p] }}>{PLATFORM_ICONS[p]}</span>
                      ))}
                    </div>
                    <span className={`ch-qi-status ${post.status}`}>{post.status.toUpperCase()}</span>
                  </div>
                  <div className="ch-qi-content">{post.content}</div>
                  <div className="ch-qi-meta">
                    <span>🕐 {new Date(post.scheduledAt).toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' })}</span>
                    <span>👤 {post.createdBy}</span>
                  </div>
                  {post.status === 'draft' && (
                    <div className="ch-qi-actions">
                      <button className="ch-btn tiny" onClick={() => moveToQueue(post.id)}>📅 Move to Queue</button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── CALENDAR VIEW ── */}
        {view === 'calendar' && (
          <div className="ch-calendar">
            <div className="ch-cal-header">
              <div className="ch-cal-title">📅 CONTENT CALENDAR — July 2026</div>
              <div className="ch-cal-nav">
                <button className="ch-btn tiny">◀ Prev</button>
                <button className="ch-btn tiny">Next ▶</button>
              </div>
            </div>
            <div className="ch-cal-grid">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => (
                <div key={d} className="ch-cal-dayhdr">{d}</div>
              ))}
              {Array.from({ length: 31 }, (_, i) => i + 1).map(day => {
                const postsToday = queue.filter(p => {
                  const d = new Date(p.scheduledAt).getDate();
                  return d === day;
                });
                const isToday = day === 5;
                return (
                  <div key={day} className={`ch-cal-cell ${isToday ? 'today' : ''} ${postsToday.length > 0 ? 'has-posts' : ''}`}>
                    <div className="ch-cal-daynum">{day}</div>
                    {postsToday.slice(0, 2).map(p => (
                      <div key={p.id} className={`ch-cal-post ${p.status}`}>
                        {p.platforms.map(pl => PLATFORM_ICONS[pl]).join('')} {p.status === 'draft' ? '✏️' : '📅'}
                      </div>
                    ))}
                    {postsToday.length > 2 && (
                      <div className="ch-cal-more">+{postsToday.length - 2} more</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── ACCOUNTS VIEW ── */}
        {view === 'accounts' && (
          <div className="ch-accounts">
            <div className="ch-acc-title">🔗 BLOTATO CONNECTED ACCOUNTS</div>
            <div className="ch-acc-desc">
              Manage your social accounts at <strong>app.blotato.com</strong>. Robusca connects to Blotato via MCP to publish posts directly.
            </div>
            <div className="ch-acc-list">
              {accounts.map(acc => (
                <div key={acc.id} className="ch-acc-card">
                  <div className="ch-acc-icon" style={{ fontSize: '32px' }}>
                    {acc.platform === 'facebook' ? '📘' : '📷'}
                  </div>
                  <div className="ch-acc-info">
                    <div className="ch-acc-platform">{acc.platform.toUpperCase()}</div>
                    <div className="ch-acc-name">{acc.name}</div>
                    <div className="ch-acc-username">{acc.username}</div>
                  </div>
                  <div className={`ch-acc-status ${acc.connected ? 'connected' : 'disconnected'}`}>
                    {acc.connected ? '✅ CONNECTED' : '❌ DISCONNECTED'}
                  </div>
                </div>
              ))}
            </div>
            <div className="ch-acc-blotato-info">
              <div className="ch-blotato-info-title">🟠 WHAT IS BLOTATO?</div>
              <div className="ch-blotato-info-text">
                Blotato is a social media scheduling tool. Connect Facebook, Instagram, TikTok, LinkedIn, and more.
                Naledi creates content → Robusca pushes to Blotato via MCP → Blotato publishes to all platforms.
                <br /><br />
                <strong>Blotato Plan:</strong> Free tier (3 platforms, 30 posts/month). Upgrade to $29/mo for unlimited.
                <br />
                <strong>Next step:</strong> Connect Meta accounts inside Blotato dashboard, then Robusca can post directly.
              </div>
              <div style={{ marginTop: '12px' }}>
                <span className="ch-btn tiny" style={{ cursor: 'pointer' }} onClick={() => window.open('https://app.blotato.com', '_blank')}>
                  🔗 Open Blotato Dashboard
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
