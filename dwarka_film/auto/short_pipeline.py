# -*- coding: utf-8 -*-
"""60-second Dwarka Short (9:16): Hindi voice (Ayodhya recipe, plain Sameer), cut, cards, logo, music, package. Visuals come from the 'dshort' generation queue."""
import difflib, io, json, os, re, subprocess, sys, time, numpy as np
from PIL import Image
from lib import *
SD = ROOT + 'dwarka_short/'; os.makedirs(SD + 'voice', exist_ok=True); SCR_ = json.load(open(SD + 'short_script.json')); IDS = list(SCR_)
BEATS = [['S1', 'S2'], ['S3', 'S4'], ['S5'], ['S6'], ['S7', 'S8'], ['S9']]
def norm(w): return re.sub(r'[^ऀ-ॿ\w]', '', w.replace('़', ''))
def txt(i): return ('[playful] ' if i == 'S9' else '') + SCR_[i]
def render(passages, tag):
    bodies = [{'text': '\n\n'.join('\n'.join(txt(i) for i in b) for b in beats), 'voice': 'sameer', 'speed': 'normal', 'expressiveness': 'normal', 'format': 'wav', 'lineGapMs': 450, 'paragraphGapMs': 700, 'idempotencyKey': f'dw-short-{tag}-{k}-v1'} for k, beats in enumerate(passages)]
    jobs = run_many('/v1/emotive-speech/speak', bodies); res = {}; keys = {k: out_key(j) for k, j in enumerate(jobs) if j['status'] == 'succeeded'}; urls = sign(list(keys.values()))
    for k, key in keys.items():
        p = f'{SD}voice/{tag}_{k}.wav'; fetch(urls[key], p); flat = [i for b in passages[k] for i in b]; res[k] = (p, [(i, l['startSec'], l['endSec']) for i, l in zip(flat, jobs[k]['result']['lines'])])
    return res
def slice_(p, a, b, dst):
    x = load(p); save_wav(dst, x[max(0, int((a - 0.04) * SR)):min(len(x), int((b + 0.06) * SR))]); return dst
def judge(i, wav):
    w = words(wav); sw = [norm(t) for t in SCR_[i].split() if norm(t)]; tw = [norm(a['word']) for a in w]
    return sum(1 for t in sw if any(difflib.SequenceMatcher(None, t, u).ratio() >= 0.7 for u in tw)) / max(1, len(sw))
def voice():
    if os.path.exists(SD + 'voice/timings.json'): return
    log('short: voice'); R = render([BEATS], 'p'); LINE = {}; gaps = {}
    p, segs = R[0]
    for n, (i, a, b) in enumerate(segs):
        LINE[i] = slice_(p, a, b, f'{SD}voice/{i}_0.wav')
        if n + 1 < len(segs): gaps[i] = min(1.0, max(0.3, segs[n + 1][1] - b))
    best = {}
    for attempt in range(3):
        bad = []
        for i in IDS:
            c = judge(i, LINE[i]); best[i] = max(best.get(i, (-1, None)), (c, LINE[i]))
            if c < 0.85: bad.append(i); log('short retake', i, round(c, 2))
        if not bad or attempt == 2: break
        for i in bad:
            pos = IDS.index(i); ctx = IDS[max(0, pos - 1):pos + 1]; R2 = render([[ctx]], f'r{attempt}{i}'); pp, sg = R2[0]; ii, a, b = sg[-1]; LINE[i] = slice_(pp, a, b, f'{SD}voice/{i}_{attempt+1}.wav')
    X = {i: load(best[i][1]) for i in IDS}; tg = np.median([np.sqrt(np.mean(v ** 2)) for v in X.values()]); t = 0.0; out = []; T = {}
    for n, i in enumerate(IDS):
        x = X[i] * (tg / np.sqrt(np.mean(X[i] ** 2) + 1e-12)); fd = int(0.008 * SR); x[:fd] *= np.linspace(0, 1, fd); x[-fd:] *= np.linspace(1, 0, fd)
        g = gaps.get(i, 0.5) if n + 1 < len(IDS) else 0; T[i] = dict(start=round(t, 3), end=round(t + len(x) / SR, 3)); out += [x, np.zeros(int(g * SR), dtype=np.float32)]; t += len(x) / SR + g
    y = np.concatenate(out); save_wav(SD + 'voice/raw.wav', y)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', SD + 'voice/raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000', '-ac', '1', SD + 'voice/Dwarka_Short_Hindi_Voice.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', SD + 'voice/Dwarka_Short_Hindi_Voice.wav', '-c:a', 'libmp3lame', '-b:a', '192k', SD + 'Dwarka_Short_Hindi_Voice.mp3'], check=True)
    W = words(SD + 'voice/Dwarka_Short_Hindi_Voice.wav'); json.dump(W, open(SD + 'voice/words.json', 'w'), ensure_ascii=False); json.dump(dict(total=round(len(y) / SR, 2), lines=T), open(SD + 'voice/timings.json', 'w'), indent=1)
    log('short: voice done', round(len(y) / SR, 1), 's')
