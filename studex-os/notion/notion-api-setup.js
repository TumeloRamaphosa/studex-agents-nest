#!/usr/bin/env node
/**
 * notion-api-setup.js
 * Studex Meat HQ — Notion Database Bootstrapper
 *
 * Creates all Notion databases for the Studex OS workspace:
 *   - Orders DB
 *   - Products DB
 *   - Delivery Partners DB
 *   - Content Calendar DB (bonus — used by Naledi)
 *
 * Seeds each with known data for Silent Valley, Noags Butchery, Moutloe Farm,
 * Dinkoko Pty Ltd, My Courier, and sample product/order rows.
 *
 * Env vars required:
 *   NOTION_API_KEY        — Integration token (secret_xxx)
 *   NOTION_WORKSPACE_ID   — Parent page ID where DBs will be created
 *
 * Optional:
 *   STUDEX_NOTION_ORDERS_DB_ID          — reuse existing Orders DB (skip creation)
 *   STUDEX_NOTION_PRODUCTS_DB_ID        — reuse existing Products DB
 *   STUDEX_NOTION_DELIVERY_PARTNERS_DB_ID — reuse existing Partners DB
 *   STUDEX_NOTION_CONTENT_CALENDAR_DB_ID  — reuse existing Calendar DB
 *
 * Usage:
 *   node notion-api-setup.js
 *
 * Output:
 *   IDs of created databases are printed to stdout.
 *   Set them in your env as STUDEX_NOTION_*_DB_ID for other scripts.
 */

'use strict';

const { Client } = require('@notionhq/client');

// ─── Configuration ───────────────────────────────────────────────────────────

const NOTION_API_KEY      = process.env.NOTION_API_KEY;
const NOTION_WORKSPACE_ID = process.env.NOTION_WORKSPACE_ID;

// Pre-existing DB IDs — set to skip creation
const SKIP_ORDERS_DB          = process.env.STUDEX_NOTION_ORDERS_DB_ID;
const SKIP_PRODUCTS_DB        = process.env.STUDEX_NOTION_PRODUCTS_DB_ID;
const SKIP_DELIVERY_PARTNERS_DB = process.env.STUDEX_NOTION_DELIVERY_PARTNERS_DB_ID;
const SKIP_CONTENT_CALENDAR_DB  = process.env.STUDEX_NOTION_CONTENT_CALENDAR_DB_ID;

// ─── Validation ─────────────────────────────────────────────────────────────

if (!NOTION_API_KEY || !NOTION_WORKSPACE_ID) {
  console.error('❌ Missing required env vars.');
  console.error('   Set NOTION_API_KEY and NOTION_WORKSPACE_ID before running.');
  console.error('   Example:');
  console.error('     NOTION_API_KEY=secret_xxx NOTION_WORKSPACE_ID=xxx node notion-api-setup.js');
  process.exit(1);
}

// ─── Notion Client ───────────────────────────────────────────────────────────

const notion = new Client({ auth: NOTION_API_KEY });

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Create a database under the given parent page.
 */
async function createDatabase(parentId, title, properties) {
  const response = await notion.databases.create({
    parent: { type: 'page_id', page_id: parentId },
    icon:   { type: 'emoji', emoji: '📋' },
    title:  [{ type: 'text', text: { content: title } }],
    properties,
    is_inline: false,
  });
  return response;
}

/**
 * Create a page (row) inside a database.
 */
async function createPage(databaseId, properties) {
  const response = await notion.pages.create({
    parent: { type: 'database_id', database_id: databaseId },
    properties,
  });
  return response;
}

/**
 * Rich-text array helper.
 */
function rt(text) {
  return [{ type: 'text', text: { content: text, link: null } }];
}

/**
 * Sleep utility — respects Notion's rate limits (~3 req/s).
 */
function sleep(ms = 400) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ─── Database Schemas ────────────────────────────────────────────────────────

