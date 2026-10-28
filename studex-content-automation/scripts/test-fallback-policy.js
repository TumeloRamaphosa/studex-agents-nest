#!/usr/bin/env node
/**
 * Fallback caption-policy unit test.
 *
 * Path A refuses to publish a caption that breaks the brand policy. Path B
 * used to refuse nothing: a caption carrying a price went live on Threads
 * at 06:59Z on 2026-10-28, and the only gate that noticed (the 09:20
 * pre-flight) runs ~20 minutes AFTER the publish. This test proves path B
 * now refuses BEFORE publishing.
 *
 * NEGATIVE CONTROL: the pre-fix source has no policyFailures(), so this test
 * cannot load it and exits 1. The fix is what makes it pass.
 *
 * Run: node scripts/test-fallback-policy.js
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const src = fs.readFileSync(path.join(__dirname, 'blotato-fallback.js'), 'utf8');
const start = src.indexOf('function pendingImageUrl');
const end = src.indexOf('async function post(target, text)');
if (start === -1 || end === -1 || end < start) {
  console.error('\u274c could not load the media helpers from blotato-fallback.js');
  console.error('   The pre-fix source has no pendingImageUrl()/withMedia(), so this test');
  console.error('   CANNOT PASS against it - that is the negative control.');
  process.exit(1);
}
if (src.indexOf('function policyFailures') === -1) {
  console.error('\u274c could not load policyFailures() from blotato-fallback.js');
  console.error('   The pre-fix source has no caption policy check, so a priced caption');
  console.error('   would be PUBLISHED. This test CANNOT PASS against it - that is the');
  console.error('   negative control.');
  process.exit(1);
}
// The sliced source references module-level `path` and `spawnSync`, so both
// are handed into the function scope. The media test did not need them
// because its helpers touch neither.
const { policyFailures } = new Function(
  'spawnSync', 'path', '__dirname',
  src.slice(start, end) + '; return { policyFailures };')(spawnSync, path, __dirname);

let failed = 0;
function check(name, cond, extra) {
  if (!cond) failed++;
  console.log((cond ? '\u2705 ' : '\u274c ') + name + (extra ? ' - ' + extra : ''));
}

// The REAL caption that went live with a price on 2026-10-28.
const realPending = JSON.parse(fs.readFileSync(
  path.join(__dirname, '../posts/pending/2026-10-28.json'), 'utf8'));

const priced = policyFailures(realPending.caption);
check('the REAL 28 Oct caption that went live with a price is flagged',
  priced.length > 0 && priced.some(f => f.indexOf('Price published on public feed') !== -1),
  priced.join(' | ') || '(nothing flagged)');
check('a caption with no price has no violations',
  policyFailures('Our biltong is the good stuff. Tag a friend #studex').length === 0);
check('R1450 without a comma is still a price',
  policyFailures('It costs R1450 today').length > 0);
check('R 1,450 is still a price',
  policyFailures('It costs R 1,450 today').length > 0);
check('an empty caption is a violation, not a pass',
  policyFailures('').length > 0);

// END TO END: a priced caption must NOT be published. The fixture uses a
// date that no real post uses, so it can never touch a live post.
const fakeDate = '1999-12-31';
const pendingDir = path.join(__dirname, '../posts/pending');
const fixture = path.join(pendingDir, fakeDate + '.json');
fs.writeFileSync(fixture, JSON.stringify({
  caption: 'Our Wagyu Biltong Gold 1kg box (R1,450) comes as fourteen 70g packets.',
  status: 'APPROVED_PENDING_FB_TOKEN',
}, null, 2));

const run = spawnSync('node', [path.join(__dirname, 'blotato-fallback.js'), fakeDate],
                      { encoding: 'utf8' });
const out = (run.stdout || '') + (run.stderr || '');
check('the fallback REFUSES a priced caption (exit 1)', run.status === 1, 'exit=' + run.status);
check('the refusal is stated in the output', out.indexOf('CAPTION POLICY VIOLATION') !== -1);
check('the caption was NOT published', out.indexOf('POSTED') === -1);
const after = JSON.parse(fs.readFileSync(fixture, 'utf8'));
check('the pending file records the violation',
  Array.isArray(after.policyFailures) && after.policyFailures.length > 0);
check('the pending file is marked blocked',
  after.status === 'BLOCKED_BY_CAPTION_POLICY', after.status);
fs.unlinkSync(fixture);

console.log(failed === 0
  ? '\n\u2705 ALL FALLBACK POLICY TESTS PASSED'
  : '\n\u274c ' + failed + ' FALLBACK POLICY TEST(S) FAILED');
process.exit(failed === 0 ? 0 : 1);
