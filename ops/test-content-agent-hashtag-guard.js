/**
 * Regression test for the content-agent hashtag handling.
 *
 * GROUND TRUTH (corrected 2026-10-23): a 7-tag caption published SUCCESSFULLY
 * and shipped with 5 tags (live IG post 8383092, published 2026-10-22 from a
 * 7-tag pending caption of 815 chars -> 793 chars / 5 tags live). The pre-fix
 * fallback had no trim, so Blotato TRUNCATES server-side - it does NOT reject
 * with 422 code 30004.
 *
 * So the correct behaviour is TRIM, not BLOCK:
 *   - blocking would mean exit(1) and NO post at all
 *   - trimming ships the post with the first 5 tags
 *
 * This test asserts:
 *   1. capHashtags() keeps exactly the first 5 tags, in order
 *   2. it removes the LAST tag (no trailing space) - the bug that made the
 *      old "replace(tag + ' ')" a silent no-op
 *   3. a caption already at 5 tags is untouched
 *   4. the caption is TRIMMED before validateCaption() runs, so a 7-tag
 *      caption does not block the run
 *   5. validateCaption() still rejects >5 tags as a BACKSTOP
 *   6. NEGATIVE CONTROL: the old "replace(tag + ' ')" implementation leaves
 *      the last tag in place - proving the test can actually fail
 */
const fs = require('fs');
const path = require('path');

const ROOT = '/workspace';
const P = path.join(ROOT, 'studex-content-automation/scripts/daily-content-agent.js');
const src = fs.readFileSync(P, 'utf8');

const PASSES = [];
const FAILS = [];

function extractFn(name) {
  const start = src.indexOf('function ' + name);
  if (start === -1) throw new Error(name + ' NOT FOUND');
  let depth = 0, i = src.indexOf('{', start);
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  return src.slice(start, i);
}

// validateCaption() closes over the module-scope FORBIDDEN_CAPTION_CLAIMS
// constant, so the constant and the functions must be evaluated TOGETHER —
// two separate eval() calls do not share scope for a `const` binding.
function extractConst(name) {
  const start = src.indexOf('const ' + name);
  if (start === -1) throw new Error(name + ' NOT FOUND');
  return src.slice(start, src.indexOf('];', start) + 2);
}

// eslint-disable-next-line no-eval
eval(extractConst('FORBIDDEN_CAPTION_CLAIMS') + '\n' +
     extractFn('capHashtags') + '\n' +
     extractFn('validateCaption') + '\n' +
     'globalThis.__cap = capHashtags; globalThis.__val = validateCaption;');
const capFn = globalThis.__cap;
const validateFn = globalThis.__val;

const product = {
  name: 'Wagyu Biltong Gold — 1kg',
  description: 'Wagyu biltong, 1kg pack, premium South African beef.',
  allowed_prices: ['1450'],
};

const body = 'Great biltong for a South African kitchen. From R1,450. ' +
             'What would you pair with it?';

const tags5 = '#biltong #wagyubiltong #southafricanfood #studex #biltonglover';
const tags7 = '#biltong #wagyubiltong #southafricanfood #studex #biltonglover ' +
              '#giftideas #proudlysa';

const cap7 = body + '\n\n' + tags7;
const cap5 = body + '\n\n' + tags5;

// 1 + 2: the 7-tag caption trims to the first 5, and the LAST tag (no trailing
// space) is actually removed.
const out7 = capFn(cap7);
const kept7 = out7.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
if (kept7.length === 5) {
  PASSES.push('7-tag caption trims to 5 tags');
} else {
  FAILS.push('expected 5 tags after trim, got ' + kept7.length + ': ' +
             JSON.stringify(kept7));
}
if (JSON.stringify(kept7) ===
    JSON.stringify(['#biltong', '#wagyubiltong', '#southafricanfood',
                    '#studex', '#biltonglover'])) {
  PASSES.push('the FIRST five tags are kept, in order');
} else {
  FAILS.push('wrong tags kept: ' + JSON.stringify(kept7));
}
if (!/#proudlysa/.test(out7) && !/#giftideas/.test(out7)) {
  PASSES.push('the trailing tags (incl. the last, which has no trailing ' +
              'space) are removed');
} else {
  FAILS.push('trailing tags survived the trim: ' +
             JSON.stringify(out7.slice(-80)));
}

