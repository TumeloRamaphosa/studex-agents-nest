#!/usr/bin/env node
/**
 * Blotato Fallback Poster — Studex Daily Content Agent
 * Used when the Facebook Graph API token is expired but the caption
 * was already generated and queued in posts/pending/.
 *
 * Usage: node scripts/blotato-fallback.js [YYYY-MM-DD]
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const BASE = 'https://backend.blotato.com/v2';

function loadEnv() {
  const env = {};
  for (const f of ['/workspace/.env', path.join(process.env.HOME || '/root', '.env')]) {
    if (!fs.existsSync(f)) continue;
    fs.readFileSync(f, 'utf8').split('\n').forEach(line => {
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

// Blotato connected accounts (verified live via GET /v2/users/me/accounts)
const TARGETS = [
  { accountId: '26628', platform: 'linkedin', media: [] },
  { accountId: '7701', platform: 'threads', media: [] },
];

// Platform character limits (Blotato counts emoji / full-width as 2)
const LIMITS = { threads: 500 };

/**
 * Social platforms do NOT render markdown - a bold headline shows up with
 * literal asterisks on the live post. This script publishes the pending
 * caption, so it MUST sanitize, or the raw markdown goes straight out.
 *
 * The final replace is the safety net for a caption with an ODD number of
 * asterisks: the pair regex cannot match an unpaired marker, so any leftover
 * markers are dropped outright.
 */
