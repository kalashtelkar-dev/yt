// Runs forever: takes jobs from Redis, submits to EngineX, polls, downloads mp4. Uses no Claude credits.
import fs from 'node:fs'; import path from 'node:path';
import { Worker } from 'bullmq'; import { api, conn, QUEUE, OUT } from './lib.mjs';
const POLL_MS = +(process.env.POLL_MS || 30000), MAX_WAIT_MS = 30 * 60000;
const sleep = ms => new Promise(r => setTimeout(r, ms));
fs.mkdirSync(OUT, { recursive: true });
new Worker(QUEUE, async job => {
  const { shot, image, idea, jobId: existing } = job.data, file = path.join(OUT, `${shot}.mp4`);
  if (fs.existsSync(file)) return 'already downloaded';
  let id = existing || job.data.submitted;
  if (!id) { // persist the id so a retry never double-submits
    id = (await api('POST', '/v1/generate/run', { workflow: 'first-image2video', values: { image, idea, float_duration: 5 } })).id;
    await job.updateData({ ...job.data, submitted: id });
  }
  for (const t0 = Date.now(); Date.now() - t0 < MAX_WAIT_MS; await sleep(POLL_MS)) {
    const j = await api('GET', `/v1/generate/jobs/${id}`);
    await job.updateProgress(j.progress?.percent ?? 0);
    if (j.status === 'failed' || j.status === 'cancelled') { await job.updateData({ ...job.data, submitted: null }); throw new Error(`${shot} ${id} ${j.status}: ${JSON.stringify(j.error)}`); }
    if (j.status === 'succeeded') {
      const d = j.downloads.find(x => x.kind === 'video'); if (!d) throw new Error(`${shot} no video output`);
      const buf = Buffer.from(await (await fetch(d.url)).arrayBuffer());
      if (buf.length < 10000) throw new Error(`${shot} download too small`);
      fs.writeFileSync(file + '.part', buf); fs.renameSync(file + '.part', file);
      return `${shot} ${id} ${buf.length} bytes`;
    }
  }
  throw new Error(`${shot} ${id} timed out`);
}, { connection: conn, concurrency: +(process.env.CONCURRENCY || 4), lockDuration: 120000 })
  .on('completed', (j, r) => console.log(new Date().toISOString(), 'done', r))
  .on('failed', (j, e) => console.log(new Date().toISOString(), 'FAIL', j?.data.shot, `(attempt ${j?.attemptsMade})`, e.message));
console.log('worker up, concurrency', process.env.CONCURRENCY || 4);

