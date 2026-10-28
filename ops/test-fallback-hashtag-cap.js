const fs = require('fs');
const src = fs.readFileSync('/workspace/studex-content-automation/scripts/blotato-fallback.js', 'utf8');

// Extract the capHashtags function by brace matching.
const start = src.indexOf('function capHashtags');
if (start === -1) { console.error('capHashtags NOT FOUND'); process.exit(1); }
let depth = 0, i = src.indexOf('{', start);
const open = i;
for (; i < src.length; i++) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') { depth--; if (depth === 0) { i++; break; } }
}
const fnSrc = src.slice(start, i);
eval(fnSrc);

const cap = 'Text here\n\n#StudexGM #SuperAgents #AgenticAI #AfricanTech #BusinessGhostMemory #AIInfrastructure';
const out = capHashtags(cap, 'instagram');
const tags = out.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
console.log('IG tags:', tags.length, JSON.stringify(tags));

const out2 = capHashtags(cap, 'threads');
console.log('threads untouched (6):', (out2.match(/#[A-Za-z][A-Za-z0-9]*/g) || []).length === 6);

const five = cap.replace(' #AIInfrastructure', '');
console.log('exactly-5 untouched:', (capHashtags(five, 'instagram').match(/#[A-Za-z][A-Za-z0-9]*/g) || []).length === 5);

const sixSp = cap + ' ';
console.log('6-with-trailing-space trimmed:', (capHashtags(sixSp, 'instagram').match(/#[A-Za-z][A-Za-z0-9]*/g) || []).length === 5);

// NEGATIVE CONTROL: the OLD behaviour (replace tag+' ') must FAIL the cap.
function oldCap(text) {
  const tags = text.match(/#[A-Za-z][A-Za-z0-9]*/g) || [];
  let out = text;
  if (tags.length > 5) for (const t of tags.slice(5)) out = out.replace(t + ' ', '');
  return out;
}
console.log('negative control (old impl ships 6):',
  (oldCap(cap).match(/#[A-Za-z][A-Za-z0-9]*/g) || []).length === 6);
