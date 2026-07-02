const PDFDocument = require('pdfkit');
const fs = require('fs');
try {
  const doc = new PDFDocument({autoFirstPage:false});
  doc.addPage();
  doc.fillColor('#1A1A1A').rect(0, 0, 200, 200).fill();
  const buf = doc.read();
  fs.writeFileSync('/tmp/test.pdf', buf);
  console.log('ok, buf size:', buf.length);
  doc.end();
} catch(e) {
  console.error('Error:', e.message);
  process.exit(1);
}
