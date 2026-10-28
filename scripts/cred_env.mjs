/**
 * ESM wrapper around scripts/cred_env.cjs.
 *
 * ESM callers cannot `require()` a .cjs file by path without the
 * createRequire dance, so this re-exports the same API in a form an ESM
 * module can import directly:
 *
 *     import { requireEnv } from './scripts/cred_env.mjs';
 *     const KEY = requireEnv('AGENTMAIL_API_KEY');
 *
 * See scripts/cred_env.cjs for the full rationale.
 */
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mod = require('./cred_env.cjs');

export const ENV_FILE = mod.ENV_FILE;
export const loadEnv = mod.loadEnv;
export const get = mod.get;
export const requireEnv = mod.requireEnv;
export const parseEnvFile = mod.parseEnvFile;

export default mod;
