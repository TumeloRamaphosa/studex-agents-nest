const PdfKit = require('pdfkit');
const fs = require('fs');

// Helper — fill a rect with a solid colour
function fillRect(doc, x, y, w, h, color) {
  doc.fillColor(color).rect(x, y, w, h).fill();
}
// Helper — stroke a line
function hLine(doc, x1, y, x2, color, lw) {
  doc.strokeColor(color).lineWidth(lw||1)
    .moveTo(x1, y).lineTo(x2, y).stroke();
}

function C(arr) { return '#' + arr.map(v => v.toString(16).padStart(2,'0')).join(''); }
const G = { maroon:[107,0,0], gold:[201,151,58], charcoal:[26,26,26], white:[255,255,255], text:[40,40,40], muted:[120,120,120], light:[248,248,248], cream:[253,246,236] };
const W = 595.28, H = 841.89, M = 56;

const doc = new PdfKit({ size:'A4', margin:M, info:{Title:'Studex Meat — Premium Halal Proposal',Author:'Studex Group'}});
const out = fs.createWriteStream('/workspace/studex-pdf/Studex-Meat-Proposal.pdf');
doc.pipe(out);

// ===== PAGE 1: COVER =====
fillRect(doc, 0, 0, W, H, C(G.charcoal));
fillRect(doc, W*0.52, 0, W*0.48, 8, C(G.gold));

// Logo centred
doc.image('/workspace/studex-pdf/studex-logo-gold.png', W/2 - 80, H*0.22, { width:160 });

doc.font('Helvetica-Bold').fontSize(10).fillColor(C(G.gold)).text('STUDEX GROUP', 0, H*0.22 + 170, { width:W, align:'center', characterSpacing:4 });
doc.fillColor(C(G.white)).font('Helvetica-Bold').fontSize(42).text('Wagyu Biltong', { align:'center' });
doc.fillColor(C(G.gold)).text('Gold', { align:'center' });
doc.fillColor([200,200,200]).font('Helvetica').fontSize(14).text('Premium Halal South African Biltong', { align:'center' });
doc.fillColor([150,150,150]).fontSize(11).text('A5 Wagyu  •  Dry-Aged 21 Days  •  South Africa', { align:'center' });

hLine(doc, M, H*0.7, W-M, C(G.gold), 1);

doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(11).text('☪  100% Halal Certified  |  10 Years Running  |  Nationwide Delivery', { align:'center' });

fillRect(doc, 0, H-56, W, 56, [18,0,0]);
doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(11).text('studexmeat.com', M, H-44);
doc.fillColor([100,100,100]).font('Helvetica').fontSize(9).text('© 2026 Studex Meat (Pty) Ltd  |  All Rights Reserved', M, H-26);

// ===== PAGE 2: THE STUDEX GROUP =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text('The Studex Group', {continued:false});
doc.moveDown(0.3); hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
doc.fillColor(C(G.text)).font('Helvetica').fontSize(10.5).text('Studex is a South African luxury food and commodities group — built to compete globally. We own the supply chain from farm to customer, powered by AI agents running 24/7 on virtual machines.', 180);
doc.moveDown(0.5);
doc.text('Our core belief: the future of business is agentic. Autonomous agents running around the clock, coordinated by a CEO agent that reports to a human founder. Tumelo Ramaphosa sets the vision, builds relationships, and closes the deals. The agents handle everything else.', 180);
doc.moveDown(1);
fillRect(doc, M, doc.y, 4, 44, C(G.gold));
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(11).text('"Every CEO needs a founder who believes."', M+14, doc.y+2);
doc.fillColor(C(G.gold)).text('— Tumelo Ramaphosa, Founder', M+14); doc.moveDown(2);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(14).text('Our Businesses', {continued:false}); doc.moveDown(0.7);

