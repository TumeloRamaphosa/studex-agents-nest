#!/usr/bin/env node
/**
 * Resolve credentials from the untracked /workspace/.env at RUNTIME.
 *
 * WHY THIS EXISTS
 * ---------------
 * On 2026-10-23 a credential scrub replaced live credential literals with the
 * text `${VAR_NAME}` across ~80 tracked files. That is a SHELL interpolation
 * idiom. In JavaScript it is just a string:
 *
 *     const KEY = '${AGENTMAIL_API_KEY}'  ->  KEY === "${AGENTMAIL_API_KEY}"
 *
 * JS only expands `${...}` inside a backtick template literal. The result is a
 * request that 401s, which the caller reports as "0 messages" / "0 posts" -
 * byte-identical to "nothing there". A false all-clear is worse than a loud
 * failure, because it is trusted.
 *
 * THE RULE
 * --------
 * A credential reference in tracked source must resolve to a real value in the
 * language it is written in:
 *
 *     Python    os.environ / scripts/cred_env.py (never a literal, never `${VAR}`)
 *     JS/TS     process.env.X, loaded from /workspace/.env
 *     shell     a sourced env file, or explicit substitution
 *
 * Secrets live in the UNTRACKED /workspace/.env. Tracked source names the
 * variable; it never contains the value. The remote is PUBLIC.
 *
 * WHAT THIS DOES NOT DO
 * ---------------------
 * It does not read a browser bundle. A key that reaches the browser reaches
 * everyone. Browser code must call a server-side proxy instead - see
 * `studex-lead-proxy/src/worker.js` (AgentMail) and the war-room server's
 * `/api/blotato/*` route (Blotato).
 *
 * Usage (CommonJS):
 *     const { requireEnv } = require('./scripts/cred_env.cjs');
 *     const KEY = requireEnv('AGENTMAIL_API_KEY');
 *
 * Usage (ESM):
 *     import { createRequire } from 'module';
 *     const require = createRequire(import.meta.url);
 *     const { requireEnv } = require('./scripts/cred_env.cjs');
 *
 * Or use the ESM wrapper directly:
 *     import { requireEnv } from './scripts/cred_env.mjs';
 */
'use strict';

const fs = require('fs');
const path = require('path');

// The single untracked env file for this workspace. It is gitignored
// (.gitignore: ".env"), so its contents never reach the public remote.
const ENV_FILE = process.env.STUDEX_ENV_FILE || '/workspace/.env';

/**
 * Parse a dotenv-style file.
 *
 * Note the `${...}` guard: a value that is still a `${VAR}` reference has NOT
 * been resolved. We treat it as absent so the caller fails loudly instead of
 * sending the placeholder text to a provider. This is the exact failure the
 * scrub created, and the exact failure this module exists to prevent.
 */
function parseEnvFile(file) {
  const out = {};
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (err) {
    if (err && err.code !== 'ENOENT') {
      process.stderr.write(`WARN: could not read ${file}: ${err.message}\n`);
    }
    return out;
  }
  for (const line of raw.split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith('#') || s.indexOf('=') === -1) continue;
    const idx = s.indexOf('=');
    const key = s.slice(0, idx).trim();
    let value = s.slice(idx + 1).trim();
    if (value.length >= 2 && value[0] === value[value.length - 1] &&
        (value[0] === '"' || value[0] === "'")) {
      value = value.slice(1, -1);
    }
    if (/^\$\{[A-Za-z_][A-Za-z_0-9]*\}$/.test(value)) continue; // unresolved
    if (key) out[key] = value;
  }
  return out;
}

/** Merged environment: the real OS environment first, then /workspace/.env. */
function loadEnv() {
  const env = Object.assign({}, process.env);
  const fromFile = parseEnvFile(ENV_FILE);
  for (const key of Object.keys(fromFile)) {
    // The OS environment wins: a live export beats a file.
    if (env[key] === undefined || env[key] === '') env[key] = fromFile[key];
  }
  return env;
}

/** Return the value of `name`, or `default` if it is not configured. */
function get(name, fallback) {
  const v = loadEnv()[name];
  if (v === undefined || v === null || v === '') return fallback;
  return v;
}

/**
 * Return the value of `name` or fail loudly.
 *
 * Failing loudly is the point. A missing credential must never become a
 * placeholder that a provider 401s on, because that reads as "empty".
 */
function requireEnv(name) {
  const v = get(name);
  if (v === undefined || v === null || v === '') {
    process.stderr.write(
      `FATAL: ${name} is not configured. Add it to ${ENV_FILE} (untracked). ` +
      `Refusing to run with a placeholder credential.\n`
    );
    process.exit(2);
  }
  return v;
}

module.exports = { ENV_FILE, loadEnv, get, requireEnv, parseEnvFile };

if (require.main === module) {
  // Print the NAMES that resolve, never the values.
  for (const k of Object.keys(loadEnv()).sort()) console.log(k);
}
