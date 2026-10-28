#!/usr/bin/env node
/**
 * Studex Daily Content Automation
 * =================================
 * GPT-4o-mini powered daily Facebook post generator + publisher
 * 
 * CRON: Run at 08:55 SAST daily (05:55 UTC) via:
 *   55 5 * * * cd /workspace && node studex-content-automation/scripts/daily-content-agent.js
 * 
 * What it does:
 *  1. Loads today's product from the rotating catalog (6 products, rotates daily)
 *  2. Generates a compelling caption via GPT-4o-mini (OpenAI)
 *  3. Posts directly to Facebook Page via Graph API
 *  4. Logs the post URL to posts/log.json
 * 
 * Tokens needed (set in /workspace/.env):
 *   FB_PAGE_TOKEN    — Facebook Page access token
 *   FB_PAGE_ID      — Facebook Page ID (108934711902801 = StudEx Meat)
 *   OPENAI_API_KEY  — OpenAI API key (for caption generation)
 * 
 * Usage:
 *   node daily-content-agent.js                    normal run
 *   node daily-content-agent.js --dry-run          generate caption, don't post
 *   node daily-content-agent.js --product=biltong  force specific product
 *   node daily-content-agent.js --help
 */

const fs = require('fs');
const path = require('path');

// ─── Config ──────────────────────────────────────────────────────────────────
const PRODUCTS_FILE = path.join(__dirname, '../products/catalog.json');
const POSTS_LOG_FILE = path.join(__dirname, '../posts/log.json');
const ENV_FILE = path.join(process.env.HOME || '/root', '.env');

const FACEBOOK_API = 'https://graph.facebook.com/v18.0';
const OPENAI_API = 'https://api.openai.com/v1';

// ─── Load .env ───────────────────────────────────────────────────────────────
function loadEnv() {
  const env = {};
  for (const f of [ENV_FILE, '/workspace/.env', path.join(__dirname, '../../.env')]) {
    if (fs.existsSync(f)) {
      fs.readFileSync(f, 'utf8').split('\n').forEach(line => {
        const t = line.trim();
        if (!t || t.startsWith('#')) return;
        const ei = t.indexOf('=');
        if (ei === -1) return;
        const k = t.slice(0, ei).trim();
        const v = t.slice(ei + 1).trim().replace(/^["']|["']$/g, '');
        if (!env[k]) env[k] = v;
      });
    }
  }
  return {
    FB_PAGE_TOKEN: process.env.FB_PAGE_TOKEN || env.FB_PAGE_TOKEN || '',
    FB_PAGE_ID: process.env.FB_PAGE_ID || env.FB_PAGE_ID || '108934711902801',
    OPENAI_API_KEY: process.env.OPENAI_API_KEY || env.OPENAI_API_KEY || '',
    KIMI_API_KEY: process.env.KIMI_API_KEY || env.KIMI_API_KEY || '',
  };
}

const CONFIG = loadEnv();

// ─── LLM Provider selection ─────────────────────────────────────────────────
// Use Dashscope (Claude) if key available, else fall back to OpenAI
const DASHSCOPE_API_KEY = process.env.DASHSCOPE_API_KEY || '';
const USE_DASHSCOPE = Boolean(DASHSCOPE_API_KEY);
const DASHSCOPE_API = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1';
const DASHSCOPE_MODEL = 'qwen-plus';

// ─── Product Catalog ───────────────────────────────────────────────────────────
function loadCatalog() {
  return JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf8'));
}

function getTodayProduct(forceId = null) {
  const catalog = loadCatalog();
  if (forceId) {
    const p = catalog.products.find(p => p.id === forceId);
    if (p && p.available) return p;
  }
  const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0)) / 86400000);
  const available = catalog.products.filter(p => p.available);
  return available[dayOfYear % available.length];
}

// ─── Time Helpers ───────────────────────────────────────────────────────────────
function formatSAST(date = new Date()) {
  return date.toLocaleString('en-ZA', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
    timeZone: 'Africa/Johannesburg',
  });
}

