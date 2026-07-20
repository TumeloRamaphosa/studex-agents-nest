const PDFDocument = require('pdfkit');

const doc = new PDFDocument({ margin: 50, size: 'A4', layout: 'portrait' });
const out = '/workspace/studex-os/proposals/rwanda-offer-PROWTC-2026-07.pdf';
const stream = require('fs').createWriteStream(out);
doc.pipe(stream);

// Colors
const GOLD = '#8B6914';
const DARK = '#1a1a1a';
const MID = '#4a4a4a';
const LIGHT = '#f5f0e8';
const TABLE_HEADER = '#2c2c2c';
const TABLE_ALT = '#f9f6f1';

// Header
doc.rect(0, 0, doc.page.width, 100).fill('#1a1a1a');
doc.fillColor('#8B6914').fontSize(28).font('Helvetica-Bold')
   .text('STUDEX', 50, 30, { lineBreak: false });
doc.fillColor('#ffffff').fontSize(11).font('Helvetica')
   .text('Coffee & Commodities Division', 50, 62);
doc.fillColor('#8B6914').fontSize(9)
   .text('PROPOSAL', doc.page.width - 150, 38)
   .text('July 2026', doc.page.width - 150, 54);

// Gold accent bar
doc.rect(0, 100, doc.page.width, 4).fill('#8B6914');

// Title section
doc.fillColor(DARK).fontSize(22).font('Helvetica-Bold')
   .text('Rwanda Coffee', 50, 125)
   .text('Partnership Proposal', 50, 155);
doc.fillColor(MID).fontSize(11).font('Helvetica')
   .text('Prepared for PROWTC — Dubai, UAE', 50, 185);

// Gold line
doc.rect(50, 205, 200, 2).fill('#8B6914');

// From / To
doc.fillColor(DARK).fontSize(9).font('Helvetica-Bold').text('FROM:', 50, 225);
doc.fillColor(DARK).fontSize(9).font('Helvetica').text('Tumelo Ramaphosa', 50, 240)
   .text('Studex — Coffee & Commodities', 50, 254)
   .text('t.ramaphosa@studexwildlife.com', 50, 268)
   .text('+27 83 593 2577 (WhatsApp)', 50, 282)
   .text('studexwildlife.com', 50, 296);

doc.fillColor(DARK).fontSize(9).font('Helvetica-Bold').text('TO:', 300, 225);
doc.fillColor(DARK).fontSize(9).font('Helvetica').text('Svetlana Savinova', 300, 240)
   .text('PROWTC — Dubai, UAE', 300, 254)
   .text('svetlana.savinova@prowtc.com', 300, 268);

// Section: Rwanda Offer
doc.rect(50, 330, doc.page.width - 100, 30).fill('#2c2c2c');
doc.fillColor('#ffffff').fontSize(11).font('Helvetica-Bold')
   .text('RWANDA WET POLISHED — CURRENT OFFER', 60, 340);

let y = 375;
// Table header
const colW = [80, 90, 90, 80, 130];
const cols = [50, 130, 220, 310, 390];
doc.rect(50, y, doc.page.width - 100, 22).fill(TABLE_HEADER);
doc.fillColor('#ffffff').fontSize(8).font('Helvetica-Bold')
   .text('GRADE', cols[0]+5, y+7, { width: colW[0]-10 })
   .text('SCREEN', cols[1]+5, y+7, { width: colW[1]-10 })
   .text('PROCESS', cols[2]+5, y+7, { width: colW[2]-10 })
   .text('VOLUME', cols[3]+5, y+7, { width: colW[3]-10 })
   .text('PRICE (USD/MT)', cols[4]+5, y+7, { width: colW[4]-10 });

