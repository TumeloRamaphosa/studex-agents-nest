import { readFileSync } from 'fs';
import { createRequire } from 'module';
const require2 = createRequire(import.meta.url);

// Try pdfjs-dist ESM
let pdfjs;
try {
  pdfjs = require2('pdfjs-dist/legacy/build/pdf.mjs');
  console.log('pdfjs-dist loaded:', typeof pdfjs);
} catch(e) {
  console.log('pdfjs-dist err:', e.message);
  process.exit(1);
}

async function extractText() {
  const doc = await pdfjs.getDocument('user_input_files/Founders Soul.MD.pdf').promise;
  console.log('pages:', doc.numPages);
  let fullText = '';
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const content = await page.getTextContent();
    const text = content.items.map(item => item.str).join(' ');
    fullText += `\n--- PAGE ${i} ---\n${text}`;
  }
  console.log(fullText.substring(0, 8000));
}

extractText().catch(e => console.log('err:', e.message));
