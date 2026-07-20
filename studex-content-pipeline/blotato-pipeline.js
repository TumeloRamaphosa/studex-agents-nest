#!/usr/bin/env node
/**
 * Studex × Blotato Content Pipeline
 * Fetches content ideas → posts to Facebook, Instagram, LinkedIn, Threads, TikTok, YouTube
 * 
 * Usage: node blotato-pipeline.js [--dry-run] [--platforms=fb,ig,li,tt,yt,th]
 * 
 * Environment:
 *   BLOTATO_API_KEY=blt_y5mVD6oMJrgFb8UsfWN3T4GSYN2ZvCeGsVWWwdaf8Og=
 */

const BLOTATO_BASE = 'https://backend.blotato.com/v2';
const API_KEY = process.env.BLOTATO_API_KEY || 'blt_y5mVD6oMJrgFb8UsfWN3T4GSYN2ZvCeGsVWWwdaf8Og=';

// Platform account IDs (fetched from /v2/users/me/accounts)
const ACCOUNT_IDS = {
  facebook:  '38744',
  instagram: '55765',
  linkedin:  '26628',
  threads:   '7701',
  tiktok:    '48423',
  youtube:   '41593',
};

// Content calendar — Studex products × platform variants
const CONTENT_CALENDAR = [
  {
    category: 'biltong',
    text: `🇿🇦 NOTHING SAYS SOUTH AFRICA LIKE REAL BILTONG.

Our premium beef biltong is dry-cured the traditional way — no shortcuts, no preservatives. Just salt, coriander, vinegar, and time.

🔥 Perfect for:
• Game nights
• Road trips
• Alto-getting moments

Order now → studex.co.za 🛒`,
    hashtags: '#Biltong #SouthAfrica #Studex #HeritageMeats #PremiumBiltong',
  },
  {
    category: 'wagyu',
    text: `🥩 WAGYU DONE RIGHT.

MS5+ Australian Wagyu from Studex. Rich marbling. Melt-on-your-tongue tenderness. This isn't your average braai meat.

Available in:
→ Ribeye
→ Sirloin  
→ Filet Mignon

DM for bulk orders. We supply fine dining restaurants across SA.`,
    hashtags: '#Wagyu #AustralianWagyu #Studex #FineDining #SouthAfrica #Steak',
  },
  {
    category: 'caviar',
    text: `✨ CAVIAR. FOR THE ONES WHO KNOW.

Oscietra Golden Caviar — the aristocrat of the sea. Rich, nutty, with that unmistakable pop of the Baltic.

Perfect for:
→ Celebrations
→ Corporate gifting
→ The finer things in life

Minimum order: 100g. Delivered anywhere in SA.`,
    hashtags: '#Caviar #Luxury #Studex #Oscietra #FineDiningSA #Gourmet',
  },
  {
    category: 'coffee',
    text: `☕ WILD. ORGANIC. IMPACT-DRIVEN.

Wildlife Coffee from Studex — single-origin African beans that taste like the savanna smells.

Every bag purchased funds wildlife conservation in SA. That's not marketing. That's the mission.

→ Organic
→ Small-batch roasted
→ Direct trade`,
    hashtags: '#WildlifeCoffee #AfricanCoffee #Studex #Conservation #OrganicCoffee #SouthAfrica',
  },
  {
    category: 'bundles',
    text: `🎁 THE STUDEX EXPERIENCE BOX.

The ultimate meat & coffee sampler — curated for the person who appreciates quality.

What's inside:
🇿🇦 Premium biltong selection
🥩 Wagyu MS5+ cut
☕ Wildlife Coffee 250g
✨ Caviar 50g tasting

One box. Every premium taste. Link in bio.`,
    hashtags: '#Studex #GourmetBox #SouthAfricanGourmet #GiftIdeas #PremiumMeats',
  },
];

// Platform-specific text adapters
function adaptForPlatform(text, hashtags, platform) {
  const full = `${text}\n\n${hashtags}`;
  switch (platform) {
    case 'instagram':
      // Keep it punchy, shorten for caption
      return full.length > 2200 ? text + '\n\n' + hashtags : full;
    case 'tiktok':
      // TikTok: short + punchy
      return text.substring(0, 150) + '...\n\n' + hashtags;
    case 'linkedin':
      // LinkedIn: professional tone
      return text + '\n\n' + hashtags + '\n\n—\nTumelo Ramaphosa | Studex';
    case 'threads':
      return full;
    case 'youtube':
      // YouTube: description text
      return full;
    case 'facebook':
    default:
      return full;
  }
}

// Platform name map (must match Blotato's targetType values)
const PLATFORM_MAP = {
  facebook:  { targetType: 'facebook',  platform: 'facebook', pageId: '108934711902801' }, // StudEx Meat page
  instagram: { targetType: 'instagram', platform: 'instagram' },
  linkedin:  { targetType: 'linkedin',  platform: 'linkedin'  },
  threads:   { targetType: 'threads',   platform: 'threads'   },
  tiktok:    { targetType: 'tiktok',    platform: 'tiktok'    },
  youtube:   { targetType: 'youtube',   platform: 'youtube'   },
};