function sanitize(text) {
  let t = text.replace(/\*\*(.+?)\*\*/gs, '$1');
  t = t.replace(/^\s*>\s?/gm, '');
  t = t.replace(/__/g, '').replace(/`/g, '');
  t = t.replace(/\*\*/g, '');
  return t.trim();
}

/**
 * Instagram's cap is 5 hashtags TOTAL (Blotato counts #StudexGM toward it).
 *
 * Ground truth (live IG post 8383092, published 2026-10-22): a pending
 * caption of 815 chars / 7 tags published FINE and shipped as 793 chars /
 * 5 tags - Blotato truncates to the first 5 server-side, it does NOT reject
 * with a 422. So this trim is not about rescuing a failed publish; it makes
 * the cut deterministic and local instead of depending on undocumented
 * platform behaviour, and keeps the tag set identical across platforms.
 *
 * The trim must remove the tag itself, not "tag + space": the LAST tag in a
 * caption has no trailing space, so a string replace of "tag " silently
 * does nothing and the tag survives. Use a regex with a lookahead that
 * matches end-of-string as well as a space.
 */
function capHashtags(text, platform) {
  if (platform !== 'instagram') return text;
  const tags = text.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
  if (tags.length <= 5) return text;
  let out = text;
  for (const t of tags.slice(5)) {
    out = out.replace(new RegExp('[ \\t]*' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?=\\s|$)'), '');
  }
  return out.replace(/[ \t]+$/, '');
}

function charWeight(ch) {
  const cp = ch.codePointAt(0);
  return (cp > 0x2e80 || (cp >= 0x1f300 && cp <= 0x1faff)) ? 2 : 1;
}

function truncate(text, platform) {
  const max = LIMITS[platform];
  if (!max) return text;

  // 🔑 CTA-SAFE TRUNCATION - the shared Python policy owns the cut, so the
  // two publish paths cannot drift apart.
  //
  // THE DEFECT (2026-10-31): this function cut the caption at 497 chars and
  // appended "...", and the CTA lives at the END of the caption - so every
  // Threads post lost its call to action. Measured on the LIVE feed: 5/5
  // Threads posts carried NO CTA and every one was exactly 500 chars, while
  // 5/5 Instagram posts carried one (they were never truncated). The
  // generator's validator had already approved the PRE-truncation caption,
  // so no gate caught it.
  //
  // The helper cuts the PROSE and keeps the CTA + hashtags. It is called via
  // the same spawnSync pattern this file already uses for the caption policy
  // (one implementation, not two).
  const policy = path.join(__dirname, '..', '..', 'scripts', 'caption_policy.py');
  const r = spawnSync('python3', [policy, '--truncate', platform, text || ''], {
    encoding: 'utf8',
    maxBuffer: 1024 * 1024,
  });
  if (r.status === 0 && r.stdout !== undefined) {
    const out = r.stdout.replace(/\n$/, '');
    if (out) return out;
  }
  // The shared helper could not be run. Fall back to the old cut rather than
  // publishing something we cannot verify.
  let out = '';
  let n = 0;
  for (const ch of Array.from(text)) {
    const w = charWeight(ch);
    if (n + w > max - 3) break;
    out += ch;
    n += w;
  }
  return out.replace(/[\s,.]+$/, '') + '...';
}

/**
 * Platforms the PILLAR publisher (scripts/daily-post.py) already used for
 * this date, read from memory/published-<date>-<pillar>.json.
 *
 * The marker file is named by pillar, so glob for all of them rather than
 * guessing the pillar from the date - the pillar rotation lives in
 * daily-post.py and must not be duplicated here (a second copy drifts).
 */
function pillarPublished(date) {
  const out = new Set();
  const memDir = path.join(ROOT, '..', 'memory');
  let files = [];
  try {
    files = fs.readdirSync(memDir).filter(
      f => f.startsWith('published-' + date + '-') && f.endsWith('.json'));
  } catch (e) {
    return out;
  }
  for (const fn of files) {
    try {
      const d = JSON.parse(fs.readFileSync(path.join(memDir, fn), 'utf8'));
      const res = d.results || d;
      for (const p of (res.posted || [])) if (typeof p === 'string') out.add(p);
      for (const p of (d.posted || [])) if (typeof p === 'string') out.add(p);
    } catch (e) { /* an unreadable marker must not block a publish */ }
  }
  return out;
}

/**
 * The pending file carries the image that was generated for the caption.
 * The TARGETS list above used a hardcoded `media: []`, so EVERY fallback
 * publish went out with no picture - which is exactly what the live posts
 * show: every imageless post is a Threads post, and Threads is the one
 * target whose grant still works (LinkedIn's grant is dead, so it fails).
 * The fallback was publishing a pictureless caption to Threads and nothing
 * else, while the image sat unused in the pending file.
 *
 * These helpers put the image back. The URL is only used if it is STILL
 * LIVE (see resolveMedia) - a dead URL would turn a working publish into a
 * failing one, which is worse than publishing without a picture.
 */
function pendingImageUrl(pending) {
  if (!pending) return null;
  const m = pending.media;
  if (typeof m === 'string') return m.trim() || null;
  if (m && typeof m === 'object') {
    for (const k of ['image', 'url', 'imageUrl', 'mediaUrl', 'src']) {
      if (typeof m[k] === 'string' && m[k].trim()) return m[k].trim();
    }
  }
  for (const k of ['mediaUrl', 'imageUrl', 'image']) {
    if (typeof pending[k] === 'string' && pending[k].trim()) return pending[k].trim();
  }
  return null;
}

function withMedia(targets, mediaUrl) {
  return targets.map(t => ({ ...t, media: mediaUrl ? [mediaUrl] : [] }));
}

async function defaultProbe(url) {
  try {
    let r = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(8000) });
    if (r.status === 405 || r.status === 501) {
      r = await fetch(url, { headers: { Range: 'bytes=0-64' }, signal: AbortSignal.timeout(8000) });
    }
    return !!r.ok;
  } catch (e) {
    return false;
  }
}

async function resolveMedia(pending, probe) {
  const url = pendingImageUrl(pending);
  if (!url) return null;
  const p = probe || defaultProbe;
  const live = await p(url);
  if (!live) {
    console.log('Pending image is not reachable - publishing without media: ' + url);
    return null;
  }
  return url;
}

// --- Caption policy ------------------------------------------------------
// Path A (scripts/daily-post.py) refuses to publish a caption that breaks
// the brand policy. Path B had NO such check, so a caption carrying a price
// went live on Threads at 06:59Z on 2026-10-28 and the 09:20 pre-flight
// only found it afterwards - a post-mortem, not a gate. The rule now lives
// in scripts/caption-policy.py so BOTH paths enforce the SAME rule, and
// this check runs BEFORE anything is published.
function policyFailures(caption) {
  // The path is computed here, not at module scope: the media test loads a
  // slice of this file with new Function(), where module-level consts do
  // not exist.
  const policy = path.join(__dirname, '..', '..', 'scripts', 'caption_policy.py');
  const r = spawnSync('python3', [policy, '--check-text', caption || ''],
                      { encoding: 'utf8' });
  if (r.error) {
    // A caption we cannot validate is a caption we cannot publish.
    return ['FAIL: Caption policy check could not be run (' + r.error.message + ')'];
  }
  return (r.stdout || '')
    .split('\n')
    .map(s => s.trim())
    .filter(s => s.startsWith('FAIL'));
}

async function post(target, text) {
  const payload = {
    post: {
      accountId: String(target.accountId),
      content: {
        platform: target.platform,
        text: text,
        mediaUrls: target.media,
      },
      target: { targetType: target.platform },
    },
  };
  const res = await fetch(BASE + '/posts', {
    method: 'POST',
    headers: { 'blotato-api-key': KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const body = await res.text();
  return { ok: res.ok, status: res.status, body: body.slice(0, 400) };
}

(async () => {
  const date = process.argv[2] || new Date().toISOString().slice(0, 10);
  const file = path.join(ROOT, 'posts', 'pending', date + '.json');
  if (!fs.existsSync(file)) {
    console.log('No pending post for ' + date);
    process.exit(0);
  }
  const pending = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!KEY) {
    console.log('BLOTATO_API_KEY not set - cannot post.');
    process.exit(1);
  }

  // --- Idempotency guard -------------------------------------------------
  // This script publishes straight to Blotato. Without a guard, a second run
  // for the same date republishes the same caption to the same platform.
  // The pending file is the record of what already went live, so read it
  // first and skip anything already published.
  const already = new Set();
  const fb = pending.fallback || {};
  if (Array.isArray(fb.posted)) for (const p of fb.posted) already.add(p);
  if (fb.instagram === 'POSTED') already.add('instagram');

  // Cross-path guard. scripts/daily-post.py is a SECOND, independent
  // publisher for the same date: it ships the pillar caption from
  // memory/post-queue/ and records what it posted in
  // memory/published-<date>-<pillar>.json. This script only knew about its
  // own `fallback.posted` record, so on 2026-10-22 Instagram received two
  // DIFFERENT captions the same day - 8383092 (biltong, via this script) and
  // 8384191 (coffee, via daily-post.py) - because neither could see the
  // other's record. They were different posts, not a re-post, so no
  // idempotency guard could have caught them.
  //
  // Read the pillar marker(s) for this date and treat those platforms as
  // already used. If the pillar post wins the race, this path stands down
  // for that platform; if this path wins, daily-post.py reads this file's
  // record (see pending_published()) and stands down instead.
  for (const p of pillarPublished(date)) already.add(p);
  if (already.size) {
    console.log('Already published for ' + date + ': ' + [...already].join(', ') + ' -> skipping those.');
  }

  // Refuse a caption that breaks the public-feed policy BEFORE publishing
  // it. The record of what already went live is never clobbered: a caption
  // that was published before this check existed keeps its posted status.
  // Validate the caption AS PUBLISHED: sanitize() is what strips the
  // markdown before it goes out, so the policy must see the same text.
  const violations = policyFailures(sanitize(pending.caption));
  if (violations.length) {
    console.log('CAPTION POLICY VIOLATION - refusing to publish:');
    for (const v of violations) console.log('  ' + v);
    console.log('The caption was NOT published. Strip the price (or get explicit');
    console.log('approval) and re-run. The 09:20 pre-flight sees the same thing.');
    pending.policyFailures = violations;
    pending.policyCheckedAt = new Date().toISOString();
    if (!already.size) pending.status = 'BLOCKED_BY_CAPTION_POLICY';
    fs.writeFileSync(file, JSON.stringify(pending, null, 2));
    process.exit(1);
  }

  // Attach the pending caption's own image. The hardcoded targets carried
  // media: [] and post() sends target.media verbatim, so the picture was
  // never sent. Resolve it from the pending file instead - but only if it
  // is still live, so a dead URL cannot break a publish that works today.
  const mediaUrl = await resolveMedia(pending);
  const targets = withMedia(TARGETS, mediaUrl);
  console.log(mediaUrl
    ? 'Attaching the pending image: ' + mediaUrl
    : 'No live image in the pending file - publishing without media.');

  const results = [];
  for (const t of targets) {
    if (already.has(t.platform)) {
      console.log(t.platform + ' (' + t.accountId + ') -> SKIPPED (already published for ' + date + ')');
      results.push({ platform: t.platform, accountId: t.accountId, ok: true, status: 'skipped', body: '' });
      continue;
    }
    const base = t.platform === 'linkedin'
      ? sanitize(pending.caption) + '\n\n- Tumelo Ramaphosa | Studex'
      : sanitize(pending.caption);
    // Cap hashtags AFTER sanitising but BEFORE truncating, and BEFORE the
    // post - Instagram's cap is 5 hashtags TOTAL and there is no delete or
    // edit route for a published post, so it goes out right or not at all.
    const capped = capHashtags(base, t.platform);
    const r = await post(t, truncate(capped, t.platform));
    console.log(t.platform + ' (' + t.accountId + ') -> HTTP ' + r.status + (r.ok ? ' POSTED' : ' FAILED'));
    if (!r.ok) console.log('   ' + r.body);
    results.push({ platform: t.platform, accountId: t.accountId, ok: r.ok, status: r.status, body: r.body });
  }

  const posted = results.filter(r => r.ok).map(r => r.platform);
  pending.fallback = {
    posted: posted,
    failed: results.filter(r => !r.ok).map(r => r.platform + ':' + r.status),
    attemptedAt: new Date().toISOString(),
  };
  pending.status = posted.length ? 'POSTED_VIA_FALLBACK' : 'APPROVED_PENDING_FB_TOKEN';
  fs.writeFileSync(file, JSON.stringify(pending, null, 2));
  console.log('\nPosted via: ' + (posted.join(', ') || 'none'));
})();
