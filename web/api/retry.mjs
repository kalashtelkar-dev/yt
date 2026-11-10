import { Queue } from 'bullmq'; import { guard } from './_lib.mjs';
export default async function (req, res) {
  if (req.method !== 'POST' || !guard(req, res)) return req.method !== 'POST' && res.status(405).end();
  const k = req.query.k; if (!['dhanu', 'dhshort'].includes(k)) return res.status(404).end();
  const u = new URL(process.env.REDIS_URL), q = new Queue(k, { connection: { host: u.hostname, port: +(u.port || 6379), username: decodeURIComponent(u.username) || undefined, password: decodeURIComponent(u.password), tls: u.protocol === 'rediss:' ? {} : undefined } });
  try { await q.retryJobs({ state: 'failed' }); res.end('ok'); } finally { await q.close(); }
}