// ─── Caption Guard ─────────────────────────────────────────────────────────────
// A caption is public copy on the Studex Meat Facebook Page. It must not carry
// a price, unit, certification or product claim that the registry does not own.
// Prices are whitelisted per product in products/catalog.json; the forbidden
// strings below mirror studex-meat/PRICE-SOURCE-REGISTRY.md §4f.
const FORBIDDEN_CAPTION_CLAIMS = [
  'per 250g', 'Sevruga Premium', 'Siberian Reserve',
  'Rainforest Alliance', 'certified farms', 'certified Russian caviar houses',
  'Every product we produce', '100% Halaal Certified', 'Halaal guaranteed',
  'MJC Halal Trust', 'agent.studexmeat.com', 'PROWTC',
  'June 2026', 'Coming Soon', '500+ MT', 'STUDESGIFT10',
  'R2,600', 'R3,400', 'R380/tin', '14-21 days',
];

/**
 * Keep only the FIRST 5 hashtags - Instagram's cap is 5 TOTAL (it counts
 * #StudexGM toward it).
 *
 * Ground truth (2026-10-22 live post 8383092): a 7-tag caption published
 * successfully and shipped with 5 tags, so Blotato truncates server-side
 * rather than rejecting with a 422. Trimming here makes that deterministic
 * and local instead of depending on undocumented platform behaviour - and it
 * keeps the extra tags from differing between platforms.
 *
 * The removal must match the tag itself with a lookahead, NOT "tag + space":
 * the LAST tag in a caption has no trailing space, so a replace of "tag "
 * silently does nothing and the tag survives.
 */
