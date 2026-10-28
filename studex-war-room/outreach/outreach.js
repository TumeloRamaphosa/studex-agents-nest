#!/usr/bin/env node
/**
 * Studex Outreach Engine
 * Usage: node outreach.js <command> [args]
 * 
 * Commands:
 *   node outreach.js list [wedding|cafe]        — list contacts
 *   node outreach.js message <id> <first|followup|closing>  — generate WhatsApp message
 *   node outreach.js send <id> <first|followup|closing>      — mark as sent + log
 *   node outreach.js status <id>                — show contact status
 *   node outreach.js update <id> <field> <value> — update contact (e.g. status, contact)
 *   node outreach.js report                    — daily outreach report
 *   node outreach.js today                     — outreach plan for today
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DATA_FILE = path.join(__dirname, 'contacts.json');
const LOG_FILE = path.join(__dirname, 'outreach-log.json');

function loadContacts() {
  return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
}

function saveContacts(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

function loadLog() {
  if (!fs.existsSync(LOG_FILE)) return [];
  return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
}

function saveLog(log) {
  fs.writeFileSync(LOG_FILE, JSON.stringify(log, null, 2));
}

function logActivity(id, type, message) {
  const log = loadLog();
  log.push({
    id,
    type,
    message: message.substring(0, 200),
    timestamp: new Date().toISOString(),
    date: new Date().toLocaleDateString('en-ZA', { timeZone: 'Africa/Johannesburg' })
  });
  saveLog(log);
}

function allContacts(data) {
  return [
    ...data.wedding.map(c => ({ ...c, category: 'wedding' })),
    ...data.cafes.map(c => ({ ...c, category: 'cafe' }))
  ];
}

// ─── LIST ───────────────────────────────────────────────────────────────────
function list(category) {
  const data = loadContacts();
  if (category === 'wedding') {
    console.log('\n🟡 WEDDING CATERERS\n');
    data.wedding.forEach(c => {
      console.log(`  [${c.id}] ${c.name} (${c.location})`);
      console.log(`       Status: ${c.status || 'pending'} | Contact: ${c.contact || 'NOT SET'}`);
      console.log(`       Angle:  ${c.angle}`);
      console.log();
    });
  } else if (category === 'cafe') {
    console.log('\n☕ CT CAFÉS\n');
    data.cafes.forEach(c => {
      console.log(`  [${c.id}] ${c.name} (${c.location})`);
      console.log(`       Status: ${c.status || 'pending'} | Contact: ${c.contact || 'NOT SET'}`);
      console.log(`       Notes:  ${c.notes}`);
      console.log();
    });
  } else {
    console.log('\n📋 ALL CONTACTS\n');
    allContacts(data).forEach(c => {
      console.log(`  [${c.id}] ${c.name} (${c.category}) — ${c.status || 'pending'}`);
    });
  }
}

// ─── MESSAGE ────────────────────────────────────────────────────────────────
function getMessage(id, type) {
  const data = loadContacts();
  const all = allContacts(data);
  const contact = all.find(c => c.id === id);
  if (!contact) { console.error('❌ Contact not found:', id); process.exit(1); }

  const msg = contact.messages[type];
  if (!msg) { console.error('❌ Unknown message type:', type); process.exit(1); }

  const filled = msg
    .replace(/\[Caterer Name\]/g, contact.name)
    .replace(/\[Name\]/g, contact.name.split(' ')[0]);

  console.log('\n──────────────────────────────────────────');
  console.log(`📱 ${contact.name.toUpperCase()} — ${type.toUpperCase()}`);
  console.log('──────────────────────────────────────────\n');
  console.log(filled);
  console.log('\n──────────────────────────────────────────\n');
  console.log('💡 Copy the message above and send via WhatsApp\n');

  return { contact, type, message: filled };
}

// ─── SEND ───────────────────────────────────────────────────────────────────
function markSent(id, type) {
  const data = loadContacts();
  const categories = ['wedding', 'cafes'];
  let found = false;

  for (const cat of categories) {
    const idx = data[cat].findIndex(c => c.id === id);
    if (idx !== -1) {
      data[cat][idx].status = 'sent';
      data[cat][idx].lastSent = new Date().toISOString();
      data[cat][idx].lastMessage = type;
      found = true;
      break;
    }
  }

  if (!found) { console.error('❌ Contact not found'); process.exit(1); }

  saveContacts(data);
  const { message } = getMessage(id, type);
  logActivity(id, type, message);
  console.log('✅ Marked as sent and logged.');
}

// ─── STATUS ─────────────────────────────────────────────────────────────────
function status(id) {
  const data = loadContacts();
  const all = allContacts(data);
  const contact = all.find(c => c.id === id);
  if (!contact) { console.error('❌ Contact not found'); process.exit(1); }

  console.log(`\n📊 ${contact.name}`);
  console.log(`   Category:  ${contact.category}`);
  console.log(`   Location:  ${contact.location}`);
  console.log(`   Status:    ${contact.status || 'pending'}`);
  console.log(`   Contact:   ${contact.contact || 'NOT SET'}`);
  console.log(`   Last sent: ${contact.lastSent || 'never'}`);
  console.log(`   Last msg:  ${contact.lastMessage || 'none'}`);
  console.log(`   Angle:     ${contact.angle || contact.notes}`);
}

// ─── UPDATE ─────────────────────────────────────────────────────────────────
function update(id, field, value) {
  const data = loadContacts();
  const categories = ['wedding', 'cafes'];
  let found = false;

  for (const cat of categories) {
    const idx = data[cat].findIndex(c => c.id === id);
    if (idx !== -1) {
      data[cat][idx][field] = value;
      found = true;
      console.log(`✅ Updated [${cat}] ${data[cat][idx].name}.${field} = "${value}"`);
      break;
    }
  }

  if (!found) { console.error('❌ Contact not found'); process.exit(1); }
  saveContacts(data);
}

// ─── REPORT ─────────────────────────────────────────────────────────────────
function report() {
  const data = loadContacts();
  const log = loadLog();
  const today = new Date().toLocaleDateString('en-ZA', { timeZone: 'Africa/Johannesburg' });
  const todayLog = log.filter(l => l.date === today);

  console.log('\n📊 OUTREACH REPORT —', today);
  console.log('─'.repeat(40));

  const all = allContacts(data);
  const pending = all.filter(c => !c.status || c.status === 'pending');
  const sent = all.filter(c => c.status === 'sent' || c.status === 'replied');
  const replied = all.filter(c => c.status === 'replied');

  console.log(`   Total contacts:  ${all.length}`);
  console.log(`   Pending:        ${pending.length}`);
  console.log(`   Sent:           ${sent.length}`);
  console.log(`   Replied:       ${replied.length}`);
  console.log(`   Today's sends:  ${todayLog.length}`);

  console.log('\n🟡 PENDING (not yet contacted):');
  pending.forEach(c => console.log(`   • ${c.name} (${c.category})`));

  if (replied.length > 0) {
    console.log('\n🟢 REPLIED:');
    replied.forEach(c => console.log(`   • ${c.name}`));
  }

  if (todayLog.length > 0) {
    console.log('\n📅 TODAY\'S ACTIVITY:');
    todayLog.forEach(l => console.log(`   [${l.timestamp.split('T')[1].substring(0,5)}] ${l.id} — ${l.type}`));
  }
}

// ─── TODAY ──────────────────────────────────────────────────────────────────
function today() {
  const data = loadContacts();
  const all = allContacts(data);
  const pending = all.filter(c => !c.status || c.status === 'pending' || c.status === 'overdue');

  console.log('\n🎯 TODAY\'S OUTREACH PLAN');
  console.log('═'.repeat(40));
  console.log(`\nFocus: Wedding Caterers (wedding season = NOW) + CT Cafés\n`);

  console.log('🟡 WEDDING CATERERS TO CONTACT TODAY:');
  data.wedding.filter(c => !c.status || c.status === 'pending').forEach(c => {
    console.log(`\n  ✦ ${c.name} (${c.location})`);
    console.log(`    Angle: ${c.angle}`);
    console.log(`    → node outreach.js message ${c.id} first`);
  });

  console.log('\n\n☕ CAFÉS TO CONTACT TODAY:');
  data.cafes.filter(c => !c.status || c.status === 'pending').slice(0,3).forEach(c => {
    console.log(`\n  ✦ ${c.name} (${c.location})`);
    console.log(`    → node outreach.js message ${c.id} first`);
  });

  console.log('\n\n📋 WORKFLOW:');
  console.log('  1. node outreach.js message <id> first   ← generate message');
  console.log('  2. Copy message → send via WhatsApp');
  console.log('  3. node outreach.js send <id> first     ← log it');
  console.log('  4. node outreach.js status <id>         ← verify');
  console.log('\n');
}

// ─── MAIN ───────────────────────────────────────────────────────────────────
const [,, cmd, arg1, arg2, arg3] = process.argv;

if (!cmd) { today(); process.exit(0); }

switch (cmd) {
  case 'list':    list(arg1); break;
  case 'message': getMessage(arg1, arg2); break;
  case 'send':    markSent(arg1, arg2); break;
  case 'status':  status(arg1); break;
  case 'update':  update(arg1, arg2, arg3); break;
  case 'report':  report(); break;
  case 'today':   today(); break;
  default:
    console.log('Unknown command:', cmd);
    console.log('Run: node outreach.js today');
}
