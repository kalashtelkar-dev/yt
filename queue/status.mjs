import { Queue } from 'bullmq'; import { conn, QUEUE } from './lib.mjs';
const q = new Queue(QUEUE, { connection: conn });
console.log(await q.getJobCounts('waiting', 'active', 'completed', 'failed', 'delayed'));
for (const j of await q.getFailed()) console.log('failed', j.data.shot, j.failedReason?.slice(0, 120));
await q.close();
