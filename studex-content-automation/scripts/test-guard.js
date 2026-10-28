#!/usr/bin/env node
/**
 * Guard unit test — proves validateCaption() blocks bad copy.
 * Run: node scripts/test-guard.js
 */
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(path.join(__dirname, 'daily-content-agent.js'), 'utf8');
const block = src.slice(src.indexOf('const FORBIDDEN_CAPTION_CLAIMS'), src.indexOf('// ─── Kimi (Moonshot) provider'));
const validateCaption = new Function(`${block}; return validateCaption;`)();

const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, '../products/catalog.json'), 'utf8'));
const ribeye = catalog.products.find(p => p.id === 'wagyu-ribeye');
const caviar = catalog.products.find(p => p.id === 'caviar-oscietra');

const cases = [
  { name: 'correct ribeye caption', product: ribeye, cap: 'Wagyu Ribeye Steak — the deepest marbling in our range. From R1,950. So tell us: rare or medium?', expect: [] },
  { name: 'stale price R1,850', product: ribeye, cap: 'Wagyu Ribeye Steak at R1,850. Our deepest marbling. Ready for the braai?', expect: ['price'] },
  { name: 'wrong caviar unit', product: caviar, cap: 'Oscietra Imperial caviar, R4,200 per 250g. Yours?', expect: ['250g'] },
  { name: 'halaal overclaim', product: ribeye, cap: 'Wagyu Ribeye — every product we produce is Halaal guaranteed. Ready?', expect: ['claim'] },
  { name: 'unsupported MS5+ / Australian', product: ribeye, cap: 'Australian MS5+ Wagyu Ribeye at R1,950. Ready?', expect: ['claim'] },
  { name: 'no CTA', product: ribeye, cap: 'Wagyu Ribeye Steak at From R1,950. Our deepest marbling in the range.', expect: ['CTA'] },
  { name: 'forbidden Rainforest Alliance', product: catalog.products.find(p => p.id === 'coffee-roasted-washed'), cap: 'Rainforest Alliance certified washed coffee at R400/kg. Who is roasting?', expect: ['claim'] },
];

let failed = 0;
for (const c of cases) {
  const problems = validateCaption(c.cap, c.product);
  const ok = c.expect.every(tag => problems.some(p => p.toLowerCase().includes(tag.toLowerCase())));
  const clean = problems.length === 0;
  const good = c.expect.length === 0 ? clean : (ok && !clean);
  if (!good) failed++;
  console.log(`${good ? '✅' : '❌'} ${c.name}`);
  console.log(`   problems: ${problems.length ? problems.join(' | ') : '(none)'}`);
}
console.log(failed === 0 ? '\nALL GUARD TESTS PASSED' : `\n${failed} GUARD TEST(S) FAILED`);
process.exit(failed === 0 ? 0 : 1);
