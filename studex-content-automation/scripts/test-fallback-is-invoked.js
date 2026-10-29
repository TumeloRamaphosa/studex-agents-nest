#!/usr/bin/env node
/**
 * test-fallback-is-invoked.js — 2026-10-29
 *
 * THE DEFECT: Facebook has been dead since 27 Jun 2026 (Graph API FB190
 * "session has expired"). daily-content-agent.js catches that failure,
 * queues the caption in posts/pending/<date>.json, and exits 1 — and
 * then NOTHING ELSE HAPPENS. The script that would publish that queued
 * caption to the platforms that still work, blotato-fallback.js, was an
 * ORPHAN: no cron job invoked it, no script invoked it, and no checklist
 * entry did either.
 *
 * The consequence: 23–27 Oct 2026 published NOWHERE. Threads and
 * Instagram were connected and healthy the entire time. The repo KNEW —
 * ops/check-staged-publish.py and the heartbeat registry both say
 * "nothing invokes the fallback" — and the escalation was never re-read.
 *
 * A known escalation nobody re-reads is a standing bug.
 *
 * WHAT THIS TEST ASSERTS: that the Facebook-failure branch of
 * daily-content-agent.js INVOKES blotato-fallback.js before it exits.
 *
 * It has a NEGATIVE CONTROL: the pre-fix source (the catch block with no
 * fallback call) must FAIL this test. A test that cannot fail proves
 * nothing — and a test that passes against the broken source is worse
 * than no test at all.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', '..');
const AGENT = path.join(ROOT, 'studex-content-automation', 'scripts', 'daily-content-agent.js');

let passes = 0;
const fails = [];

function check(name, cond, detail) {
  if (cond) {
    console.log('PASS  ' + name);
    passes++;
  } else {
    console.log('FAIL  ' + name + (detail ? '  ' + detail : ''));
    fails.push(name);
  }
}

console.log('=== the fallback must be INVOKED, not merely mentioned ===');

const src = fs.readFileSync(AGENT, 'utf8');

// --- locate the Facebook-failure catch block -----------------------------
const catchIdx = src.indexOf('Facebook Error:');
check('the Facebook failure branch exists', catchIdx > 0,
      'no "Facebook Error:" in ' + path.basename(AGENT));

const tail = catchIdx > 0 ? src.slice(catchIdx) : '';

// Does the branch actually RUN the fallback?
// Check the CODE, not the whole tail: my own explanatory comment
// mentions the filename, and a test that reads a comment is a test of
// prose. The invocation must be in real code.
const codeOnly = tail
  .split('\n')
  .filter(l => !/^\s*(\/\/|\*|\/\*)/.test(l))
  .join('\n');
const invokesFallback =
  /blotato-fallback\.js/.test(codeOnly) &&
  /(execFileSync|spawnSync|execSync|execFile)\s*\(/.test(codeOnly);

check('the Facebook failure branch INVOKES blotato-fallback.js',
      invokesFallback,
      invokesFallback ? '' : 'the catch block mentions no fallback invocation');

// It must be an invocation, not a comment or a string in a message.
const commentOnly = /^\s*(\/\/|\*)/.test(
  (codeOnly.split('\n').find(l => /blotato-fallback\.js/.test(l)) || '').trim());
check('the reference is CODE, not a comment', !commentOnly,
      commentOnly ? 'the only mention is in a comment' : '');

// The fallback must receive the DATE, or it will publish the wrong
// caption - a fallback that publishes yesterday's post is worse than no
// fallback. The argument can sit on the next line, so look at the
// invocation as a block, not as one line.
const callIdx = codeOnly.indexOf('blotato-fallback.js');
const callBlock = callIdx >= 0 ? codeOnly.slice(callIdx, callIdx + 320) : '';
const passesDate = /\bdate[A-Za-z]*\b/.test(callBlock) ||
                   /\d{4}-\d{2}-\d{2}/.test(callBlock);
check('the fallback is given the DATE (not the wrong caption)',
      passesDate, 'no date argument next to the fallback path');

// It must run BEFORE the process exits.
const exitIdx = tail.indexOf('process.exit');
const fallbackIdx = tail.indexOf('blotato-fallback.js');
check('the fallback runs BEFORE the process exits',
      fallbackIdx > 0 && (exitIdx < 0 || fallbackIdx < exitIdx),
      exitIdx < 0 ? 'no process.exit found' : 'the exit comes first');

// A failure in the fallback must NOT lose the caption: the caption is
// already queued, so the branch must still exit non-zero, and it must
// say so.
check('a failing fallback does not claim success',
      /Fallback did not complete/.test(tail) && /NOT lost/.test(tail),
      'the branch does not report a failed fallback honestly');

console.log('');
console.log('=== NEGATIVE CONTROL: the PRE-FIX source must FAIL this test ===');
// The pre-fix catch block: queues the caption and exits, with no
// fallback call. The golden reference is written out inline, because a
// control taken from git history can silently stop being a control when
// the history is rewritten.
const PRE_FIX = `
      } catch (err) {
        console.error(\`\\n❌ Facebook Error: \${err.message}\`);
        logPost({
          timestamp: started.toISOString(),
          product: product.id, productName: product.name,
          category: product.category, price: product.price,
          status: 'FAILED', error: err.message,
          captionPreview: caption.slice(0, 150),
          caption,
      });
      try {
        const pendingDir = path.join(__dirname, '..', 'posts', 'pending');
        fs.mkdirSync(pendingDir, { recursive: true });
        const file = path.join(pendingDir, \`\${started.toISOString().slice(0, 10)}.json\`);
        const existing = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
        fs.writeFileSync(file, JSON.stringify({
          ...existing,
          timestamp: started.toISOString(),
          product: product.id, productName: product.name,
          category: product.category, price: product.price,
          status: 'APPROVED_PENDING_FB_TOKEN',
          blocker: err.message,
          caption,
        }, null, 2));
      } catch (qErr) {
        console.error(\`   ⚠️  Could not queue caption: \${qErr.message}\`);
      }
      process.exit(1);
`;

const preTail = PRE_FIX;
const preCode = preTail
  .split('\n')
  .filter(l => !/^\s*(\/\/|\*|\/\*)/.test(l))
  .join('\n');
const preInvokes =
  /blotato-fallback\.js/.test(preCode) &&
  /(execFileSync|spawnSync|execSync|execFile)\s*\(/.test(preCode);
check('NEGATIVE CONTROL: the pre-fix source does NOT invoke the fallback',
      !preInvokes,
      preInvokes ? 'the control unexpectedly invokes it - the control is broken' : '');

// The control must be judged by the SAME assertion as the real source,
// otherwise it proves nothing. An earlier version of this test compared
// the FIXED source's result against the control's, which asserted that
// two things agreed - and would have passed whatever the fix was.
check('NEGATIVE CONTROL: the pre-fix source FAILS the main assertion',
      !preInvokes,
      preInvokes ? 'the pre-fix source passes - the test does not detect the defect' : '');

console.log('');
if (fails.length) {
  console.log('FAILURES: ' + fails.length + ' -> ' + JSON.stringify(fails));
  process.exit(1);
}
console.log('ALL CHECKS PASS (' + passes + ')');
