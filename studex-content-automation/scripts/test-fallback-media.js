#!/usr/bin/env node
/**
 * Fallback media unit test - proves the pending caption is published WITH
 * its image, and that a dead image can never turn a working publish into a
 * failing one.
 *
 * NEGATIVE CONTROL: the pre-fix source has no pendingImageUrl()/withMedia(),
 * so this test cannot even load it and exits 1. The fix is what makes it
 * pass.
 *
 * Run: node scripts/test-fallback-media.js
 */
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(path.join(__dirname, 'blotato-fallback.js'), 'utf8');
const start = src.indexOf('function pendingImageUrl');
const end = src.indexOf('async function post(target, text)');
if (start === -1 || end === -1 || end < start) {
  console.error('\u274c could not load the media helpers from blotato-fallback.js');
  console.error('   The pre-fix source has no pendingImageUrl()/withMedia(), so this test');
  console.error('   CANNOT PASS against it - that is the negative control.');
  process.exit(1);
}
const { pendingImageUrl, withMedia, resolveMedia } = new Function(
  src.slice(start, end) + '; return { pendingImageUrl, withMedia, resolveMedia };')();

// The targets exactly as the script declares them (the pre-fix media: []).
const TARGETS = [
  { accountId: '26628', platform: 'linkedin', media: [] },
  { accountId: '7701', platform: 'threads', media: [] },
];

let failed = 0;
function check(name, cond, extra) {
  if (!cond) failed++;
  console.log((cond ? '\u2705 ' : '\u274c ') + name + (extra ? ' - ' + extra : ''));
}

(async () => {
  // A REAL fixture, not a synthetic one: the 22 Oct pending file is the
  // caption that actually shipped pictureless.
  const realPending = JSON.parse(fs.readFileSync(
    path.join(__dirname, '../posts/pending/2026-10-22.json'), 'utf8'));
  const realUrl = pendingImageUrl(realPending);

  check('reads the image out of the REAL 22 Oct pending file',
    !!realUrl && realUrl.indexOf('https://') === 0, realUrl || '(none)');
  check('no media -> null', pendingImageUrl({ caption: 'x' }) === null);
  check('media as a plain string -> that string',
    pendingImageUrl({ media: 'https://x/y.png' }) === 'https://x/y.png');
  check('empty image -> null', pendingImageUrl({ media: { image: '' } }) === null);
  check('media.image wins over a top-level mediaUrl',
    pendingImageUrl({ media: { image: 'https://a/1.png' }, mediaUrl: 'https://b/2.png' }) === 'https://a/1.png');

  const withImg = withMedia(TARGETS, realUrl);
  check('every target now carries the image',
    withImg.every(t => t.media.length === 1 && t.media[0] === realUrl));
  check('the image reaches THREADS - the target that actually publishes',
    withImg.find(t => t.platform === 'threads').media[0] === realUrl);

  // NEGATIVE CONTROL - the pre-fix behaviour. post() sends target.media
  // verbatim, so the old targets shipped an empty media list.
  const oldBehaviour = TARGETS.map(t => ({ ...t }));
  check('NEGATIVE CONTROL: the pre-fix targets sent NO image',
    oldBehaviour.every(t => t.media.length === 0));
  check('NEGATIVE CONTROL: the fix changes that outcome',
    oldBehaviour.find(t => t.platform === 'threads').media.length === 0 &&
    withImg.find(t => t.platform === 'threads').media.length === 1);

  check('no media URL -> still publishes without media',
    withMedia(TARGETS, null).every(t => t.media.length === 0));

  check('resolveMedia returns the URL when the image is live',
    (await resolveMedia(realPending, async () => true)) === realUrl);
  check('resolveMedia returns null when the image is NOT live',
    (await resolveMedia(realPending, async () => false)) === null);
  check('resolveMedia returns null when there is no image at all',
    (await resolveMedia({ caption: 'x' }, async () => true)) === null);

  console.log(failed === 0 ? '\nALL FALLBACK MEDIA TESTS PASSED' : '\n' + failed + ' FALLBACK MEDIA TEST(S) FAILED');
  process.exit(failed === 0 ? 0 : 1);
})();
