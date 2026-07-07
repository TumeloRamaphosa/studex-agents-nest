import { useState, useEffect } from 'react';

// ── Types ────────────────────────────────────────────────────────────────────
interface FBPagestats {
  fans: number;
  reach: number;
  impressions: number;
  engagement: number;
  messages: number;
  postsToday: number;
 趋势: string;
}

interface FBPost {
  id: string;
  text: string;
  date: string;
  likes: number;
  comments: number;
  shares: number;
  reach: number;
  type: 'photo' | 'video' | 'text' | 'link';
}

interface WhatsAppStats {
  messagesReceived: number;
  messagesSent: number;
  pending: number;
}

interface AgentMailStats {
  unread: number;
  sent: number;
  bounced: number;
  domain: string;
  status: 'active' | 'pending' | 'invalid';
}

// ── Static data (live refresh can be wired to Meta Graph API) ─────────────────
const PAGE_ID = '108934711902801'; // StudEx Meat Facebook Page
const PAGE_TOKEN = 'EAASNg25ZBOoUBR8dT2diYUmUzfZAspz8r5aneEYoB8fZBBXFkyrFe459n1cZCXczTO4B994nS9F8QRLot1P0ocSsZCgjJpxZAQBwZCzp0vR9SbgSGKKK7w8JxmCHyvKyCE1DdfUwpk4N7x08Pfip4PW2WZBrBBEZCZBwKP4Fy4WjS5sKUIZBU1TJuge6zhAWAZDZD';

const pageStatsDefault: FBPagestats = {
  fans: 2544,
  reach: 0,
  impressions: 0,
  engagement: 0,
  messages: 0,
  postsToday: 0,
  趋势: '↑',
};

const recentPosts: FBPost[] = [
  {
    id: 'p1',
    text: '🐄 StudEx Meat is now live! Premium South African beef, delivered to your door. Order now via WhatsApp 👇',
    date: '2026-07-07',
    likes: 47,
    comments: 6,
    shares: 3,
    reach: 1240,
    type: 'text',
  },
  {
    id: 'p2',
    text: '🍖 Our biltong is hand-crafted from grass-fed RSA beef. Zero artificial preservatives. Pure protein.',
    date: '2026-07-05',
    likes: 89,
    comments: 14,
    shares: 7,
    reach: 2180,
    type: 'photo',
  },
  {
    id: 'p3',
    text: '📦 New stock drop — Wagyu Ribeye and Caviar now available. DM us to order.',
    date: '2026-07-03',
    likes: 63,
    comments: 9,
    shares: 4,
    reach: 1870,
    type: 'photo',
  },
  {
    id: 'p4',
    text: '🇿🇦 Proudly South African. Studex Meat — where heritage meets premium quality.',
    date: '2026-07-01',
    likes: 112,
    comments: 22,
    shares: 15,
    reach: 3420,
    type: 'video',
  },
  {
    id: 'p5',
    text: '☕ Coffee update: Humbe & Sons harvest shipped. Next container loading August.',
    date: '2026-06-28',
    likes: 34,
    comments: 5,
    shares: 2,
    reach: 980,
    type: 'text',
  },
];

const whatsappDefault: WhatsAppStats = {
  messagesReceived: 23,
  messagesSent: 18,
  pending: 2,
};

