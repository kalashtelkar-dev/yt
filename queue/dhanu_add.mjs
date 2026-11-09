// node dwarka_add.mjs [N]  adds the first N shots from dhanu.json that are not queued yet, in film order (default all)
import fs from 'node:fs'; import { Queue } from 'bullmq'; import { conn } from './lib.mjs'; import { DQ } from './dhanu_worker.mjs';
const q = new Queue(DQ, { connection: conn }); let left = +(process.argv[2] || 1e9), n = 0;
for (const s of JSON.parse(fs.readFileSync(new URL('./dhanu.json', import.meta.url)))) { if (!left) break; if (await q.getJob(s.shot)) continue;
  await q.add('dhanu', s, { jobId: s.shot, attempts: 3, backoff: { type: 'exponential', delay: 60000 } }); left--; n++; console.log('queued', s.shot); }
console.log('added', n); await q.close();
