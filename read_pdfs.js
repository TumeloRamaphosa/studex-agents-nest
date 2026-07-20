const { PDFParse } = require('/workspace/node_modules/pdf-parse/dist/pdf-parse/cjs/index.cjs');
const fs = require('fs');

const buf1 = fs.readFileSync('/workspace/user_input_files/Founders Soul.MD.pdf');
const parser = new PDFParse(buf1, 0, 2);
const result = parser.getText();
console.log('result type:', typeof result, Array.isArray(result) ? '(array)' : '');
if (Array.isArray(result)) {
  // pages array - join page texts
  const pageTexts = result.map(p => typeof p === 'object' ? JSON.stringify(Object.keys(p)) : String(p));
  console.log('page count:', result.length);
  // Try to get text from each page object
  result.forEach((p, i) => {
    console.log(`Page ${i}: type=${typeof p}, keys=${typeof p === 'object' ? Object.keys(p).join(',') : 'N/A'}`);
  });
  // Try joining as strings
  console.log('\nAs strings:');
  console.log(result.map(p => String(p)).join('\n').substring(0, 8000));
} else {
  console.log(String(result).substring(0, 8000));
}
