/**
 * Studex Workflow Engine
 * Lightweight webhook-based automation server
 * Handles: Shopify orders → WhatsApp + Discord alerts
 */

require('dotenv').config();
const express = require('express');
const { shopifyOrderAlert } = require('./workflows/shopify-order-alert');
const { facebookLeadAlert } = require('./workflows/facebook-lead-alert');
const { morningOpsReport } = require('./workflows/morning-ops-report');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logger
app.use((req, res, next) => {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${req.method} ${req.path}`);
  next();
});

// ─── Health Check ───────────────────────────────────────────
app.get('/health', (req, res) => {
  res.json({
    status: 'RUNNING',
    service: 'Studex Workflow Engine',
    version: '1.0.0',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

// ─── Shopify Webhooks ────────────────────────────────────────
app.post('/webhooks/shopify/order', async (req, res) => {
  console.log('[Shopify] Order webhook received:', JSON.stringify(req.body, null, 2).substring(0, 500));
  try {
    const result = await shopifyOrderAlert(req.body);
    res.status(200).json({ ok: true, ...result });
  } catch (err) {
    console.error('[Shopify] Error:', err.message);
    res.status(500).json({ ok: false, error: err.message });
  }
});

// ─── Facebook Lead Webhooks ──────────────────────────────────
// Facebook sends leads via webhook — this endpoint receives them
app.post('/webhooks/facebook/lead', async (req, res) => {
  console.log('[Facebook] Lead webhook received');
  try {
    const result = await facebookLeadAlert(req.body);
    res.status(200).json({ ok: true, ...result });
  } catch (err) {
    console.error('[Facebook] Error:', err.message);
    res.status(500).json({ ok: false, error: err.message });
  }
});

// ─── Manual Trigger: Morning Ops Report ───────────────────────
app.post('/workflows/morning-ops', async (req, res) => {
  try {
    const result = await morningOpsReport();
    res.status(200).json({ ok: true, ...result });
  } catch (err) {
    console.error('[MorningOps] Error:', err.message);
    res.status(500).json({ ok: false, error: err.message });
  }
});

// ─── 404 Handler ─────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ ok: false, error: 'Endpoint not found' });
});

// ─── Start Server ─────────────────────────────────────────────
app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🚀 Studex Workflow Engine running on port ${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Shopify webhook: POST http://localhost:${PORT}/webhooks/shopify/order`);
  console.log(`   Facebook lead: POST http://localhost:${PORT}/webhooks/facebook/lead`);
  console.log(`   Morning ops: POST http://localhost:${PORT}/workflows/morning-ops\n`);
});
