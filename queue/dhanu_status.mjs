import { Queue } from 'bullmq'; import { conn } from './lib.mjs'; import { DQ } from './dhanu_worker.mjs';
const q = new Queue(DQ, { connection: conn }); console.log(await q.getJobCounts('waiting', 'active', 'completed', 'failed', 'delayed'));
if (process.argv[2] === 'retry') { let n = 0; for (const j of await q.getFailed()) { await j.retry(); n++; } console.log('retried', n); }
await q.close(); process.exit(0);
