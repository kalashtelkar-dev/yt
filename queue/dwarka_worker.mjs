// Dwarka 16:9 pipeline, ONE shot at a time by default: [real photo -> clean edit] or [painted still] -> upscale x2 -> image-to-video.
// Resumable: every step id is saved on the queue job, finished files are never redone.
import fs from 'node:fs'; import path from 'node:path'; import { Worker } from 'bullmq'; import { api, conn, API, KEY } from './lib.mjs';
export const DQ = 'dwarka';
const OUT = path.join(path.dirname(new URL(import.meta.url).pathname), '../dwarka_film');
const POLL = +(process.env.POLL_MS || 30000), sleep = ms => new Promise(r => setTimeout(r, ms));
for (const d of ['stills', 'up', 'clips', 'photos']) fs.mkdirSync(path.join(OUT, d), { recursive: true });
async function upload(file) {
  const buf = fs.readFileSync(file), u = await api('POST', '/v1/uploads', { filename: path.basename(file) });
  const r = await fetch(u.url, { method: 'PUT', body: buf, headers: { 'content-type': 'image/jpeg' } }); if (!r.ok) throw new Error('upload PUT ' + r.status);
  await api('POST', '/v1/uploads/complete', { key: u.key, filename: path.basename(file), bytes: buf.length }); return u.key;
}
async function step(job, name, run, ext, dir) {
  const file = path.join(OUT, dir, `${job.data.shot}.${ext}`), ids = job.data.ids || {};
  if (ids[name]?.done && fs.existsSync(file)) return ids[name].key;
  if (!ids[name]?.id) { ids[name] = { id: (await run()).id }; await job.updateData({ ...job.data, ids }); }
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
const gen = (workflow, values) => () => api('POST', '/v1/generate/run', { workflow, values });
if (process.argv[1].endsWith('dwarka_worker.mjs')) {
  new Worker(DQ, async job => {
    const { shot, prompt, idea, photo, edit } = job.data; let still;
    if (photo) { // real photo: upload, then clean it with image_editing
      const ids = job.data.ids || {}; if (!ids.up0?.key) { const key = await upload(photo); ids.up0 = { key, done: true }; await job.updateData({ ...job.data, ids }); }
      still = await step(job, 'still', gen('image_editing', { prompt: edit, image_1: job.data.ids.up0.key, format: 'jpeg' }), 'jpg', 'stills');
    } else still = await step(job, 'still', gen('Imagine-Ultra', { prompt, width: 1536, height: 864 }), 'png', 'stills');
    await job.updateProgress(33);
    const up = await step(job, 'up', gen('upscale_image', { image: still, resize_type_multiplier: 2, format: 'jpeg' }), 'jpg', 'up'); await job.updateProgress(66);
    await step(job, 'vid', gen('first-image2video', { image: up, idea, float_duration: 5 }), 'mp4', 'clips'); await job.updateProgress(100);
    return shot;
  }, { connection: conn, concurrency: +(process.env.CONCURRENCY || 1) })
    .on('completed', j => console.log(new Date().toISOString(), 'done', j.data.shot))
    .on('failed', (j, e) => console.log(new Date().toISOString(), 'FAIL', j?.data.shot, e.message));
  console.log('dwarka worker up, concurrency', process.env.CONCURRENCY || 1);
}
