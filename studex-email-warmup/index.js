/**
 * studex-email-warmup/index.js
 * =============================================
 * Studex Exchange Email Warmup System
 * ---------------------------------------------
 * Gradually warms up stud.exchange domain reputation
 * by sending authentic, varied emails to a warmup pool.
 *
 * Usage:
 *   node index.js                    — run warmup cycle
 *   node index.js --dry-run          — preview without sending
 *   node index.js --status          — show warmup status
 *   node index.js --reset           — reset daily counters
 *
 * Cron: run every 2-3 hours during build/business hours
 * =============================================
 */

import dotenv from 'dotenv';
// Load the workspace-level .env (the script's own dir has none). Fall back to
// the local .env so the script works standalone too.
dotenv.config({ path: '/workspace/.env' });
dotenv.config();

const CONFIG = {
  // AgentMail credentials. AGENTMAIL_API_KEY is revoked (403 Forbidden), so
  // prefer the warmup/main keys which are verified working.
  agentMailApiKey:
    process.env.AGENTMAIL_WARMUP_API_KEY ||
    process.env.AGENTMAIL_MAIN_API_KEY ||
    process.env.AGENTMAIL_API_KEY ||
    requireEnv('AGENTMAIL_API_KEY'),
  agentMailBase: 'https://api.agentmail.to/v0',
  
  // AgentMail verified inbox — used as the FROM address for sending
  // Currently using robusca.romanov@studex-group.com (confirmed active)
  // TODO: Once stud.exchange domain is verified in AgentMail, add custom domain sending
  senderInbox: 'robusca.romanov@studex-group.com',
  senderEmail: 'robusca.romanov@studex-group.com',
  
  // Warmup pool — email addresses that receive our warmup emails
  // Rotate through these to build reciprocal engagement signals
  // Live AgentMail inboxes (proven working 2026-10-22). The old pool used
  // t.ramaphosa@agentmail.to and studex-2571@agentmail.to, which no
  // longer receive — every send to them failed.
  // RE-PROBED 2026-10-26: studex-2571 is 200 on the main account (0
  // messages) and t.ramaphosa is reachable on the CIIE key. Neither is
  // read, so both stay out of the pool - warmup only helps an inbox that
  // someone actually opens.
  warmupPool: [
    'robusca.romanov@studex-group.com',        // Robusca CEO
    'naledi-cmo@studex-group.com',             // Naledi CMO
    'project-2571-studex-agent-2077@agentmail.to', // StudEx general
  ],
  
  // Daily limits — start LOW, ramp up over weeks
  // Week 1: 5/day, Week 2: 10/day, Week 3: 20/day, Week 4+: 30/day
  dailyLimits: {
    week1: 5,
    week2: 10,
    week3: 20,
    week4: 30,
  },
  
  // How many emails per warmup cycle (run every 2-3 hours)
  emailsPerCycle: 2,
  
  // Minimum interval between sends (ms) — be polite to mail servers
  minIntervalMs: 45 * 60 * 1000, // 45 minutes
};

