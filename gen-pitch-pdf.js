#!/usr/bin/env node
// Generate Studex Meat Pitch Deck PDF using jsPDF
const { jsPDF } = require('jspdf');
const fs = require('fs');

// ── Colour palette ─────────────────────────────────────────────────────────────
const C = {
  black:   [10,  5,   5  ],
  dark:    [20,  16,  14 ],
  red:     [139, 26,  26 ],
  gold:    [212, 160, 23 ],
  cream:   [245, 240, 232],
  creamD:  [200, 192, 176],
  white:   [255, 255, 255],
  steel:   [30,  58,  95 ],
};

// ── Content ───────────────────────────────────────────────────────────────────
const PAGES = [
  {
    type: 'cover',
    title: 'STUDEX MEAT',
    subtitle: 'Premium Halal Meat',
    tagline: 'Farm to Table — South Africa',
    date: 'June 2026',
  },
  {
    type: 'section',
    label: 'About Us',
    heading: 'FROM THE FARM\nTO YOUR DOOR',
    body: [
      'Studex Meat is South Africa\'s premium online butchery — sourcing heritage and luxury breeds directly from verified farms and delivering to homes and businesses across the country.',
      'Full provenance transparency. Every cut shows the farm, the animal age, and the slaughter date. Customers know exactly what they\'re buying.',
    ],
    callout: 'All products are 100% Halal certified. Direct farm relationships. No middlemen markup.',
    stats: [['100%', 'Halal Certified'], ['3', 'Supplier Farms'], ['2', 'Delivery Partners']],
  },
  {
    type: 'section',
    label: 'Our Products',
    heading: 'PREMIUM BREEDS',
    body: [
      'Wagyu Biltong Gold — Grade A5 Wagyu, dry-aged and slow-cured in the traditional South African biltong style.',
      'Heritage Japanese breed meets South African craft.',
    ],
    table: {
      headers: ['Product', 'Origin', 'Price'],
      rows: [
        ['Wagyu Biltong Gold 500g', 'Moutloe Farm', 'R549'],
        ['Wagyu Biltong Gold 1kg', 'Moutloe Farm', 'R999'],
        ['Premium Beef Short Ribs', 'Moutloe Farm', 'R499'],
        ['Fresh Farm Lamb Chops', 'Moutloe Farm', 'R549'],
        ['Beef Sausage Bulk Pack', 'Moutloe Farm', 'R399'],
      ],
    },
    note: 'Ankole Cattle — Coming Soon: drought-resistant, native to Southern Africa, intensely flavoured lean beef.',
  },
  {
    type: 'section',
    label: 'Farm Network',
    heading: 'VERIFIED SOURCES',
    body: [
      'Direct relationships with farms and suppliers — no middlemen, full transparency, consistent quality.',
    ],
    table: {
      headers: ['Farm / Supplier', 'Location', 'Speciality'],
      rows: [
        ['Moutloe Farm', 'South Africa', 'Wagyu, Lamb, Premium Beef'],
        ['Silent Valley', '190 Rooiberg St, N4 Gateway, Pretoria', 'Fresh cuts, supplier'],
        ['Noags Butchery', '19 Pomona Rd, Kempton Park, 1623', 'Bulk orders'],
      ],
    },
  },
  {
    type: 'section',
    label: 'Delivery Network',
    heading: 'BUILT TO DELIVER',
    body: [
      'Vetted specialist food delivery providers ensuring every order arrives fresh, on time, in perfect condition.',
    ],
    partners: [
      { name: 'Dinkoko Pty Ltd', contact: 'Derrick Selepe  ·  +27 67 681 3076', coverage: 'Nationwide' },
      { name: 'My Courier',        contact: 'Willy  ·  +27 61 362 3448',         coverage: 'Gauteng Metro' },
    ],
    callout: 'All deliveries include real-time WhatsApp tracking updates. Orders assigned to optimal partner by routing zone.',
  },
  {
    type: 'section',
    label: 'Why Studex',
    heading: 'THE DIFFERENCE',
    bullets: [
      '100% Halal certified — every product, every supplier',
      'Farm provenance on every product page',
      'Same-day delivery available in Gauteng',
      'Dry-aged & premium cuts unavailable in retail stores',
      'Direct farm relationships — no middlemen markup',
      'Online ordering with real-time delivery scheduling',
      'AI-powered order management (Charlie orchestrator)',
      'Post-delivery automated review requests',
    ],
  },
  {
    type: 'section',
    label: 'How It Works',
    heading: 'THE PIPELINE',
    steps: [
      ['01', 'Order', 'Customer places order at studexmeat.com'],
      ['02', 'Route', 'Charlie AI assigns delivery & fulfilment'],
      ['03', 'Source', 'Product from Moutloe Farm or supplier network'],
      ['04', 'Pack & Dispatch', 'Via Dinkoko or My Courier'],
      ['05', 'Track', 'WhatsApp updates at every stage'],
      ['06', 'Review', 'Automated review request 24h post-delivery'],
    ],
  },
  {
    type: 'section',
    label: 'Opportunity',
    heading: 'MARKET REALITY',
    body: [
      'South Africa\'s premium meat e-commerce market is growing rapidly. Studex is positioned to be the leading online specialist for heritage and luxury breeds in Southern Africa.',
    ],
    bullets: [
      'Rising middle class demand for premium food',
      'Farm-to-table transparency trends',
      'Shift to online grocery accelerated by convenience',
      'African luxury meat market growing to 2034',
      'Agent infrastructure running 24/7',
    ],
  },
  {
    type: 'contact',
    heading: 'LET\'S TALK',
    body: [
      'studexmeat.com',
      'orders@studexmeat.com',
      'Tumelo Ramaphosa — Director, Studex Meat (Pty) Ltd',
    ],
    partners: [
      'Dinkoko Pty Ltd — Derrick Selepe — +27 67 681 3076',
      'My Courier — Willy — +27 61 362 3448',
      'Silent Valley — +27 71 346 5083',
    ],
  },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function rgb(c) { return `rgb(${c.join(',')})`; }
function hexRgb(h) {
  const r = parseInt(h.slice(1,3),16);
  const g = parseInt(h.slice(3,5),16);
  const b = parseInt(h.slice(5,7),16);
  return [r,g,b];
}

function setFill(doc, c) { doc.setFillColor(...c); }
function setDraw(doc, c) { doc.setDrawColor(...c); }
function setText(doc, c) { doc.setTextColor(...c); }

function addHeader(doc, label) {
  const W = doc.internal.pageSize.getWidth();
  setFill(doc, C.dark);
  doc.rect(0, 0, W, 14, 'F');
  setText(doc, C.gold);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(7);
  doc.text(label.toUpperCase(), 18, 9);
  setText(doc, C.creamD);
  doc.setFont('helvetica', 'normal');
  doc.text('STUDEX MEAT', W - 18, 9, { align: 'right' });
}

function addFooter(doc, page) {
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();
  setFill(doc, C.dark);
  doc.rect(0, H - 12, W, 12, 'F');
  setText(doc, C.creamD);
  doc.setFontSize(7);
  doc.text('© 2026 Studex Meat (Pty) Ltd. All rights reserved.', 18, H - 4);
  doc.text(`Page ${page}`, W - 18, H - 4, { align: 'right' });
  setDraw(doc, C.red);
  doc.setLineWidth(0.3);
  doc.line(18, H - 12, W - 18, H - 12);
}

// ── Cover page ────────────────────────────────────────────────────────────────
function drawCover(doc, page) {
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();

  // Background
  setFill(doc, C.black);
  doc.rect(0, 0, W, H, 'F');

  // Radial glow
  setFill(doc, [40, 10, 10]);
  doc.circle(W * 0.5, H * 0.45, W * 0.6, 'F');

  // Left panel
  setFill(doc, C.red);
  doc.rect(0, 0, W * 0.42, H, 'F');

  // Label
  setText(doc, C.gold);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.text('INVESTOR PITCH DECK', 22, 50);
  doc.text('JUNE 2026', 22, 62);

  // Red divider
  setFill(doc, C.gold);
  doc.rect(22, 72, 40, 1, 'F');

  // Title on panel
  setText(doc, C.cream);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(52);
  doc.text('STUDEX', 22, 110);
  doc.setTextColor(...C.gold);
  doc.text('MEAT', 22, 158);

  // Right side title
  setText(doc, C.cream);
  doc.setFontSize(28);
  doc.setFont('helvetica', 'normal');
  doc.text('Premium Halal Meat', W * 0.5, H * 0.42, { align: 'center' });
  doc.setFontSize(14);
  setText(doc, C.creamD);
  doc.text('Farm to Table — South Africa', W * 0.5, H * 0.42 + 14, { align: 'center' });

  // Gold divider
  setFill(doc, C.gold);
  doc.rect(W * 0.5 - 30, H * 0.42 + 22, 60, 1, 'F');

  // URL
  setText(doc, C.creamD);
  doc.setFontSize(10);
  doc.text('studexmeat.com', W * 0.5, H * 0.42 + 36, { align: 'center' });

  // Bottom accent strip
  setFill(doc, C.red);
  doc.rect(0, H - 24, W, 24, 'F');
  setText(doc, C.cream);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.text('© 2026 Studex Meat (Pty) Ltd. All rights reserved.', W * 0.5, H - 8, { align: 'center' });

  return 1; // page count
}

// ── Content page ────────────────────────────────────────────────────────────────
function drawContentPage(doc, pageData, pageNum, totalPages) {
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();
  const M = 18;

  // Background
  setFill(doc, C.black);
  doc.rect(0, 0, W, H, 'F');

  addHeader(doc, pageData.label);
  addFooter(doc, `${pageNum} of ${totalPages}`);

  const yStart = 22;
  let y = yStart;

  // Section label
  setText(doc, C.gold);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(7);
  doc.text(pageData.label.toUpperCase(), M, y + 5);
  y += 12;

  // Heading
  setText(doc, C.cream);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(34);
  const lines = pageData.heading.split('\n');
  lines.forEach((line, i) => {
    doc.text(line, M, y + i * 12);
  });
  y += lines.length * 12 + 8;

  // Red underline
  setFill(doc, C.red);
  doc.rect(M, y, 50, 2, 'F');
  y += 10;

  // Body text
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  setText(doc, C.creamD);
  if (pageData.body) {
    pageData.body.forEach(para => {
      const splitted = doc.splitTextToSize(para, W - M * 2);
      doc.text(splitted, M, y);
      y += splitted.length * 6 + 4;
    });
  }

  // Callout box
  if (pageData.callout) {
    setFill(doc, [30, 10, 10]);
    doc.rect(M, y, W - M * 2, 18, 'F');
    setFill(doc, C.gold);
    doc.rect(M, y, 2, 18, 'F');
    setText(doc, C.cream);
    doc.setFontSize(9);
    const ct = doc.splitTextToSize(pageData.callout, W - M * 2 - 10);
    doc.text(ct, M + 8, y + 7);
    y += 26;
  }

  // Stats row
  if (pageData.stats) {
    const statW = (W - M * 2) / pageData.stats.length;
    pageData.stats.forEach((stat, i) => {
      const sx = M + i * statW;
      setFill(doc, C.dark);
      doc.rect(sx + 2, y, statW - 4, 32, 'F');
      setFill(doc, C.red);
      doc.rect(sx + 2, y, statW - 4, 2, 'F');
      setText(doc, C.cream);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(20);
      doc.text(stat[0], sx + statW / 2, y + 14, { align: 'center' });
      setText(doc, C.gold);
      doc.setFontSize(7);
      doc.setFont('helvetica', 'normal');
      doc.text(stat[1], sx + statW / 2, y + 24, { align: 'center' });
    });
    y += 40;
  }

  // Table
  if (pageData.table) {
    const { headers, rows } = pageData.table;
    const colW = [(W - M * 2) * 0.45, (W - M * 2) * 0.32, (W - M * 2) * 0.23];
    const rowH = 12;
    let tx = M;

    // Header
    setFill(doc, C.red);
    doc.rect(tx, y, colW.reduce((a,b)=>a+b,0), rowH, 'F');
    setText(doc, C.gold);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(7);
    headers.forEach((h, i) => {
      doc.text(h.toUpperCase(), tx + 4, y + 8);
      tx += colW[i];
    });
    y += rowH;

    // Rows
    rows.forEach((row, ri) => {
      setFill(doc, ri % 2 === 0 ? C.black : C.dark);
      doc.rect(M, y, colW.reduce((a,b)=>a+b,0), rowH, 'F');
      tx = M;
      setText(doc, ri % 2 === 0 ? C.cream : C.creamD);
      doc.setFont('helvetica', ri === rows.length - 1 ? 'bold' : 'normal');
      doc.setFontSize(8);
      row.forEach((cell, ci) => {
        doc.text(cell, tx + 4, y + 8);
        tx += colW[ci];
      });
      y += rowH;
    });
    y += 8;
  }

  // Bullets
  if (pageData.bullets) {
    pageData.bullets.forEach(b => {
      setFill(doc, C.red);
      doc.circle(M + 3, y + 4, 2, 'F');
      setText(doc, C.creamD);
      doc.setFontSize(9);
      const bt = doc.splitTextToSize(b, W - M * 2 - 14);
      doc.text(bt, M + 12, y + 5);
      y += bt.length * 5.5 + 5;
    });
  }

  // Steps pipeline
  if (pageData.steps) {
    const stepW = (W - M * 2) / pageData.steps.length;
    pageData.steps.forEach((step, i) => {
      const sx = M + i * stepW;
      setFill(doc, C.dark);
      doc.rect(sx + 2, y, stepW - 4, 48, 'F');
      setFill(doc, C.red);
      doc.rect(sx + 2, y, stepW - 4, 2, 'F');
      setText(doc, C.gold);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);
      doc.text(step[0], sx + stepW / 2, y + 14, { align: 'center' });
      setText(doc, C.cream);
      doc.setFontSize(8);
      doc.text(step[1], sx + stepW / 2, y + 26, { align: 'center' });
      setText(doc, C.creamD);
      doc.setFontSize(7);
      const st = doc.splitTextToSize(step[2], stepW - 8);
      doc.text(st, sx + stepW / 2, y + 38, { align: 'center' });
    });
    y += 56;
  }

  // Partners
  if (pageData.partners && Array.isArray(pageData.partners[0])) {
    pageData.partners.forEach(p => {
      setFill(doc, C.dark);
      doc.rect(M, y, W - M * 2, 28, 'F');
      setFill(doc, C.red);
      doc.rect(M, y, 3, 28, 'F');
      setText(doc, C.cream);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(13);
      doc.text(p[0], M + 10, y + 12);
      setText(doc, C.creamD);
      doc.setFontSize(8);
      doc.text(p[1], M + 10, y + 22);
      setFill(doc, C.dark);
      doc.setLineWidth(0.3);
      doc.roundedRect(W - M - 62, y + 4, 60, 18, 2, 2, 'S');
      setText(doc, C.gold);
      doc.setFontSize(7);
      doc.text(p[2], W - M - 32, y + 14, { align: 'center' });
      y += 36;
    });
    y += 4;
  }

  // Note
  if (pageData.note) {
    setText(doc, C.creamD);
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    const nt = doc.splitTextToSize('▶ ' + pageData.note, W - M * 2);
    doc.text(nt, M, y + 5);
  }
}