const mailDefault: AgentMailStats = {
  unread: 4,
  sent: 127,
  bounced: 2,
  domain: 'stud.exchange',
  status: 'pending', // DNS missing per TOOLS.md
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function StatCard({ label, value, sub, accent }: { label: string; value: string | number; sub?: string; accent?: string }) {
  return (
    <div className="comms-stat-card" style={{ borderTop: accent ? `3px solid ${accent}` : undefined }}>
      <div className="comms-stat-label">{label}</div>
      <div className="comms-stat-value" style={{ color: accent || '#4a9eff' }}>{value}</div>
      {sub && <div className="comms-stat-sub">{sub}</div>}
    </div>
  );
}

function PostRow({ post }: { post: FBPost }) {
  const typeIcon = { photo: '📷', video: '🎬', text: '📝', link: '🔗' }[post.type];
  return (
    <div className="comms-post-row">
      <div className="comms-post-icon">{typeIcon}</div>
      <div className="comms-post-body">
        <div className="comms-post-text">{post.text.length > 90 ? post.text.slice(0, 87) + '…' : post.text}</div>
        <div className="comms-post-meta">
          <span>📅 {post.date}</span>
          <span>👁 {post.reach.toLocaleString()}</span>
          <span>❤️ {post.likes}</span>
          <span>💬 {post.comments}</span>
          <span>🔁 {post.shares}</span>
        </div>
      </div>
    </div>
  );
}

function EngagementBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="engagement-row">
      <div className="engagement-label">{label}</div>
      <div className="engagement-bar-bg">
        <div className="engagement-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <div className="engagement-value">{value.toLocaleString()}</div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function CommsPanel() {
  const [pageStats] = useState<FBPagestats>(pageStatsDefault);
  const [whatsapp] = useState<WhatsAppStats>(whatsappDefault);
  const [mail] = useState<AgentMailStats>(mailDefault);
  const [activeSection, setActiveSection] = useState<'overview' | 'posts' | 'whatsapp' | 'mail'>('overview');

  const totalEngagement = recentPosts.reduce((s, p) => s + p.likes + p.comments + p.shares, 0);
  const topPost = [...recentPosts].sort((a, b) => b.reach - a.reach)[0];

  return (
    <div className="comms-root">
      {/* Header */}
      <div className="comms-header">
        <div>
          <div className="comms-title">📡 STUDENT COMMS HUB</div>
          <div className="comms-subtitle">StudEx Meat · Social & Messaging Pipeline</div>
        </div>
        <div className="comms-live-badge">● LIVE</div>
      </div>

      {/* Section tabs */}
      <div className="comms-tabs">
        {(['overview', 'posts', 'whatsapp', 'mail'] as const).map(tab => (
          <button
            key={tab}
            className={`comms-tab ${activeSection === tab ? 'active' : ''}`}
            onClick={() => setActiveSection(tab)}
          >
            {{ overview: '📊 Overview', posts: '📝 Posts', whatsapp: '💬 WhatsApp', mail: '📧 AgentMail' }[tab]}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {activeSection === 'overview' && (
        <div className="comms-section">
          <div className="comms-section-title">Facebook Page — @studexmeat</div>
          <div className="comms-stats-grid">
            <StatCard label="Total Fans" value={pageStats.fans.toLocaleString()} sub="@studexmeat" accent="#4a9eff" />
            <StatCard label="Pending Msgs" value={whatsapp.pending} sub="WhatsApp" accent="#ff8800" />
            <StatCard label="Posts This Week" value={recentPosts.length} sub="5 visible" accent="#3a3aff" />
            <StatCard label="Total Reach" value={recentPosts.reduce((s, p) => s + p.reach, 0).toLocaleString()} sub="last 5 posts" accent="#d4a017" />
          </div>

          <div className="comms-two-col">
            {/* Top Post */}
            <div className="comms-panel">
              <div className="comms-panel-title">🏆 Top Performing Post</div>
              {topPost && (
                <div className="comms-post-row" style={{ border: '1px solid #d4a017', borderRadius: 6, padding: 10, background: 'rgba(212,160,23,0.05)' }}>
                  <div className="comms-post-icon">{'📈'}</div>
                  <div className="comms-post-body">
                    <div className="comms-post-text">{topPost.text}</div>
                    <div className="comms-post-meta">
                      <span>📅 {topPost.date}</span>
                      <span>👁 {topPost.reach.toLocaleString()} reach</span>
                      <span>❤️ {topPost.likes} likes</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Engagement breakdown */}
            <div className="comms-panel">
              <div className="comms-panel-title">📊 Weekly Engagement</div>
              <div style={{ padding: '8px 0' }}>
                <EngagementBar label="Likes" value={recentPosts.reduce((s, p) => s + p.likes, 0)} max={500} color="#4a9eff" />
                <EngagementBar label="Comments" value={recentPosts.reduce((s, p) => s + p.comments, 0)} max={100} color="#3a3aff" />
                <EngagementBar label="Shares" value={recentPosts.reduce((s, p) => s + p.shares, 0)} max={50} color="#d4a017" />
                <EngagementBar label="Total Reach" value={recentPosts.reduce((s, p) => s + p.reach, 0)} max={10000} color="#ff8800" />
              </div>
            </div>
          </div>

          {/* Pipeline alerts */}
          <div className="comms-alerts">
            <div className="comms-alert warn">
              ⚠️ <strong>Meta User Token</strong> expired Jun 22 — ad analytics blocked. Refresh at developers.facebook.com
            </div>
            <div className="comms-alert info">
              💡 <strong>Blotato</strong> — 0 accounts connected. Connect FB/IG in dashboard to enable auto-posting.
            </div>
            <div className="comms-alert error">
              🚫 <strong>AgentMail domain</strong> (stud.exchange) — DNS MISSING. Set MX records to enable inbound.
            </div>
          </div>
        </div>
      )}

      {/* ── Posts ── */}
      {activeSection === 'posts' && (
        <div className="comms-section">
          <div className="comms-section-title">Recent Posts — @studexmeat</div>
          <div className="comms-posts-list">
            {recentPosts.map(post => <PostRow key={post.id} post={post} />)}
          </div>
          <div className="comms-action-bar">
            <button className="comms-btn primary" onClick={() => window.open('https://business.facebook.com', '_blank')}>
              📝 Compose New Post
            </button>
            <button className="comms-btn secondary" onClick={() => setActiveSection('whatsapp')}>
              📋 View WhatsApp Broadcast
            </button>
          </div>
        </div>
      )}

      {/* ── WhatsApp ── */}
      {activeSection === 'whatsapp' && (
        <div className="comms-section">
          <div className="comms-section-title">WhatsApp Business</div>
          <div className="comms-stats-grid">
            <StatCard label="Received (7d)" value={whatsapp.messagesReceived} accent="#25d366" />
            <StatCard label="Sent (7d)" value={whatsapp.messagesSent} accent="#128c7e" />
            <StatCard label="Pending Reply" value={whatsapp.pending} accent="#ff8800" />
            <StatCard label="Accounts" value={2} sub="Business ID: 599570915061463" accent="#25d366" />
          </div>
          <div className="comms-panel" style={{ marginTop: 16 }}>
            <div className="comms-panel-title">Quick Actions</div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
              <button className="comms-btn primary" onClick={() => window.open('https://business.facebook.com', '_blank')}>
                📤 Send Broadcast
              </button>
              <button className="comms-btn secondary" onClick={() => window.open('https://wa.me/27721234567', '_blank')}>
                💬 Open WhatsApp
              </button>
              <button className="comms-btn secondary" onClick={() => window.open('https://app.agentmail.to', '_blank')}>
                🔗 AgentMail Setup
              </button>
            </div>
          </div>
          <div className="comms-alerts" style={{ marginTop: 16 }}>
            <div className="comms-alert info">
              💡 Naledi (CMO agent) can send WhatsApp broadcasts once Blotato is connected to the Meta page.
            </div>
          </div>
        </div>
      )}

      {/* ── AgentMail ── */}
      {activeSection === 'mail' && (
        <div className="comms-section">
          <div className="comms-section-title">AgentMail — stud.exchange</div>
          <div className="comms-stats-grid">
            <StatCard label="Unread" value={mail.unread} accent="#ff4444" />
            <StatCard label="Sent (total)" value={mail.sent} accent="#4a9eff" />
            <StatCard label="Bounced" value={mail.bounced} accent="#ff8800" />
            <StatCard label="Domain Status" value={mail.status.toUpperCase()} sub={mail.domain} accent={mail.status === 'active' ? '#25d366' : '#ff4444'} />
          </div>

          <div className="comms-panel" style={{ marginTop: 16 }}>
            <div className="comms-panel-title">Email Addresses</div>
            <table className="comms-table">
              <thead>
                <tr><th>Agent</th><th>Address</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr><td>🤖 Robusca (CEO)</td><td>ceo@stud.exchange</td><td style={{ color: '#ff4444' }}>⚠ DNS Missing</td></tr>
                <tr><td>📣 Naledi (CMO)</td><td>naledi@stud.exchange</td><td style={{ color: '#ff4444' }}>⚠ DNS Missing</td></tr>
                <tr><td>🕵️ Charlie (Ops)</td><td>charlie@stud.exchange</td><td style={{ color: '#ff4444' }}>⚠ DNS Missing</td></tr>
              </tbody>
            </table>
          </div>

          <div className="comms-alerts" style={{ marginTop: 16 }}>
            <div className="comms-alert error">
              🚫 <strong>DNS not configured</strong> for stud.exchange. Add MX record pointing to <code>mx.agentmail.to</code>
            </div>
            <div className="comms-alert warn">
              ⚠️ Warmup inbox score is low (0/100). Run the email warmup script daily to improve deliverability.
            </div>
            <div className="comms-alert info">
              💡 AgentMail API: <code>https://api.agentmail.to/v0/</code> — can send via Naledi once DNS is live.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
