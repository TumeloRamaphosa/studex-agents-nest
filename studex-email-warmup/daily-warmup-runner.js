#!/usr/bin/env node
/**
 * Studex Daily Warmup Runner
 * ==============================
 * Cron-able script: runs the warmup engine, generates HTML report,
 * and emails it to Tumelo via AgentMail.
 *
 * Schedule (cron): 0 9 * * *  (09:00 SAST daily)
 * Run manually: node daily-warmup-runner.js [--dry-run]
 *
 * Output state mirrored to: /workspace/studex-war-room/public/warmup-state.json
 * so the War Room EmailWarmupDashboard reads live data.
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createHash } from 'crypto';
import dotenv from 'dotenv';

// Load the workspace-level .env (the script's own dir has none), then fall back
// to a local .env so the script also works standalone.
dotenv.config({ path: '/workspace/.env' });
dotenv.config();

// ─── Config ────────────────────────────────────────────────────────────────
const STATE_FILE     = '/workspace/studex-email-warmup/state.json';
const LOG_FILE       = '/workspace/studex-email-warmup/warmup.log';
const PUBLIC_STATE   = '/workspace/studex-war-room/public/warmup-state.json';
// AGENTMAIL_API_KEY is revoked (403 Forbidden on every route). The warmup and
// main keys are verified working, so prefer those.
const AGENTMAIL_KEY  = process.env.AGENTMAIL_WARMUP_API_KEY
  || process.env.AGENTMAIL_MAIN_API_KEY
  || process.env.AGENTMAIL_API_KEY
  || '';
const AGENTMAIL_BASE = 'https://api.agentmail.to/v0';

const RECIPIENT = { address: 'tumelor001@gmail.com', name: 'Tumelo Ramaphosa' };

// ─── Volume schedule ────────────────────────────────────────────────────────
const VOLUME = { week1: 2, week2: 4, week3: 7, week4: 10 };

// Varied subjects (rotating)
const SUBJECTS = [
  'Q3 pipeline review — Studex',
  'Re: Sample shipment update',
  'Follow-up: Rwanda A1 availability',
  'CIIE 2026 — buyer meetings',
  'Quick question on your order',
  'RE: Dubai meeting notes',
  'Coffee origin documentation attached',
  'Re: Tumelo — introduction',
  'Studex product catalog update',
  'Re: cupping sample feedback',
  'CIIE Shanghai Nov 5-10 — buyer meetings',
  'Pricing update — Q3',
  'RE: Luckin Coffee opportunity',
  'Delivery confirmation — Sandton',
  'Re: GCC distribution interest',
  'Weekly update — Studex',
  'Re: Rwanda harvest schedule',
  'Studex partner inquiry',
  'Re: Rwanda A1 documentation',
  'Studex Meat — quarterly review',
];

// Warmup bodies
const BODIES = [
  `Hi,\n\nHope you're well. Quick follow-up on our conversation last week.\n\nI've attached the updated Rwanda A1/A2 product sheet — let me know if you need anything else before CIIE.\n\nBest,\nTumelo\nStudex Group`,
  `Hello,\n\nThank you for your interest in Studex Premium. Our Rwanda A1 Washed lot is available for sample shipment from October.\n\nHappy to arrange a call this week to discuss requirements.\n\nRegards,\nTumelo Ramaphosa\nStudex Group`,
  `Hi there,\n\nJust circling back on the Dubai distributor conversation. We're seeing strong interest from UAE importers given the China zero-tariff corridor.\n\nWould a call Thursday work?\n\nBest,\nTumelo`,
  `Good day,\n\nIf you're attending CIIE 2026 in Shanghai (5-10 November), I'd love to arrange a meeting.\n\nWe're showcasing Rwanda A1/A2 green coffee — the timing aligns with your China procurement cycle.\n\nTumelo\nStudex Group`,
  `Hi,\n\nQuick question — did the cupping sample arrive safely? Happy to send a follow-up lot if you'd like to compare.\n\nBest regards,\nTumelo`,
  `Hello,\n\nFollowing up on our discussion about the Studex Premium range. We have caviar (Oscietra Imperial, Kaluga Prestige, Sevtruga Medium) and biltong available for Q4 gifting season.\n\nCatalog attached.\n\nTumelo`,
];

const WARMUP_TARGETS = [
  { name: 'Tumelo Personal', address: 'tumelor001@gmail.com' },
];

// Per-inbox API keys (more granular access control).
// A credential can only act on inboxes visible to it, so each inbox is bound to
// a key that actually owns it:
//   - robusca.romanov@ / naledi-cmo@  -> warmup or main key (10 shared inboxes)
//   - project-2571-studex-agent-2077@  -> CIIE key (3 separate inboxes)
const INBOX_KEYS = {
  'robusca.romanov@studex-group.com':
    process.env.AGENTMAIL_WARMUP_API_KEY || process.env.AGENTMAIL_MAIN_API_KEY || '',
  'naledi-cmo@studex-group.com':
    process.env.AGENTMAIL_WARMUP_API_KEY || process.env.AGENTMAIL_MAIN_API_KEY || '',
  'project-2571-studex-agent-2077@agentmail.to':
    process.env.AGENTMAIL_CIIE_KEY || process.env.AGENTMAIL_WARMUP_API_KEY || '',
};

function getInboxKey(inboxAddress) {
  return INBOX_KEYS[inboxAddress] || AGENTMAIL_KEY;
}

// ─── Helpers ────────────────────────────────────────────────────────────────
function shuffle(arr) {
  return [...arr].sort(() => 0.5 - Math.random());
}

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

// The body is interpolated into an HTML email - escape it, so a stray
// ampersand or angle bracket in the copy cannot break the markup.
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

async function agentMailReq(inboxAddress, endpoint, options = {}) {
  const key = getInboxKey(inboxAddress);
  const res = await fetch(`${AGENTMAIL_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`AgentMail ${res.status}: ${JSON.stringify(data)}`);
  return data;
}

async function sendEmail(from, to, subject, html) {
  // AgentMail v0: POST /v0/inboxes/{inbox_id}/messages/send
  return agentMailReq(from.address, `/inboxes/${encodeURIComponent(from.address)}/messages/send`, {
    method: 'POST',
    body: JSON.stringify({ to: [to], subject, html }),
  });
}

function loadState() {
  try {
    return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { startDate: new Date().toISOString(), totalSent: 0, dailyLogs: {} };
  }
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  try { writeFileSync(PUBLIC_STATE, JSON.stringify(state, null, 2)); } catch { /* non-fatal */ }
}

