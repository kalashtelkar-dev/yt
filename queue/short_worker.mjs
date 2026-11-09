// 9:16 reel pipeline per shot: still (Imagine-Ultra 864x1536) -> upscale x2 -> image-to-video. Resumable: step job ids are saved on the queue job.
import fs from 'node:fs'; import path from 'node:path'; import { Worker, Queue } from 'bullmq'; import { api, conn } from './lib.mjs';
export const RQ = 'dshort';
const OUT = path.join(path.dirname(new URL(import.meta.url).pathname), '../dwarka_short');
const POLL = +(process.env.POLL_MS || 30000), sleep = ms => new Promise(r => setTimeout(r, ms));
for (const d of ['stills', 'up', 'clips']) fs.mkdirSync(path.join(OUT, d), { recursive: true });
async function step(job, name, workflow, values, ext, dir) {
  const file = path.join(OUT, dir, `${job.data.shot}.${ext}`);
  const ids = job.data.ids || {};
  if (ids[name]?.done && fs.existsSync(file)) return ids[name].key;
  if (!ids[name]?.id) { ids[name] = { id: (await api('POST', '/v1/generate/run', { workflow, values })).id }; await job.updateData({ ...job.data, ids }); }
  for (const t0 = Date.now(); Date.now() - t0 < 40 * 60000; await sleep(POLL)) {
    const j = await api('GET', `/v1/generate/jobs/${ids[name].id}`);
    if (j.status === 'failed' || j.status === 'cancelled' || j.status === 'canceled') { delete ids[name]; await job.updateData({ ...job.data, ids }); throw new Error(`${job.data.shot} ${name} ${j.status}: ${JSON.stringify(j.error)}`); }
    if (j.status === 'succeeded') {
      const d = j.downloads[0], buf = Buffer.from(await (await fetch(d.url)).arrayBuffer());
      if (buf.length < 5000) throw new Error(`${job.data.shot} ${name} download too small`);
      fs.writeFileSync(file + '.part', buf); fs.renameSync(file + '.part', file);
      ids[name] = { ...ids[name], done: true, key: d.key }; await job.updateData({ ...job.data, ids }); return d.key;
    }
  }
  throw new Error(`${job.data.shot} ${name} timed out`);
}
if (process.argv[1].endsWith('short_worker.mjs')) {
  new Worker(RQ, async job => {
    const { shot, prompt, idea } = job.data;
    const still = await step(job, 'still', 'Imagine-Ultra', { prompt, width: 864, height: 1536 }, 'png', 'stills'); await job.updateProgress(33);
    const up = await step(job, 'up', 'upscale_image', { image: still, resize_type_multiplier: 2, format: 'jpeg' }, 'jpg', 'up'); await job.updateProgress(66);
    await step(job, 'vid', 'first-image2video', { image: up, idea, float_duration: 5 }, 'mp4', 'clips'); await job.updateProgress(100);
    return shot;
  }, { connection: conn, concurrency: +(process.env.CONCURRENCY || 4) })
    .on('completed', j => console.log(new Date().toISOString(), 'done', j.data.shot))
    .on('failed', (j, e) => console.log(new Date().toISOString(), 'FAIL', j?.data.shot, e.message));
  console.log('dwarka short worker up');
}