function capHashtags(caption) {
  const tags = caption.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
  if (tags.length <= 5) return caption;
  let out = caption;
  for (const t of tags.slice(5)) {
    out = out.replace(new RegExp('[ \\t]*' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?=\\s|$)'), '');
  }
  return out.replace(/[ \t]+$/, '');
}

function validateCaption(caption, product) {
  const problems = [];

  // 1. Every ZAR amount in the caption must be owned by the product.
  const allowed = (product.allowed_prices || []).map(String);
  const amounts = caption.match(/R\s?[\d][\d,]*(\.\d+)?/g) || [];
  for (const raw of amounts) {
    const digits = raw.replace(/[^0-9]/g, '');
    if (!allowed.includes(digits)) {
      problems.push(`unowned price "${raw}" (allowed for this product: ${allowed.join(', ') || 'none'})`);
    }
  }

  // 2. Forbidden claims (retired names, wrong units, unsourced certifications).
  const lower = caption.toLowerCase();
  for (const claim of FORBIDDEN_CAPTION_CLAIMS) {
    if (lower.includes(claim.toLowerCase())) {
      problems.push(`forbidden claim "${claim}"`);
    }
  }

  // 3. Hashtag count. Instagram's cap is 5 hashtags TOTAL.
  //
  // This is a BACKSTOP, not the primary control. The caption is already
  // trimmed to 5 tags by capHashtags() before it reaches here, so this check
  // should never fire; if capHashtags() ever breaks, it blocks rather than
  // shipping 7 tags to Instagram.
  //
  // It deliberately does NOT block on its own. Live evidence (post 8383092,
  // published 2026-10-22) shows a 7-tag caption published fine and shipped
  // with 5 tags - Blotato truncates server-side, it does not reject with a
  // 422. Blocking here would mean NO post at all, which is worse than two
  // hashtags being dropped.
  const tagCount = (caption.match(/#[A-Za-z][A-Za-z0-9]*/g) || []).length;
  if (tagCount > 5) {
    problems.push(`${tagCount} hashtags - Instagram's cap is 5 TOTAL`);
  }

  // 4. Claims the product record does not support (grade, origin, variant sizes).
  // NB: `MS5+` needs an explicit pattern — `\b` after `+` is not a word
  // boundary, so a naive \b(...)\b silently fails to match it.
  const claims = caption.match(/(MS5\+|\bA5\b|Australian|New Zealand|Ankole|Sevruga)/gi) || [];
  for (const c of claims) {
    const key = c.toLowerCase();
    const supported = product.name.toLowerCase().includes(key) ||
      (product.description || '').toLowerCase().includes(key);
    if (!supported) {
      problems.push(`unsupported product claim "${c}"`);
    }
  }

  // 4. A caption must end with a CTA, not a dead stop.
  // Strip the trailing hashtag block, then require the prose to carry a
  // question (the CTA). A question may be followed by one more instruction
  // line ("...who would you share it with? Grab yours at the link in bio."),
  // so the question mark need not be the final character.
  const body = caption.replace(/(?:\s*#\w+)+\s*$/, '').trim();
  if (!body.includes('?')) {
    problems.push('no closing question/CTA');
  }

  return problems;
}

// ─── Kimi (Moonshot) provider ─────────────────────────────────────────────────
// NOTE: the api.moonshot.cn host returns 401 invalid_authentication_error for
// this credential; api.moonshot.ai is the working host for the same key.
async function callKimi(prompt, kimiKey) {
  const res = await fetch('https://api.moonshot.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${kimiKey}`,
    },
    body: JSON.stringify({
      model: 'kimi-k3',
      messages: [{ role: 'user', content: prompt }],
      temperature: 1,
      // kimi-k3 is a reasoning model — it spends most of the token budget on
      // reasoning tokens, so the completion cap must be generous.
      max_tokens: 6000,
    }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`HTTP ${res.status}: ${err.slice(0, 200)}`);
  }
  const data = await res.json();
  const caption = data.choices?.[0]?.message?.content?.trim();
  if (!caption) throw new Error('Kimi returned empty response');
  return caption;
}

// ─── Caption Generation ───────────────────────────────────────────────────────
async function generateCaption(product) {
  const prompt = `You are the content writer for Studex — South Africa's premium online butcher and specialty food company. Studex sells artisan biltong, Australian Wagyu beef, Oscietra caviar, Wildlife Coffee (conservation-themed), and gourmet gift bundles.

Write ONE engaging Facebook post caption for a product. Rules:
- Under 180 words total (including hashtags)
- Conversational, warm, premium but accessible
- South African flavour (mention SA)
- Natural hook in the first line — grab attention
- Include product description + use case or social proof angle
- End with a question or clear CTA to drive comments
- EXACTLY 5 hashtags at the end (lowercase, no emoji) - no more, no fewer.
  Instagram's cap is 5 hashtags TOTAL. Blotato truncates to the first 5
  server-side rather than rejecting the post, so an over-cap caption still
  goes out - but the extra tags are silently dropped, and the same caption
  can render differently on each platform. A published post cannot be edited
  or deleted, so count them and return exactly 5.
- NO bullet points, keep it as one flowing paragraph
- Do NOT use placeholders
- Output ONLY the caption itself — no preamble, no headings, no bold markdown, no commentary

Product:
${JSON.stringify(product, null, 2)}

HARD RULES — these are checked before the caption is published:
- Do NOT put a price in the caption. NO price, in any form: not "R1,450", not "From R650", not "R4,200 per 100g", not "under R700", not a price range. This is house rule [10] of the Studex posting skill: NO price on a public feed - trade pricing stays on the China page. The product record below contains a price for INTERNAL REFERENCE ONLY; do not write it into the caption and do not refer to it. A caption with a price in it is REFUSED before it is published, and a published post cannot be edited or deleted. Write the value proposition instead ("R650 a kilo" is a price - "a kilo of wagyu biltong" is not).
- Mention only the variant sizes listed in the product record. If the list is empty, do not mention sizes.
- Do NOT add grade marks, countries of origin, certifications or product names that are not in the product record.
- Do NOT quote a different currency or a per-kg figure unless it is in the description.
- The caption must end with a question or a clear call to action.`;

  // Provider priority: Kimi (Moonshot) first — it is the only provider whose
  // account is currently in good standing. Dashscope (Arrearage) and OpenAI
  // (no credits) are kept as fallbacks for when their billing is restored.
  const kimiKey = CONFIG.KIMI_API_KEY;
  if (kimiKey) {
    try {
      const caption = await callKimi(prompt, kimiKey);
      return caption;
    } catch (err) {
      console.warn(`   ⚠️  Kimi error — falling back to next provider (${err.message})`);
    }
  }

  // Try Dashscope first, fall back to OpenAI on Arrearage (overdue payment)
  if (USE_DASHSCOPE) {
    try {
      // Dashscope — OpenAI-compatible API with Claude
      const response = await fetch(`${DASHSCOPE_API}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DASHSCOPE_API_KEY}`,
        },
        body: JSON.stringify({
          model: DASHSCOPE_MODEL,
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.8,
          max_tokens: 400,
        }),
      });
      if (!response.ok) {
        const err = await response.text();
        // Arrearage = account overdue — fall back to OpenAI silently
        if (response.status === 400 && err.includes('Arrearage')) {
          console.warn('   ⚠️  Dashscope overdue — falling back to OpenAI');
        } else {
          throw new Error(`Dashscope error ${response.status}: ${err}`);
        }
      } else {
        const data = await response.json();
        const caption = data.choices?.[0]?.message?.content?.trim();
        if (!caption) throw new Error('Dashscope returned empty response');
        return caption;
      }
    } catch (err) {
      // Re-throw non-arrearage errors; fall through to OpenAI for arrearage
      if (!err.message.includes('Arrearage')) throw err;
      console.warn('   ⚠️  Dashscope overdue — falling back to OpenAI');
    }
  }

  // OpenAI fallback (runs if Dashscope unavailable or failed with Arrearage)
  const apiKey = CONFIG.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set. Add it to /workspace/.env');
  const response = await fetch(`${OPENAI_API}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.8,
      max_tokens: 400,
    }),
  });
if (!response.ok) {
    const err = await response.text();
    throw new Error(`OpenAI error ${response.status}: ${err}`);
  }
  const data = await response.json();
  const caption = data.choices?.[0]?.message?.content?.trim();
  if (!caption) throw new Error('OpenAI returned empty response');
  return caption;
}

// ─── Facebook Poster ────────────────────────────────────────────────────────────
async function postToFacebook(caption) {
  const { FB_PAGE_TOKEN, FB_PAGE_ID } = CONFIG;
  if (!FB_PAGE_TOKEN) throw new Error('FB_PAGE_TOKEN not set. Renew at: https://developers.facebook.com → Meta Business Suite → Page Settings → Tokens');

  const res = await fetch(`${FACEBOOK_API}/${FB_PAGE_ID}/feed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: caption, access_token: FB_PAGE_TOKEN }),
  });

  const data = await res.json();
  if (data.error) throw new Error(`Facebook ${data.error.code}: ${data.error.message}`);

  const postId = data.id;
  const [actorId, , storyId] = postId.split('_');
  const postUrl = `https://www.facebook.com/${actorId}/posts/${storyId || postId}`;

  return { postId, postUrl };
}

