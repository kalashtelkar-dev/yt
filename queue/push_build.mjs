// Run on the Mac (where the pipeline writes dhanushkodi_film/auto/): publishes the Build tab to Redis. `node push_build.mjs --watch` repeats every 15 s.
import fs from 'node:fs'; import { Queue } from 'bullmq'; import Redis from 'ioredis'; import { conn, rurl } from './lib.mjs';
const D = new URL('../dhanushkodi_film/', import.meta.url).pathname, A = D + 'auto/', r = new Redis(rurl), dq = new Queue('dhanu', { connection: conn }), oq = new Queue('ops', { connection: conn });
const rd = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return {}; } };
async function once() {
  const st = rd(A + 'stage.json'), passed = Object.values(rd(A + 'qa_state.json')).filter(v => v.pass).length, clips = fs.existsSync(D + 'clips') ? fs.readdirSync(D + 'clips').length : 0;
  const defs = [['voice_hi', 'Hindi voiceover', 'Sameer, checked line by line'], ['voice_en', 'English voiceover', 'Oliver, fitted to the Hindi timing'], ['visuals', 'Pictures and clips', clips + ' of 48 clips made, ' + passed + ' passed my checks'],
    ['cut', 'Cut to the voice', 'every shot starts on its spoken word'], ['cards', '25 cards and logo', 'timed to the words, in quiet corners'], ['mix', 'Hindi sound mix', 'shot-by-shot sounds, ducked music'], ['mix_en', 'English sound mix', 'same sounds, English voice'], ['package', 'YouTube package', 'titles, description, tags, subtitles, thumbnails']];
  let active = false; const stages = defs.map(([k, name, note]) => { const done = k in st; return { name, note, state: done ? 'done' : !active ? (active = true, 'active') : 'waiting', at: st[k] }; });
  let log = ''; try { log = fs.readFileSync(A + 'autopilot.log', 'utf8').trim().split('\n').slice(-14).join('\n'); } catch {}
  const [dc, oc] = await Promise.all([dq.getJobCounts('waiting', 'active', 'completed', 'failed'), oq.getJobCounts('waiting', 'active', 'completed', 'failed')]);
  await r.set('snap:build', JSON.stringify({ build: { stages, done: stages.filter(x => x.state == 'done').length, log, queues: `generation queue: ${dc.active} running, ${dc.waiting} waiting, ${dc.completed} done · ops queue: ${oc.active} running, ${oc.waiting} waiting` } }));
}
do { await once().catch(e => console.log(e.message)); if (process.argv[2] === '--watch') await new Promise(x => setTimeout(x, 15000)); } while (process.argv[2] === '--watch');
process.exit(0);
