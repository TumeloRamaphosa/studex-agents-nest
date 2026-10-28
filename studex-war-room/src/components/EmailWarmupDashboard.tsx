import { useState, useEffect } from 'react';

interface WarmupState {
  startDate: string;
  totalSent: number;
  dailyLogs: Record<string, { date: string; sent: number; opened?: number; replied?: number }>;
}

interface InboxStatus {
  address: string;
  name: string;
  priority: number;
  warmupDay: number;
  volumeToday: number;
  sentToday: number;
  totalSent: number;
  status: 'cold' | 'warming' | 'active' | 'strong';
  estimatedReputation: 'poor' | 'fair' | 'good' | 'excellent';
  lastWarmup: string | null;
  nextWarmup: string;
  volumeSchedule: { week: string; daily: number };
}

const INBOXES: Omit<InboxStatus, 'warmupDay' | 'volumeToday' | 'sentToday' | 'totalSent' | 'status' | 'estimatedReputation' | 'lastWarmup' | 'nextWarmup' | 'volumeSchedule'>[] = [
  { address: 'robusca.romanov@studex-group.com', name: 'Robusca CEO', priority: 1 },
  { address: 'naledi-cmo@studex-group.com', name: 'Naledi CMO', priority: 2 },
  { address: 'info@studex-group.com', name: 'StudEx General', priority: 3 },
];

const VOLUME_SCHEDULE: Record<string, { week: string; daily: number; label: string }> = {
  week1: { week: 'week1', daily: 2, label: 'Cold Start — 2/day' },
  week2: { week: 'week2', daily: 4, label: 'Ramping — 4/day' },
  week3: { week: 'week3', daily: 7, label: 'Building — 7/day' },
  week4: { week: 'week4', daily: 10, label: 'Active — 10/day' },
};

const WARMUP_TARGETS = [
  'tumelor001@gmail.com',
  'robusca.romanov@outlook.com',
  'naledi.services@gmail.com',
];

const REPUTATION_THRESHOLDS = {
  poor: { min: 0, color: '#ff4444', label: 'POOR', days: 0 },
  fair: { min: 14, color: '#ffaa44', label: 'FAIR', days: 14 },
  good: { min: 28, color: '#4a9eff', label: 'GOOD', days: 28 },
  excellent: { min: 42, color: '#4aff88', label: 'EXCELLENT', days: 42 },
};

function getWarmupWeek(startDate: string): { week: string; daily: number; label: string } {
  const days = Math.floor((Date.now() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24));
  if (days < 7) return VOLUME_SCHEDULE.week1;
  if (days < 14) return VOLUME_SCHEDULE.week2;
  if (days < 21) return VOLUME_SCHEDULE.week3;
  return VOLUME_SCHEDULE.week4;
}

function getReputation(totalSent: number): { level: InboxStatus['estimatedReputation']; color: string; label: string; daysToGood: number } {
  const days = Math.floor(totalSent / 3); // rough estimate: 3 emails/day avg
  if (days >= 42) return { level: 'excellent', color: '#4aff88', label: 'EXCELLENT', daysToGood: 0 };
  if (days >= 28) return { level: 'good', color: '#4a9eff', label: 'GOOD', daysToGood: 42 - days };
  if (days >= 14) return { level: 'fair', color: '#ffaa44', label: 'FAIR', daysToGood: 28 - days };
  return { level: 'poor', color: '#ff4444', label: 'POOR', daysToGood: 14 - days };
}

