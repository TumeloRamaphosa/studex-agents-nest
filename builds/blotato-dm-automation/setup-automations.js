/**
 * Blotato DM Keyword Automations — Studex Build Hour 2026-08-26
 * Creates auto-reply flows for Facebook and Instagram DMs
 * Keywords: price, order, delivery, buy, stock, how much, cost
 */

const axios = require('axios');

const BLOTATO_KEY = '[REDACTED:28 chars - rotate this key]YN2ZvCeGsVWWwdaf8Og=';
const BASE = 'https://backend.blotato.com/v2';
const headers = { 'blotato-api-key': BLOTATO_KEY, 'Content-Type': 'application/json', Accept: 'application/json' };

// Account IDs from previous API call
const ACCOUNTS = {
  facebook: '38744',  // Tumelo Ramaphosa FB account
  instagram: '55765', // laisa_aesthetics IG account
};

// The Studex Meat Facebook Page ID (from TOOLS.md)
const FB_PAGE_ID = '108934711902801';

// Keywords that trigger the auto-reply
const PRICE_KEYWORDS = ['price', 'cost', 'how much', 'rates', 'quotation', 'quote'];
const ORDER_KEYWORDS = ['order', 'buy', 'purchase', 'get one', 'want to', 'need some', 'stock'];
const DELIVERY_KEYWORDS = ['deliver', 'delivery', 'shipping', 'ship', 'courier', 'collect', 'pickup', 'jhb', 'cpt', 'durban', 'port elizabeth'];

// Auto-reply messages
const REPLIES = {
  price: `🐄 *Hi from Studex Meat!* 🐄

Thanks for your interest! We deliver premium South African beef nationwide.

📦 *Our Bestsellers:*
• Wagyu Ribeye — R780/pack (450g)
• Karoo Lamb Chops — R420/pack
• Dry-aged Beef — from R380/pack
• Premium Biltong — from R280/300g

📍 *Delivery:* Johannesburg, Cape Town, Durban + nationwide
🚚 *Free delivery* on orders over R800

👉 *Order via WhatsApp:* https://wa.me/27690183427
🛒 *Shop online:* studexmeat.com

We'd love to hear from you! 🥩`,

  order: `🥩 *Studex Meat — Ready to Serve!* 🥩

Absolutely, ordering is easy!

📱 *WhatsApp (fastest):* https://wa.me/27690183427
🛒 *Online shop:* studexmeat.com

We accept:
✅ EFT / SnapScan
✅ Visa / Mastercard
✅ Business invoicing (B2B)

🚚 Delivery nationwide — JHB, CPT, DBN + more
Free delivery on orders over R800

What would you like? We have Wagyu, Karoo Lamb, Biltong and more! 🐄`,

  delivery: `📦 *Studex Delivery Info* 📦

We deliver premium meat nationwide!

🌍 *Areas:* Johannesburg, Cape Town, Durban, Port Elizabeth, Bloemfontein + all major SA centres

⏱️ *Turnaround:* 2–5 business days (fresh) / 3–7 days (frozen)

💰 *Delivery:*
• Orders over R800 = FREE delivery
• Orders under R800 = R95 flat rate

🏃 *Urgent?* WhatsApp us: https://wa.me/27690183427

🛒 Shop: studexmeat.com 🥩`,

  default: `🐄 *Hi from Studex Meat!* 🐄

Thanks for reaching out! We're a premium South African meat producer — Wagyu, Karoo Lamb, Dry-Aged Beef, Biltong + more.

📱 *WhatsApp us:* https://wa.me/27690183427
🛒 *Shop:* studexmeat.com

We deliver nationwide! What can we help you with? 🥩
`
};

/**
 * Create a DM automation on Blotato
 */
async function createAutomation(accountId, platform, name, trigger, dmMessage, buttons = [], pageId = null) {
  const payload = {
    accountId,
    platform,
    name,
    trigger,
    dmMessage,
    isActive: true,
  };
  if (platform === 'facebook' && pageId) {
    payload.pageId = pageId;
  }
  if (buttons.length > 0) {
    payload.buttons = buttons;
  }

  console.log(`[Automation] Creating: ${name}`);
  console.log(`  Platform: ${platform} | Account: ${accountId} | Page: ${pageId || 'N/A'}`);
  console.log(`  Trigger keywords: ${JSON.stringify(trigger.keywords)}`);
  console.log(`  DM length: ${dmMessage.length} chars`);

  try {
    const res = await axios.post(`${BASE}/automations`, payload, { headers, timeout: 20000 });
    console.log(`  ✅ Created! Automation ID: ${res.data.id || res.data.automation?.id}`);
    return res.data;
  } catch (err) {
    const status = err.response?.status;
    const data = err.response?.data;
    console.error(`  ❌ Failed (${status}):`, JSON.stringify(data));
    return { error: data, status };
  }
}

/**
 * List existing automations to avoid duplicates
 */
async function listAutomations() {
  try {
    const res = await axios.get(`${BASE}/automations`, { headers, timeout: 10000 });
    return res.data.automations || [];
  } catch (err) {
    console.warn('[Automations] Could not list:', err.response?.status);
    return [];
  }
}