// ── Contact page ────────────────────────────────────────────────────────────────
function drawContactPage(doc, pageData, pageNum, totalPages) {
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();
  const M = 18;

  setFill(doc, C.black);
  doc.rect(0, 0, W, H, 'F');
  setFill(doc, C.red);
  doc.rect(0, 0, W, H * 0.55, 'F');

  addFooter(doc, `${pageNum} of ${totalPages}`);

  let y = 60;
  setText(doc, C.gold);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(7);
  doc.text('GET IN TOUCH', M, y - 6);

  setText(doc, C.cream);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(40);
  doc.text("LET'S TALK", M, y + 10);

  setFill(doc, C.gold);
  doc.rect(M, y + 18, 50, 2, 'F');

  y += 38;
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(11);
  setText(doc, C.cream);
  (pageData.body || []).forEach(line => {
    doc.text(line, M, y);
    y += 8;
  });

  y += 12;
  setText(doc, C.gold);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.text('DELIVERY PARTNERS & SUPPLIERS', M, y);
  y += 8;
  setText(doc, C.creamD);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  (pageData.partners || []).forEach(line => {
    doc.text('•  ' + line, M, y);
    y += 7;
  });
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();

  const totalPages = PAGES.length;
  let pageNum = 1;

  // Cover
  drawCover(doc, PAGES[0]);
  doc.addPage();

  // Content pages
  for (let i = 1; i < PAGES.length; i++) {
    const p = PAGES[i];
    if (p.type === 'contact') {
      drawContactPage(doc, p, i + 1, totalPages);
    } else {
      drawContentPage(doc, p, i + 1, totalPages);
    }
    if (i < PAGES.length - 1) doc.addPage();
    pageNum++;
  }

  // Save
  const buf = doc.output('arraybuffer');
  fs.writeFileSync('/workspace/studex-pitch/Studex-Meat-Pitch-Deck.pdf', Buffer.from(buf));
  console.log('PDF written — ' + (doc.internal.pages.length - 1) + ' pages');
  const bytes = fs.statSync('/workspace/studex-pitch/Studex-Meat-Pitch-Deck.pdf').size;
  console.log('Size: ' + (bytes / 1024).toFixed(1) + ' KB');
}

main().catch(e => { console.error(e); process.exit(1); });