function getInboxStatus(inbox: typeof INBOXES[0], state: WarmupState): InboxStatus {
  const today = new Date().toISOString().split('T')[0];
  const daysSinceStart = Math.floor((Date.now() - new Date(state.startDate).getTime()) / (1000 * 60 * 60 * 24));
  const week = getWarmupWeek(state.startDate);
  const dailyLog = state.dailyLogs?.[inbox.address];
  const sent = dailyLog?.date === today ? (dailyLog?.sent ?? 0) : 0;
  const total = Object.values(state.dailyLogs ?? {}).reduce((s, l) => s + (l.sent ?? 0), 0);

  const reputation = getReputation(total);
  const warmupDay = Math.min(daysSinceStart + 1, 28);
  const isWarmedUp = total >= 30;
  const isActive = total >= 60;

  let status: InboxStatus['status'] = 'cold';
  if (isActive) status = 'strong';
  else if (isWarmedUp) status = 'active';
  else if (daysSinceStart > 0) status = 'warming';

  const nextWarmupTime = new Date();
  nextWarmupTime.setDate(nextWarmupTime.getDate() + 1);
  nextWarmupTime.setHours(9, 0, 0, 0);

  return {
    ...inbox,
    warmupDay,
    volumeToday: week.daily,
    sentToday: sent,
    totalSent: total,
    status,
    estimatedReputation: reputation.level,
    lastWarmup: dailyLog?.date ?? null,
    nextWarmup: nextWarmupTime.toLocaleString('en-ZA', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }),
    volumeSchedule: { week: Object.keys(VOLUME_SCHEDULE).find(k => VOLUME_SCHEDULE[k].daily === week.daily) ?? 'week1', daily: week.daily },
  };
}

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  cold:    { color: '#7a8099', label: 'COLD' },
  warming: { color: '#ffaa44', label: 'WARMING' },
  active: { color: '#4a9eff', label: 'ACTIVE' },
  strong:  { color: '#4aff88', label: 'STRONG' },
};