def build():
    if os.path.exists(SD + 'Dwarka_Short_Hindi_9x16.mp4'): return
    while not all(os.path.exists(f'{FILM}cards/{n}.webm') for n in ('c02_gold', 'c01_dwarka', 'c08_news', 'c10_temple', 'c20_fee')): time.sleep(60)
    T = json.load(open(SD + 'voice/timings.json')); WORDS = json.load(open(SD + 'voice/words.json')); TOT = T['total']; cfg = json.load(open(ROOT + 'queue/short.json'))
    def first(i): a, b = T['lines'][i]['start'], T['lines'][i]['end']; return next((w['start'] for w in WORDS if a - 0.05 <= w['start'] <= b), a)
    def wt(i, key, after=0):
        a, b = T['lines'][i]['start'] - 0.05, T['lines'][i]['end'] + 0.1; k = norm(key)
        for w in WORDS:
            if a <= w['start'] <= b and w['start'] >= after and (k in norm(w['word']) or difflib.SequenceMatcher(None, k, norm(w['word'])).ratio() >= 0.8): return w['start']
        return first(i) + 0.3
    shots = [s['shot'] for s in cfg]; line = {s['shot']: s['line'] for s in cfg}; starts = {}
    for s in shots:
        i = line[s]; same = [x for x in shots if line[x] == i]
        starts[s] = first(i) - 0.12 if s == same[0] else wt(i, 'और', first(i) + 0.4) - 0.12
    starts[shots[0]] = 0.0; Tm = [starts[s] for s in shots]; X = 0.2; Sx = [0.0] + [Tm[k] - X / 2 for k in range(1, len(shots))]; Ex = [Tm[k + 1] + X / 2 for k in range(len(shots) - 1)] + [TOT + 0.05]
    ins = []; fl = []
    for k, s in enumerate(shots):
        d = Ex[k] - Sx[k]; ins += ['-i', f'{SD}clips/{s}.mp4']; f = d / (124 / 24) if d > 124 / 24 else 1.0
        c = f'[{k}:v]scale=1080:1920:flags=lanczos,setsar=1,fps=24,setpts=PTS-STARTPTS'
        if f > 1.0: c += f',setpts=PTS*{min(f, 2.0):.4f}' + (',minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1' if f > 1.25 else ',fps=24')
        fl.append(c + f',tpad=stop_mode=clone:stop_duration=4,trim=0:{d:.4f},setpts=PTS-STARTPTS[v{k}]')
    cur = 'v0'
    for k in range(len(shots) - 1): fl.append(f'[{cur}][v{k+1}]xfade=transition=fade:duration={X}:offset={Sx[k+1]:.4f}[x{k}]'); cur = f'x{k}'
    n = len(shots); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-i', SD + 'voice/Dwarka_Short_Hindi_Voice.wav', '-filter_complex', ';'.join(fl + [f'[{cur}]format=yuv420p[vout]']), '-map', '[vout]', '-map', f'{n}:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-r', '24', '-c:a', 'pcm_s16le', '-t', f'{TOT:.3f}', SD + 'cut.mkv'], check=True)
    CARDS = [('c02_gold', 'S1', 'सोने', 3.4), ('c01_dwarka', 'S4', 'द्वारका', 3.8), ('c08_news', 'S6', 'पच्चीस', 3.8), ('c10_temple', 'S7', 'द्वारकाधीश', 3.8), ('c20_fee', 'S8', 'शुल्क', 3.0)]
    def png(c): return Image.open(io.BytesIO(subprocess.check_output(c)))
    def bbox(f):
        a = np.asarray(png(['ffmpeg', '-loglevel', 'error', '-c:v', 'libvpx-vp9', '-ss', '1.2', '-i', f, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-']).convert('RGBA'))[:, :, 3] > 200; ys, xs = np.where(a); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    def frame(tt):
        g = np.asarray(png(['ffmpeg', '-loglevel', 'error', '-ss', f'{tt:.3f}', '-i', SD + 'cut.mkv', '-frames:v', '1', '-vf', 'scale=270:480,format=gray', '-f', 'image2pipe', '-vcodec', 'png', '-']), float); gy, gx = np.gradient(g); return np.hypot(gx, gy)
    PAD = 24; ins3 = []; fl3 = []; cur = '0:v'; k = 1; used = []
    for name, i, key, d in CARDS:
        f = f'{FILM}cards/{name}.webm'; ct = max(0.05, wt(i, key) - 0.45); x0, y0, x1, y1 = bbox(f); iw, ih = 900, 220; sc = min(1.0, 940 / (x1 - x0)); pw, ph = (x1 - x0) * sc, (y1 - y0) * sc
        cx0, cy0, cx1, cy1 = max(0, x0 - PAD), max(0, y0 - PAD), min(iw, x1 + PAD), min(ih, y1 + PAD); px, py = (x0 - cx0) * sc, (y0 - cy0) * sc
        cand = {'TL': (64, 280), 'TR': (1080 - 64 - pw, 280), 'BL': (64, 1920 - 430 - ph)}; fr = [frame(ct + d * (q + .5) / 6) for q in range(6)]; scs = {}
        for nm, (X0, Y0) in cand.items():
            if any(u[0] == nm and u[1] < ct + d and u[2] > ct for u in used): continue
            s_ = 0
            for g in fr: reg = g[int(Y0 / 4):int((Y0 + ph) / 4), int(X0 / 4):int((X0 + pw) / 4)]; s_ += reg.mean() + 0.5 * np.percentile(reg, 90)
            scs[nm] = s_
        nm = min(scs, key=scs.get) if scs else 'TL'; X0, Y0 = cand[nm]; used.append((nm, ct, ct + d)); ins3 += ['-c:v', 'libvpx-vp9', '-i', f]
        fl3.append(f'[{k}:v]format=yuva420p,crop={cx1-cx0}:{cy1-cy0}:{cx0}:{cy0},scale=iw*{sc}:ih*{sc},setpts=PTS-STARTPTS+{ct}/TB[c{k}]'); fl3.append(f"[{cur}][c{k}]overlay=x={int(X0-px)}:y={int(Y0-py)}:eof_action=pass:enable='between(t,{ct},{ct+d})'[o{k}]"); cur = f'o{k}'; k += 1
    ins3 += ['-loop', '1', '-i', ROOT + 'ayodhya_film/logo_circle.png']; fl3 += [f'[{k}:v]scale=96:96[lg]', f'[{cur}][lg]overlay=x={1080-24-96}:y=130:shortest=1[vout]']
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', SD + 'cut.mkv', *ins3, '-filter_complex', ';'.join(fl3), '-map', '[vout]', '-map', '0:a', '-c:a', 'pcm_s16le', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-r', '24', '-t', f'{TOT:.3f}', SD + 'cards.mkv'], check=True)
    MUS = ROOT + 'ayodhya_film/sfx/music.mp4'; mg = -30 - lufs(MUS)
    fm = (f'[0:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];[1:a]aformat=channel_layouts=stereo,volume={mg:.2f}dB,atrim=0:{TOT},afade=t=in:d=1.5,afade=t=out:st={TOT-2.5}:d=2.5[m];'
          f'[m][v1]sidechaincompress=threshold=0.015:ratio=4:attack=30:release=600[mm];[v2][mm]amix=inputs=2:normalize=0:duration=first,atrim=0:{TOT}[out]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', SD + 'voice/Dwarka_Short_Hindi_Voice.wav', '-stream_loop', '-1', '-i', MUS, '-filter_complex', fm, '-map', '[out]', '-c:a', 'pcm_s16le', SD + 'mix_raw.wav'], check=True)
    g = -15 - lufs(SD + 'mix_raw.wav'); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', SD + 'mix_raw.wav', '-af', f'volume={g:.2f}dB,alimiter=limit=0.89', '-c:a', 'aac', '-b:a', '192k', SD + 'mix.m4a'], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', SD + 'cards.mkv', '-i', SD + 'mix.m4a', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', f'{TOT:.3f}', '-movflags', '+faststart', SD + 'Dwarka_Short_Hindi_9x16.mp4'], check=True)
    log('short: built', round(lufs(SD + 'Dwarka_Short_Hindi_9x16.mp4'), 1), 'LUFS')
