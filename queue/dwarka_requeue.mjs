// node dwarka_requeue.mjs A4 B9 ...  -> removes those waiting jobs and re-adds them from dwarka.json (new prompts)
import fs from 'node:fs'; import { Queue } from 'bullmq'; import { conn } from './lib.mjs'; import { DQ } from './dwarka_worker.mjs';
const q = new Queue(DQ, { connection: conn }), cfg = JSON.parse(fs.readFileSync(new URL('./dwarka.json', import.meta.url)));
for (const id of process.argv.slice(2)) { const j = await q.getJob(id); if (j) { if ((await j.getState()) === 'active') { console.log('skip active', id); continue; } await j.remove(); }
  await q.add('dwarka', cfg.find(s => s.shot === id), { jobId: id, attempts: 3, backoff: { type: 'exponential', delay: 60000 } }); console.log('requeued', id); }
await q.close();
