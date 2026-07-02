/**
 * DenchClaw CRM Channel Plugin for AionUI
 *
 * Integrates DenchClaw CRM (https://www.dench.com/studeex-group/gateway)
 * as a channel in AionUI — messages from DenchClaw flow into AionUI agents,
 * and agent responses flow back to DenchClaw.
 *
 * Based on ext-wecom-bot pattern from AionUI examples.
 */

const { Plugin } = require('./ BasePlugin');

class DenchclawChannelPlugin {
  constructor(config = {}) {
    this.config = config;
    this.running = false;
    this.messageHandler = null;
    this.activeUsers = new Map(); // chatId -> user info
    this.messageIdCounter = 1;
  }

  /**
   * Register callback for incoming messages from DenchClaw
   */
  onMessage(handler) {
    this.messageHandler = handler;
  }

  /**
   * Called by PluginManager to initialize the plugin with config
   * Validates credentials and sets up the DenchClaw API client
   */
  async onInitialize(config) {
    const { baseUrl, apiKey, webhookSecret } = config;

    if (!baseUrl) {
      throw new Error('DenchClaw base URL is required');
    }

    this.config = { baseUrl, apiKey, webhookSecret };
    this.baseUrl = baseUrl.replace(/\/$/, ''); // normalize
    this.apiKey = apiKey;
    this.webhookSecret = webhookSecret;

    return { ok: true };
  }

  /**
   * Start the DenchClaw channel — sets up webhook listener
   */
  async onStart() {
    if (this.running) return { ok: true };

    console.log('[DenchClaw Channel] Starting DenchClaw CRM integration...');
    console.log(`[DenchClaw Channel] Gateway: ${this.baseUrl}`);

    // In a full implementation, this would:
    // 1. Register a webhook with DenchClaw at ${baseUrl}/webhook
    // 2. Or start a long-poll loop to ${baseUrl}/messages
    // 3. Validate the webhook secret if provided
    //
    // For now, we mark as running and accept messages via sendMessage
    // from within the AionUI agent context.

    this.running = true;
    return { ok: true };
  }

  /**
   * Stop the DenchClaw channel
   */
  async onStop() {
    if (!this.running) return { ok: true };

    console.log('[DenchClaw Channel] Stopping...');
    this.running = false;
    this.messageHandler = null;
    return { ok: true };
  }

  /**
   * Send a message out through DenchClaw
   * @param {string} chatId - DenchClaw user/chat ID
   * @param {object} message - Message object { type, text, markdown?, imageUrl? }
   * @returns {Promise<string>} - Platform message ID
   */
  async sendMessage(chatId, message) {
    if (!this.running) throw new Error('DenchClaw plugin not running');

    const msgId = `denchclaw-msg-${Date.now()}-${this.messageIdCounter++}`;

    try {
      // Send via DenchClaw REST API
      const endpoint = `${this.baseUrl}/api/messages`;
      const payload = {
        chatId,
        content: message.text || message.content?.text,
        type: message.type || 'text',
        ...(message.imageUrl && { imageUrl: message.imageUrl }),
        ...(message.markdown && { markdown: message.markdown }),
      };

      // In production: use fetch or axios here with apiKey auth header
      console.log(`[DenchClaw Channel] → Sending to ${chatId}:`, payload.content?.substring(0, 50));

      // Simulate successful send — in real impl, check HTTP response
      return msgId;
    } catch (error) {
      console.error('[DenchClaw Channel] Send error:', error.message);
      throw error;
    }
  }

  /**
   * Edit an existing message (for streaming updates)
   */
  async editMessage(chatId, messageId, message) {
    if (!this.running) throw new Error('DenchClaw plugin not running');

    console.log(`[DenchClaw Channel] Editing message ${messageId}`);
    // DenchClaw API: PUT /api/messages/{messageId}
    return { ok: true };
  }

  /**
   * Get number of active users
   */
  getActiveUserCount() {
    return this.activeUsers.size;
  }

  /**
   * Get bot info for DenchClaw
   */
  getBotInfo() {
    return {
      username: 'studex-denchclaw',
      displayName: 'Studex DenchClaw Bot',
      version: '0.1.0',
    };
  }

  // ============================================================
  // Inbound message conversion — DenchClaw → Unified format
  // Called by the webhook handler when DenchClaw sends a message
  // ============================================================

  /**
   * Convert DenchClaw inbound payload to AionUI unified format
   * @param {object} payload - Raw DenchClaw message payload
   * @returns {object} - IUnifiedIncomingMessage
   */
  toUnifiedIncomingMessage(payload) {
    return {
      id: payload.id || `denchclaw-${Date.now()}`,
      platform: 'studex-dench',
      chatId: payload.chatId || payload.userId || payload.from?.id,
      user: {
        id: payload.userId || payload.from?.id,
        displayName: payload.userName || payload.from?.name || 'DenchClaw User',
      },
      content: {
        type: payload.type || 'text',
        text: payload.text || payload.content || payload.message,
        imageUrl: payload.imageUrl,
      },
      timestamp: payload.timestamp || Date.now(),
      raw: payload,
    };
  }

  // ============================================================
  // Webhook handler — call this from your DenchClaw gateway
  // when a new message arrives at the webhook endpoint
  // ============================================================

  /**
   * Handle inbound message from DenchClaw webhook
   * Call this from the webserver route that receives DenchClaw callbacks
   *
   * @param {object} payload - DenchClaw webhook payload
   */
  async handleInboundMessage(payload) {
    if (!this.messageHandler) {
      console.warn('[DenchClaw Channel] No message handler registered');
      return;
    }

    const unified = this.toUnifiedIncomingMessage(payload);
    this.activeUsers.set(unified.chatId, unified.user);

    if (this.messageHandler) {
      await this.messageHandler(unified);
    }
  }

  // ============================================================
  // Streaming support (for Claude responses)
  // ============================================================

  /**
   * Stream a message in parts (streaming responses from agents)
   */
  async sendStreamingMessage(chatId, message, onChunk) {
    if (!this.running) throw new Error('DenchClaw plugin not running');

    const fullMsgId = `denchclaw-msg-${Date.now()}-${this.messageIdCounter++}`;

    if (onChunk) {
      // For streaming, send chunks as they arrive
      let sentFirst = false;
      let sentMsgId = null;

      onChunk.on('chunk', async (text) => {
        if (!sentFirst) {
          sentFirst = true;
          // Send initial message
          sentMsgId = await this.sendMessage(chatId, { type: 'text', text });
        } else if (sentMsgId) {
          // Edit the existing message with accumulated text
          const accumulated = text; // streaming tokenizer handles accumulation
          await this.editMessage(chatId, sentMsgId, { type: 'text', text: accumulated });
        }
      });
    }

    return fullMsgId;
  }
}

module.exports = { DenchclawChannelPlugin };
module.exports.default = DenchclawChannelPlugin;
module.exports.Plugin = DenchclawChannelPlugin;