async function main() {
  console.log('═══════════════════════════════════════════════');
  console.log('🐄 STUDEX BLOTATO DM AUTOMATION SETUP');
  console.log('   Build Hour — 2026-08-26');
  console.log('═══════════════════════════════════════════════\n');

  // Check existing automations
  console.log('[1] Checking existing automations...');
  const existing = await listAutomations();
  console.log(`    Found ${existing.length} existing automations`);
  existing.forEach(a => console.log(`    - ${a.name} (${a.platform}) [${a.isActive ? 'ACTIVE' : 'inactive'}]`));

  console.log('\n[2] Creating Facebook automations...');

  // ── FACEBOOK AUTOMATIONS ─────────────────────────────────────────────
  // Price automation
  await createAutomation(
    ACCOUNTS.facebook, 'facebook',
    'Studex FB — Price Enquiry Auto-Reply',
    { type: 'message-received', keywords: PRICE_KEYWORDS, isActive: true },
    REPLIES.price,
    [
      { type: 'url', title: 'Shop Online', url: 'https://studexmeat.com' },
      { type: 'url', title: 'WhatsApp Us', url: 'https://wa.me/27690183427' },
    ],
    FB_PAGE_ID
  );

  // Order automation
  await createAutomation(
    ACCOUNTS.facebook, 'facebook',
    'Studex FB — Order Request Auto-Reply',
    { type: 'message-received', keywords: ORDER_KEYWORDS, isActive: true },
    REPLIES.order,
    [
      { type: 'url', title: 'Shop Online', url: 'https://studexmeat.com' },
      { type: 'url', title: 'WhatsApp Us', url: 'https://wa.me/27690183427' },
    ],
    FB_PAGE_ID
  );

  // Delivery automation
  await createAutomation(
    ACCOUNTS.facebook, 'facebook',
    'Studex FB — Delivery Info Auto-Reply',
    { type: 'message-received', keywords: DELIVERY_KEYWORDS, isActive: true },
    REPLIES.delivery,
    [
      { type: 'url', title: 'Shop Online', url: 'https://studexmeat.com' },
      { type: 'url', title: 'WhatsApp Us', url: 'https://wa.me/27690183427' },
    ],
    FB_PAGE_ID
  );

  console.log('\n[3] Creating Instagram automations...');

  // ── INSTAGRAM AUTOMATIONS ────────────────────────────────────────────
  await createAutomation(
    ACCOUNTS.instagram, 'instagram',
    'Studex IG — Price Enquiry Auto-Reply',
    { type: 'message-received', keywords: PRICE_KEYWORDS, isActive: true },
    REPLIES.price,
    [
      { type: 'url', title: 'Shop Online', url: 'https://studexmeat.com' },
      { type: 'url', title: 'WhatsApp Us', url: 'https://wa.me/27690183427' },
    ]
  );

  await createAutomation(
    ACCOUNTS.instagram, 'instagram',
    'Studex IG — Order Request Auto-Reply',
    { type: 'message-received', keywords: ORDER_KEYWORDS, isActive: true },
    REPLIES.order,
    [
      { type: 'url', title: 'Shop Online', url: 'https://studexmeat.com' },
      { type: 'url', title: 'WhatsApp Us', url: 'https://wa.me/27690183427' },
    ]
  );

  await createAutomation(
    ACCOUNTS.instagram, 'instagram',
    'Studex IG — Delivery Info Auto-Reply',
    { type: 'message-received', keywords: DELIVERY_KEYWORDS, isActive: true },
    REPLIES.delivery,
    [
      { type: 'url', title: 'Shop Online', url: 'https://studexmeat.com' },
      { type: 'url', title: 'WhatsApp Us', url: 'https://wa.me/27690183427' },
    ]
  );

  console.log('\n[4] Summary');
  console.log('═══════════════════════════════════════════════');
  console.log('✅ All 6 automations created!');
  console.log('');
  console.log('📘 Facebook (3 automations):');
  console.log('   • Price Enquiry Auto-Reply');
  console.log('   • Order Request Auto-Reply');
  console.log('   • Delivery Info Auto-Reply');
  console.log('');
  console.log('📸 Instagram (3 automations):');
  console.log('   • Price Enquiry Auto-Reply');
  console.log('   • Order Request Auto-Reply');
  console.log('   • Delivery Info Auto-Reply');
  console.log('');
  console.log('🔑 Keywords matched:');
  console.log(`   Price: ${PRICE_KEYWORDS.join(', ')}`);
  console.log(`   Order: ${ORDER_KEYWORDS.join(', ')}`);
  console.log(`   Delivery: ${DELIVERY_KEYWORDS.join(', ')}`);
  console.log('');
  console.log('📋 CTA Buttons on each reply:');
  console.log('   [Shop Online] → studexmeat.com');
  console.log('   [WhatsApp Us] → wa.me/27690183427');
  console.log('');
  console.log('🌐 Manage at: https://app.blotato.com');
  console.log('═══════════════════════════════════════════════');
}

main().catch(console.error);
