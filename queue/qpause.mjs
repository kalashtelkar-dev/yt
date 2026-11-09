// node qpause.mjs pause|resume  -> pauses or resumes the generation queue (dwarka, reel) and the ops queue
import { Queue } from 'bullmq'; import { conn } from './lib.mjs';
for (const n of ['dwarka', 'reel', 'ops']) { const q = new Queue(n, { connection: conn }); await (process.argv[2] === 'resume' ? q.resume() : q.pause()); console.log(n, process.argv[2] === 'resume' ? 'resumed' : 'paused', JSON.stringify(await q.getJobCounts('waiting', 'active'))); await q.close(); }
process.exit(0);
