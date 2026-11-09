// node reel_redo.mjs R8  -> re-run only the clip step (keeps still and upscale), using the idea currently in reel.json
import fs from 'node:fs'; import { Queue } from 'bullmq'; import { conn } from './lib.mjs'; import { RQ } from './reel_worker.mjs';
const shot = process.argv[2], q = new Queue(RQ, { connection: conn }), old = await q.getJob(shot), cfg = JSON.parse(fs.readFileSync(new URL('./reel.json', import.meta.url))).find(s => s.shot === shot);
const ids = { ...(old?.data.ids || {}) }; delete ids.vid; if (old) await old.remove();
const f = new URL(`../ayodhya_film/reel/clips/${shot}.mp4`, import.meta.url).pathname; if (fs.existsSync(f)) fs.renameSync(f, f.replace('.mp4', '_old.mp4'));
await q.add('reel', { ...cfg, ids }, { jobId: shot, attempts: 3, backoff: { type: 'exponential', delay: 60000 } }); console.log('requeued', shot, Object.keys(ids)); await q.close();