const bCols=[162,80,235];
const bizData=[
  ['Business','Status','Description'],
  ['Studex Meat','Active','Luxury halal meat delivered nationwide'],
  ['Studex Wildlife','Active','Premium coffee export/import across Africa'],
  ['Studex Caviar','Building','Russian caviar import — luxury SA market'],
  ['Dark Factory','Building','Open-core development environment'],
];
bizData.forEach(function(row,ri){
  const bg=ri===0?C(G.gold):(ri%2===1?C(G.light):C(G.white));
  const fc=ri===0?C(G.charcoal):(ri>0&&row[1]==='Active'?'#2a7a2a':C(G.muted));
  const ff=ri===0||(ri>0&&row[1]==='Active')?'Helvetica-Bold':'Helvetica';
  [0,1,2].forEach(function(ci){
    const xp=[M, M+bCols[0], M+bCols[0]+bCols[1]][ci];
    const cw=[bCols[0],bCols[1],bCols[2]][ci];
    const yp=ri===0?doc.y:doc.y+ri*22;
    const hh=ri===0?18:22;
    fillRect(doc, xp, yp, cw, hh, bg);
    doc.fillColor(fc).font(ff).fontSize(9.5).text(row[ci], xp+4, yp+5, {width:cw-8, continued:ci<2});
  });
});
doc.y += 18 + 4*22; doc.moveDown(1.5);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(14).text('What Sets Us Apart', {continued:false}); doc.moveDown(0.7);
[['☪ 100% Halal Certified','Every product and every supplier — certified and verified. No compromises.'],['🏔️ Full Provenance','Every cut shows the farm, breed, and slaughter date.'],['🤝 Direct Farm Access','No middlemen. We know every farmer by name.'],['🤖 AI Operations','Autonomous agents running 24/7.']].forEach(function(v,i){
  const cx=i<2?M:W/2+4; const cw=(W-M*2)/2-8;
  doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(10).text(v[0],cx,doc.y,{width:cw});
  doc.fillColor(C(G.muted)).font('Helvetica').fontSize(9.5).text(v[1],cx,doc.y+14,{width:cw});
});

// ===== PAGE 3: OUR STORY =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text("Our Story — 10 Years Building SA's Premium Meat Brand",{continued:false});
doc.moveDown(0.3); hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
doc.fillColor(C(G.text)).font('Helvetica').fontSize(10.5).text("Ten years ago, Tumelo Ramaphosa set out to build South Africa's most trusted premium meat brand — one built on integrity, halal integrity, and the belief that Black-owned South African businesses could compete at the highest level.",180);
doc.moveDown(0.5);
doc.text("From those first Wagyu biltong batches to today's nationwide operation, Studex has stayed true to one principle: your clients deserve to know exactly where their meat comes from — every single time.",180);
doc.moveDown(0.5);
doc.text("Today, Studex Meat serves clients across South Africa — from families wanting the finest biltong for their Sunday braai, to corporate clients seeking premium gift boxes.",180);
doc.moveDown(0.8);
fillRect(doc, M, doc.y, 4, 48, C(G.gold));
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(10.5).text('"Our 100% halal commitment is non-negotiable. Every supplier, every product, every time — verified and certified."',M+14,doc.y+2,{width:W-M*2-14});
doc.fillColor(C(G.gold)).text('— Tumelo Ramaphosa, Founder',M+14); doc.moveDown(2);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(14).text('Our Journey',{continued:false}); doc.moveDown(0.8);
[['2016','Studex founded — first premium meat batches produced'],['2019','Halal certification achieved — first Black-owned halal premium brand in SA'],['2022','Supply network expanded to verified partners — nationwide delivery launched'],['2024','AI launched — Charlie, Naledi & Delivery Agent running 24/7'],['2026',"Studex positioned as SA's leading farm-to-door premium commodities group"]].forEach(function(m,i){
  const bg=i===4?C(G.gold):C(G.charcoal);
  const tc=i===4?C(G.charcoal):C(G.white);
  fillRect(doc, M, doc.y, 56, 20, bg);
  doc.fillColor(tc).font('Helvetica-Bold').fontSize(9.5).text(m[0],M+4,doc.y+5,{width:48});
  fillRect(doc, M+60, doc.y, W-M*2-60, 20, i%2===1?C(G.light):C(G.white));
  doc.fillColor(C(G.text)).font('Helvetica').fontSize(9.5).text(m[1],M+64,doc.y+5,{width:W-M*2-68});
  doc.y+=20;
});