const ORDERS_SCHEMA = {
  'Order ID': {
    title: {},
  },
  'Customer Name': {
    rich_text: {},
  },
  'WhatsApp': {
    phone_number: null,
  },
  'Address': {
    rich_text: {},
  },
  'Products': {
    rich_text: {},
  },
  'Quantity (kg)': {
    number: { format: 'kilograms' },
  },
  'Total (ZAR)': {
    number: { format: 'rand' },
  },
  'Status': {
    select: {
      options: [
        { name: 'New',        color: 'red'    },
        { name: 'Dispatched', color: 'orange' },
        { name: 'In Transit', color: 'yellow' },
        { name: 'Delivered',  color: 'green'  },
        { name: 'Cancelled',  color: 'gray'   },
      ],
    },
  },
  'Driver': {
    rich_text: {},
  },
  'ETA': {
    date: {},
  },
  'Shop Name': {
    rich_text: {},
  },
  'Notes': {
    rich_text: {},
  },
};

const PRODUCTS_SCHEMA = {
  'Product Name': {
    title: {},
  },
  'SKU': {
    rich_text: {},
  },
  'Category': {
    select: {
      options: [
        { name: 'Beef',       color: 'brown'  },
        { name: 'Lamb',       color: 'purple' },
        { name: 'Poultry',    color: 'yellow' },
        { name: 'Processed',  color: 'red'   },
      ],
    },
  },
  'Supplier': {
    rich_text: {},
  },
  'Farm': {
    rich_text: {},
  },
  'Provenance': {
    rich_text: {},
  },
  'Stock (kg)': {
    number: { format: 'kilograms' },
  },
  'Price (ZAR/kg)': {
    number: { format: 'number' },
  },
  'Halal Certified': {
    checkbox: {},
  },
  'Status': {
    select: {
      options: [
        { name: 'Available',   color: 'green'  },
        { name: 'Low Stock',  color: 'yellow' },
        { name: 'Out of Stock', color: 'red'  },
      ],
    },
  },
};

const DELIVERY_PARTNERS_SCHEMA = {
  'Partner Name': {
    title: {},
  },
  'Contact': {
    phone_number: null,
  },
  'WhatsApp': {
    rich_text: {},
  },
  'Areas': {
    multi_select: {
      options: [
        { name: 'Cape Town',            color: 'blue'   },
        { name: 'Southern Suburbs',     color: 'green'  },
        { name: 'Northern Suburbs',     color: 'purple' },
        { name: 'Atlantic Seaboard',    color: 'yellow' },
        { name: 'Winelands',            color: 'orange' },
        { name: 'Helderberg',           color: 'red'    },
      ],
    },
  },
  'Rate (ZAR/km)': {
    number: { format: 'number' },
  },
  'Min Charge (ZAR)': {
    number: { format: 'rand' },
  },
  'SLA': {
    rich_text: {},
  },
  'Status': {
    select: {
      options: [
        { name: 'Active',   color: 'green' },
        { name: 'On Hold',  color: 'gray'  },
      ],
    },
  },
  'Notes': {
    rich_text: {},
  },
};

const CONTENT_CALENDAR_SCHEMA = {
  'Post Title': {
    title: {},
  },
  'Platform': {
    multi_select: {
      options: [
        { name: 'Facebook',        color: 'blue'   },
        { name: 'Instagram',      color: 'pink'   },
        { name: 'WhatsApp Status', color: 'green' },
      ],
    },
  },
  'Content Type': {
    select: {
      options: [
        { name: 'Reel',     color: 'purple' },
        { name: 'Static',   color: 'yellow' },
        { name: 'Story',    color: 'orange' },
        { name: 'Carousel', color: 'blue'   },
        { name: 'Blog',     color: 'gray'   },
      ],
    },
  },
  'Publish Date': {
    date: {},
  },
  'Caption': {
    rich_text: {},
  },
  'Status': {
    select: {
      options: [
        { name: 'Idea',      color: 'gray'   },
        { name: 'Draft',     color: 'yellow' },
        { name: 'Scheduled', color: 'blue'   },
        { name: 'Posted',    color: 'green'  },
      ],
    },
  },
  'Posted By': {
    rich_text: {},
  },
  'Notes': {
    rich_text: {},
  },
};

// ─── Seeding Data ────────────────────────────────────────────────────────────