def package():
    T = json.load(open(SD + 'voice/timings.json')); WORDS = json.load(open(SD + 'voice/words.json'))
    def first(i): a, b = T['lines'][i]['start'], T['lines'][i]['end']; return next((w['start'] for w in WORDS if a - 0.05 <= w['start'] <= b), a)
    def wrap(s, w=26):
        if len(s) <= w: return s
        ws = s.split(); b = None
        for q in range(1, len(ws)):
            a, c = ' '.join(ws[:q]), ' '.join(ws[q:]); sc = abs(len(a) - len(c))
            if b is None or sc < b[0]: b = (sc, a, c)
        return b[1] + '\n' + b[2]
    cues = []
    for i in IDS:
        t0 = first(i); t1 = T['lines'][i]['end']; parts = [p.strip() for p in re.split(r'(?<=[,।?!])\s+', SCR_[i]) if p.strip()]; chs = []; cur = ''
        for p in parts:
            if cur and len(cur) + len(p) + 1 > 40: chs.append(cur); cur = p
            else: cur = (cur + ' ' + p).strip()
        if cur: chs.append(cur)
        tot = sum(len(c) for c in chs); a = t0
        for c in chs: b = a + (t1 - t0) * len(c) / tot; cues.append([a, b, c]); a = b
    for q in range(len(cues) - 1): cues[q][1] = min(cues[q][1], cues[q + 1][0] - 0.02)
    ts = lambda t: f'{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round((t%1)*1000))%1000:03d}'
    open(SD + 'Dwarka_Short_Hindi_Subtitles.srt', 'w', encoding='utf-8').write('\n'.join(f'{q+1}\n{ts(a)} --> {ts(b)}\n{wrap(c)}\n' for q, (a, b, c) in enumerate(cues)))
    titles = ['Samandar Mein Doobi Sone Ki Nagri 😱 Dwarka Ka Gadar Raaz #Shorts', 'Bhai Dwarka Mein Kya Chhupa Hai Samandar Ke Neeche? 🔥 #Shorts', 'Krishna Ke Jaate Hi Samandar Ne Nigal Liya Poora Shehar! 😳 #Shorts', 'Dwarka Ka Fodu Sach, Poora Bawaal Ek Minute Mein 🚩 #Shorts']
    desc = """🔥 Samandar mein aaj bhi samaya hua hai ye shehar, jise sone ka shehar kehte hain... Ek minute mein Dwarka ka poora gadar raaz! 😱

Krishna ne basaya, ek din mein samandar ne nigal liya, aur 2025 mein ASI ki nayi team ne phir se khoj shuru ki. Mandir ka darshan bilkul free, bag uthao aur nikal lo! 🚩

📺 Poora video (kaise pahunchein, darshan time, ek din ka plan) hamare channel par hai.
🔔 GEO Dismantled ko subscribe karo, taaki hamara channel na doobe, bhai! 🙏

🤖 Visuals aur animation AI se bane hain. Kahaniyan Mahabharata ki kathaon par aadharit hain, khoj ki jaankari news reports se li gayi hai.

#Shorts #Dwarka #Krishna #DwarkaUnderwater #Dwarkadhish #Mahabharata #GEODismantled #Gujarat #Travel"""
    tags = ['dwarka', 'dwarka shorts', 'dwarka underwater city', 'dwarka mystery', 'krishna dwarka', 'dwarkadhish temple', 'mahabharata', 'dwarka sunk in sea', 'dwarka latest news', 'gujarat tourism', 'hindi shorts', 'travel shorts', 'GEO Dismantled']
    open(SD + 'Dwarka_Short_YouTube_Package.txt', 'w', encoding='utf-8').write('TITLE OPTIONS (best = #1)\n' + '\n'.join(f'{q+1}. {t}  [{len(t)} chars]' for q, t in enumerate(titles)) + '\n\nDESCRIPTION\n' + desc + '\n\nTAGS\n' + ', '.join(tags))
    CSS = """<!doctype html><meta charset="utf-8"><style>*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;position:relative;overflow:hidden;background:#000;font-family:Impact,"Arial Black","Helvetica Neue",sans-serif;text-align:center}img.bg{position:absolute;inset:0;width:1080px;height:1920px;filter:contrast(1.18) saturate(1.3) brightness(1.05)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(2,10,20,.85) 0%,rgba(2,10,20,.55) 30%,rgba(2,10,20,0) 52%),linear-gradient(0deg,rgba(0,0,0,.55),rgba(0,0,0,0) 28%)}.t{position:absolute;left:0;right:0;line-height:.95;-webkit-text-stroke:16px #000;paint-order:stroke fill;text-shadow:0 12px 0 rgba(0,0,0,.45);letter-spacing:2px}.a{top:200px;font-size:250px;color:#ffd600}.b{top:455px;font-size:140px;color:#fff;white-space:nowrap}
.tag{position:absolute;left:50%;top:735px;transform:translateX(-50%) rotate(-2deg);white-space:nowrap;background:#e11616;color:#fff;font-size:76px;padding:6px 40px 14px;border-radius:24px;border:7px solid #fff;box-shadow:0 10px 0 rgba(0,0,0,.45)}img.logo{position:absolute;right:40px;bottom:470px;width:120px;height:120px;border-radius:50%;border:6px solid #fff}</style>"""
    os.makedirs(SD + 'thumb', exist_ok=True)
    for name, clip, a, b, tag in (('Dwarka_Short_Thumbnail', 'H1', 'SONE KA', 'SHEHAR SAMANDAR MEIN?!', 'DWARKA KA RAAZ 🔥'), ('Dwarka_Short_Thumbnail_Alt', 'H6', 'DOOB GAYA!', 'POORA SHEHAR EK DIN MEIN', 'KRISHNA KE JAATE HI 😱')):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '3', '-i', f'{SD}clips/{clip}.mp4', '-frames:v', '1', '-vf', 'scale=1080:1920:flags=lanczos', f'{SD}thumb/{name}_raw.png'], check=True)
        open(f'{SD}thumb/{name}.html', 'w').write(CSS + f'<img class="bg" src="{name}_raw.png"><div class="shade"></div><div class="t a">{a}</div><div class="t b">{b}</div><div class="tag">{tag}</div><img class="logo" src="{ROOT}ayodhya_film/logo_circle.png">')
        subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1920', f'--screenshot={SD}{name}.png', f'file://{SD}thumb/{name}.html'], capture_output=True)
    log('short: package done')
log('short pipeline started'); voice()
while not all(os.path.exists(f'{SD}clips/{s["shot"]}.mp4') for s in json.load(open(ROOT + 'queue/short.json'))): time.sleep(120)
build(); package(); log('SHORT ALL DONE')
