import { Queue } from 'bullmq'; import { conn, api } from './lib.mjs';
const q = new Queue('dshort', { connection: conn });
console.log(await q.getJobCounts('waiting', 'active', 'completed', 'failed'));
for (const id of ['H6', 'H5', 'H7', 'H8']) { const j = await q.getJob(id); console.log(id, await j.getState(), JSON.stringify(Object.fromEntries(Object.entries(j.data.ids || {}).map(([k, v]) => [k, (v.id || '').slice(0, 8) + (v.done ? ' done' : '')])))); }
const j = await q.getJob('H6'); for (const [k, v] of Object.entries(j.data.ids || {})) { if (v.id) { const r = await api('GET', '/v1/generate/jobs/' + v.id); console.log('H6', k, v.id.slice(0, 8), r.status); } }
await q.close(); process.exit(0);
