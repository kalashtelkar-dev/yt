import { same, mint, redis } from './_lib.mjs';
export default async function (req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'x', k = 'rl:' + ip, n = await redis().incr(k); if (n === 1) await redis().expire(k, 900);
  if (n > 10) return res.status(429).json({ error: 'too many tries, wait 15 minutes' }); // 10 wrong passwords per IP per 15 min
  let pw = req.body?.password; if (typeof pw !== 'string') pw = '';
  if (!process.env.UI_PASSWORD || !same(pw, process.env.UI_PASSWORD)) return res.status(401).json({ error: 'wrong password' });
  res.setHeader('set-cookie', `s=${mint()}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${7 * 86400}`); res.json({ ok: true });
}