y += 22;
const rows = [
   ['A1 Premium', '17+', 'Wet Polished', '20 MT', 'USD 4,200–4,800 FOB Djibouti'],
   ['A2 Commercial', '15–16', 'Wet Polished', '40 MT', 'USD 3,600–4,000 FOB Djibouti'],
];
rows.forEach((row, i) => {
   const bg = i % 2 === 0 ? '#ffffff' : TABLE_ALT;
   doc.rect(50, y + i*22, doc.page.width - 100, 22).fill(bg);
   doc.fillColor(DARK).fontSize(8).font('Helvetica')
      .text(row[0], cols[0]+5, y+i*22+7, { width: colW[0]-10 })
      .text(row[1], cols[1]+5, y+i*22+7, { width: colW[1]-10 })
      .text(row[2], cols[2]+5, y+i*22+7, { width: colW[2]-10 })
      .text(row[3], cols[3]+5, y+i*22+7, { width: colW[3]-10 })
      .text(row[4], cols[4]+5, y+i*22+7, { width: colW[4]-10 });
});

// Table border
doc.rect(50, y, doc.page.width - 100, 44).stroke('#cccccc');

y += 60;
doc.fillColor('#8B6914').fontSize(8).font('Helvetica-Bold')
   .text('Cupping Score A1: 84+  |  Very low cup defects  |  Clean, bright acidity with stone fruit sweetness', 50, y);

// Full Origins
y += 35;
doc.rect(50, y, doc.page.width - 100, 22).fill('#2c2c2c');
doc.fillColor('#ffffff').fontSize(11).font('Helvetica-Bold')
   .text('FULL ORIGIN PORTFOLIO', 60, y+7);
y += 35;

const origins = [
   ['🇪🇹', 'Ethiopia', 'Yirgacheffe · Sidama · Guji'],
   ['🇰🇪', 'Kenya', 'AA · AB — Nyeri · Kirinyaga'],
   ['🇺🇬', 'Uganda', 'Bugisu AA · Drugar'],
   ['🇿🇦', 'South Africa', 'Bourbon · Castillo'],
];
const colW2 = 235;
origins.forEach((o, i) => {
   const x = i % 2 === 0 ? 50 : 300;
   const ry = y + Math.floor(i/2) * 50;
   doc.fillColor(o[0]).fontSize(20).text(o[0], x, ry);
   doc.fillColor(DARK).fontSize(10).font('Helvetica-Bold')
      .text(o[1], x + 30, ry, { width: 80 })
      .font('Helvetica').fontSize(8).fillColor(MID)
      .text(o[2], x + 30, ry + 14, { width: colW2 - 30 });
});
doc.rect(50, y - 5, doc.page.width - 100, 95).stroke('#cccccc');

// What We Arrange
y = 540;
doc.rect(50, y, doc.page.width - 100, 22).fill('#2c2c2c');
doc.fillColor('#ffffff').fontSize(11).font('Helvetica-Bold')
   .text('WHAT WE ARRANGE', 60, y+7);
y += 35;

const checks = [
   'Sample shipments (5–10kg) prior to bulk commitment',
   'Private label packaging — your brand on our green coffee',
   'Flexible incoterms: FOB Djibouti, CIF, or DAP to destination',
   'Full documentation: phytosanitary certificates, COA, fumigation records',
   'Cupping sessions via video call before shipment confirmation',
];
checks.forEach((c, i) => {
   doc.fillColor('#8B6914').fontSize(10).text('✓', 50, y + i*22);
   doc.fillColor(DARK).fontSize(9).font('Helvetica')
      .text(c, 70, y + i*22);
});

// CTA
y = 655;
doc.rect(50, y, doc.page.width - 100, 60).fill('#1a1a1a');
doc.fillColor('#ffffff').fontSize(9).font('Helvetica')
   .text('Ready to schedule a call this week to review samples and agree delivery terms?', 60, y+12)
   .text('Tumelo Ramaphosa  ·  +27 83 593 2577 (WhatsApp)  ·  t.ramaphosa@studexwildlife.com', 60, y+30)
   .fillColor('#8B6914')
   .text('studexwildlife.com', 60, y+46);

// Footer
doc.rect(0, doc.page.height - 30, doc.page.width, 30).fill('#f0ede6');
doc.fillColor(MID).fontSize(7)
   .text('Studex — Coffee & Commodities Division  ·  July 2026  ·  Confidential', 50, doc.page.height - 18);

doc.end();
stream.on('finish', () => console.log('PDF written:', out));
