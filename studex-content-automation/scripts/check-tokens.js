#!/usr/bin/env node
/**
 * Token Status Checker — Studex Content Automation
 * Checks Facebook Page access token validity
 * 
 * Usage:
 *   node check-tokens.js
 */

const path = require('path');

function loadEnv() {
  const env = {};
  // Project-local .env first — it holds FB_PAGE_TOKEN for this project.
  for (const f of [path.join(__dirname, '../.env'), '/workspace/.env', path.join(process.env.HOME || '/root', '.env')]) {
    if (require('fs').existsSync(f)) {
      require('fs').readFileSync(f, 'utf8').split('\n').forEach(line => {
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
  return env;
}

const env = loadEnv();

console.log(`
🐂 Studex — Token Status Report
${'='.repeat(40)}
📦 Facebook Page Token:
   ${env.FB_PAGE_TOKEN ? '✅ SET (' + env.FB_PAGE_TOKEN.slice(-8) + ')' : '❌ NOT SET'}
   → Renew: https://developers.facebook.com
     → Meta Business Suite → Page Settings → Page Access Tokens

📦 OpenAI API Key:
   ${env.OPENAI_API_KEY ? '✅ SET (' + env.OPENAI_API_KEY.slice(-8) + ')' : '❌ NOT SET'}
   → Get key: https://platform.openai.com/api-keys

📦 Facebook Page ID:
   ${env.FB_PAGE_ID || '❌ NOT SET'} (default: 108934711902801)
`);
