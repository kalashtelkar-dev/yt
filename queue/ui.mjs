// node ui.mjs  ->  http://localhost:3939  (local only)
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
import { Queue } from 'bullmq'; import { conn, QUEUE, OUT } from './lib.mjs';
const REEL = new URL('../ayodhya_film/reel/', import.meta.url).pathname;
const rq = new Queue('reel', { connection: conn }), sq = new Queue('dshort', { connection: conn }); const SHORT = new URL('../dwarka_film/dwarka_short/', import.meta.url).pathname; const DWH = new URL('../dhanushkodi_film/', import.meta.url).pathname, dhq = new Queue('dhanu', { connection: conn });
const DW = new URL('../dwarka_film/', import.meta.url).pathname, dq = new Queue('dwarka', { connection: conn });
const q = new Queue(QUEUE, { connection: conn }), CONC = +(process.env.CONCURRENCY || 4);
const order = () => JSON.parse(fs.readFileSync(new URL('./shots.json', import.meta.url))).map(s => s.shot);
const page = `<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Clip queue</title>
<style>
:root{--bg:#120e0b;--card:#1d1611;--line:#33281f;--tx:#f4eadb;--mut:#a39482;--gold:#e8b64a;--ok:#62c07a;--bad:#e5604a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.4 system-ui,-apple-system,sans-serif}
header{position:sticky;top:0;z-index:5;background:rgba(18,14,11,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:16px 28px}
.top{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap}h1{margin:0;font-size:22px}.sub{color:var(--mut)}
.pct{margin-left:auto;font-size:30px;font-weight:700;color:var(--gold)}
#bar{height:10px;background:var(--line);border-radius:5px;overflow:hidden;margin:12px 0}#bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#b8651b,var(--gold));transition:width .6s}
.stats{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.chip{border:1px solid var(--line);background:var(--card);color:var(--tx);padding:6px 12px;border-radius:20px;cursor:pointer;font:inherit}
.chip.on{border-color:var(--gold);color:var(--gold)}.chip b{margin-right:5px}.eta{margin-left:auto;color:var(--mut)}
button.retry{background:var(--bad);color:#fff;border:0;border-radius:20px;padding:6px 14px;cursor:pointer;font:inherit}
main{padding:8px 28px 60px}h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);margin:26px 0 10px;display:flex;gap:10px}h2 span{color:var(--gold)}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.c{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;position:relative}
.c .v{aspect-ratio:16/9;background:#0b0806;display:flex;align-items:center;justify-content:center;position:relative;cursor:pointer}
.tabs{display:flex;gap:8px}.gt{grid-template-columns:repeat(auto-fill,minmax(170px,1fr))}.tall .v{aspect-ratio:9/16}.c .v{position:relative;overflow:hidden}.c video{width:100%;height:100%;object-fit:cover;display:block}.c .meta{display:flex;justify-content:space-between;padding:8px 10px;align-items:center}
.tag{font-size:12px;color:var(--mut)}.done .tag{color:var(--ok)}.active{border-color:var(--gold)}.active .tag{color:var(--gold)}.failed{border-color:var(--bad)}.failed .tag{color:var(--bad)}
.wait{color:var(--mut);font-size:13px}.spin{width:26px;height:26px;border:3px solid var(--line);border-top-color:var(--gold);border-radius:50%;animation:s 1s linear infinite}@keyframes s{to{transform:rotate(360deg)}}
.pulse{position:absolute;inset:0;background:radial-gradient(circle at 50% 60%,rgba(232,182,74,.16),transparent 70%)}@keyframes p{50%{opacity:.3}}
.err{padding:0 10px 8px;color:var(--bad);font-size:12px}
#m{position:fixed;inset:0;background:rgba(0,0,0,.88);display:none;align-items:center;justify-content:center;z-index:10;flex-direction:column;gap:10px}#m video{max-width:92vw;max-height:84vh;border-radius:8px}
</style>
<header><div class=top><h1>Ayodhya clips</h1><span class=tabs><button class='chip on' id=tf onclick="TAB='film';LAST='';t()">Film 16:9</button><button class=chip id=tr onclick="TAB='reel';LAST='';t()">Reel 9:16</button><button class=chip id=td onclick="TAB='dwarka';LAST='';t()">Dwarka film 16:9</button><button class=chip id=tb onclick="TAB='build';LAST='';t()">Dwarka build</button><button class=chip id=ts onclick="TAB='short';LAST='';t()">Dwarka Short 9:16</button><button class=chip id=th onclick="TAB='dhanu';LAST='';t()">Dhanushkodi film 16:9</button><button class=chip id=tk onclick="TAB='dhanubuild';LAST='';t()">Dhanushkodi build</button></span><span class=sub id=sub></span><span class=pct id=pct></span></div><div id=bar><i></i></div>
<div class=stats id=chips></div></header><main id=g></main>
<div id=m onclick="this.style.display='none';mv.pause()"><div id=mt class=sub></div><video id=mv controls onclick="event.stopPropagation()"></video></div>
<script>
let F='all',D=null,TAB='film',LAST='';function tick(){if(!D||!D.jobs)return;D.jobs.forEach(j=>{if(j.state!='active')return;const el=document.querySelector('.v[data-s="'+j.shot+'"]');const tg=el&&el.parentNode.querySelector('.tag');if(tg)tg.textContent=(j.step?j.step+' · ':'')+fmt(j.age||0)})}const LDH={A:'A · Hook',B:'B · The ghost town',C:'C · Ram Setu and the sights',D:'D · How to reach',E:'E · Plan'};const LD={A:'A · Hook',B:'B · Krishna and the sea',C:'C · Mystery, news and sights',D:'D · How to reach',E:'E · Plan'};const L={A:'A · Hook',B:'B · Story',C:'C · Places',D:'D · How to reach',E:'E · Plan'};
const fmt=s=>s>3600?Math.round(s/360)/10+' h':Math.max(1,Math.round(s/60))+' min';
function open_(s){mt.textContent=s;mv.src=(TAB=='short'?'/short/clips/':TAB=='reel'?'/reel/clips/':TAB=='dwarka'?'/dwarka/clips/':TAB=='dhanu'?'/dhanu/clips/':'/clip/')+s+'.mp4';mv.style.maxHeight=TAB=='reel'?'88vh':'84vh';m.style.display='flex';mv.play()}
async function retry(){await fetch('/retry',{method:'POST'});t()}
function drawBuild(){const B=D.build;sub.textContent=B.done+' of '+B.stages.length+' build steps';pct.textContent=Math.round(100*B.done/B.stages.length)+'%';bar.firstChild.style.width=100*B.done/B.stages.length+'%';chips.innerHTML='<span class=eta>'+B.queues+'</span>';
g.innerHTML='<div class=g style="grid-template-columns:repeat(auto-fill,minmax(240px,1fr))">'+B.stages.map(x=>'<div class="c '+(x.state=='done'?'done':x.state=='active'?'active':'waiting')+'"><div class=meta><b>'+x.name+'</b><span class=tag>'+(x.state=='done'?'done '+(x.at||''):x.state=='active'?'running':'waiting')+'</span></div><div class=meta style="padding-top:0;color:var(--mut)">'+x.note+'</div></div>').join('')+'</div><h2>Latest log</h2><pre style="background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;font-size:12px;line-height:1.5;white-space:pre-wrap">'+B.log.replace(/</g,'&lt;')+'</pre>'}
function draw(){if(!D)return;if(D.build){drawBuild();return}const J=D.jobs,n=J.length,c=x=>J.filter(j=>j.state==x).length,k=c('done');
sub.textContent=k+' of '+n+' clips';pct.textContent=Math.round(100*k/n)+'%';bar.firstChild.style.width=100*k/n+'%';
const eta=D.avg&&n-k?'about '+fmt((n-k)/D.conc*D.avg)+' left':n==k?'all done':'';
chips.innerHTML=[['all','All',n],['active','Generating',c('active')],['waiting','Waiting',c('waiting')],['done','Done',k],['failed','Failed',c('failed')]].map(a=>'<button class="chip '+(F==a[0]?'on':'')+'" onclick="F=\\''+a[0]+'\\';draw()"><b>'+a[2]+'</b>'+a[1]+'</button>').join('')+(c('failed')?'<button class=retry onclick=retry()>Retry failed</button>':'')+'<span class=eta>'+eta+'</span>';
const sec={};J.filter(j=>F=='all'||j.state==F).forEach(j=>(sec[TAB=='reel'?'R':j.shot[0]]??=[]).push(j));const REELP=TAB=='reel'||TAB=='short';
const U=j=>REELP?(TAB=='short'?'/short/clips/':'/reel/clips/')+j.shot+'.mp4':TAB=='dwarka'?'/dwarka/clips/'+j.shot+'.mp4':TAB=='dhanu'?'/dhanu/clips/'+j.shot+'.mp4':'/clip/'+j.shot+'.mp4';const DWT=()=>TAB=='dwarka'||TAB=='dhanu';
const card=j=>'<div class="c '+j.state+(REELP?' tall':'')+'"><div class=v data-s="'+j.shot+'" '+(j.state=='done'?'onclick="open_(this.dataset.s)" onmouseenter="this.querySelector(&quot;video&quot;).play()" onmouseleave="this.querySelector(&quot;video&quot;).pause()"':'')+'>'+
(j.state=='done'?'<video src="'+U(j)+'#t=0.6" preload=metadata muted loop playsinline></video>':((REELP||DWT())&&j.still?'<img src="'+(DWT()?(TAB=='dhanu'?'/dhanu/stills/':'/dwarka/stills/')+j.shot+'.'+j.ext:(TAB=='short'?'/short/stills/':'/reel/stills/')+j.shot+'.png')+'" style="width:100%;height:100%;object-fit:cover;opacity:.55">':'')+(j.state=='active'?'<div class=pulse></div><div class=spin style="position:absolute"></div>':((REELP||DWT())&&j.still?'':'<span class=wait>in queue</span>')))+'</div>'+
'<div class=meta><b>'+j.shot+'</b><span class=tag>'+(j.state=='done'?'ready':j.state=='active'?(j.step?j.step+' · ':'')+fmt(j.age||0):j.state=='failed'?'failed':'waiting')+'</span></div>'+(j.err?'<div class=err>'+j.err+'</div>':'')+'</div>';
g.innerHTML=Object.keys(sec).map(s=>'<h2>'+((TAB=='dhanu'?LDH:DWT()?LD:L)[s]||(REELP?'Reel · 9:16 · 70 s':s))+'<span>'+sec[s].filter(j=>j.state=='done').length+'/'+sec[s].length+'</span></h2><div class="g'+(REELP?' gt':'')+'">'+sec[s].map(card).join('')+'</div>').join('')}
async function t(){try{D=await (await fetch(TAB=='reel'?'/api/reel':TAB=='dwarka'?'/api/dwarka':TAB=='build'?'/api/build':TAB=='short'?'/api/short':TAB=='dhanu'?'/api/dhanu':TAB=='dhanubuild'?'/api/build?film=dhanu':'/api')).json();tf.className='chip'+(TAB=='film'?' on':'');tr.className='chip'+(TAB=='reel'?' on':'');td.className='chip'+(TAB=='dwarka'?' on':'');tb.className='chip'+(TAB=='build'?' on':'');ts.className='chip'+(TAB=='short'?' on':'');th.className='chip'+(TAB=='dhanu'?' on':'');tk.className='chip'+(TAB=='dhanubuild'?' on':'');const sig=TAB+'|'+F+'|'+JSON.stringify(D,(k,v)=>k=='age'?undefined:v);if(sig===LAST){tick();return}LAST=sig;draw()}catch{}}
t();setInterval(t,5000)
</script>`;
const range = (req, res, f, type) => { const size = fs.statSync(f).size, r = req.headers.range?.match(/bytes=(\d+)-(\d*)/);
  if (r) { const a = +r[1], b = r[2] ? +r[2] : size - 1; res.writeHead(206, { 'content-type': type, 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${b}/${size}`, 'content-length': b - a + 1 }); return fs.createReadStream(f, { start: a, end: b }).pipe(res); }
  res.writeHead(200, { 'content-type': type, 'accept-ranges': 'bytes', 'content-length': size }); fs.createReadStream(f).pipe(res); };
http.createServer(async (req, res) => {
  if (req.url.startsWith('/api/build')) {
    const DH = req.url.includes('dhanu'), DWx = DH ? DWH : DW, NT = DH ? 48 : 53, NC = DH ? 25 : 27, dqx = DH ? dhq : dq;
    const rd = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return {}; } }, A = new URL(DH ? '../dhanushkodi_film/auto/' : '../dwarka_film/auto/', import.meta.url).pathname, st = rd(A + 'stage.json'), qs = rd(A + 'qa_state.json');
    const passed = Object.values(qs).filter(v => v.pass).length, clips = fs.existsSync(DWx + 'clips') ? fs.readdirSync(DWx + 'clips').length : 0, has = f => fs.existsSync(DWx + f);
    const defs = [['voice_hi', 'Hindi voiceover', 'Sameer, checked line by line'], ['voice_en', 'English voiceover', 'Oliver, fitted to the Hindi timing'], ['visuals', 'Pictures and clips', clips + ' of ' + NT + ' clips made, ' + passed + ' passed my checks'],
      ['cut', 'Cut to the voice', 'every shot starts on its spoken word'], ['cards', NC + ' cards and logo', 'timed to the words, in quiet corners'], ['mix', 'Hindi sound mix', 'shot-by-shot sounds, ducked music'], ['mix_en', 'English sound mix', 'same sounds, English voice'], ['package', 'YouTube package', 'titles, description, tags, subtitles, thumbnails']];
    let active = false; const stages = defs.map(([k, name, note]) => { const done = k in st; const state = done ? 'done' : (!active ? (active = true, 'active') : 'waiting'); return { name, note, state, at: st[k] }; });
    let log = ''; try { log = fs.readFileSync(A + 'autopilot.log', 'utf8').trim().split('\n').slice(-14).join('\n'); } catch {}
    const [dc, oc] = await Promise.all([dqx.getJobCounts('waiting', 'active', 'completed', 'failed'), new Queue('ops', { connection: conn }).getJobCounts('waiting', 'active', 'completed', 'failed')]);
    res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify({ build: { stages, done: stages.filter(x => x.state == 'done').length, log, queues: `generation queue: ${dc.active} running, ${dc.waiting} waiting, ${dc.completed} done · ops queue: ${oc.active} running, ${oc.waiting} waiting` } }));
  }
  if (req.url === '/api/dhanu') {
    const o = JSON.parse(fs.readFileSync(new URL('./dhanu.json', import.meta.url))).map(s => s.shot), now = Date.now();
    const js = await dhq.getJobs(['waiting', 'active', 'delayed', 'failed', 'completed'], 0, 200);
    const jobs = await Promise.all(js.map(async j => { const st = await j.getState(), sh = j.data.shot, has = d => fs.existsSync(`${DWH}${d}`);
      const ext = has(`stills/${sh}.jpg`) ? 'jpg' : 'png', clip = has(`clips/${sh}.mp4`), still = has(`stills/${sh}.${ext}`);
      return { shot: sh, state: clip ? 'done' : st === 'delayed' ? 'waiting' : st === 'completed' ? 'done' : st, still, ext, step: clip ? 'clip' : has(`up/${sh}.jpg`) ? 'clip generating' : still ? 'upscaling' : (j.data.photo ? 'cleaning photo' : 'still generating'), age: st === 'active' && j.processedOn ? (now - j.processedOn) / 1000 : 0, err: st === 'failed' ? (j.failedReason || '').slice(0, 90) : '' }; }));
    jobs.sort((a, b) => o.indexOf(a.shot) - o.indexOf(b.shot));
    res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify({ jobs, conc: 1, avg: 420 }));
  }
  const hm = req.url.match(/^\/dhanu\/(clips|stills)\/(\w+)\.(mp4|png|jpg)/), hf = hm && `${DWH}${hm[1]}/${hm[2]}.${hm[3]}`;
  if (hf && fs.existsSync(hf)) return range(req, res, hf, hm[3] === 'mp4' ? 'video/mp4' : hm[3] === 'jpg' ? 'image/jpeg' : 'image/png');
  if (req.url === '/api/dwarka') {
    const o = JSON.parse(fs.readFileSync(new URL('./dwarka.json', import.meta.url))).map(s => s.shot), now = Date.now();
    const js = await dq.getJobs(['waiting', 'active', 'delayed', 'failed', 'completed'], 0, 200);
    const jobs = await Promise.all(js.map(async j => { const st = await j.getState(), sh = j.data.shot, has = d => fs.existsSync(`${DW}${d}`);
      const ext = has(`stills/${sh}.jpg`) ? 'jpg' : 'png', clip = has(`clips/${sh}.mp4`), still = has(`stills/${sh}.${ext}`);
      return { shot: sh, state: clip ? 'done' : st === 'delayed' ? 'waiting' : st === 'completed' ? 'done' : st, still, ext, step: clip ? 'clip' : has(`up/${sh}.jpg`) ? 'clip generating' : still ? 'upscaling' : (j.data.photo ? 'cleaning photo' : 'still generating'), age: st === 'active' && j.processedOn ? (now - j.processedOn) / 1000 : 0, err: st === 'failed' ? (j.failedReason || '').slice(0, 90) : '' }; }));
    jobs.sort((a, b) => o.indexOf(a.shot) - o.indexOf(b.shot));
    res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify({ jobs, conc: 1, avg: 420 }));
  }
  const dm = req.url.match(/^\/dwarka\/(clips|stills)\/(\w+)\.(mp4|png|jpg)/), df = dm && `${DW}${dm[1]}/${dm[2]}.${dm[3]}`;
  if (df && fs.existsSync(df)) return range(req, res, df, dm[3] === 'mp4' ? 'video/mp4' : dm[3] === 'jpg' ? 'image/jpeg' : 'image/png');
  if (req.url === '/api/short') {
    const o = JSON.parse(fs.readFileSync(new URL('./short.json', import.meta.url))).map(s => s.shot), now = Date.now();
    const js = await sq.getJobs(['waiting', 'active', 'delayed', 'failed', 'completed'], 0, 200);
    const jobs = await Promise.all(js.map(async j => { const st = await j.getState(), sh = j.data.shot, has = d => fs.existsSync(`${SHORT}${d}`);
      const clip = has(`clips/${sh}.mp4`), still = has(`stills/${sh}.png`), prog = clip ? 100 : j.progress || 0;
      return { shot: sh, state: clip ? 'done' : st === 'delayed' ? 'waiting' : st === 'completed' ? 'done' : st, still, step: clip ? 'clip' : has(`up/${sh}.jpg`) ? 'clip generating' : still ? 'upscaling' : 'still generating', age: st === 'active' && j.processedOn ? (now - j.processedOn) / 1000 : 0, err: st === 'failed' ? (j.failedReason || '').slice(0, 90) : '' }; }));
    jobs.sort((a, b) => o.indexOf(a.shot) - o.indexOf(b.shot));
    res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify({ jobs, conc: CONC, avg: 480 }));
  }
  const sm = req.url.match(/^\/short\/(clips|stills)\/(\w+)\.(mp4|png)/), sf = sm && `${SHORT}${sm[1]}/${sm[2]}.${sm[3]}`;
  if (sf && fs.existsSync(sf)) return range(req, res, sf, sm[3] === 'mp4' ? 'video/mp4' : 'image/png');
  if (req.url === '/api/reel') {
    const o = JSON.parse(fs.readFileSync(new URL('./reel.json', import.meta.url))).map(s => s.shot), now = Date.now();
    const js = await rq.getJobs(['waiting', 'active', 'delayed', 'failed', 'completed'], 0, 200);
    const jobs = await Promise.all(js.map(async j => { const st = await j.getState(), sh = j.data.shot, has = d => fs.existsSync(`${REEL}${d}`);
      const clip = has(`clips/${sh}.mp4`), still = has(`stills/${sh}.png`), prog = clip ? 100 : j.progress || 0;
      return { shot: sh, state: clip ? 'done' : st === 'delayed' ? 'waiting' : st === 'completed' ? 'done' : st, still, step: clip ? 'clip' : has(`up/${sh}.jpg`) ? 'clip generating' : still ? 'upscaling' : 'still generating', age: st === 'active' && j.processedOn ? (now - j.processedOn) / 1000 : 0, err: st === 'failed' ? (j.failedReason || '').slice(0, 90) : '' }; }));
    jobs.sort((a, b) => o.indexOf(a.shot) - o.indexOf(b.shot));
    res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify({ jobs, conc: CONC, avg: 480 }));
  }
  const rm = req.url.match(/^\/reel\/(clips|stills)\/(\w+)\.(mp4|png)/), rf = rm && `${REEL}${rm[1]}/${rm[2]}.${rm[3]}`;
  if (rf && fs.existsSync(rf)) return range(req, res, rf, rm[3] === 'mp4' ? 'video/mp4' : 'image/png');
  if (req.url === '/api') {
    const js = await q.getJobs(['waiting', 'active', 'delayed', 'failed', 'completed'], 0, 500), o = order(), now = Date.now(), dur = [];
    const jobs = await Promise.all(js.map(async j => { const st = await j.getState(), done = fs.existsSync(path.join(OUT, j.data.shot + '.mp4'));
      if (st === 'completed' && j.finishedOn && j.processedOn && j.finishedOn - j.processedOn > 90000) dur.push((j.finishedOn - j.processedOn) / 1000);
      return { shot: j.data.shot, state: done || st === 'completed' ? 'done' : st === 'delayed' ? 'waiting' : st, age: st === 'active' && j.processedOn ? (now - j.processedOn) / 1000 : 0, err: st === 'failed' ? (j.failedReason || '').slice(0, 90) : '' }; }));
    jobs.sort((a, b) => o.indexOf(a.shot) - o.indexOf(b.shot));
    res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify({ jobs, conc: CONC, avg: dur.length ? dur.reduce((a, b) => a + b) / dur.length : 210 }));
  }
  if (req.url === '/retry' && req.method === 'POST') { for (const j of await q.getFailed()) await j.retry(); return res.end('ok'); }
  const m = req.url.match(/^\/clip\/([\w-]+\.mp4)/), f = m && path.join(OUT, m[1]);
  if (f && fs.existsSync(f)) { // Range support so the browser can show a frame and seek
    const size = fs.statSync(f).size, r = req.headers.range?.match(/bytes=(\d+)-(\d*)/);
    if (r) { const a = +r[1], b = r[2] ? +r[2] : size - 1; res.writeHead(206, { 'content-type': 'video/mp4', 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${b}/${size}`, 'content-length': b - a + 1 }); return fs.createReadStream(f, { start: a, end: b }).pipe(res); }
    res.writeHead(200, { 'content-type': 'video/mp4', 'accept-ranges': 'bytes', 'content-length': size }); return fs.createReadStream(f).pipe(res);
  }
  res.setHeader('content-type', 'text/html'); res.end(page);
}).listen(3939, '127.0.0.1', () => console.log('http://localhost:3939'));
