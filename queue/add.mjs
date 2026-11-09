// node add.mjs shots.json [N]   shots.json = [{shot, image, idea, jobId?}]; adds the first N not already queued (default all)
import fs from 'node:fs'; import { Queue } from 'bullmq'; import { conn, QUEUE, OUT } from './lib.mjs';
const [file, n] = process.argv.slice(2), q = new Queue(QUEUE, { connection: conn });
let left = n ? +n : Infinity, added = 0;
for (const s of JSON.parse(fs.readFileSync(file, 'utf8'))) {
  if (!left) break;
  if (fs.existsSync(`${OUT}/${s.shot}.mp4`) || await q.getJob(s.shot)) continue;
  await q.add('i2v', s, { jobId: s.shot, attempts: 3, backoff: { type: 'exponential', delay: 60000 }, removeOnComplete: false }); added++; left--; console.log('queued', s.shot);
}
console.log('added', added); await q.close();
