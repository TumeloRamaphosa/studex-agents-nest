/**
 * Charlie Agent — Chief Orchestrator
 * Node.js 20 + Express + PostgreSQL + Winston
 * Connects: Tumelo ↔ Charlie ↔ Robusca ↔ Sub-Agents
 */
require('dotenv').config();

const express = require('express');
const { Pool } = require('pg');
const winston = require('winston');
const WebSocket = require('ws');
const fetch = require('node-fetch');
const { v4: uuidv4 } = require('uuid');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

// ── Logger ────────────────────────────────────────────────────────────────
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.colorize(),
    winston.format.printf(({ timestamp, level, message }) =>
      `[${timestamp}] 🎯 Charlie: ${message}`
    )
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: process.env.LOG_FILE || '/var/log/charlie/app.log' }),
  ],
});

// ── PostgreSQL ────────────────────────────────────────────────────────────
const db = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: false,
  max: 20,
  idleTimeoutMillis: 30000,
});

db.query('SELECT NOW()').then(() => logger.info('✅ PostgreSQL connected')).catch(e => logger.warn('⚠️  DB connect failed:', e.message));

// ── App ──────────────────────────────────────────────────────────────────
const app = express();
app.use(cors());
app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json({ limit: '1mb' }));
app.use(rateLimit({ windowMs: 60000, max: 200 }));

// ── Sub-Agent Registry ────────────────────────────────────────────────────
const AGENTS = {
  'naledi':    { url: process.env.NALEDI_URL    || 'http://localhost:3002', role: 'CMO — Content & Social' },
  'shopify':   { url: process.env.SHOPIFY_URL   || 'http://localhost:3003', role: 'E-Commerce & Orders' },
  'discord':   { url: process.env.DISCORD_URL   || 'http://localhost:3004', role: 'Community & Outreach' },
  'content':   { url: process.env.CONTENT_URL   || 'http://localhost:3005', role: 'Content Pipeline' },
  'approval':  { url: process.env.APPROVAL_URL  || 'http://localhost:3006', role: 'Deal Approval Workflow' },
  'robusca':   { url: process.env.ROBUSCA_URL   || 'http://localhost:8001', role: 'CEO — Chief of Staff' },
};

// ── Task Queue (in-memory + PG-backed) ───────────────────────────────────
const taskQueue = [];
const ACTIVE_SESSIONS = new Map();

// ── Helper: Log to DB ─────────────────────────────────────────────────────
async function logToDB(level, source, message, meta = {}) {
  const sql = `INSERT INTO agent_logs(id, ts, level, source, message, meta) VALUES($1,$2,$3,$4,$5,$6)`;
  try {
    await db.query(sql, [uuidv4(), new Date(), level, source, message, JSON.stringify(meta)]);
  } catch (e) {
    logger.warn('DB log failed:', e.message);
  }
}

// ── Helper: Call a sub-agent ──────────────────────────────────────────────
async function delegateToAgent(agentName, task) {
  const agent = AGENTS[agentName];
  if (!agent) return { ok: false, error: `Unknown agent: ${agentName}` };

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 55000);

    const res = await fetch(`${agent.url}/task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Charlie-Key': process.env.ROBUSCA_API_KEY },
      body: JSON.stringify({ task, sessionId: task.sessionId, from: 'charlie' }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    const data = await res.json().catch(() => ({}));
    logger.info(`✅ ${agentName} responded [${res.status}]: ${JSON.stringify(data).slice(0, 80)}`);
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    logger.warn(`⚠️  ${agentName} unreachable: ${e.message}`);
    return { ok: false, error: e.message };
  }
}

// ── Helper: Report to Robusca ─────────────────────────────────────────────
async function reportToRobusca(message, context = {}) {
  if (!process.env.ROBUSCA_URL) return;
  try {
    await fetch(`${process.env.ROBUSCA_URL}/api/charlie-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Charlie-Key': process.env.ROBUSCA_API_KEY },
      body: JSON.stringify({ from: 'charlie', message, context, ts: new Date().toISOString() }),
    });
  } catch (e) {
    logger.warn('Robusca report failed:', e.message);
  }
}

// ── Routes ────────────────────────────────────────────────────────────────

// Health
app.get('/health', (req, res) => res.json({ status: 'ok', agent: 'charlie', ts: new Date().toISOString() }));

// Status overview
app.get('/api', (req, res) => {
  res.json({
    name: 'Charlie',
    role: 'Chief Orchestrator',
    emoji: '🎯',
    parent: 'Robusca',
    uptime: process.uptime(),
    queueDepth: taskQueue.length,
    agents: Object.entries(AGENTS).map(([k, v]) => ({ name: k, role: v.role, url: v.url })),
  });
});

// Dispatch a task
app.post('/api/dispatch', async (req, res) => {
  const { task, targets, priority, sessionId } = req.body;
  if (!task) return res.status(400).json({ error: 'task is required' });

  const id = uuidv4();
  const session = sessionId || uuidv4();

  logger.info(`📋 Dispatching task [${id}] → ${(targets || Object.keys(AGENTS)).join(', ')}: ${task.slice(0, 80)}`);
  await logToDB('info', 'charlie', `Task dispatched: ${task.slice(0, 100)}`, { id, targets, priority });

  const results = {};
  const agents = targets && targets.length ? targets : Object.keys(AGENTS).filter(k => k !== 'robusca');

  await Promise.allSettled(
    agents.map(agentName =>
      delegateToAgent(agentName, task).then(r => { results[agentName] = r; })
    )
  );

  // Report completion to Robusca
  const anyFailed = Object.values(results).some(r => !r.ok);
  await reportToRobusca(
    `Task ${anyFailed ? 'partially' : 'fully'} completed: ${task.slice(0, 60)}${anyFailed ? ' ⚠️' : ''}`,
    { taskId: id, results }
  );

  res.json({ taskId: id, session, results });
});