export default function EmailWarmupDashboard() {
  const [state, setState] = useState<WarmupState | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<string>('');
  const [runError, setRunError] = useState<string>('');

  const START_DATE = '2026-07-29T00:00:00.000Z';

  useEffect(() => {
    fetchState();
  }, []);

  async function fetchState() {
    try {
      // Read state from the JSON file the warmup script writes to public/
      const res = await fetch('/warmup-state.json');
      if (res.ok) {
        const data = await res.json();
        setState(data);
      } else {
        setState({ startDate: START_DATE, totalSent: 0, dailyLogs: {} });
      }
    } catch {
      setState({ startDate: START_DATE, totalSent: 0, dailyLogs: {} });
    } finally {
      setLoading(false);
    }
  }

  async function runWarmup(dryRun = false) {
    setRunning(true);
    setRunResult('');
    setRunError('');
    try {
      // Run the warmup script via a server-side endpoint
      // In production this calls: POST /api/warmup/run
      // For now: simulate a successful run and show the command
      await new Promise(r => setTimeout(r, 800));
      const cmd = `cd /workspace/studex-email-warmup && node warmup.js${dryRun ? ' --dry-run' : ''}`;
      if (dryRun) {
        setRunResult(`Dry run ready. Command: ${cmd}`);
      } else {
        // Attempt actual run via fetch to a potential backend route
        try {
          const res = await fetch('/api/warmup/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dryRun: false }),
          });
          if (res.ok) {
            const data = await res.json();
            setRunResult(`Warmup complete — ${data.sent ?? '?'} emails sent`);
            fetchState();
          } else {
            setRunResult(`⚠️  Backend not available. Run manually: ${cmd}`);
          }
        } catch {
          setRunResult(`⚠️  Run manually in terminal: ${cmd}`);
        }
      }
    } finally {
      setRunning(false);
    }
  }

  const week = state ? getWarmupWeek(state.startDate) : VOLUME_SCHEDULE.week1;
  const inboxes = state ? INBOXES.map(i => getInboxStatus(i, state)) : [];

  const totalSentAll = inboxes.reduce((s, i) => s + i.totalSent, 0);
  const warmedInboxes = inboxes.filter(i => i.status !== 'cold').length;
  const strongestInbox = inboxes.reduce((best, i) => i.totalSent > (best?.totalSent ?? 0) ? i : best, inboxes[0]);
  const avgReputation = getReputation(Math.round(totalSentAll / Math.max(inboxes.length, 1)));

  const dailyHistory = state
    ? Object.entries(state.dailyLogs).flatMap(([addr, log]) =>
        (log as any).sent
          ? [{ date: log.date, inbox: addr.split('@')[0], sent: (log as any).sent }]
          : []
      ).sort((a, b) => b.date.localeCompare(a.date)).slice(0, 14)
    : [];

  if (loading) {
    return <div className="warmup-loading">Loading warmup status...</div>;
  }

  return (
    <div className="email-warmup-dashboard">
      {/* ── Header ── */}
      <div className="wud-header">
        <div className="wud-title">
          <span style={{ fontSize: '20px' }}>📧</span>
          <span>EMAIL WARMUP COMMAND CENTER</span>
          <span className="wud-badge" style={{ backgroundColor: avgReputation.color }}>
            {avgReputation.label} REPUTATION
          </span>
        </div>
        <div className="wud-actions">
          <button className="wud-btn secondary" onClick={() => runWarmup(true)} disabled={running}>
            🔍 Dry Run
          </button>
          <button className="wud-btn primary" onClick={() => runWarmup(false)} disabled={running}>
            {running ? '⏳ Running...' : '▶️ Run Warmup Now'}
          </button>
        </div>
      </div>

      {/* ── Run Result ── */}
      {runResult && (
        <div className="wud-alert success">
          ✅ {runResult}
          <button className="wud-alert-close" onClick={() => setRunResult('')}>✕</button>
        </div>
      )}
      {runError && (
        <div className="wud-alert error">
          ❌ {runError}
          <button className="wud-alert-close" onClick={() => setRunError('')}>✕</button>
        </div>
      )}

      {/* ── KPI Row ── */}
      <div className="wud-kpis">
        <div className="wud-kpi">
          <div className="wud-kpi-val" style={{ color: '#4a9eff' }}>{totalSentAll}</div>
          <div className="wud-kpi-lbl">TOTAL EMAILS SENT</div>
          <div className="wud-kpi-sub">across all inboxes</div>
        </div>
        <div className="wud-kpi">
          <div className="wud-kpi-val" style={{ color: '#4aff88' }}>{warmedInboxes}/{inboxes.length}</div>
          <div className="wud-kpi-lbl">INBOXES WARMED</div>
          <div className="wud-kpi-sub">active or stronger</div>
        </div>
        <div className="wud-kpi">
          <div className="wud-kpi-val" style={{ color: '#d4a017' }}>{week.daily}/day</div>
          <div className="wud-kpi-lbl">CURRENT VOLUME</div>
          <div className="wud-kpi-sub">{week.label}</div>
        </div>
        <div className="wud-kpi">
          <div className="wud-kpi-val" style={{ color: '#ff6eb4' }}>
            {strongestInbox ? strongestInbox.name.split(' ')[0] : '—'}
          </div>
          <div className="wud-kpi-lbl">TOP INBOX</div>
          <div className="wud-kpi-sub">
            {strongestInbox ? `${strongestInbox.totalSent} total` : '—'}
          </div>
        </div>
        <div className="wud-kpi">
          <div className="wud-kpi-val" style={{ color: '#7a8099' }}>
            {avgReputation.daysToGood > 0 ? `${avgReputation.daysToGood}d` : '✅'}
          </div>
          <div className="wud-kpi-lbl">TO GOOD REPUTATION</div>
          <div className="wud-kpi-sub">{avgReputation.daysToGood > 0 ? 'until ~Good' : 'ready for outreach'}</div>
        </div>
        <div className="wud-kpi">
          <div className="wud-kpi-val" style={{ color: '#4a9eff' }}>
            {state ? Math.floor((Date.now() - new Date(state.startDate).getTime()) / (1000 * 60 * 60 * 24)) + 1 : 0}d
          </div>
          <div className="wud-kpi-lbl">WARMUP AGE</div>
          <div className="wud-kpi-sub">since Jul 29</div>
        </div>
      </div>

      {/* ── Volume Schedule ── */}
      <div className="wud-schedule">
        <div className="wud-section-title">📅 4-WEEK VOLUME SCHEDULE</div>
        <div className="wud-schedule-grid">
          {Object.entries(VOLUME_SCHEDULE).map(([wk, cfg]) => {
            const isCurrent = cfg.daily === week.daily;
            const isPast = Object.values(VOLUME_SCHEDULE).indexOf(cfg) < Object.values(VOLUME_SCHEDULE).indexOf(week);
            return (
              <div key={wk} className={`wud-schedule-card ${isCurrent ? 'current' : ''} ${isPast ? 'past' : 'future'}`}>
                <div className="wsc-week">{wk.toUpperCase()}</div>
                <div className="wsc-daily">{cfg.daily} emails/day</div>
                <div className="wsc-label">{cfg.label}</div>
                {isCurrent && <div className="wsc-badge">CURRENT</div>}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Inbox Cards ── */}
      <div className="wud-section-title">📬 INBOX STATUS</div>
      <div className="wud-inbox-grid">
        {inboxes.map(inbox => {
          const cfg = STATUS_CONFIG[inbox.status];
          const rep = getReputation(inbox.totalSent);
          return (
            <div key={inbox.address} className="wud-inbox-card">
              <div className="wic-header" style={{ borderColor: cfg.color }}>
                <div className="wic-name">{inbox.name}</div>
                <div className="wic-status" style={{ color: cfg.color }}>{cfg.label}</div>
              </div>
              <div className="wic-address">{inbox.address}</div>

              <div className="wic-metrics">
                <div className="wic-metric">
                  <span className="wic-mval">{inbox.totalSent}</span>
                  <span className="wic-mlbl">TOTAL SENT</span>
                </div>
                <div className="wic-metric">
                  <span className="wic-mval" style={{ color: inbox.sentToday > 0 ? '#4aff88' : '#7a8099' }}>
                    {inbox.sentToday}/{inbox.volumeToday}
                  </span>
                  <span className="wic-mlbl">TODAY</span>
                </div>
                <div className="wic-metric">
                  <span className="wic-mval">Day {inbox.warmupDay}</span>
                  <span className="wic-mlbl">WARMUP DAY</span>
                </div>
              </div>

              <div className="wic-reputation">
                <div className="wic-rep-label">REPUTATION</div>
                <div className="wic-rep-bar-bg">
                  <div
                    className="wic-rep-bar-fill"
                    style={{ width: `${Math.min((inbox.totalSent / 60) * 100, 100)}%`, backgroundColor: rep.color }}
                  />
                </div>
                <div className="wic-rep-badge" style={{ color: rep.color }}>{rep.label}</div>
              </div>

              <div className="wic-footer">
                <div className="wic-next">
                  <span className="wic-next-label">NEXT WARMUP</span>
                  <span className="wic-next-time">{inbox.nextWarmup}</span>
                </div>
                {inbox.lastWarmup && (
                  <div className="wic-last">
                    <span className="wic-next-label">LAST WARMUP</span>
                    <span className="wic-next-time">{inbox.lastWarmup}</span>
                  </div>
                )}
              </div>

              {inbox.status === 'cold' && (
                <div className="wic-cta">
                  ⚠️ Never warmed — run warmup to begin building reputation
                </div>
              )}
              {inbox.status === 'strong' && (
                <div className="wic-cta success">
                  ✅ Inbox fully warmed — ready for UAE/China outreach
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Warmup Targets ── */}
      <div className="wud-section-title">🎯 WARMUP TARGETS (safe senders)</div>
      <div className="wud-targets">
        {WARMUP_TARGETS.map(t => (
          <div key={t} className="wud-target-chip">{t}</div>
        ))}
        <div className="wud-target-note">
          These addresses auto-mark Studex emails as important — builds positive sender reputation
        </div>
      </div>

      {/* ── Daily History ── */}
      {dailyHistory.length > 0 && (
        <>
          <div className="wud-section-title">📊 14-DAY SEND HISTORY</div>
          <div className="wud-history">
            {dailyHistory.map((h, i) => (
              <div key={i} className="wud-history-row">
                <span className="whr-date">{h.date}</span>
                <span className="whr-inbox">{h.inbox}</span>
                <div className="whr-bar-bg">
                  <div className="whr-bar-fill" style={{ width: `${Math.min((h.sent / 10) * 100, 100)}%` }} />
                </div>
                <span className="whr-sent">{h.sent} sent</span>
              </div>
            ))}
          </div>
        </>
      )}

      {/* ── Cron Setup ── */}
      <div className="wud-section-title">⏰ AUTOMATED SCHEDULE</div>
      <div className="wud-cron-box">
        <div className="wud-cron-cmd">
          <code># Add to crontab — runs daily at 09:00 SAST</code>
          <code>0 9 * * * cd /workspace/studex-email-warmup \&\& node warmup.js \&gt;\&gt; /workspace/studex-email-warmup/warmup.log 2\&gt;&amp;1</code>
        </div>
        <div className="wud-cron-note">
          Cron job runs warmup automatically each morning. Monitor via this dashboard.
          Volume ramps from 2 → 10 emails/day over 4 weeks.
        </div>
      </div>
    </div>
  );
}
