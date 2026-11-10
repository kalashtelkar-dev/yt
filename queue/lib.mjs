import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
let env = ''; try { env = fs.readFileSync(path.join(here, '../.env'), 'utf8'); } catch {} // on Railway the secrets are real env vars, no file
for (const l of env.split('\n')) { const m = l.match(/^\s*([A-Z_]+)\s*=\s*(.*)$/); if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, ''); }
// BASE_URL in .env is the MCP endpoint; the REST API lives at its origin.
export const API = new URL(process.env.BASE_URL).origin;
export const KEY = process.env.AUTH_KEY;
export const OUT = process.env.CLIPS_DIR || path.join(here, '../ayodhya_film/clips');
export const rurl = process.env.REDIS_URL || `redis://${process.env.REDIS_HOST || '127.0.0.1'}:${process.env.REDIS_PORT || 6379}`; // rediss:// for TLS (Upstash etc.)
const ru = new URL(rurl);
export const conn = { host: ru.hostname, port: +(ru.port || 6379), username: decodeURIComponent(ru.username) || undefined, password: decodeURIComponent(ru.password) || undefined, tls: ru.protocol === 'rediss:' ? {} : undefined, maxRetriesPerRequest: null };
export const QUEUE = 'i2v';
export async function api(method, p, body) {
  const r = await fetch(API + p, { method, headers: { Authorization: `Bearer ${KEY}`, 'content-type': 'application/json' }, body: body && JSON.stringify(body) });
  const t = await r.text(); let j;
  if (r.status === 403 && t.includes('account_paused')) { console.log(new Date().toISOString(), 'account paused by EngineX, waiting 5 min:', t.slice(0, 160)); await new Promise(x => setTimeout(x, 300000)); return api(method, p, body); } try { j = JSON.parse(t); } catch { throw new Error(`${method} ${p} -> ${r.status} non-JSON`); }
  if (!r.ok) throw new Error(`${method} ${p} -> ${r.status} ${t.slice(0, 200)}`);
  return j;
}
