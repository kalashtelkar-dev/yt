import { guard, redis } from './_lib.mjs';
export default async function (req, res) {
  if (!guard(req, res)) return;
  const k = req.query.k; if (!['dhanu', 'dhshort', 'build'].includes(k)) return res.status(404).end();
  res.setHeader('cache-control', 'no-store'); res.setHeader('content-type', 'application/json');
  res.end(await redis().get('snap:' + k) || (k === 'build' ? '{"build":{"stages":[],"done":0,"log":"","queues":"no data yet"}}' : '{"jobs":[],"conc":1,"avg":420}'));
}
