/**
 * Blotato Content Pipeline — Studex
 * Connects Naledi's content output to Blotato for Facebook & Instagram posting
 * 
 * Usage:
 *   BLOTATO_API_KEY=blt_xxx PAGE_ACCESS_TOKEN=EAASxxx node blotato-content-pipeline.js --post " caption text" --image-url "https://..." --platform facebook
 *   BLOTATO_API_KEY=blt_xxx PAGE_ACCESS_TOKEN=EAASxxx node blotato-content-pipeline.js --sync-accounts
 * 
 * Environment:
 *   BLOTATO_API_KEY     — Blotato API key
 *   FB_PAGE_TOKEN      — Facebook Page access token (for direct API fallback)
 *   FB_PAGE_ID         — Facebook Page ID (108934711902801 = StudEx Meat)
 *   IG_ACCOUNT_ID      — Instagram Business Account ID
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// ─── Config ──────────────────────────────────────────────────────────────────
const BLOTATO_BASE = 'https://backend.blotato.com/v2';
const {
  BLOTATO_API_KEY,
  FB_PAGE_TOKEN,
  FB_PAGE_ID = '108934711902801',
  IG_ACCOUNT_ID,
} = process.env;

// ─── Blotato API ─────────────────────────────────────────────────────────────

/**
 * Get all connected accounts from Blotato
 */
async function getBlotatoAccounts() {
  if (!BLOTATO_API_KEY) throw new Error('BLOTATO_API_KEY not set');
  const res = await axios.get(`${BLOTATO_BASE}/users/me/accounts`, {
    headers: { 'blotato-api-key': BLOTATO_API_KEY },
    timeout: 10000,
  });
  return res.data;
}

/**
 * Post content via Blotato
 * @param {string} caption  - Post caption/text
 * @param {string} imageUrl - Public image URL
 * @param {string} platform - 'facebook' | 'instagram'
 * @param {object} options  - Additional options (tags, scheduling, etc.)
 */
async function postViaBlotato(caption, imageUrl, platform = 'facebook', options = {}) {
  if (!BLOTATO_API_KEY) throw new Error('BLOTATO_API_KEY not set');
  
  const payload = {
    caption,
    ...(imageUrl && { image_url: imageUrl }),
    platform, // 'facebook' | 'instagram'
    ...options,
  };

  const res = await axios.post(`${BLOTATO_BASE}/posts`, payload, {
    headers: {
      'blotato-api-key': BLOTATO_API_KEY,
      'Content-Type': 'application/json',
    },
    timeout: 15000,
  });
  return res.data;
}

/**
 * Get post status from Blotato
 */
async function getPostStatus(postId) {
  if (!BLOTATO_API_KEY) throw new Error('BLOTATO_API_KEY not set');
  const res = await axios.get(`${BLOTATO_BASE}/posts/${postId}`, {
    headers: { 'blotato-api-key': BLOTATO_API_KEY },
    timeout: 10000,
  });
  return res.data;
}

// ─── Facebook Direct API (fallback when Blotato not fully connected) ─────────

/**
 * Post directly to Facebook Page via Graph API
 * Uses the EAAS... token from TOOLS.md
 */
async function postToFacebookPage(caption, imageUrl) {
  if (!FB_PAGE_TOKEN) throw new Error('FB_PAGE_TOKEN not set');

  let endpoint = `https://graph.facebook.com/v18.0/${FB_PAGE_ID}/feed`;
  let payload = { message: caption, access_token: FB_PAGE_TOKEN };

  if (imageUrl) {
    // Photo post — use /photos endpoint
    endpoint = `https://graph.facebook.com/v18.0/${FB_PAGE_ID}/photos`;
    payload = {
      url: imageUrl,
      caption,
      access_token: FB_PAGE_TOKEN,
    };
  }

  const res = await axios.post(endpoint, payload, { timeout: 15000 });
  return res.data;
}

/**
 * Post to Instagram Business Account via Graph API
 */
async function postToInstagram(caption, imageUrl) {
  if (!FB_PAGE_TOKEN || !IG_ACCOUNT_ID) {
    console.warn('[Instagram] IG_ACCOUNT_ID not set — skipping');
    return null;
  }

  // 1. Create media container
  const containerRes = await axios.post(
    `https://graph.facebook.com/v18.0/${IG_ACCOUNT_ID}/media`,
    {
      image_url: imageUrl,
      caption,
      access_token: FB_PAGE_TOKEN,
    },
    { timeout: 15000 }
  );

  const containerId = containerRes.data.id;

  // 2. Publish
  const publishRes = await axios.post(
    `https://graph.facebook.com/v18.0/${IG_ACCOUNT_ID}/media_publish`,
    {
      creation_id: containerId,
      access_token: FB_PAGE_TOKEN,
    },
    { timeout: 15000 }
  );

  return publishRes.data;
}

// ─── Content Templates for Studex ───────────────────────────────────────────