const DELIVERY_PARTNERS_SEED = [
  {
    name: 'Dinkoko Pty Ltd',
    contact: '+27 78 161 0332',
    whatsapp: '+27 78 161 0332',
    areas: ['Cape Town', 'Southern Suburbs', 'Northern Suburbs', 'Atlantic Seaboard'],
    rate: 9,
    minCharge: 100,
    sla: '2-hour delivery window within CT metro',
    status: 'Active',
    notes: 'Preferred partner for bulk orders.',
  },
  {
    name: 'My Courier',
    contact: '+27 81 555 0198',
    whatsapp: '+27 81 555 0198',
    areas: ['Cape Town', 'Southern Suburbs', 'Northern Suburbs'],
    rate: 8,
    minCharge: 80,
    sla: 'Same-day within 4-hour window',
    status: 'Active',
    notes: 'Good for smaller/single-item orders.',
  },
];

const PRODUCTS_SEED = [
  {
    name: 'Moutloe Farm Lamb Ribs',
    sku: 'STX-LAM-001',
    category: 'Lamb',
    supplier: 'Moutloe Farm',
    farm: 'Moutloe Farm, Rawsonville',
    provenance: 'Kill date: Fresh weekly · Abattoir: Certified Halal · Cert: HL-2024-0117',
    stock: 45,
    price: 189,
    halal: true,
    status: 'Available',
  },
  {
    name: 'Moutloe Farm Lamb Chops',
    sku: 'STX-LAM-002',
    category: 'Lamb',
    supplier: 'Moutloe Farm',
    farm: 'Moutloe Farm, Rawsonville',
    provenance: 'Kill date: Fresh weekly · Abattoir: Certified Halal · Cert: HL-2024-0117',
    stock: 30,
    price: 229,
    halal: true,
    status: 'Available',
  },
  {
    name: 'Silent Valley Beef Rump',
    sku: 'STX-BEF-001',
    category: 'Beef',
    supplier: 'Silent Valley',
    farm: 'Silent Valley Farm, Philadelphia',
    provenance: 'Kill date: Fresh weekly · Abattoir: Licensed · Contact: 083 254 6777',
    stock: 60,
    price: 169,
    halal: true,
    status: 'Available',
  },
  {
    name: 'Silent Valley Beef Sirloin',
    sku: 'STX-BEF-002',
    category: 'Beef',
    supplier: 'Silent Valley',
    farm: 'Silent Valley Farm, Philadelphia',
    provenance: 'Kill date: Fresh weekly · Abattoir: Licensed · Contact: 083 254 6777',
    stock: 40,
    price: 219,
    halal: true,
    status: 'Available',
  },
  {
    name: 'Noags Chicken Full',
    sku: 'STX-POU-001',
    category: 'Poultry',
    supplier: 'Noags Butchery',
    farm: 'Noagas Kraal, Main Road',
    provenance: 'Farm-fresh daily · Contact: 021 001 2345 / 074 580 0815',
    stock: 80,
    price: 79,
    halal: true,
    status: 'Available',
  },
  {
    name: 'Noags Chicken Wings',
    sku: 'STX-POU-002',
    category: 'Poultry',
    supplier: 'Noags Butchery',
    farm: 'Noagas Kraal, Main Road',
    provenance: 'Farm-fresh daily · Contact: 021 001 2345 / 074 580 0815',
    stock: 20,
    price: 99,
    halal: true,
    status: 'Low Stock',
  },
];

