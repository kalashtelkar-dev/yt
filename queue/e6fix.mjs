import fs from 'node:fs'; import { Queue } from 'bullmq'; import { conn } from './lib.mjs'; import { DQ } from './dwarka_worker.mjs';
const q = new Queue(DQ, { connection: conn }), j = await q.getJob('E6'), data = { ...j.data, ids: { still: j.data.ids.still, up: j.data.ids.up } };
await j.remove().catch(() => {}); await q.add('dwarka', data, { jobId: 'E6', attempts: 3, backoff: { type: 'exponential', delay: 60000 } }); console.log('E6 requeued, video step reset'); await q.close(); process.exit(0);