const CONTENT_TEMPLATES = {
  productLaunch: (product, price, description) =>
    `🐄 *${product}*\n\n${description}\n\n💰 R${price}\n\n📦 Order now: studexmeat.com\n.\n.\n.\n.\n.\n#StudexMeat #PremiumBeef #SouthAfrica #HeritageBeef`,

  testimonial: (quote, customerName) =>
    `"${quote}"\n\n— ${customerName}\n.\n.\n.\n.\n.\n#StudexMeat #CustomerLove`,

  behindTheScenes: (caption) =>
    `📸 ${caption}\n.\n.\n.\n.\n.\n#StudexMeat #FarmToTable #TraceableBeef`,

  promotion: (headline, details, cta) =>
    `🎉 *${headline}*\n\n${details}\n\n👉 ${cta}\n.\n.\n.\n.\n.\n#StudexMeat #LimitedOffer`,
};

// ─── CLI Interface ────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === '--sync-accounts' || command === 'sync') {
    console.log('[Blotato] Fetching connected accounts...');
    try {
      const accounts = await getBlotatoAccounts();
      console.log('[Blotato] Connected accounts:', JSON.stringify(accounts, null, 2));
    } catch (err) {
      console.error('[Blotato] Account fetch failed:', err.response?.data || err.message);
      // Fallback: try direct Facebook API
      console.log('[Facebook] Trying direct Graph API...');
      try {
        const res = await axios.get(
          `https://graph.facebook.com/v18.0/me/accounts?access_token=${FB_PAGE_TOKEN}`
        );
        console.log('[Facebook] Pages:', JSON.stringify(res.data, null, 2));
      } catch (fbErr) {
        console.error('[Facebook] Failed:', fbErr.response?.data || fbErr.message);
      }
    }
    return;
  }

  if (command === '--accounts') {
    console.log('[Studex] Account Status Report');
    console.log('─'.repeat(40));
    console.log('Facebook Page ID:', FB_PAGE_ID);
    console.log('Blotato configured:', BLOTATO_API_KEY ? 'YES' : 'NO');
    console.log('Page token configured:', FB_PAGE_TOKEN ? 'YES (last 8: ...' + FB_PAGE_TOKEN.slice(-8) + ')' : 'NO');
    console.log('IG account configured:', IG_ACCOUNT_ID || 'NO');
    console.log('─'.repeat(40));
    return;
  }

  if (command === '--post' || command === 'post') {
    // Parse: --post "caption" --image-url "url" --platform facebook
    const captionIdx = args.indexOf('--caption');
    const imageIdx = args.indexOf('--image-url');
    const platformIdx = args.indexOf('--platform');

    const caption = captionIdx !== -1 ? args[captionIdx + 1] : args[1] || 'Studex premium beef — farm to table';
    const imageUrl = imageIdx !== -1 ? args[imageIdx + 1] : null;
    const platform = platformIdx !== -1 ? args[platformIdx + 1] : 'facebook';

    console.log(`[Blotato] Posting to ${platform}...`);
    console.log(`  Caption: ${caption}`);
    console.log(`  Image:   ${imageUrl || 'none'}`);

    try {
      // Try Blotato first
      if (BLOTATO_API_KEY) {
        const result = await postViaBlotato(caption, imageUrl, platform);
        console.log('[Blotato] ✅ Post successful:', result);
        return result;
      }
    } catch (blotatoErr) {
      console.warn('[Blotato] Failed, falling back to direct Facebook API:', blotatoErr.response?.data || blotatoErr.message);
    }

    // Fallback: direct Facebook Graph API
    if (platform === 'facebook' || platform === 'all') {
      const result = await postToFacebookPage(caption, imageUrl);
      console.log('[Facebook] ✅ Posted:', result);
      return result;
    }

    if (platform === 'instagram') {
      const result = await postToInstagram(caption, imageUrl);
      console.log('[Instagram] ✅ Posted:', result);
      return result;
    }
  }

  if (command === '--template') {
    const templateName = args[1];
    const templateArgs = args.slice(2);
    const template = CONTENT_TEMPLATES[templateName];
    if (!template) {
      console.error(`[Template] Unknown: ${templateName}`);
      console.log('Available:', Object.keys(CONTENT_TEMPLATES).join(', '));
      return;
    }
    console.log(template(...templateArgs));
    return;
  }

  // Default: print help
  console.log(`
📝 Blotato Content Pipeline — Studex
=====================================
Usage:
  node blotato-content-pipeline.js --accounts
    → Show configured accounts

  node blotato-content-pipeline.js --sync-accounts
    → Fetch live account status from Blotato API

  node blotato-content-pipeline.js --post --caption "..." --image-url "..." --platform facebook
    → Post content (Blotato first, Facebook fallback)

  node blotato-content-pipeline.js --template productLaunch "Wagyu Biltong" "850" "Description..."
    → Generate content from template

Templates: ${Object.keys(CONTENT_TEMPLATES).join(', ')}
`);
}

main().catch(console.error);
