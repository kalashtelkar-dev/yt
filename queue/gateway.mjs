// Every non-generation EngineX call (voice, transcription, OCR, motion graphics, trims, ...) goes through here: BullMQ queue "ops", 2 at a time.
// Generation (images, upscale, video) goes through the "dwarka"/"reel" queues, 1 at a time. Nothing talks to EngineX directly.
// POST http://127.0.0.1:3940/run {path, body} -> waits in the queue, runs, returns the finished EngineX job.
import http from 'node:http'; import { Queue, Worker, QueueEvents } from 'bullmq'; import { api, conn } from './lib.mjs';
const sleep = ms => new Promise(r => setTimeout(r, ms)), name = 'ops', q = new Queue(name, { connection: conn }), ev = new QueueEvents(name, { connection: conn });
new Worker(name, async job => {
  const { path, body } = job.data, sub = await api('POST', path, body), id = sub.id; if (!id) return sub;
  for (const t0 = Date.now(); Date.now() - t0 < 3600e3; await sleep(3000)) { const j = await api('GET', '/v1/jobs/' + id); if (['succeeded', 'failed', 'cancelled', 'canceled'].includes(j.status)) return j; }
  throw new Error('timeout ' + id);
}, { connection: conn, concurrency: +(process.env.OPS_CONCURRENCY || 2), lockDuration: 120000 }).on('failed', (j, e) => console.log(new Date().toISOString(), 'ops FAIL', j?.data.path, e.message));
http.createServer(async (req, res) => {
  if (req.method === 'GET') { res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify(await q.getJobCounts('waiting', 'active', 'completed', 'failed'))); }
  let b = ''; for await (const c of req) b += c;
  try { const { path, body } = JSON.parse(b), job = await q.add('op', { path, body }, { attempts: 3, backoff: { type: 'exponential', delay: 20000 }, removeOnComplete: { age: 3600 }, removeOnFail: { age: 86400 } });
    const out = await job.waitUntilFinished(ev, 3700e3); res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(out)); }
  catch (e) { res.statusCode = 500; res.end(JSON.stringify({ error: String(e.message || e) })); }
}).listen(3940, '127.0.0.1', () => console.log('gateway up: ops queue, concurrency', process.env.OPS_CONCURRENCY || 2));
