#!/usr/bin/env node
/**
 * Studex Daily Posting Pipeline — 2026-10-22 (Thursday, Business pillar)
 *
 * Context: FeedHive API is DOWN (404 on all documented endpoints since 15 Oct;
 * token invalid since 5 Oct). Blotato is the live publish path.
 * Accounts verified live via GET /v2/users/me/accounts.
 */
const fs = require('fs');
const path = require('path');

const BASE = 'https://backend.blotato.com/v2';
const ROOT = path.join(__dirname, '..');
const DATE = '2026-10-22';
const PILLAR = 'Business';
const QUEUE_FILE = path.join(ROOT, 'memory', 'post-queue', DATE + '-thursday-business.md');
const IMAGE_LOCAL = path.join(ROOT, 'memory', '2026-10-22-business.png');
const IMAGE_URL = 'https://agent-cdn.minimax.io/mcp/cdn_upload/364053150926602246/376428811559175/1792703697_f9c3883f.png';

function loadEnv() {
  const env = {};
  for (const f of ['/workspace/.env', path.join(process.env.HOME || '/root', '.env')]) {
    if (!fs.existsSync(f)) continue;
    fs.readFileSync(f, 'utf8').split('\n').forEach((line) => {
      const t = line.trim();
      if (!t || t.startsWith('#')) return;
      const i = t.indexOf('=');
      if (i === -1) return;
      const k = t.slice(0, i).trim();
      const v = t.slice(i + 1).trim().replace(/^["']|["']$/g, '');
      if (!env[k]) env[k] = v;
    });
  }
  return env;
}
const KEY = process.env.BLOTATO_API_KEY || loadEnv().BLOTATO_API_KEY;

// ---------- 1. Load content from the queue file ----------
const md = fs.readFileSync(QUEUE_FILE, 'utf8');
const m = md.match(/## Generated Post Content\s*\n+([\s\S]*?)\n---/);
if (!m) { console.error('Could not extract content from ' + QUEUE_FILE); process.exit(1); }
const content = m[1].trim();
if (!fs.existsSync(IMAGE_LOCAL)) { console.error('Missing image ' + IMAGE_LOCAL); process.exit(1); }

// ---------- 2. MANDATORY validate_brand() ----------
function validate_brand(content, pillar) {
  const checks = [];
  const lower = content.toLowerCase();
  if (!content.includes('#StudexGM')) checks.push('FAIL: Missing #StudexGM');
  // CTA must be a VERIFIED LIVE address. agent.studexmeat.com has NO DNS — banned.
  if (/@agent\.studexmeat\.com/.test(content)) checks.push('FAIL: CTA uses dead domain @agent.studexmeat.com');
  if (!/info@studexmeat\.com/.test(content)) checks.push('FAIL: CTA info@studexmeat.com missing');
  for (const w of ['guaranteed returns', 'will make you rich', 'our competitors', 'risk-free', 'guaranteed profit']) {
    if (lower.includes(w.toLowerCase())) checks.push("FAIL: Suspicious claim '" + w + "'");
  }
  // Business pillar may reference Global Markets; other pillars may not.
  if (pillar !== 'Business' && pillar !== 'Africa' && lower.includes('global markets')) {
    checks.push('FAIL: "Global Markets" platform reference outside Business/Africa pillar');
  }
  // No unverified booth/stand/pavilion claim (CIIE booth still unconfirmed).
  if (/\b(our|the)\s+(booth|stand|pavilion)\b/i.test(content)) checks.push('FAIL: Unverified booth/stand/pavilion claim');
  // No price published on a public feed.
  if (/R\s?\d[\d,\.]*/.test(content)) checks.push('FAIL: Price published on public feed');
  // Hashtag discipline: #StudexGM plus at most 5 extra.
  const tags = content.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
  const extra = tags.filter((t) => t.toLowerCase() !== '#studexgm');
  if (extra.length > 5) checks.push('FAIL: Too many extra hashtags (' + extra.length + ')');
  // Length
  if (content.length > 2000) checks.push('FAIL: Exceeds 2000 char Twitter limit (' + content.length + ')');
  return checks;
}

const issues = validate_brand(content, PILLAR);
console.log('=== Studex Daily Post — ' + DATE + ' (' + PILLAR + ') ===');
console.log('Content chars: ' + content.length);
console.log('Image: ' + IMAGE_URL);
if (issues.length) {
  console.error('❌ VALIDATION FAILED — not publishing:');
  issues.forEach((i) => console.error('  ' + i));
  process.exit(1);
}
console.log('✅ validate_brand() passed (8 checks)');

// ---------- 3. Targets (accounts verified live 2026-10-22) ----------
// Per-platform text adaptations required by platform API rules:
//   instagram — max 5 hashtags TOTAL (Blotato counts #StudexGM too)
//   threads   — max 500 chars, needs a purpose-written short cut, not blind truncation
const igContent = content.replace('#GreenCoffee ', '');
const igTags = (igContent.match(/#[A-Za-z][A-Za-z0-9]*/g) || []).length;
if (igTags > 5) { console.error('❌ Instagram hashtag count still ' + igTags); process.exit(1); }

const threadsContent = [
  'China Just Opened Its Doors to African Coffee.',
  '',
  'From 1 May 2026, China applies a 0% import tariff across all 53 African countries. From 20 July, coffee moves under a unified phytosanitary system.',
  '',
  'For Rwanda, both doors open now — CIF Shanghai, 1 MT minimum on washed grades, 5–7 weeks Kigali → Djibouti → Shanghai.',
  '',
  'CIIE 2026: 5–10 November, Shanghai.',
  '',
  'Ask us what is available from Rwanda right now: info@studexmeat.com',
  '',
  '#StudexGM #RwandaCoffee #ChinaTrade #AfricanTrade #CIIE2026',
].join('\n');
if (threadsContent.length > 500) { console.error('❌ Threads copy ' + threadsContent.length + ' chars'); process.exit(1); }

const TARGETS = [
  { accountId: '38744', platform: 'facebook', media: [IMAGE_URL], text: content,
    target: { targetType: 'facebook', pageId: '108934711902801' } },
  { accountId: '76978', platform: 'instagram', media: [IMAGE_URL], text: igContent,
    target: { targetType: 'instagram' } },
  { accountId: '26628', platform: 'linkedin', media: [IMAGE_URL],
    text: content + '\n\n- Tumelo Ramaphosa | Studex',
    target: { targetType: 'linkedin' } },
  { accountId: '7701', platform: 'threads', media: [IMAGE_URL], text: threadsContent,
    target: { targetType: 'threads' } },
];

async function post(target) {
  const text = target.text;
  const payload = {
    post: {
      accountId: String(target.accountId),
      content: { platform: target.platform, text: text, mediaUrls: target.media },
      target: target.target,
    },
  };
  const res = await fetch(BASE + '/posts', {
    method: 'POST',
    headers: { 'blotato-api-key': KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const body = await res.text();
  return { ok: res.ok, status: res.status, body: body.slice(0, 300) };
}

/**
 * Platforms already used for this date, read from BOTH records:
 *   - memory/published-<date>-<pillar>.json   (the pillar publisher)
 *   - posts/pending/<date>.json -> fallback.posted  (the fallback publisher)
 *
 * This script is a THIRD publisher for the same platforms and the same date.
 * It had NO idempotency guard whatsoever, so re-running it would republish a
 * caption that is already live (Instagram 8383092 and Threads 8383081 both
 * went out on 2026-10-22). There is no delete or edit route for a published
 * Blotato post, so a duplicate is permanent.
 */
function alreadyPublished() {
  const out = new Set();
  const marker = path.join(ROOT, 'memory', 'published-' + DATE + '-' + PILLAR.toLowerCase() + '.json');
  try {
    const d = JSON.parse(fs.readFileSync(marker, 'utf8'));
    const res = d.results || d;
    for (const x of (res.posted || [])) if (typeof x === 'string') out.add(x);
    for (const x of (d.posted || [])) if (typeof x === 'string') out.add(x);
  } catch (e) { /* no marker yet - nothing published via that path */ }
  try {
    const p2 = path.join(ROOT, 'studex-content-automation', 'posts', 'pending', DATE + '.json');
    const d2 = JSON.parse(fs.readFileSync(p2, 'utf8'));
    const fb = d2.fallback || {};
    for (const x of (fb.posted || [])) if (typeof x === 'string') out.add(x);
    if (fb.instagram === 'POSTED') out.add('instagram');
  } catch (e) { /* no pending record - nothing published via that path */ }
  return out;
}

(async () => {
  if (!KEY) { console.error('BLOTATO_API_KEY not set'); process.exit(1); }
  const already = alreadyPublished();
  if (already.size) {
    console.log('Already published for ' + DATE + ': ' + [...already].join(', ') +
                ' -> skipping those.');
  }
  const results = [];
  for (const t of TARGETS) {
    if (already.has(t.platform)) {
      console.log(t.platform + ' (' + t.accountId + ') -> SKIPPED (already published for ' + DATE + ')');
      results.push({ platform: t.platform, accountId: t.accountId, ok: true, status: 'skipped', body: '' });
      continue;
    }
    const r = await post(t);
    console.log(t.platform + ' (' + t.accountId + ') -> HTTP ' + r.status + (r.ok ? ' POSTED' : ' FAILED'));
    if (!r.ok) console.log('   ' + r.body);
    results.push({ platform: t.platform, accountId: t.accountId, ok: r.ok, status: r.status, body: r.body });
  }
  console.log('\nPOSTED: ' + (results.filter((r) => r.ok).map((r) => r.platform).join(', ') || 'none'));
  console.log('FAILED: ' + (results.filter((r) => !r.ok).map((r) => r.platform + ':' + r.status).join(', ') || 'none'));
  fs.writeFileSync(path.join(ROOT, 'memory', 'post-results-' + DATE + '.json'), JSON.stringify(results, null, 2));
})();