// Warmup email templates — varied, authentic, natural
const EMAIL_TEMPLATES = [
  {
    subject: 'Re: Q4 pipeline review',
    body: `Hi,

Following up on the pipeline review — I've attached the updated figures for Q4.

The Rwanda A1/A2 sample shipment looks promising. We should have a formal quote ready by end of week.

Let me know if you want to jump on a call tomorrow.

Best,
T`,
  },
  {
    subject: 'CIIE 2026 — buyer meeting request',
    body: `Great speaking with you yesterday.

Following up on CIIE 2026 in Shanghai (5-10 November) — if you're attending, I'd like to set up time to meet and walk you through our Rwanda green coffee and caviar range.

I'll send the origin and compliance documentation across separately.

Looking forward to it.

T`,
  },
  {
    subject: 'Re: Rwanda A1 sample pricing',
    body: `Hi,

Thanks for the interest. Here's the sample pricing for our Rwanda A1 Washed (Nyamasheke):

- Sample shipment (5-10 kg): USD 28-45/kg
- Roasted SA price guide: Washed R400/kg, Aerobic R380/kg, Honey R350/kg, Natural R270/kg
- Trade MOQ (roasted): 50 kg

Shipping from Durban to most SA centres is 2-3 days.

Happy to send a sample box ahead of any larger order.

T`,
  },
  {
    subject: 'Re: Dubai distribution partnership',
    body: `Hi,

The UAE angle is interesting — we've had a few conversations with Dubai importers about GCC re-export.

The key advantage is 0% import duty within the GCC common external tariff on green coffee (HS 0901.11).

Are you connected with any specialty roasters in the UAE currently?

T`,
  },
  {
    subject: 'Follow-up: Youth Day content drop',
    body: `Hey,

The Youth Day content calendar looks solid — Naledi's team put together some strong visuals for the WhatsApp broadcast.

The biltong sampler campaign is running parallel. I'll share the first-week metrics on Monday.

Are you around for a quick sync Friday morning?

T`,
  },
  {
    subject: 'Re: SA coffee export documentation',
    body: `Hi,

Quick question — for Rwanda-origin coffee being re-exported through SA, does the DAFF phytosanitary cover the full chain or only the SA leg?

We're trying to get the documentation flow right before the next shipment.

Thanks,
T`,
  },
  {
    subject: 'Caviar inquiry — response',
    body: `Hi,

Thanks for reaching out about the caviar line.

We source Oscietra, Kaluga and Sevtruga caviar. Retail pricing is per 100g — Oscietra Imperial R4,200, Kaluga Prestige R2,800, Sevtruga Medium R1,600 — and private-label tins start from a 5 kg MOQ.

Import lead time is 7-14 days, counted from the date the DAFF veterinary import permit is issued. The permit needs applying for at least 4 weeks before shipment, and takes 5-10 working days to issue once approved.

Let me know if you'd like a sample selection.

Regards,
T`,
  },
  {
    subject: 'Re: order status — ORD-007',
    body: `Hi,

ORD-007 dispatched this morning via Courier Guy — tracking will be sent separately.

Delivery to Four Ways, JHB should be tomorrow by 2pm.

Appreciate the patience on this one.

T`,
  },
  {
    subject: 'Re: biltong bulk pricing',
    body: `Hi,

Bulk biltong pricing for Q4 (ex VAT, per kg):

- Craft biltong (original): R380/kg
- Craft biltong (peri-peri): R410/kg

We can do custom cuts and spice profiles. Standard is coriander and black pepper.

Lead time is 5 working days from deposit.

T`,
  },
  {
    subject: 'Re: newsletter content — October',
    body: `Hi,

I've drafted the October newsletter content — a focus on the CIIE buildup, Rwanda sourcing trip recap, and the Youth Day campaign results.

Should be ready to send Thursday morning.

Let me know if you want any adjustments to the copy before we push.

T`,
  },
];

// State file
const STATE_FILE = './warmup-state.json';
const LOG_FILE = './warmup.log';

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

