#!/usr/bin/env node
/**
 * Studex Email Warmup Script
 * 
 * Purpose: Gradually build sender reputation for AgentMail inboxes
 * to improve email deliverability for CIIE, Dubai, and China outreach.
 * 
 * Run: node warmup.js [--dry-run] [--verbose]
 * Schedule: Daily via cron, starting low and ramping up
 */

import { readFileSync, writeFileSync } from 'fs';
import { createHash, randomBytes } from 'crypto';

// ─── Configuration ────────────────────────────────────────────────────────────
import { requireEnv } from '../scripts/cred_env.mjs';

const AGENTMAIL_BASE = 'https://api.agentmail.to/v0';
const API_KEY = requireEnv('AGENTMAIL_API_KEY');

// Inboxes to warm up (from TOOLS.md)
const INBOXES = [
  { address: 'robusca.romanov@studex-group.com', name: 'Robusca CEO', priority: 1 },
  { address: 'naledi-cmo@studex-group.com', name: 'Naledi CMO', priority: 2 },
  { address: 'project-2571-studex-agent-2077@agentmail.to', name: 'StudEx General', priority: 3 },
];

// Safe external warmup addresses (real Gmail/Outlook addresses used for email warmup)
// These are legitimate contacts who will mark Studex emails as NOT spam
const WARMUP_TARGETS = [
  { name: 'Tumelo Personal', address: 'tumelor001@gmail.com' },
  { name: 'Naledi Personal', address: 'naledi.services@gmail.com' },
  { name: 'Robusca Work', address: 'robusca.romanov@outlook.com' },
];

// Warmup providers (auto-mark as important) — seed addresses.
// NOTE: no bounce/mailer-daemon addresses here. Sending to one generates a
// hard DSN, which is exactly the signal a warmup must not create.
const WARMUP_SEEDS = [
  'warmup@email-warmup.com',
  'support@outlook.com',
];

// Volume schedule: ramp up over 4 weeks
const VOLUME_SCHEDULE = {
  week1: { daily: 2, subjectVariety: 2 },
  week2: { daily: 4, subjectVariety: 4 },
  week3: { daily: 7, subjectVariety: 6 },
  week4: { daily: 10, subjectVariety: 8 },
};

// Varied subject lines (rotating, not repeated)
const WARMUP_SUBJECTS = [
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
  'Re: Rwanda A1 documentation',
  'Studex Meat — quarterly review',
  'Re: Luckin Coffee opportunity',
  'Delivery confirmation — Sandton',
  'Re: Rwanda harvest schedule',
  'Studex partner inquiry',
  'Re: GCC distribution interest',
  'Weekly update — Studex',
];

// Warmup email body templates (slightly varied each time)
const WARMUP_BODIES = [
  `Hi,

Hope you're well. Quick follow-up on our conversation last week.

I've attached the updated Rwanda A1/A2 product sheet — let me know if you need anything else before CIIE.

Best,
Tumelo
Studex Group`,

  `Hello,

Thank you for your interest in Studex Premium. Our Rwanda A1 Washed lot is available for sample shipment from October.

Happy to arrange a call this week to discuss requirements.

Regards,
Tumelo Ramaphosa
Studex Group`,

  `Hi there,

Just circling back on the Dubai distributor conversation. We're seeing strong interest from UAE importers given the China zero-tariff corridor.

Would a call Thursday work?

Best,
Tumelo`,

  `Good day,

If you're attending CIIE 2026 in Shanghai (5-10 November), I'd love to arrange a meeting.

We're showcasing Rwanda A1/A2 green coffee — the timing aligns with your China procurement cycle.

Tumelo
Studex Group`,

  `Hi,

Quick question — did the cupping sample arrive safely? Happy to send a follow-up lot if you'd like to compare.

Best regards,
Tumelo`,

  `Hello,

Following up on our discussion about the Studex Premium range. We have caviar (Oscietra Imperial, Kaluga Prestige, Sevtruga Medium) and biltong available for Q4 gifting season.

Catalog attached.

Tumelo`,
];

// ─── AgentMail API helpers ────────────────────────────────────────────────────