// Build the correct Blotato v2 post payload
function buildPostPayload(accountId, text, platform, options = {}) {
  const p = PLATFORM_MAP[platform];
  if (!p) throw new Error(`Unknown platform: ${platform}`);

  const payload = {
    post: {
      accountId: String(accountId),
      content: {
        platform: p.platform,
        text: text,
        mediaUrls: options.mediaUrls || [],
        ...(options.extra && { ...options.extra }),
      },
      target: {
        targetType: p.targetType,
        ...(p.pageId && { pageId: p.pageId }),
      },
    },
  };

  // Add scheduling if provided (SAST = UTC+2)
  if (options.scheduledAt) {
    payload.post.scheduledAt = options.scheduledAt.toISOString();
  }

  return payload;
}

// Create or schedule a post
async function postToBlotato(accountId, text, platform, options = {}) {
  const { dryRun = false } = options;

  if (dryRun) {
    const preview = options.scheduledAt
      ? `[DRY RUN] Would schedule to ${platform} at ${options.scheduledAt.toISOString()}`
      : `[DRY RUN] Would post to ${platform}`;
    console.log(`  ${preview} (${accountId}): "${text.substring(0, 60)}..."`);
    return { id: 'dry-run' };
  }

  const payload = buildPostPayload(accountId, text, platform, options);

  const res = await fetch(`${BLOTATO_BASE}/posts`, {
    method: 'POST',
    headers: {
      'blotato-api-key': API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(`${platform} (${accountId}): ${JSON.stringify(err)}`);
  }

  return res.json();
}

// Main run
async function run() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const platformsArg = args.find(a => a.startsWith('--platforms='));
  const targetPlatforms = platformsArg 
    ? platformsArg.split('=')[1].split(',').map(p => p.trim())
    : Object.keys(ACCOUNT_IDS);

  console.log(`\n🐂 Studex × Blotato Content Pipeline`);
  console.log(`====================================`);
  console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'}`);
  console.log(`Platforms: ${targetPlatforms.join(', ')}`);
  console.log(`Content items: ${CONTENT_CALENDAR.length}`);
  console.log('');

  // Pick today's content (rotates through calendar based on day of year)
  const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0)) / 86400000);
  const todayContent = CONTENT_CALENDAR[dayOfYear % CONTENT_CALENDAR.length];
  
  // Also post tomorrow's teaser (offset by 1)
  const tomorrowContent = CONTENT_CALENDAR[(dayOfYear + 1) % CONTENT_CALENDAR.length];

  console.log(`📅 Today's focus: ${todayContent.category.toUpperCase()}`);
  console.log(`   "${todayContent.text.substring(0, 80)}..."\n`);

  const options = { mediaUrls: [] };
  let posted = 0;
  let errors = [];

  // Post today's content to each target platform
  for (const platform of targetPlatforms) {
    const accountId = ACCOUNT_IDS[platform];
    if (!accountId) {
      console.log(`⚠️  Unknown platform: ${platform}`);
      continue;
    }

    const adaptedText = adaptForPlatform(todayContent.text, todayContent.hashtags, platform);
    
    try {
      console.log(`📤 Posting to ${platform} (${accountId})...`);
      
      // Schedule for staggered times (9am, 12pm, 3pm, 6pm SAST = 7, 10, 13, 16 UTC)
      const staggerIndex = targetPlatforms.indexOf(platform);
      const scheduledAt = new Date();
      scheduledAt.setUTCHours(7 + staggerIndex * 3, 0, 0, 0);
      if (scheduledAt <= new Date()) {
        scheduledAt.setDate(scheduledAt.getDate() + 1); // tomorrow if time has passed
      }

      const result = await postToBlotato(accountId, adaptedText, platform, {
        scheduledAt,
        mediaUrls: options.mediaUrls || [],
      });
      console.log(`   ✅ Posted to ${platform} (ID: ${result.id || result.postId || 'ok'})`);
      console.log(`   📆 Scheduled for: ${scheduledAt.toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' })}`);
      posted++;
      
      // Rate limit between posts
      await new Promise(r => setTimeout(r, 1500));
    } catch (err) {
      console.log(`   ❌ Error: ${err.message}`);
      errors.push({ platform, error: err.message });
    }
  }

  // Summary
  console.log(`\n📊 Pipeline Summary`);
  console.log(`===================`);
  console.log(`✅ Posted: ${posted}/${targetPlatforms.length}`);
  if (errors.length > 0) {
    console.log(`❌ Errors:`);
    errors.forEach(e => console.log(`   ${e.platform}: ${e.error}`));
  }
  console.log(`\n🌐 Blotato Dashboard: https://app.blotato.com`);
  console.log(`📅 Studex content calendar rotates through: ${CONTENT_CALENDAR.map(c => c.category).join(', ')}`);
  
  if (dryRun) {
    console.log(`\n⚠️  DRY RUN — no posts were actually published. Remove --dry-run to go live.`);
  }

  process.exit(errors.length > 0 ? 1 : 0);
}

run().catch(err => {
  console.error('Pipeline crashed:', err);
  process.exit(1);
});