// ===== PAGE 4: BILTONG HERO =====
doc.addPage();
doc.image('/workspace/studex-pdf/biltong-hero.jpg', 0, 0, { width:W, height:260, align:'center', valign:'middle' });
// Dark overlay
fillRect(doc, 0, 0, W, 260, [0,0,0,0.6]);
// Gold top bar
fillRect(doc, 0, 0, W, 6, C(G.gold));
doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(8).text('A5 WAGYU  •  DRY-AGED 21 DAYS  •  HALAL CERTIFIED  •  SOUTH AFRICAN CRAFT', M, 14, {width:W-M*2});
doc.fillColor(C(G.white)).font('Helvetica-Bold').fontSize(36).text('Wagyu Biltong Gold', M, 30, {width:W-M*2});
fillRect(doc, 0, 214, W, 46, [0,0,0,0.75]);
doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(11).text('☪ 100% Halal Certified', M, 222);
doc.fillColor([220,220,220]).font('Helvetica').fontSize(10).text('South Africa  |  A5 Wagyu  |  Dry-Aged 21 Days', M+200, 222);
doc.moveDown(34);
doc.fillColor(C(G.text)).font('Helvetica').fontSize(10.5).text('Premium A5 Wagyu beef. Dry-aged for 21 days under controlled conditions — then slow-cured in the traditional South African biltong style. Japanese genetics. South African craft. No equal in the world.',220);
doc.moveDown(1.5);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(14).text('Product Specifications',{continued:false}); doc.moveDown(0.7);
[['Breed','A5 Wagyu — Japanese genetics, dry-aged 21 days'],['Origin','South Africa'],['Cure Method','Traditional South African biltong — slow, dry, natural'],['Certification','☪ 100% Halal Certified — every batch verified'],['Provenance','Full farm-to-door traceability on every package'],['Packaging','Vacuum-sealed, chilled delivery']].forEach(function(s,i){
  const bg=i%2===1?C(G.light):C(G.white);
  const hw=(W-M*2)*0.36, vw=(W-M*2)*0.64;
  fillRect(doc, M, doc.y, hw, 18, bg); fillRect(doc, M+hw, doc.y, vw, 18, bg);
  doc.fillColor(C(G.text)).font('Helvetica-Bold').fontSize(9.5).text(s[0],M+4,doc.y+5,{width:hw-8});
  doc.font('Helvetica').fontSize(9.5).text(s[1],M+hw+4,doc.y+5,{width:vw-8});
  doc.y+=18;
});
doc.moveDown(1.5);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(14).text('What Sets It Apart',{continued:false}); doc.moveDown(0.7);
['A5 Wagyu beef — dry-aged 21 days under controlled conditions','Traditional South African biltong cure — slow, dry, natural','☪ Halal certified — every batch verified','Full farm provenance on every package','Delivered fresh to your door nationwide'].forEach(function(t){
  doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(10).text('▪',M,doc.y+2);
  doc.fillColor(C(G.text)).font('Helvetica').fontSize(10).text(t,M+16,doc.y,{width:W-M*2-16});
  doc.moveDown(0.65);
});