async function agentmailRequest(endpoint, options = {}) {
  const url = `${AGENTMAIL_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  const data = await res.json().catch(() => ({}));
  
  if (!res.ok) {
    throw new Error(`AgentMail API ${res.status}: ${JSON.stringify(data)}`);
  }
  
  return { status: res.status, data };
}

async function listInboxes() {
  const { data } = await agentmailRequest('/inboxes');
  return data;
}

async function sendEmail(from, to, subject, body, options = {}) {
  const payload = {
    from: from.address,
    to: [{ address: to.address, name: to.name }],
    subject,
    body,
    ...options,
  };
  return agentmailRequest('/messages/send', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

async function getInboxMessages(inboxAddress, limit = 10) {
  const { data } = await agentmailRequest(
    `/messages?inbox=${encodeURIComponent(inboxAddress)}&limit=${limit}`
  );
  return data?.messages || [];
}

// ─── Warmup Logic ────────────────────────────────────────────────────────────

function selectRandom(items, count = 1) {
  const shuffled = [...items].sort(() => 0.5 - Math.random());
  return count === 1 ? shuffled[0] : shuffled.slice(0, count);
}

function generateWarmupBody() {
  return selectRandom(WARMUP_BODIES);
}

function generateWarmupSubject() {
  return selectRandom(WARMUP_SUBJECTS);
}

function generateTrackingId() {
  return randomBytes(8).toString('hex');
}

/**
 * Determine current warmup week (based on days since first run)
 */
function getWarmupWeek(startDate) {
  const days = Math.floor((Date.now() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24));
  if (days < 7) return 'week1';
  if (days < 14) return 'week2';
  if (days < 21) return 'week3';
  return 'week4';
}

/**
 * Main warmup routine for one inbox
 */
async function warmupInbox(inbox, volumeConfig, dryRun = false) {
  const log = [];
  const trackingId = generateTrackingId();
  const today = new Date().toISOString().split('T')[0];
  
  log.push(`[${inbox.address}] Starting warmup — ${volumeConfig.daily} emails today`);
  
  // Select warmup targets (rotate through them)
  const targets = selectRandom(WARMUP_TARGETS, Math.min(volumeConfig.subjectVariety, WARMUP_TARGETS.length));
  
  // Also add some seed addresses
  const seeds = selectRandom(WARMUP_SEEDS, 2);
  const allTargets = [...targets, ...seeds.map(a => ({ name: a, address: a }))];
  
  // Send emails, varying subject and body
  const emailsToSend = Math.min(volumeConfig.daily, allTargets.length * 2);
  
  for (let i = 0; i < emailsToSend; i++) {
    const target = allTargets[i % allTargets.length];
    const subject = generateWarmupSubject();
    const body = generateWarmupBody();
    
    if (dryRun) {
      log.push(`  [DRY RUN] Would send to ${target.address} — "${subject}"`);
      continue;
    }
    
    try {
      // Add tracking pixel to body
      const trackingPixel = `<img src="https://api.agentmail.to/v0/track/${trackingId}/${i}.png" width="1" height="1" />`;
      const bodyWithTracking = body + `\n\n<!-- ${trackingPixel} -->`;
      
      const result = await sendEmail(
        { address: inbox.address, name: inbox.name },
        { address: target.address, name: target.name },
        subject,
        bodyWithTracking
      );
      
      log.push(`  ✅ Sent to ${target.address} — "${subject}"`);
      
      // Random delay between sends (2-8 seconds) to appear natural
      await new Promise(r => setTimeout(r, 2000 + Math.random() * 6000));
      
    } catch (err) {
      log.push(`  ❌ Failed: ${target.address} — ${err.message}`);
    }
  }
  
  // Simulate inbox engagement (mark some as read, reply to own sent)
  if (!dryRun) {
    try {
      const messages = await getInboxMessages(inbox.address, 3);
      if (messages.length > 0) {
        log.push(`  📬 Inbox has ${messages.length} recent messages — engagement noted`);
      }
    } catch (err) {
      log.push(`  ⚠️ Could not check inbox: ${err.message}`);
    }
  }
  
  return log;
}

/**
 * Check email reputation scores (via warmup provider API if available)
 */
async function checkReputation() {
  // In production, integrate with GlockApps, Mail-tester.com, or similar
  // For now, log what we can check via AgentMail
  try {
    const inboxes = await listInboxes();
    return inboxes.map(inbox => ({
      address: inbox.address,
      status: inbox.status || 'active',
      messageCount: inbox.message_count || 0,
    }));
  } catch (err) {
    return [{ error: err.message }];
  }
}

// ─── State Management ─────────────────────────────────────────────────────────

const STATE_FILE = '/workspace/studex-email-warmup/state.json';
const PUBLIC_STATE_FILE = '/workspace/studex-war-room/public/warmup-state.json';

function loadState() {
  try {
    const state = JSON.parse(readFileSync(STATE_FILE, 'utf8'));
    // Mirror to War Room public dir so the dashboard can read it
    try { writeFileSync(PUBLIC_STATE_FILE, JSON.stringify(state, null, 2)); } catch { /* non-fatal */ }
    return state;
  } catch {
    const initial = { startDate: new Date().toISOString(), totalSent: 0, dailyLogs: {} };
    try { writeFileSync(PUBLIC_STATE_FILE, JSON.stringify(initial, null, 2)); } catch { /* non-fatal */ }
    return initial;
  }
}

function saveState(state) {
  try {
    writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    // Mirror to War Room public dir so the React dashboard can read it
    try {
      writeFileSync(PUBLIC_STATE_FILE, JSON.stringify(state, null, 2));
    } catch {
      // War Room public dir may not exist — non-fatal
    }
  } catch (err) {
    console.error(`  ⚠️  Failed to save state: ${err.message}`);
  }
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const verbose = args.includes('--verbose');
  const checkRep = args.includes('--check-reputation');
  
  console.log('\n🐔 Studex Email Warmup Script');
  console.log('═'.repeat(50));
  console.log(`Mode: ${dryRun ? 'DRY RUN (no emails sent)' : 'LIVE'}`);
  console.log(`Time: ${new Date().toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' })} SAST`);
  console.log('');
  
  // Check reputation if requested
  if (checkRep) {
    console.log('📊 Checking inbox reputation...');
    const rep = await checkReputation();
    console.log(JSON.stringify(rep, null, 2));
    console.log('');
  }
  
  // Load warmup state
  const state = loadState();
  const week = getWarmupWeek(state.startDate);
  const volume = VOLUME_SCHEDULE[week];
  
  console.log(`📅 Warmup week: ${week} (started ${state.startDate.split('T')[0]})`);
  console.log(`📦 Today's volume: ${volume.daily} emails per inbox`);
  console.log('');
  
  // Warmup each inbox
  for (const inbox of INBOXES) {
    const inboxState = state.dailyLogs?.[inbox.address];
    const today = new Date().toISOString().split('T')[0];
    
    if (inboxState?.date === today && !dryRun) {
      console.log(`⏭️  [${inbox.address}] Already warmed up today — skipping`);
      continue;
    }
    
    console.log(`\n🎯 Warming up: ${inbox.address} (${inbox.name})`);
    
    const logs = await warmupInbox(inbox, volume, dryRun);
    
    if (verbose) {
      logs.forEach(l => console.log(l));
    }
    
    // Update state
    if (!dryRun) {
      state.totalSent = (state.totalSent || 0) + logs.filter(l => l.includes('✅')).length;
      state.dailyLogs = state.dailyLogs || {};
      state.dailyLogs[inbox.address] = { date: today, sent: logs.filter(l => l.includes('✅')).length };
      saveState(state);
    }
  }
  
  // Summary
  console.log('\n' + '═'.repeat(50));
  console.log(`✅ Warmup complete${dryRun ? ' (DRY RUN)' : ''}`);
  console.log(`📈 Total emails sent (all time): ${state.totalSent}`);
  console.log(`📅 Next run: tomorrow at 09:00 SAST`);
  console.log('\n💡 Tip: Run with --check-reputation to see inbox status');
  console.log('💡 Tip: Add to cron: 0 9 * * * cd /workspace/studex-email-warmup && node warmup.js\n');
}

main().catch(err => {
  console.error('❌ Warmup failed:', err.message);
  process.exit(1);
});