function appendLog(line) {
  const ts = new Date().toISOString();
  const entry = `[${ts}] ${line}\n`;
  try { writeFileSync(LOG_FILE, entry, { flag: 'a' }); } catch { /* non-fatal */ }
}

// ─── Warmup one inbox ────────────────────────────────────────────────────────
async function warmupInbox(inbox, dailyLimit, dryRun = false) {
  const results = { sent: 0, failed: 0, skipped: 0, errors: [] };
  const targets = shuffle(WARMUP_TARGETS);
  const today = new Date().toISOString().split('T')[0];

  for (let i = 0; i < dailyLimit; i++) {
    const target = targets[i % targets.length];
    const subject = pick(SUBJECTS);
    const body = pick(BODIES);

    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <div style="background: #1a1a1a; color: #e0c875; padding: 20px; border-radius: 8px 8px 0 0;">
          <strong>Studex Group</strong> — Internal Warmup #${i + 1}
        </div>
        <div style="background: #fafafa; padding: 20px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
          <p style="margin: 0 0 12px; white-space: pre-wrap; line-height: 1.6;">${escapeHtml(body).replace(/\n/g, '<br>')}</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 16px 0;">
          <p style="font-size: 12px; color: #999;">Sent via Studex Email Warmup Engine · ${today}</p>
        </div>
      </div>`;

    if (dryRun) {
      results.skipped++;
      appendLog(`[DRY] ${inbox.address} → ${target.address}: ${subject}`);
      continue;
    }

    try {
      await sendEmail({ address: inbox.address, name: inbox.name }, target.address, subject, html);
      results.sent++;
      appendLog(`[SENT] ${inbox.address} → ${target.address}: ${subject}`);
      // 3–8s between sends to appear natural
      await new Promise(r => setTimeout(r, 3000 + Math.random() * 5000));
    } catch (err) {
      results.failed++;
      results.errors.push(err.message);
      appendLog(`[FAIL] ${inbox.address} → ${target.address}: ${err.message}`);
    }
  }
  return results;
}

// ─── HTML Report Generator ──────────────────────────────────────────────────
function buildHtmlReport(state, week, volume, resultsPerInbox, dryRun) {
  const today = new Date().toLocaleDateString('en-ZA', { timeZone: 'Africa/Johannesburg', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const totalSent = resultsPerInbox.reduce((s, r) => s + r.sent, 0);
  const totalFailed = resultsPerInbox.reduce((s, r) => s + r.failed, 0);
  const daysRunning = Math.floor((Date.now() - new Date(state.startDate).getTime()) / 86400000);

  const inboxRows = resultsPerInbox.map(r => `
    <tr>
      <td style="padding: 10px 14px; border-bottom: 1px solid #eee; font-weight: bold;">${r.inbox}</td>
      <td style="padding: 10px 14px; border-bottom: 1px solid #eee; color: #22c55e;">${r.sent}</td>
      <td style="padding: 10px 14px; border-bottom: 1px solid #eee; color: #ef4444;">${r.failed}</td>
      <td style="padding: 10px 14px; border-bottom: 1px solid #eee; color: #f59e0b;">${r.skipped}</td>
      <td style="padding: 10px 14px; border-bottom: 1px solid #eee; font-size: 12px; color: #666;">${r.errors.slice(0, 2).join(', ') || '—'}</td>
    </tr>`).join('');

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Studex Warmup Report — ${today}</title>
</head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px;">
  <div style="max-width: 640px; margin: auto;">

    <!-- Header -->
    <div style="background: linear-gradient(135deg, #1a1a1a, #2a2a2a); color: white; padding: 28px 32px; border-radius: 12px 12px 0 0;">
      <div style="font-size: 11px; letter-spacing: 2px; color: #e0c875; margin-bottom: 6px;">STUDEX OS // AUTOMATED REPORT</div>
      <h1 style="margin: 0; font-size: 22px; font-weight: bold;">🐔 Email Warmup Engine</h1>
      <div style="margin-top: 8px; font-size: 14px; color: #aaa;">${today} · SAST</div>
      ${dryRun ? '<div style="margin-top: 10px; background: #f59e0b; color: #000; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: bold; display: inline-block;">⚠️ DRY RUN — NO EMAILS SENT</div>' : ''}
    </div>

    <!-- KPI Row -->
    <div style="background: white; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; border: 1px solid #e0e0e0; border-top: none;">
      <div style="background: #fafafa; padding: 16px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold; color: #1a1a1a;">${volume.daily}</div>
        <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Today</div>
      </div>
      <div style="background: #fafafa; padding: 16px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold; color: #22c55e;">${totalSent}</div>
        <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Sent</div>
      </div>
      <div style="background: #fafafa; padding: 16px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold; color: #ef4444;">${totalFailed}</div>
        <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Failed</div>
      </div>
      <div style="background: #fafafa; padding: 16px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold; color: #1a1a1a;">${state.totalSent}</div>
        <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">All-Time</div>
      </div>
    </div>

    <!-- Campaign Summary -->
    <div style="background: white; padding: 24px 28px; border: 1px solid #e0e0e0; border-top: none;">
      <h2 style="margin: 0 0 16px; font-size: 16px; color: #1a1a1a; border-bottom: 2px solid #e0c875; padding-bottom: 8px;">Campaign Summary</h2>
      <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
        <thead>
          <tr style="background: #fafafa;">
            <th style="padding: 8px 14px; text-align: left; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Inbox</th>
            <th style="padding: 8px 14px; text-align: center; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">✅ Sent</th>
            <th style="padding: 8px 14px; text-align: center; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">❌ Failed</th>
            <th style="padding: 8px 14px; text-align: center; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">⏭️ Skip</th>
            <th style="padding: 8px 14px; text-align: left; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Notes</th>
          </tr>
        </thead>
        <tbody>${inboxRows}</tbody>
      </table>
    </div>

    <!-- Warmup Progress -->
    <div style="background: white; padding: 24px 28px; border: 1px solid #e0e0e0; border-top: none;">
      <h2 style="margin: 0 0 16px; font-size: 16px; color: #1a1a1a; border-bottom: 2px solid #e0c875; padding-bottom: 8px;">Warmup Progress</h2>
      <table style="width: 100%; font-size: 14px;">
        <tr><td style="padding: 6px 0; color: #666;">Started</td><td style="text-align: right; font-weight: bold;">${state.startDate.split('T')[0]}</td></tr>
        <tr><td style="padding: 6px 0; color: #666;">Days running</td><td style="text-align: right; font-weight: bold;">${daysRunning}</td></tr>
        <tr><td style="padding: 6px 0; color: #666;">Current week</td><td style="text-align: right; font-weight: bold; color: #e0c875; background: #1a1a1a; padding: 2px 8px; border-radius: 4px; display: inline-block;">${week.toUpperCase()}</td></tr>
        <tr><td style="padding: 6px 0; color: #666;">Daily volume</td><td style="text-align: right; font-weight: bold;">${volume.daily} emails/inbox</td></tr>
        <tr><td style="padding: 6px 0; color: #666;">Phase target</td><td style="text-align: right;">${volume.daily < 5 ? 'Ramp-up' : volume.daily < 8 ? 'Building' : 'Active'}</td></tr>
      </table>
    </div>

    <!-- Footer -->
    <div style="background: #1a1a1a; color: #555; padding: 16px 28px; border-radius: 0 0 12px 12px; font-size: 12px; text-align: center;">
      Studex Email Warmup Engine · Nightly run at 09:00 SAST · Built by Robusca CEO
    </div>

  </div>
</body>
</html>`;
}

// ─── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const today  = new Date().toISOString().split('T')[0];

  console.log('\n🐔 Studex Daily Warmup Runner');
  console.log('═'.repeat(50));
  console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'}`);
  console.log(`Time: ${new Date().toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' })} SAST`);

  // Load state
  const state = loadState();
  const week  = (() => {
    const days = Math.floor((Date.now() - new Date(state.startDate).getTime()) / 86400000);
    if (days < 7)  return 'week1';
    if (days < 14) return 'week2';
    if (days < 21) return 'week3';
    return 'week4';
  })();
  const volume = { daily: VOLUME[week] || 10 };

  appendLog(`=== Warmup run started — ${today} — ${dryRun ? 'DRY' : 'LIVE'} ===`);

  const INBOXES = [
    { address: 'robusca.romanov@studex-group.com',   name: 'Robusca CEO' },
    { address: 'naledi-cmo@studex-group.com',          name: 'Naledi CMO' },
    { address: 'project-2571-studex-agent-2077@agentmail.to', name: 'StudEx General' },
  ];

  const resultsPerInbox = [];

  for (const inbox of INBOXES) {
    console.log(`\n🎯 ${inbox.address}`);

    // Skip if already run today
    const key = `dailyLogs.${inbox.address}.date`;
    const lastRun = state.dailyLogs?.[inbox.address]?.date;
    if (lastRun === today && !dryRun) {
      console.log(`⏭️  Already run today — skipping`);
      resultsPerInbox.push({ inbox: inbox.address, sent: 0, failed: 0, skipped: 0, errors: ['Already run'] });
      continue;
    }

    const result = await warmupInbox(inbox, volume.daily, dryRun);
    result.inbox = inbox.address;
    resultsPerInbox.push(result);

    console.log(`   Sent: ${result.sent} | Failed: ${result.failed} | Skipped: ${result.skipped}`);
  }

  // Update state
  if (!dryRun) {
    state.totalSent = (state.totalSent || 0) + resultsPerInbox.reduce((s, r) => s + r.sent, 0);
    state.dailyLogs = state.dailyLogs || {};
    for (const r of resultsPerInbox) {
      // Don't clobber a real run's counts with the zeroes of a skipped inbox.
      if (r.errors?.includes('Already run')) continue;
      state.dailyLogs[r.inbox] = { date: today, sent: r.sent, failed: r.failed };
    }
    saveState(state);
    console.log(`\n💾 State saved — all-time total: ${state.totalSent} sent`);
  }

  // Build and send HTML report to Tumelo
  const reportHtml = buildHtmlReport(state, week, volume, resultsPerInbox, dryRun);

  if (!dryRun) {
    try {
      await sendEmail(
        { address: 'robusca.romanov@studex-group.com', name: 'Robusca (Studex OS)' },
        RECIPIENT.address,
        `🐔 Studex Warmup Report — ${today}`,
        reportHtml
      );
      console.log(`\n📧 Report sent to ${RECIPIENT.address}`);
      appendLog(`[REPORT] Emailed to ${RECIPIENT.address}`);
    } catch (err) {
      console.error(`\n❌ Failed to send report email: ${err.message}`);
      appendLog(`[ERROR] Report email failed: ${err.message}`);
    }
  } else {
    console.log(`\n[DRY RUN] Would email report to ${RECIPIENT.address}`);
    // Write report to disk for inspection
    writeFileSync('/workspace/studex-email-warmup/dry-run-report.html', reportHtml);
    console.log('[DRY RUN] Report written to /workspace/studex-email-warmup/dry-run-report.html');
  }

  appendLog(`=== Warmup run complete — ${resultsPerInbox.reduce((s,r)=>s+r.sent,0)} sent ===\n`);
  console.log('\n✅ Done.\n');
}

main().catch(err => {
  console.error('❌ Fatal error:', err.message);
  appendLog(`[FATAL] ${err.message}`);
  process.exit(1);
});