// ===== PAGE 5: HALAL CERTIFICATE =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text('Halal Certification',{continued:false}); doc.moveDown(0.3);
hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
doc.fillColor(C(G.text)).font('Helvetica').fontSize(10.5).text('All Studex Meat products are certified halal by the South African Islamic Council (MUSLIMAAT). Every batch, every supplier, every time — verified and documented.',180); doc.moveDown(1);
const certImgW = W - M*2;
const certImgH = certImgW * 0.707;
doc.image('/workspace/studex-pdf/halal-cert.png', M, doc.y, { width:certImgW, height:certImgH });

// ===== PAGE 6: PRODUCT RANGE =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text('Full Product Range',{continued:false});
doc.moveDown(0.3); hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
const pCols=[220,360]; let prY=doc.y;
['Product','Description'].forEach(function(h,ci){
  const px=ci===0?M:M+pCols[0];
  fillRect(doc, px, prY, pCols[ci], 18, C(G.gold));
  doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(9.5).text(h,px+4,prY+5,{width:pCols[ci]-8,continued:ci<1});
});
prY+=18;
[['Wagyu Biltong Gold 500g','A5 Wagyu — dry-aged 21 days, traditional cure, halal certified'],['Wagyu Biltong Gold 1kg','A5 Wagyu — whole piece, premium gifting format, halal certified'],['Premium Beef Short Ribs','Dry-aged heritage breed, full bloodline verified'],['Fresh Farm Lamb Chops','Spring lamb, pasture-raised'],['Beef Sausage Bulk Pack','Traditional boerewors, bulk format'],['Ankole Heritage Beef — Coming Soon','East African heritage breed, limited availability']].forEach(function(row,ri){
  const bg=ri%2===1?C(G.light):C(G.white);
  fillRect(doc, M, prY, W-M*2, 20, bg);
  doc.fillColor(ri===5?C(G.maroon):C(G.charcoal)).font(ri===5?'Helvetica-Bold':'Helvetica').fontSize(10).text(row[0],M+4,prY+5,{width:pCols[0]-8});
  doc.fillColor(C(G.muted)).font('Helvetica').fontSize(9.5).text(row[1],M+pCols[0]+4,prY+5,{width:pCols[1]-8});
  prY+=20;
});

// ===== PAGE 7: THE NUMBERS =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text('The Numbers Behind Studex',{continued:false});
doc.moveDown(0.3); hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
[['10+','Years in business'],['100%','Halal certified supply chain'],['3+','Verified partner farms'],['24/7','AI agents running autonomously'],['Nationwide','Delivery across South Africa'],['6','Premium product lines']].forEach(function(pair){
  const bg=Math.floor(doc.y)%104<52?C(G.light):C(G.white);
  fillRect(doc, M, doc.y, 100, 52, bg); fillRect(doc, M+100, doc.y, W-M*2-100, 52, bg);
  doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(26).text(pair[0],M+10,doc.y+10,{width:80});
  doc.fillColor(C(G.text)).font('Helvetica').fontSize(11).text(pair[1],M+110,doc.y+18,{width:W-M*2-120});
  doc.y+=52;
});
doc.moveDown(1.5);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(14).text('Certifications & Standards',{continued:false}); doc.moveDown(0.7);
['☪ All products halal certified by recognised Islamic authority','Full chain of custody — every cut traceable to source','Temperature-controlled cold chain from storage to door','ISO-aligned food safety standards across all partner facilities'].forEach(function(cert){
  doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(10).text('▪',M,doc.y+2);
  doc.fillColor(C(G.text)).font('Helvetica').fontSize(10).text(cert,M+16,doc.y,{width:W-M*2-16});
  doc.moveDown(0.65);
});

