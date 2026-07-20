/**
 * Shopify Order → WhatsApp + Discord Alert
 * Triggered when a new order is created in Shopify
 */

const axios = require('axios');

const {
  AGENTMAIL_API_KEY,
  AGENTMAIL_BASE_URL = 'https://api.agentmail.to/v0',
  DISCORD_WEBHOOK_URL,
  WHATSAPP_NOTIFY_NUMBER,       // e.g. +27820000000 — Naledi/Tumelo
  WHATSAPP_STUDEX_NUMBER,       // e.g. +27820000000 — Studex WhatsApp Business
} = process.env;

/**
 * Format order items for WhatsApp message
 */
function formatOrderItems(order) {
  const lines = (order.line_items || []).map(item => {
    return `• ${item.quantity}x ${item.title} — R${((item.price || 0) * item.quantity).toFixed(2)}`;
  }).join('\n');
  return lines || '• No items found';
}

/**
 * Send WhatsApp message via AgentMail API
 */
async function sendWhatsApp(message, toNumber) {
  if (!AGENTMAIL_API_KEY || !toNumber) {
    console.log('[WhatsApp] Skipped — no API key or number configured');
    return null;
  }

  try {
    const response = await axios.post(
      `${AGENTMAIL_BASE_URL}/messages/send`,
      {
        to: toNumber,
        message,
        channel: 'whatsapp',
      },
      {
        headers: {
          'Authorization': `Bearer ${AGENTMAIL_API_KEY}`,
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      }
    );
    console.log('[WhatsApp] Message sent:', response.data);
    return response.data;
  } catch (err) {
    const msg = err.response?.data || err.message;
    console.error('[WhatsApp] Send failed:', msg);
    return null;
  }
}

/**
 * Send Discord embed via webhook
 */
async function sendDiscord(order) {
  if (!DISCORD_WEBHOOK_URL) {
    console.log('[Discord] Skipped — no webhook URL configured');
    return null;
  }

  const total = parseFloat(order.total_price || 0).toFixed(2);
  const currency = order.currency || 'ZAR';
  const customerName = order.customer
    ? `${order.customer.first_name} ${order.customer.last_name}`.trim()
    : 'Unknown';
  const customerEmail = order.customer?.email || 'N/A';
  const orderId = order.id || 'N/A';
  const createdAt = new Date().toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' });

  const items = (order.line_items || [])
    .slice(0, 5)
    .map(item => `**${item.quantity}x** ${item.title} — R${((item.price || 0) * item.quantity).toFixed(2)}`)
    .join('\n');

  const embed = {
    title: `🛒 New Studex Order — R${total}`,
    description: items,
    color: 0x00b37e, // Studex green
    fields: [
      { name: '👤 Customer', value: customerName, inline: true },
      { name: '📧 Email', value: customerEmail, inline: true },
      { name: '🆔 Order ID', value: String(orderId), inline: true },
      { name: '💳 Payment', value: order.financial_status?.toUpperCase() || 'PENDING', inline: true },
      { name: '🚚 Fulfillment', value: order.fulfillment_status || 'UNFULFILLED', inline: true },
    ],
    footer: { text: 'Studex Ops — Automated Alert' },
    timestamp: new Date().toISOString(),
  };

  // Add note if low stock item detected
  const hasLowStock = (order.line_items || []).some(i =>
    (i.title || '').toLowerCase().includes('low stock')
  );
  if (hasLowStock) {
    embed.fields.push({
      name: '⚠️ Low Stock Alert',
      value: 'One or more items may need restocking',
      inline: false,
    });
  }

  try {
    const response = await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embed] }, { timeout: 10000 });
    console.log('[Discord] Embed sent:', response.status);
    return response.data;
  } catch (err) {
    console.error('[Discord] Send failed:', err.message);
    return null;
  }
}

/**
 * Main workflow function
 */
async function shopifyOrderAlert(order) {
  console.log('[Workflow] Processing Shopify order:', order.id);

  const total = parseFloat(order.total_price || 0).toFixed(2);
  const customerName = order.customer
    ? `${order.customer.first_name} ${order.customer.last_name}`.trim()
    : 'Customer';
  const itemCount = (order.line_items || []).reduce((sum, i) => sum + (i.quantity || 0), 0);

  // WhatsApp message to ops team
  const whatsappMessage = `🛒 *New Studex Order!*

👤 ${customerName}
📦 ${itemCount} item(s)
💰 *R${total}*

View in Shopify: https://${order.domain || 'studexmeat.com'}/admin/orders/${order.id}`;

  // ─── Dispatch alerts ────────────────────────────────────────
  const [whatsappResult, discordResult] = await Promise.allSettled([
    sendWhatsApp(whatsappMessage, WHATSAPP_NOTIFY_NUMBER),
    sendDiscord(order),
  ]);

  const results = {
    orderId: order.id,
    total: `R${total}`,
    customer: customerName,
    itemCount,
    whatsapp: whatsappResult.status === 'fulfilled' ? 'SENT' : 'FAILED',
    discord: discordResult.status === 'fulfilled' ? 'SENT' : 'FAILED',
  };

  console.log('[Workflow] Order alert complete:', results);
  return results;
}

module.exports = { shopifyOrderAlert };
