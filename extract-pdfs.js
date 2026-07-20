const { createRequire } = require('module');
const require2 = createRequire(__filename);
let pdfParse;
try {
  pdfParse = require2('pdf-parse');
} catch(e) {
  console.log('PDF parse not found');
  process.exit(1);
}
const fs = require('fs');

async function extract(filepath, label) {
  try {
    const buf = fs.readFileSync(filepath);
    const mod = pdfParse;
    const fn = mod.default || mod;
    const r = await fn(buf);
    console.log(`\n========== ${label} ==========\n`);
    console.log(r.text.substring(0, 8000));
  } catch(e) {
    console.log(`Error extracting ${label}:`, e.message);
  }
}

(async () => {
  await extract('user_input_files/Wagyu Biltong Gold.pdf', 'WAGYU BILTONG GOLD');
  await extract('user_input_files/Founders Soul.MD.pdf', 'FOUNDERS SOUL');
})();