// ===== PAGE 8: WHY CHOOSE STUDEX =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text('Why Clients Choose Studex',{continued:false});
doc.moveDown(0.3); hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
[{t:'10 Years of Craft',d:"A decade building relationships with SA's finest farms.",c:G.maroon},{t:'100% Halal Certified',d:'Every supplier and product is fully halal certified.',c:G.gold},{t:'Premium Heritage Breeds',d:'Wagyu, Ankole, Spring Lamb — not found in any supermarket.',c:G.charcoal},{t:'Farm-to-Door Transparency',d:'Full provenance on every product.',c:G.maroon},{t:'Same-Day Gauteng',d:'Order before noon. Receive your meat the same day.',c:G.gold},{t:'AI-Tracked Orders',d:'Real-time WhatsApp updates from order to doorstep.',c:G.charcoal}].forEach(function(r){
  fillRect(doc, M, doc.y, 4, 44, C(r.c));
  doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(11).text(r.t,M+16,doc.y+4,{width:W-M*2-16});
  doc.fillColor(C(G.muted)).font('Helvetica').fontSize(9.5).text(r.d,M+16,doc.y+18,{width:W-M*2-16});
  doc.y+=52;
});

// ===== PAGE 9: DELIVERY =====
doc.addPage();
hLine(doc, M, doc.y, W-M, C(G.gold), 1.5); doc.moveDown(0.4);
doc.fillColor(C(G.charcoal)).font('Helvetica-Bold').fontSize(20).text('Delivery & Logistics',{continued:false});
doc.moveDown(0.3); hLine(doc, M, doc.y, W-M, C(G.gold), 1); doc.moveDown(1);
doc.fillColor(C(G.text)).font('Helvetica').fontSize(10.5).text('We work with vetted specialist food delivery providers to ensure your meat arrives fresh and on time, every time.',180); doc.moveDown(1.5);
['Nationwide delivery coverage across South Africa','Temperature-controlled cold chain from storage to doorstep','Real-time order tracking via WhatsApp','Same-day delivery available in Gauteng','Vetted, halal-aware logistics partners'].forEach(function(item,i){
  const bg=i%2===0?C(G.light):C(G.white);
  fillRect(doc, M, doc.y, W-M*2, 28, bg);
  doc.fillColor(C(G.gold)).font('Helvetica-Bold').fontSize(10).text('▪',M+8,doc.y+8);
  doc.fillColor(C(G.text)).font('Helvetica').fontSize(10).text(item,M+24,doc.y+8,{width:W-M*2-32});
  doc.y+=28;
});

// ===== PAGE 10: CONTACT =====
doc.addPage();
fillRect(doc, 0, 0, W, H, C(G.charcoal));
fillRect(doc, 0, H-40, W, 40, [14,0,0]);
doc.image('/workspace/studex-pdf/studex-logo-gold.png', W/2-70, H*0.22, { width:140 });
doc.fillColor(C(G.white)).font('Helvetica-Bold').fontSize(36).text('Ready to Taste', M, H*0.22+155);
doc.fillColor(C(G.gold)).text('the Difference?', M);
hLine(doc, M, doc.y+4, W-M, C(G.gold), 1);
doc.fillColor(C(G.gold)).font('Helvetica').fontSize(10).text('☪  100% Halal Certified  |  10 Years of Craft  |  Nationwide Delivery',M,doc.y+10);
doc.moveDown(2);
doc.font('Helvetica-Bold').fontSize(22).text('www.studexmeat.com', M);
doc.moveDown(2);
['☪ 100% Halal Certified — every product, every batch','10+ Years of premium meat expertise','Nationwide delivery — every major centre in South Africa','AI-powered order tracking and support'].forEach(function(c){
  doc.fillColor([200,200,200]).font('Helvetica').fontSize(11).text('•  '+c,M);
  doc.moveDown(0.65);
});
doc.fillColor([80,80,80]).fontSize(8).text('© 2026 Studex Meat (Pty) Ltd. All rights reserved.',0,H-24,{width:W,align:'center'});

doc.end();
out.on('finish',function(){
  const s=fs.statSync('/workspace/studex-pdf/Studex-Meat-Proposal.pdf');
  console.log('PDF written: /workspace/studex-pdf/Studex-Meat-Proposal.pdf ('+Math.round(s.size/1024)+' KB)');
});
