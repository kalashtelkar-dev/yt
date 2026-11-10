// Padmanabhaswamy still runs on the Mac (its queue lives in LOCAL Redis). This mirrors it to the web UI:
// status -> cloud Redis (snap:padma), new clips/stills -> private Blob (pn/clips, pn/stills). `node push_padma.mjs --watch` repeats every 20 s.
import fs from 'node:fs'; import { Queue } from 'bullmq'; import Redis from 'ioredis'; import { rurl } from './lib.mjs'; import { toBlob, blobSet } from './blob.mjs';
const PF = new URL('../padmanabhaswamy_film/', import.meta.url).pathname, local = { host: '127.0.0.1', port: 6379, maxRetriesPerRequest: null }, cloud = new Redis(rurl);
const lq = new Queue('padma', { connection: local }), oq = new Queue('ops', { connection: local }), rdj = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return {}; } }, ex = f => fs.existsSync(PF + f);
const have = await blobSet('pn/');
async function once() {
  const raw = rdj(PF + 'auto/shots.json'), shots = (Array.isArray(raw) ? raw : []).map(s => ({ ...s, clip: ex(`clips/${s.id}.mp4`) || s.type === 'real footage', still: ex(`stills/${s.id}.png`), fx: ex(`graded/${s.id}.mp4`) }));
  for (const [d, ext] of [['clips', 'mp4'], ['stills', 'png']]) for (const f of ex(d) ? fs.readdirSync(PF + d) : []) { const key = `pn/${d}/${f}`; if (f.endsWith('.' + ext) && !have.has(key)) { await toBlob(PF + d + '/' + f, key); have.add(key); console.log('up', key); } }
  const gq = await lq.getJobCounts('waiting', 'active', 'completed', 'failed'), ops = await oq.getJobCounts('waiting', 'active', 'completed', 'failed');
  let log = ''; try { log = fs.readFileSync(PF + 'auto/autopilot.log', 'utf8').trim().split('\n').slice(-16).join('\n'); } catch {}
  await cloud.set('snap:padma', JSON.stringify({ shots, st: rdj(PF + 'auto/stage.json'), log, gq, oq: ops, texts: ex('cards') ? fs.readdirSync(PF + 'cards').filter(f => f.endsWith('.webm')).length : 0, finals: [], voice: ex('voiceover_master_sameer.mp3') })); // finals stay local (large)
}
do { await once().catch(e => console.log(new Date().toISOString(), e.message)); if (process.argv[2] === '--watch') await new Promise(x => setTimeout(x, 20000)); } while (process.argv[2] === '--watch');
process.exit(0);
