// Runs next to the workers. Every 30 s (PUBLISH_MS; keeps Redis command count low) it writes what the web UI shows into Redis (snap:dhanu, snap:dhshort). "Done" = the clip is in Blob.
import fs from 'node:fs'; import { Queue } from 'bullmq'; import Redis from 'ioredis'; import { conn, rurl } from './lib.mjs'; import { blobSet } from './blob.mjs';
const FILMS = { dhanu: { conc: 1, avg: 420 }, dhshort: { conc: +(process.env.CONCURRENCY || 4), avg: 480 } };
const r = new Redis(rurl), qs = Object.fromEntries(Object.keys(FILMS).map(k => [k, new Queue(k, { connection: conn })]));
let files = new Set(), at = 0;
async function film(k) {
  const order = JSON.parse(fs.readFileSync(new URL(`./${k}.json`, import.meta.url))).map(s => s.shot), now = Date.now(), by = {};
  for (const j of await qs[k].getJobs(['waiting', 'active', 'delayed', 'failed', 'completed'], 0, 200)) by[j.data.shot] = [j, await j.getState()];
  const jobs = order.map(sh => { const [j, st] = by[sh] || [], ids = j?.data.ids || {}, ext = files.has(`${k}/stills/${sh}.jpg`) ? 'jpg' : 'png', clip = files.has(`${k}/clips/${sh}.mp4`), still = files.has(`${k}/stills/${sh}.${ext}`);
    return { shot: sh, state: clip || st === 'completed' ? 'done' : !st || st === 'delayed' ? 'waiting' : st, still, ext, step: clip ? 'clip' : ids.up?.done || ids.vid?.id ? 'clip generating' : ids.still?.done ? 'upscaling' : j?.data.photo ? 'cleaning photo' : 'still generating',
      age: st === 'active' && j.processedOn ? (now - j.processedOn) / 1000 : 0, err: st === 'failed' ? (j.failedReason || '').slice(0, 90) : '' }; });
  await r.set('snap:' + k, JSON.stringify({ jobs, ...FILMS[k], at: now }));
}
for (;;) {
  try { if (Date.now() - at > 30000) { files = await blobSet(''); at = Date.now(); } for (const k in FILMS) await film(k); } catch (e) { console.log(new Date().toISOString(), 'publish error', e.message); }
  await new Promise(x => setTimeout(x, +(process.env.PUBLISH_MS || 30000)));
}
