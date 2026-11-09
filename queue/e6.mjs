import { Queue } from 'bullmq'; import { conn, api } from './lib.mjs'; import { DQ } from './dwarka_worker.mjs';
const q = new Queue(DQ, { connection: conn }), j = await q.getJob('E6'); console.log(await j.getState(), JSON.stringify(j.data.ids));
const id = j.data.ids?.vid?.id; if (id) { const r = await api('GET', '/v1/generate/jobs/' + id); console.log(r.status, JSON.stringify(r.progress), r.queuePosition, JSON.stringify(r.error), JSON.stringify(r.timings)); }
await q.close(); process.exit(0);