// 3: exactly-5 is untouched.
if (capFn(cap5) === cap5) {
  PASSES.push('an exactly-5-tag caption is untouched (no off-by-one)');
} else {
  FAILS.push('a 5-tag caption was modified: ' +
             JSON.stringify(capFn(cap5).slice(-90)));
}

// 4: THE REGRESSION GUARD. The trim must run BEFORE validateCaption(),
// otherwise a 7-tag caption blocks the whole 08:55 content-agent run.
const flowIdx = src.indexOf('const trimmed = capHashtags(caption);');
const valIdx = src.indexOf('const problems = validateCaption(caption, product);');
if (flowIdx === -1) {
  FAILS.push('the caption is never trimmed before validation');
} else if (valIdx === -1) {
  FAILS.push('validateCaption call not found');
} else if (flowIdx < valIdx) {
  PASSES.push('the caption is TRIMMED before validateCaption() runs - a ' +
              '7-tag caption cannot block the run');
} else {
  FAILS.push('validateCaption() runs BEFORE the trim - a 7-tag caption ' +
             'would block the publish');
}

// 5: validateCaption still rejects >5 tags as a backstop.
const r7 = validateCaption(cap7, product);
const r5 = validateCaption(cap5, product);
if (r7.some(p => /hashtag/i.test(p))) {
  PASSES.push('validateCaption still rejects >5 tags as a backstop: ' +
              r7.filter(p => /hashtag/i.test(p)).join('; '));
} else {
  FAILS.push('validateCaption no longer backstops the hashtag count');
}
if (!r5.some(p => /hashtag/i.test(p))) {
  PASSES.push('a 5-tag caption passes the guard (no false positive)');
} else {
  FAILS.push('5-tag caption wrongly rejected: ' + JSON.stringify(r5));
}

// 6: NEGATIVE CONTROL - the old implementation must fail this test.
function oldCap(text) {
  const tags = text.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
  if (tags.length <= 5) return text;
  let out = text;
  for (const t of tags.slice(5)) {
    out = out.replace(t + ' ', '');   // the old, broken form
  }
  return out;
}
const oldOut = oldCap(cap7);
const oldKept = oldOut.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
if (oldKept.length > 5) {
  PASSES.push('negative control: the OLD implementation leaves ' +
              oldKept.length + ' tags - the test can detect the bug');
} else {
  FAILS.push('negative control failed - the old implementation also trims, ' +
             'so this test cannot detect the bug it was written for');
}

// The prompt must instruct exactly 5.
if (/EXACTLY 5 hashtags/.test(src)) {
  PASSES.push('the prompt instructs EXACTLY 5 hashtags');
} else {
  FAILS.push('the prompt does not instruct EXACTLY 5 hashtags');
}
if (/-\s*5-7 hashtags/.test(src)) {
  FAILS.push("the prompt still says '5-7 hashtags'");
} else {
  PASSES.push("the prompt no longer says '5-7 hashtags'");
}

// The wrong "422 rejection" claim must not be asserted anywhere.
if (/rejected by\s*\n?\s*\*?\/?\s*Blotato with 422/.test(src) ||
    /is rejected by Blotato with 422/.test(src)) {
  FAILS.push('the source still claims Blotato rejects with 422 - that is ' +
             'FALSE, it truncates');
} else {
  PASSES.push('the false "Blotato rejects with 422" claim is gone');
}

console.log('='.repeat(70));
PASSES.forEach(p => console.log('  PASS  ' + p));
FAILS.forEach(f => console.log('  FAIL  ' + f));
console.log('='.repeat(70));
console.log(`${PASSES.length} passed, ${FAILS.length} failed`);
process.exit(FAILS.length ? 1 : 0);
