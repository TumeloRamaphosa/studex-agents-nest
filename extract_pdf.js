const { PDFParse } = require('/workspace/node_modules/pdf-parse');
const fs = require('fs');
const parser = new PDFParse();
parser.parse(fs.readFileSync('/workspace/user_input_files/Wagyu Biltong Gold.pdf')).then(d => {
  fs.writeFileSync('/workspace/wagyu_text.txt', d.text);
  console.log('PAGES:', d.numpages);
  console.log('TEXT_LENGTH:', d.text.length);
  console.log(d.text.slice(0, 3000));
}).catch(e => console.log('ERR:', e.message));