const ORDERS_SEED = [
  {
    orderId: 'STX-2026-0001',
    customer: 'Thandi Khumalo',
    whatsapp: '+27 82 555 0101',
    address: '14 Rose Street, Gardens, Cape Town, 8001',
    products: 'Moutloe Farm Lamb Ribs (2kg), Moutloe Farm Lamb Chops (1.5kg)',
    quantity: 3.5,
    total: 758.50,
    status: 'Delivered',
    driver: 'Dinkoko Pty Ltd',
    eta: '2026-06-27T13:00:00',
    shopName: 'Thandi\'s Kitchen',
    notes: 'Leave at gate — dog on premises.',
  },
  {
    orderId: 'STX-2026-0002',
    customer: 'Sibusiso Dlamini',
    whatsapp: '+27 83 444 0222',
    address: '45 Dolphin Road, Sea Point, Cape Town, 8060',
    products: 'Silent Valley Beef Rump (3kg), Silent Valley Beef Sirloin (2kg)',
    quantity: 5,
    total: 925.00,
    status: 'In Transit',
    driver: 'My Courier',
    eta: '2026-06-29T15:00:00',
    shopName: 'Sibusiso\'s Butchery',
    notes: 'Call on arrival.',
  },
  {
    orderId: 'STX-2026-0003',
    customer: 'Lerato Mokoena',
    whatsapp: '+27 71 666 0333',
    address: '8 Pine Street, Stellenbosch, 7600',
    products: 'Noags Chicken Full (4 units), Noags Chicken Wings (2kg)',
    quantity: 8,
    total: 514.00,
    status: 'New',
    driver: '',
    eta: '',
    shopName: 'Lerato\'s Kitchen',
    notes: 'First-time customer — include welcome card.',
  },
  {
    orderId: 'STX-2026-0004',
    customer: 'Nqobile Zulu',
    whatsapp: '+27 76 777 0444',
    address: '22 Main Road, Muizenberg, Cape Town, 7945',
    products: 'Moutloe Farm Lamb Ribs (5kg)',
    quantity: 5,
    total: 945.00,
    status: 'Dispatched',
    driver: 'Dinkoko Pty Ltd',
    eta: '2026-06-30T11:00:00',
    shopName: 'Nqobile\'s Eatery',
    notes: 'Bulk order — extra ice pack requested.',
  },
];

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  console.log('═══════════════════════════════════════════════');
  console.log('  Studex Meat HQ — Notion Database Bootstrapper');
  console.log('  Kanan Band · Studex OS · Powered by Charlie');
  console.log('═══════════════════════════════════════════════\n');

  console.log(`Workspace ID : ${NOTION_WORKSPACE_ID}`);
  console.log(`API Key      : ${NOTION_API_KEY.slice(0, 12)}...${NOTION_API_KEY.slice(-4)}`);
  console.log('');

  // ── 1. Orders DB ────────────────────────────────────────────────────────────

  if (SKIP_ORDERS_DB) {
    console.log('✅ Orders DB already exists — skipping creation.');
    console.log(`   DB ID: ${SKIP_ORDERS_DB}`);
    var ordersDbId = SKIP_ORDERS_DB;
  } else {
    console.log('🔧 Creating Orders DB…');
    const ordersDb = await createDatabase(NOTION_WORKSPACE_ID, 'Orders', ORDERS_SCHEMA);
    var ordersDbId = ordersDb.id;
    console.log(`   ✅ Orders DB created: ${ordersDbId}`);
  }

  // ── 2. Products DB ──────────────────────────────────────────────────────────

  if (SKIP_PRODUCTS_DB) {
    console.log('✅ Products DB already exists — skipping creation.');
    console.log(`   DB ID: ${SKIP_PRODUCTS_DB}`);
    var productsDbId = SKIP_PRODUCTS_DB;
  } else {
    console.log('🔧 Creating Products DB…');
    const productsDb = await createDatabase(NOTION_WORKSPACE_ID, 'Products', PRODUCTS_SCHEMA);
    var productsDbId = productsDb.id;
    console.log(`   ✅ Products DB created: ${productsDbId}`);
  }

  // ── 3. Delivery Partners DB ────────────────────────────────────────────────

  if (SKIP_DELIVERY_PARTNERS_DB) {
    console.log('✅ Delivery Partners DB already exists — skipping creation.');
    console.log(`   DB ID: ${SKIP_DELIVERY_PARTNERS_DB}`);
    var deliveryDbId = SKIP_DELIVERY_PARTNERS_DB;
  } else {
    console.log('🔧 Creating Delivery Partners DB…');
    const deliveryDb = await createDatabase(NOTION_WORKSPACE_ID, 'Delivery Partners', DELIVERY_PARTNERS_SCHEMA);
    var deliveryDbId = deliveryDb.id;
    console.log(`   ✅ Delivery Partners DB created: ${deliveryDbId}`);
  }

  // ── 4. Content Calendar DB ──────────────────────────────────────────────────

  if (SKIP_CONTENT_CALENDAR_DB) {
    console.log('✅ Content Calendar DB already exists — skipping creation.');
    console.log(`   DB ID: ${SKIP_CONTENT_CALENDAR_DB}`);
    var calendarDbId = SKIP_CONTENT_CALENDAR_DB;
  } else {
    console.log('🔧 Creating Content Calendar DB…');
    const calendarDb = await createDatabase(NOTION_WORKSPACE_ID, 'Content Calendar', CONTENT_CALENDAR_SCHEMA);
    var calendarDbId = calendarDb.id;
    console.log(`   ✅ Content Calendar DB created: ${calendarDbId}`);
  }

  // ── 5. Seed Delivery Partners ───────────────────────────────────────────────

  console.log('\n🌱 Seeding Delivery Partners…');
  for (const partner of DELIVERY_PARTNERS_SEED) {
    await sleep(500);
    const page = await createPage(deliveryDbId, {
      'Partner Name': { title: rt(partner.name) },
      'Contact':       { phone_number: partner.contact },
      'WhatsApp':     { rich_text: rt(partner.whatsapp) },
      'Areas':        { multi_select: partner.areas.map(n => ({ name: n })) },
      'Rate (ZAR/km)':{ number: partner.rate },
      'Min Charge (ZAR)': { number: partner.minCharge },
      'SLA':          { rich_text: rt(partner.sla) },
      'Status':       { select: { name: partner.status } },
      'Notes':        { rich_text: rt(partner.notes) },
    });
    console.log(`   ✅ ${partner.name}`);
  }

  // ── 6. Seed Products ────────────────────────────────────────────────────────

  console.log('\n🌱 Seeding Products…');
  for (const product of PRODUCTS_SEED) {
    await sleep(500);
    const page = await createPage(productsDbId, {
      'Product Name':   { title: rt(product.name) },
      'SKU':           { rich_text: rt(product.sku) },
      'Category':      { select: { name: product.category } },
      'Supplier':      { rich_text: rt(product.supplier) },
      'Farm':          { rich_text: rt(product.farm) },
      'Provenance':    { rich_text: rt(product.provenance) },
      'Stock (kg)':    { number: product.stock },
      'Price (ZAR/kg)':{ number: product.price },
      'Halal Certified': { checkbox: product.halal },
      'Status':        { select: { name: product.status } },
    });
    console.log(`   ✅ ${product.name}`);
  }

  // ── 7. Seed Orders ─────────────────────────────────────────────────────────

  console.log('\n🌱 Seeding Orders…');
  for (const order of ORDERS_SEED) {
    await sleep(500);
    const props = {
      'Order ID':      { title: rt(order.orderId) },
      'Customer Name': { rich_text: rt(order.customer) },
      'WhatsApp':     { phone_number: order.whatsapp },
      'Address':       { rich_text: rt(order.address) },
      'Products':      { rich_text: rt(order.products) },
      'Quantity (kg)': { number: order.quantity },
      'Total (ZAR)':   { number: order.total },
      'Status':        { select: { name: order.status } },
      'Driver':        { rich_text: rt(order.driver) },
      'Shop Name':    { rich_text: rt(order.shopName) },
      'Notes':         { rich_text: rt(order.notes) },
    };
    if (order.eta) {
      props['ETA'] = { date: { start: order.eta } };
    }
    const page = await createPage(ordersDbId, props);
    console.log(`   ✅ ${order.orderId} — ${order.customer} (${order.status})`);
  }

  // ── 8. Summary ─────────────────────────────────────────────────────────────

  console.log('\n═══════════════════════════════════════════════');
  console.log('  ✅ All databases created and seeded!');
  console.log('═══════════════════════════════════════════════');
  console.log('\nAdd these to your .env:');
  console.log('');
  console.log(`STUDEX_NOTION_ORDERS_DB_ID=${ordersDbId}`);
  console.log(`STUDEX_NOTION_PRODUCTS_DB_ID=${productsDbId}`);
  console.log(`STUDEX_NOTION_DELIVERY_PARTNERS_DB_ID=${deliveryDbId}`);
  console.log(`STUDEX_NOTION_CONTENT_CALENDAR_DB_ID=${calendarDbId}`);
  console.log('');
  console.log('Then share each database with the Studex OS integration:');
  console.log('  Open each DB → ··· → Add connections → Studex OS');
  console.log('');
}

main().catch(err => {
  console.error('\n❌ Setup failed:', err.message);
  if (err.code === 'object_not_found') {
    console.error('   → Check NOTION_WORKSPACE_ID is a valid page ID.');
    console.error('   → Ensure the integration (NOTION_API_KEY) has access to this page.');
    console.error('   → Share the page with the integration: open it → ··· → Add connections.');
  }
  if (err.status === 429) {
    console.error('   → Rate limited by Notion. Wait 60 seconds and re-run.');
  }
  process.exit(1);
});
