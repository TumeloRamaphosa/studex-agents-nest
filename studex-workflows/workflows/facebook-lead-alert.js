/**
 * Facebook Lead → WhatsApp + Discord Alert
 * Triggered when someone submits a Facebook lead form
 */

const axios = require('axios');

const {
  AGENTMAIL_API_KEY,
  AGENTMAIL_BASE_URL = 'https://api.agentmail.to/v0',
  DISCORD_WEBHOOK_URL,
  WHATSAPP_NOTIFY_NUMBER,
} = process.env;

async function sendWhatsApp(message, toNumber) {
  if (!AGENTMAIL_API_KEY || !toNumber) return null;
  try {
    return await axios.post(
      `${AGENTMAIL_BASE_URL}/messages/send`,
      { to: toNumber, message, channel: 'whatsapp' },
      { headers: { 'Authorization': `Bearer ${AGENTMAIL_API_KEY}`, 'Content-Type': 'application/json' } },
      { timeout: 10000 }
    );
  } catch (err) {
    console.error('[WhatsApp] Send failed:', err.message);
    return null;
  }
}

async function sendDiscord(lead) {
  if (!DISCORD_WEBHOOK_URL) return null;

  const embed = {
    title: '📋 New Facebook Lead',
    color: 0x1877f2, // Facebook blue
    fields: [
      { name: '👤 Name', value: lead.full_name || 'N/A', inline: true },
      { name: '📧 Email', value: lead.email || 'N/A', inline: true },
      { name: '📱 Phone', value: lead.phone_number || 'N/A', inline: true },
      { name: '📝 Message', value: (lead.questions_and_answers?.[0]?.answer || lead.message || 'No message').substring(0, 300), inline: false },
    ],
    footer: { text: 'Facebook Lead Gen — Studex CRM' },
    timestamp: new Date().toISOString(),
  };

  try {
    return await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embed] }, { timeout: 10000 });
  } catch (err) {
    console.error('[Discord] Send failed:', err.message);
    return null;
  }
}

async function facebookLeadAlert(lead) {
  console.log('[Workflow] Processing Facebook lead:', JSON.stringify(lead).substring(0, 200));

  const name = lead.full_name || 'Unknown';
  const email = lead.email || 'N/A';
  const phone = lead.phone_number || 'N/A';

  const whatsappMessage = `📋 *New Facebook Lead!*

👤 ${name}
📧 ${email}
📱 ${phone}

Reply to convert this lead into a customer!`;

  const [whatsappResult, discordResult] = await Promise.allSettled([
    sendWhatsApp(whatsappMessage, WHATSAPP_NOTIFY_NUMBER),
    sendDiscord(lead),
  ]);

  return {
    name,
    email,
    whatsapp: whatsappResult.status === 'fulfilled' ? 'SENT' : 'FAILED',
    discord: discordResult.status === 'fulfilled' ? 'SENT' : 'FAILED',
  };
}

module.exports = { facebookLeadAlert };