// ─── Logger ────────────────────────────────────────────────────────────────────
function logPost(entry) {
  let log = [];
  if (fs.existsSync(POSTS_LOG_FILE)) {
    try { log = JSON.parse(fs.readFileSync(POSTS_LOG_FILE, 'utf8')); } catch (e) {}
  }
  log.unshift(entry);
  if (log.length > 100) log = log.slice(0, 100);
  fs.mkdirSync(path.dirname(POSTS_LOG_FILE), { recursive: true });
  fs.writeFileSync(POSTS_LOG_FILE, JSON.stringify(log, null, 2));
}

// ─── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  const isDryRun = args.includes('--dry-run') || args.includes('-n');
  const isTestLLM = args.includes('--test-llm');
  const forceProductId = args.find(a => a.startsWith('--product='))?.split('=')[1] || null;
  const showHelp = args.includes('--help') || args.includes('-h');

  if (showHelp) {
    console.log(fs.readFileSync(__filename, 'utf8').match(/\/\*\*[\s\S]*?\*\//)?.[0].replace(/\/\*|\*\//g, '').trim() || 'Usage: node daily-content-agent.js [options]');
    process.exit(0);
  }

  const started = new Date();
  console.log(`\n🐂 Studex Daily Content Agent — ${started.toISOString().slice(0,10)}`);
  console.log(`═`.repeat(50));
  console.log(`⏰ SAST: ${formatSAST(started)}`);
  console.log(`📦 Mode: ${isDryRun ? 'DRY RUN' : isTestLLM ? 'LLM TEST' : 'LIVE POST'}`);

  const product = getTodayProduct(forceProductId);
  console.log(`\n📦 Product: ${product.name}`);
  console.log(`   💰 ${product.price} | ${product.category}`);

  // Generate caption
  let caption;
  try {
    const llmLabel = CONFIG.KIMI_API_KEY ? 'Kimi k3 (Moonshot)' : (USE_DASHSCOPE ? 'Qwen-plus (Dashscope)' : 'GPT-4o-mini');
    console.log(`\n🖊️  Generating caption via ${llmLabel}...`);
    caption = await generateCaption(product);
    console.log(`   ✅ ${caption.length} chars`);

    // Trim to Instagram's 5-hashtag cap BEFORE validating. Trimming (not
    // blocking) is what keeps a caption that carries extra tags from
    // failing the whole run: a published post with 5 tags beats no post.
    const trimmed = capHashtags(caption);
    if (trimmed !== caption) {
      const dropped = (caption.match(/#[A-Za-z][A-Za-z0-9]*/g) || []).slice(5);
      console.log(`   ✂️  Trimmed ${dropped.length} hashtag(s) for Instagram: ` +
                  dropped.join(' '));
      caption = trimmed;
    }

    // Guard: never publish a caption the registry does not support.
    const problems = validateCaption(caption, product);
    if (problems.length) {
      console.error(`\n🛑 Caption blocked by guard — ${problems.length} problem(s):`);
      for (const p of problems) console.error(`   • ${p}`);
      console.error(`   ── caption ──\n   ${caption}`);
      logPost({
        timestamp: started.toISOString(),
        product: product.id, productName: product.name,
        status: 'BLOCKED', error: problems.join(' | '),
        captionPreview: caption.slice(0, 150),
      });
      process.exit(1);
    }
    console.log(`   🛡️  Caption passed the registry guard`);

    if (isDryRun || isTestLLM) {
      console.log(`\n${'─'.repeat(50)}`);
      console.log(caption);
      console.log(`{'─'.repeat(50)}`);
      if (isTestLLM) return;
    }
  } catch (err) {
    console.error(`\n❌ LLM Error: ${err.message}`);
    process.exit(1);
  }

  // Post
  let result = null;
  if (!isDryRun) {
    console.log(`\n📤 Posting to Facebook Page ${CONFIG.FB_PAGE_ID}...`);
    try {
      result = await postToFacebook(caption);
      console.log(`   ✅ Posted!`);
      console.log(`   📎 ${result.postUrl}`);
    } catch (err) {
      console.error(`\n❌ Facebook Error: ${err.message}`);
      logPost({
        timestamp: started.toISOString(),
        product: product.id, productName: product.name,
        category: product.category, price: product.price,
        status: 'FAILED', error: err.message,
        captionPreview: caption.slice(0, 150),
        // Keep the full guard-approved copy — the post can be re-sent the
        // moment the token is restored, without regenerating it.
        caption,
      });
      // Also queue it so nothing is lost between here and a working token.
      try {
        const pendingDir = path.join(__dirname, '..', 'posts', 'pending');
        fs.mkdirSync(pendingDir, { recursive: true });
        const file = path.join(pendingDir, `${started.toISOString().slice(0, 10)}.json`);
        const existing = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
        fs.writeFileSync(file, JSON.stringify({
          ...existing,
          timestamp: started.toISOString(),
          product: product.id, productName: product.name,
          category: product.category, price: product.price,
          status: 'APPROVED_PENDING_FB_TOKEN',
          blocker: err.message,
          postTo: { platform: 'facebook', pageId: CONFIG.FB_PAGE_ID, pageName: 'Studex Meat' },
          caption,
        }, null, 2));
        console.error(`   💾 Caption queued at posts/pending/${path.basename(file)}`);
      } catch (qErr) {
        console.error(`   ⚠️  Could not queue caption: ${qErr.message}`);
      }
      process.exit(1);
    }
  }

  // Log
  const entry = {
    timestamp: started.toISOString(),
    product: product.id, productName: product.name,
    category: product.category, price: product.price,
    status: isDryRun ? 'DRY_RUN' : 'POSTED',
    postId: result?.postId || null,
    postUrl: result?.postUrl || null,
    captionLength: caption.length,
    caption,
  };
  logPost(entry);

  const elapsed = ((Date.now() - started.getTime()) / 1000).toFixed(1);
  console.log(`\n📊 Done in ${elapsed}s — ${isDryRun ? 'NOT POSTED (dry run)' : 'LIVE ON FACEBOOK'}`);
  console.log(`📅 Next run: Tomorrow 08:55 SAST\n`);

  return entry;
}

main().catch(err => {
  console.error('💥 Fatal:', err.message);
  process.exit(1);
});
