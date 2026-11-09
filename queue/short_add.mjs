// node reel_add.mjs [N]  queues the first N reel shots from short.json not yet queued (default all)
import fs from 'node:fs'; import { Queue } from 'bullmq'; import { conn } from './lib.mjs'; import { RQ } from './short_worker.mjs';
const q = new Queue(RQ, { connection: conn }); let left = +(process.argv[2] || 1e9), n = 0;
for (const s of JSON.parse(fs.readFileSync(new URL('./short.json', import.meta.url)))) { if (!left) break; if (await q.getJob(s.shot)) continue;
  await q.add('dshort', s, { jobId: s.shot, attempts: 3, backoff: { type: 'exponential', delay: 60000 } }); left--; n++; console.log('queued', s.shot); }
console.log('added', n); await q.close();
