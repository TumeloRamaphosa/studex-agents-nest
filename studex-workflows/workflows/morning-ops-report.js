/**
 * Morning Operations Report
 * Scheduled daily at 07:00 SAST — posts to Discord
 * Fetches Shopify stats and sends a morning digest
 */

const axios = require('axios');

const {
  SHOPIFY_STORE_URL,
  SHOPIFY_ACCESS_TOKEN,
  DISCORD_WEBHOOK_URL,
  WHATSAPP_NOTIFY_NUMBER,
  AGENTMAIL_API_KEY,
  AGENTMAIL_BASE_URL = 'https://api.agentmail.to/v0',
} = process.env;

async function getShopifyOrders(daysAgo = 1) {
  if (!SHOPIFY_STORE_URL || !SHOPIFY_ACCESS_TOKEN) {
    console.log('[Shopify] Credentials not set — skipping order fetch');
    return null;
  }

  try {
    const since = new Date();
    since.setDate(since.getDate() - daysAgo);
    const created_at_min = since.toISOString();

    const response = await axios.get(
      `${SHOPIFY_STORE_URL}/admin/api/2024-01/orders.json`,
      {
        params: {
          status: 'any',
          created_at_min,
          limit: 50,
          fields: 'id,email,total_price,currency,financial_status,fulfillment_status,created_at,line_items',
        },
        headers: {
          'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
          'Content-Type': 'application/json',
        },
        timeout: 15000,
      }
    );

    return response.data.orders || [];
  } catch (err) {
    console.error('[Shopify] API error:', err.message);
    return null;
  }
}

async function getShopifyProducts() {
  if (!SHOPIFY_STORE_URL || !SHOPIFY_ACCESS_TOKEN) return null;

  try {
    const response = await axios.get(
      `${SHOPIFY_STORE_URL}/admin/api/2024-01/products.json`,
      {
        params: { limit: 10, fields: 'id,title,variants,status' },
        headers: { 'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN },
        timeout: 15000,
      }
    );
    return response.data.products || [];
  } catch (err) {
    console.error('[Shopify] Products API error:', err.message);
    return null;
  }
}

async function sendDiscordReport(report) {
  if (!DISCORD_WEBHOOK_URL) return null;

  const { orders, revenue, lowStock, products } = report;

  const embed = {
    title: '☕ Studex Morning Ops Report',
    description: `📅 ${new Date().toLocaleDateString('en-ZA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} — South Africa`,
    color: 0x00b37e,
    fields: [
      {
        name: '💰 Revenue (24h)',
        value: orders.length > 0 ? `**R${revenue.toFixed(2)}** across **${orders.length}** order(s)` : 'No orders in last 24h',
        inline: false,
      },
      {
        name: '📦 Top Products',
        value: orders.length > 0
          ? orders.slice(0, 3).map(o => `• ${o.line_items?.[0]?.title || 'Product'} — R${parseFloat(o.total_price || 0).toFixed(2)}`).join('\n')
          : '—',
        inline: false,
      },
      {
        name: '⚠️ Low Stock Products',
        value: lowStock.length > 0 ? lowStock.map(p => `• ${p}`).join('\n') : '✅ All OK',
        inline: false,
      },
    ],
    footer: { text: 'Studex Ops Engine — Automated Report' },
    timestamp: new Date().toISOString(),
  };

  try {
    return await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embed] }, { timeout: 10000 });
  } catch (err) {
    console.error('[Discord] Report send failed:', err.message);
    return null;
  }
}

async function morningOpsReport() {
  console.log('[MorningOps] Generating daily report...');

  const orders = await getShopifyOrders(1);
  const products = await getShopifyProducts();

  let revenue = 0;
  let lowStock = [];

  if (orders) {
    revenue = orders.reduce((sum, o) => sum + parseFloat(o.total_price || 0), 0);
  }

  if (products) {
    lowStock = products
      .filter(p => p.status !== 'active' || (p.variants || []).some(v => (v.inventory_quantity || 999) < 5))
      .map(p => p.title);
  }

  const report = { orders: orders || [], revenue, lowStock, products: products || [] };
  const discordResult = await sendDiscordReport(report);

  // WhatsApp summary to ops team
  if (WHATSAPP_NOTIFY_NUMBER && AGENTMAIL_API_KEY && orders?.length > 0) {
    const msg = `☕ *Studex Morning Brief*\n\n${new Date().toLocaleDateString('en-ZA')}\n💰 R${revenue.toFixed(2)} revenue (24h)\n📦 ${orders.length} order(s)\n⚠️ ${lowStock.length > 0 ? lowStock.join(', ') : 'All stock OK'}`;
    await axios.post(
      `${AGENTMAIL_BASE_URL}/messages/send`,
      { to: WHATSAPP_NOTIFY_NUMBER, message: msg, channel: 'whatsapp' },
      { headers: { 'Authorization': `Bearer ${AGENTMAIL_API_KEY}`, 'Content-Type': 'application/json' } },
      { timeout: 10000 }
    ).catch(e => console.error('[WhatsApp] Morning brief failed:', e.message));
  }

  console.log('[MorningOps] Report sent:', { revenue, orderCount: orders?.length || 0, lowStock });
  return report;
}

module.exports = { morningOpsReport };