function loadState() {
  const path = join(__dirname, STATE_FILE);
  if (!existsSync(path)) {
    return {
      week: 1,
      sentToday: 0,
      lastSentDate: null,
      totalSent: 0,
      log: [],
    };
  }
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function saveState(state) {
  const path = join(__dirname, STATE_FILE);
  writeFileSync(path, JSON.stringify(state, null, 2));
}

function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}`;
  console.log(line);
  const path = join(__dirname, LOG_FILE);
  const existing = existsSync(path) ? readFileSync(path, 'utf-8') : '';
  const maxLines = 500;
  const lines = [line, ...existing.split('\n')].filter(Boolean).slice(0, maxLines);
  writeFileSync(path, lines.join('\n'));
}

function getDailyLimit(state) {
  const week = state.week || 1;
  const limits = Object.entries(CONFIG.dailyLimits).sort((a, b) => {
    const wa = parseInt(a[0].replace('week', ''));
    const wb = parseInt(b[0].replace('week', ''));
    return wb - wa;
  });
  for (const [key, val] of limits) {
    const w = parseInt(key.replace('week', ''));
    if (week >= w) return val;
  }
  return CONFIG.dailyLimits.week1;
}

function advanceWeek(state) {
  const sentTotal = state.totalSent || 0;
  const week1Limit = CONFIG.dailyLimits.week1;
  const week2Limit = CONFIG.dailyLimits.week2;
  const week3Limit = CONFIG.dailyLimits.week3;
  const week4Limit = CONFIG.dailyLimits.week4;
  
  if (sentTotal >= week4Limit * 28) return 4;
  if (sentTotal >= week3Limit * 21) return 3;
  if (sentTotal >= week2Limit * 14) return 2;
  return 1;
}

function resetDailyIfNeeded(state) {
  const today = new Date().toISOString().split('T')[0];
  if (state.lastSentDate !== today) {
    state.sentToday = 0;
    state.lastSentDate = today;
    state.week = advanceWeek(state);
  }
  return state;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

async function sendEmail(to, template) {
  // AgentMail v0 sends inbox-scoped: POST /v0/inboxes/{inbox}/messages/send
  // The old code tried ".../messages" and "/messages", both of which 404 with
  // "Route not found" — every send since 2026-10-03 failed silently.
  const url = `${CONFIG.agentMailBase}/inboxes/${encodeURIComponent(CONFIG.senderInbox)}/messages/send`;
  const payload = {
    to: [to],
    subject: template.subject,
    html: `<div style="font-family: Arial, sans-serif; max-width: 600px;">
             <div style="background:#1a1a1a;color:#e0c875;padding:16px;border-radius:8px 8px 0 0;"><strong>Studex Group</strong></div>
             <div style="background:#fafafa;padding:20px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 8px 8px;">
               <p style="white-space:pre-wrap;line-height:1.6;margin:0;">${escapeHtml(template.body)}</p>
             </div>
           </div>`,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${CONFIG.agentMailApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`AgentMail API error ${response.status}: ${err}`);
  }
  return await response.json();
}

async function runWarmupCycle({ dryRun = false } = {}) {
  const state = resetDailyIfNeeded(loadState());
  const dailyLimit = getDailyLimit(state);
  const remaining = Math.max(0, dailyLimit - state.sentToday);
  
  log(`=== Warmup Cycle ===`);
  log(`Day: ${state.lastSentDate} | Week ${state.week} | Today: ${state.sentToday}/${dailyLimit} | Total: ${state.totalSent}`);
  
  if (remaining <= 0) {
    log(`Daily limit reached (${dailyLimit}). Skipping. Next cycle tomorrow.`);
    return { done: true, reason: 'daily_limit_reached' };
  }
  
  const toSend = Math.min(remaining, CONFIG.emailsPerCycle);
  const templates = [...EMAIL_TEMPLATES].sort(() => Math.random() - 0.5);
  let sentCount = 0;   // real successes — the old code reported `toSend` regardless
  let failedCount = 0;
  
  for (let i = 0; i < toSend; i++) {
    const target = CONFIG.warmupPool[i % CONFIG.warmupPool.length];
    const template = templates[i % templates.length];
    
    if (dryRun) {
      log(`[DRY RUN] Would send to: ${target}`);
      log(`[DRY RUN] Subject: ${template.subject}`);
    } else {
      try {
        await sendEmail(target, template);
        log(`✓ Sent to: ${target} | Subject: ${template.subject}`);
        state.sentToday++;
        state.totalSent++;
        sentCount++;
        
        // Log to state
        state.log = [{
          ts: new Date().toISOString(),
          to: target,
          subject: template.subject,
          success: true,
        }, ...(state.log || []).slice(0, 99)];
        
        saveState(state);
      } catch (err) {
        log(`✗ Failed to send to ${target}: ${err.message}`);
        state.log = [{
          ts: new Date().toISOString(),
          to: target,
          subject: template.subject,
          success: false,
          error: err.message,
        }, ...(state.log || []).slice(0, 99)];
        saveState(state);
      }
    }
    
    // Wait between sends
    if (i < toSend - 1) {
      const waitMs = CONFIG.minIntervalMs;
      log(`Pausing ${Math.round(waitMs / 60000)}min-worth of interval before next send (2s actual)`);
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  
  log(`Cycle complete. Sent ${sentCount} emails (${failedCount} failed). Total today: ${state.sentToday}/${dailyLimit}`);
  return { sent: sentCount, failed: failedCount, totalToday: state.sentToday, dailyLimit, total: state.totalSent };
}

async function showStatus() {
  const state = loadState();
  const dailyLimit = getDailyLimit(state);
  
  console.log('\n📧 STUDEX EMAIL WARMUP STATUS');
  console.log('============================');
  console.log(`Week:            ${state.week}`);
  console.log(`Sent Today:      ${state.sentToday} / ${dailyLimit}`);
  console.log(`Total Sent:      ${state.totalSent}`);
  console.log(`Last Sent Date:  ${state.lastSentDate || 'never'}`);
  console.log(`Daily Limit:     ${dailyLimit} emails/day`);
  console.log('\nWarmup Pool:');
  CONFIG.warmupPool.forEach(e => console.log(`  → ${e}`));
  console.log('\nRecent Activity:');
  (state.log || []).slice(0, 10).forEach(entry => {
    const icon = entry.success ? '✓' : '✗';
    const when = new Date(entry.ts).toLocaleString('en-ZA');
    console.log(`  ${icon} ${when} | ${entry.to} | ${entry.subject}`);
  });
  console.log('\n');
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--status')) {
    await showStatus();
    return;
  }
  
  if (args.includes('--reset')) {
    const state = loadState();
    state.sentToday = 0;
    state.lastSentDate = null;
    state.week = 1;
    saveState(state);
    log('State reset.');
    console.log('✅ Warmup state reset.');
    return;
  }
  
  const dryRun = args.includes('--dry-run');
  
  if (dryRun) {
    console.log('🔎 DRY RUN — no emails will be sent\n');
  }
  
  const result = await runWarmupCycle({ dryRun });
  console.log('\n📊 Result:', result);
}

// Run
main().catch(err => {
  log(`FATAL: ${err.message}`);
  console.error('FATAL:', err);
  process.exit(1);
});