// Direct message (voice/text from Tumelo → Charlie)
app.post('/api/message', async (req, res) => {
  const { message, voice, from } = req.body;
  if (!message) return res.status(400).json({ error: 'message required' });

  logger.info(`💬 Message from ${from || 'unknown'}: ${message.slice(0, 80)}`);
  await logToDB('info', from || 'unknown', message);

  // Parse intent
  const lower = message.toLowerCase();
  let response = 'Message received. I will coordinate that now.';
  let delegated = false;

  if (/order|shopify|sale|customer/i.test(lower)) {
    const r = await delegateToAgent('shopify', message);
    response = r.ok
      ? `Shopify agent actioned: ${JSON.stringify(r.data || {}).slice(0, 100)}`
      : 'Shopify agent could not be reached. I will try an alternative.';
    delegated = true;
  } else if (/content|post|social|instagram|facebook|tweet/i.test(lower)) {
    const r = await delegateToAgent('naledi', message);
    response = r.ok ? `Naledi is on it: ${JSON.stringify(r.data || {}).slice(0, 100)}` : 'Naledi is unavailable.';
    delegated = true;
  } else if (/approve|deal|contract|prowtc/i.test(lower)) {
    const r = await delegateToAgent('approval', message);
    response = r.ok ? `Approval workflow triggered: ${JSON.stringify(r.data || {}).slice(0, 100)}` : 'Approval workflow unavailable.';
    delegated = true;
  } else if (/status|report|summary/i.test(lower)) {
    const queueDepth = taskQueue.length;
    const agentsUp = await Promise.allSettled(
      Object.keys(AGENTS).map(async (k) => {
        const r = await fetch(`${AGENTS[k].url}/health`).catch(() => null);
        return { name: k, up: !!r };
      })
    );
    const status = agentsUp.map(r => r.status === 'fulfilled' ? r.value : null).filter(Boolean);
    response = `Current status: ${status.filter(s => s.up).length}/${status.length} agents online. Queue: ${queueDepth} tasks. ${status.map(s => `${s.name}=${s.up ? '🟢' : '🔴'}`).join(' ')}`;
  } else if (/help|commands/i.test(lower)) {
    response = 'Charlie commands: "status" / "order [x]" / "post [content]" / "approve [deal]" / "delegate [task]"';
  }

  await reportToRobusca(`[Charlie] ${from || 'Tumelo'}: ${message.slice(0, 60)} → ${response.slice(0, 80)}`, { delegated });

  res.json({ response, delegated, from: 'charlie', ts: new Date().toISOString() });
});

// Get agent status
app.get('/api/agents/:name/status', async (req, res) => {
  const name = req.params.name.toLowerCase();
  if (!AGENTS[name]) return res.status(404).json({ error: 'Unknown agent' });
  try {
    const r = await fetch(`${AGENTS[name].url}/health`, { timeout: 5000 });
    const data = await r.json().catch(() => ({}));
    res.json({ name, status: r.ok ? 'up' : 'down', detail: data });
  } catch (e) {
    res.json({ name, status: 'unreachable', error: e.message });
  }
});

// Session management
app.post('/api/session/start', (req, res) => {
  const id = uuidv4();
  ACTIVE_SESSIONS.set(id, { started: new Date(), tasks: [] });
  res.json({ sessionId: id });
});

// ── WebSocket — Real-time updates ────────────────────────────────────────
const wss = new WebSocket.Server({ port: parseInt(process.env.WS_PORT || 3002) });
wss.on('connection', (ws, req) => {
  const id = uuidv4();
  logger.info(`🔗 WS client connected: ${id}`);
  ws.send(JSON.stringify({ type: 'connected', agent: 'charlie', id }));

  ws.on('message', async (raw) => {
    try {
      const msg = JSON.parse(raw);
      if (msg.type === 'dispatch') {
        const result = await delegateToAgent(msg.target, msg.task);
        ws.send(JSON.stringify({ type: 'result', taskId: msg.taskId, result }));
      }
    } catch (e) {
      ws.send(JSON.stringify({ type: 'error', message: e.message }));
    }
  });

  ws.on('close', () => logger.info(`🔌 WS client disconnected: ${id}`));
});

// ── Start ─────────────────────────────────────────────────────────────────
const PORT = parseInt(process.env.PORT) || 3001;
app.listen(PORT, '0.0.0.0', () => {
  logger.info(`
⚔️  ═══════════════════════════════════════
   Charlie Agent — LIVE ✅
   Port:  ${PORT}
   Node:  ${process.version}
   Parent: Robusca
   DB:    PostgreSQL 16
   ═══════════════════════════════════════`);
  logToDB('info', 'charlie', 'Charlie agent started', { port: PORT, version: '1.0.0' });
  reportToRobusca('Charlie agent started and ready for commands 🎯');
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM — shutting down gracefully');
  await db.end();
  process.exit(0);
});