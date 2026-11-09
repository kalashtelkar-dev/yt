# -*- coding: utf-8 -*-
"""Cut to the voice, word-synced cards in quiet corners, logo, shot-by-shot sound beds and ducked music, for Hindi and English."""
import difflib, io, json, os, re, subprocess, sys, collections, urllib.parse, numpy as np
from PIL import Image
from lib import *
HI = FILM + 'voice_hi/'; ORD = order(); SEC = sections(); SH = ORD
os.makedirs(FILM + 'cards', exist_ok=True); os.makedirs(AUTO + 'snd', exist_ok=True)
T = json.load(open(HI + 'timings.json')); TOT = T['total']; WORDS = json.load(open(HI + 'words.json'))
def norm(w): return re.sub(r'[^ऀ-ॿ\w]', '', w.replace('़', ''))
def onset(i):
    a, b = T['lines'][i]['start'], T['lines'][i]['end']
    return next((w['start'] for w in WORDS if a - 0.05 <= w['start'] <= b), a)
ON = {i: onset(i) for i in ORD}
def wtime(i, key):
    a, b = T['lines'][i]['start'] - 0.05, T['lines'][i]['end'] + 0.1; k = norm(key)
    for w in WORDS:
        if a <= w['start'] <= b and (k in norm(w['word']) or difflib.SequenceMatcher(None, k, norm(w['word'])).ratio() >= 0.8): return w['start']
    return ON[i] + 0.3
# ---------------- cut
def place_originals():
    """real clips the user dropped into original_clips/ are cut into the film on the strongest shots, in this order"""
    os.makedirs(FILM + 'clips_original', exist_ok=True); src = sorted(f for f in os.listdir(FILM + 'original_clips') if f.lower().endswith(('.mp4', '.mov', '.mkv', '.webm')))
    for f, shot in zip(src, ['A2', 'C8', 'C9', 'A1', 'B1', 'C7', 'E5', 'E3', 'B8', 'D6']):
        d = f'{FILM}clips_original/{shot}.mp4'
        if not os.path.exists(d): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '1', '-i', FILM + 'original_clips/' + f, '-t', '9', '-vf', 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24', '-an', '-c:v', 'libx264', '-crf', '17', d], check=True)
        log('original clip', f, '->', shot)
def clip_of(s): return f'{FILM}clips_original/{s}.mp4' if os.path.exists(f'{FILM}clips_original/{s}.mp4') else f'{FILM}clips/{s}.mp4'
def cut():
    place_originals()
    if os.path.exists(FILM + 'cut_nocards.mp4'): return
    t = [0.0] + [max(0, ON[i] - 0.12) for i in SH[1:]]; bound = {'B1', 'C1', 'D1', 'E1'}
    Xf = [0.5 if SH[k + 1] in bound else 0.2 for k in range(len(SH) - 1)] + [0]
    S = [0.0] + [t[k] - Xf[k - 1] / 2 for k in range(1, len(SH))]; E = [t[k + 1] + Xf[k] / 2 for k in range(len(SH) - 1)] + [TOT]
    json.dump(dict(shots=SH, start=S, end=E, on=ON), open(FILM + 'timing.json', 'w')); CLIP = 124 / 24; ins = []; fl = []
    for k, s in enumerate(SH):
        d = E[k] - S[k]; ins += ['-i', clip_of(s)]; f = d / CLIP if d > CLIP and 'clips_original' not in clip_of(s) else 1.0
        c = f'[{k}:v]scale=1920:1080:flags=lanczos,setsar=1,fps=24,setpts=PTS-STARTPTS'
        if f > 1.0: c += f',setpts=PTS*{min(f, 2.1):.4f}' + (',minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1' if f > 1.25 else ',fps=24')
        fl.append(c + f',tpad=stop_mode=clone:stop_duration=4,trim=0:{d:.4f},setpts=PTS-STARTPTS[v{k}]')
    cur = 'v0'
    for k in range(len(SH) - 1):
        fl.append(f"[{cur}][v{k+1}]xfade=transition={'fadeblack' if Xf[k] > .3 else 'fade'}:duration={Xf[k]}:offset={S[k+1]:.4f}[x{k}]"); cur = f'x{k}'
    fl.append(f'[{cur}]format=yuv420p[vout]'); ins += ['-i', FILM + 'voiceover_master_sameer.mp3']
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(fl), '-map', '[vout]', '-map', f'{len(SH)}:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '24', '-c:a', 'copy', '-t', f'{TOT:.3f}', FILM + 'cut_nocards.mp4'], check=True)
# ---------------- cards
CARDS = [  # name, line, key word, label, title, sub, dur
 ('c01_place', 'A2', 'धनुषकोडी', 'Location', 'धनुषकोडी, तमिलनाडु', 'Dhanushkodi, Tamil Nadu', 3.8),
 ('c02_1964', 'B4', 'दिसंबर', 'The cyclone', 'दिसंबर 1964', 'The storm that ended the town', 3.6),
 ('c03_unfit', 'B6', 'वीरान', 'After the storm', 'रहने लायक नहीं', 'Declared unfit to live in', 3.4),
 ('c04_station', 'B7', 'स्टेशन', 'Ruins', 'टूटा रेलवे स्टेशन', 'Dhanushkodi railway station', 3.6),
 ('c05_adam', 'C2', 'आदम', 'Also called', 'आदम का पुल', "Adam's Bridge", 3.4),
 ('c06_len', 'C3', 'अड़तालीस', 'Length', 'लगभग 48 किमी', 'A chain of limestone shoals', 3.4),
 ('c07_isro', 'C4', 'इसरो', 'Satellite map', 'इसरो का नक्शा', 'Joins Dhanushkodi and Mannar', 3.6),
 ('c08_asi', 'C5', 'इक्कीस', '2021', 'पुरातत्व सर्वेक्षण', 'A deeper study approved', 3.6),
 ('c09_arichal', 'C8', 'अरिचल', 'Landmark', 'अरिचल मुनई', 'Where the two seas meet', 3.8),
 ('c10_church', 'C10', 'गिरिजाघर', 'Ruins', 'गिरिजाघर के खंडहर', 'The church ruins', 3.4),
 ('c11_temple', 'C11', 'रामनाथस्वामी', 'Landmark', 'रामनाथस्वामी मंदिर', 'Rameswaram', 3.6),
 ('c12_pamban', 'C12', 'पंबन', 'Bridge', 'नया पंबन पुल', 'First vertical-lift sea bridge, April 2025', 4.0),
 ('c13_l1', 'C14', 'अरिचल', 'Place 1', 'अरिचल मुनई', '', 1.7),
 ('c14_l2', 'C15', 'टूटा', 'Place 2', 'टूटा रेलवे स्टेशन', '', 1.7),
 ('c15_l3', 'C16', 'गिरिजाघर', 'Place 3', 'गिरिजाघर के खंडहर', '', 1.7),
 ('c16_l4', 'C17', 'रामनाथस्वामी', 'Place 4', 'रामनाथस्वामी मंदिर', '', 1.7),
 ('c17_air', 'D2', 'मदुरै', 'By air', 'मदुरै हवाई अड्डा', '175 km from Rameswaram', 3.8),
 ('c18_rail', 'D4', 'ट्रेनें', 'By rail', 'रामेश्वरम स्टेशन', 'Trains from Chennai, Madurai, Kanyakumari', 4.0),
 ('c19_road', 'D5', 'अठारह', 'By road', 'रामेश्वरम से 18 किमी', 'Government bus or jeep', 3.8),
 ('c20_day', 'D6', 'दिन', 'Timing', 'सिर्फ़ दिन में', 'Daytime only', 3.2),
 ('c21_season', 'D7', 'अक्टूबर', 'Best season', 'अक्टूबर से मार्च', 'October to March', 3.8),
 ('c22_plan1', 'E2', 'सुबह', 'Morning', 'रामनाथस्वामी मंदिर', 'Start with darshan', 3.4),
 ('c23_plan2', 'E3', 'दस', '10:00 AM', 'धनुषकोडी की ओर', 'Bus or jeep', 3.0),
 ('c24_plan3', 'E4', 'दोपहर', 'Afternoon', 'स्टेशन और गिरिजाघर', 'The ruins', 3.4),
 ('c25_plan4', 'E5', 'अरिचल', 'Before evening', 'अरिचल मुनई', 'Sea view', 3.4)]
def cards():
    rows = [dict(name=n, variables=dict(label=l, title=t, sub=s, dur=d)) for n, i, k, l, t, s, d in CARDS if not os.path.exists(f'{FILM}cards/{n}.webm')]
    if rows:
        html = open(ROOT + 'ayodhya_film/../../private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/card_v2.html').read() if False else open('/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/card_v2.html').read()
        j = wait(call('POST', '/v1/motion-graphic/batch', {'html': html, 'rows': rows, 'format': 'webm', 'quality': 'high', 'fps': 24, 'idempotencyKey': 'dhanu-cards-v1-' + str(len(rows))})['id'], every=5, limit=3600)
        ks = [o['key'] for o in j['result']['outputs'] if o['key'].endswith('.webm')]; u = sign(ks)
        for k in ks: fetch(u[k], FILM + 'cards/' + re.sub(r'^row-\d+-', '', os.path.basename(k)))
def comp():
    if os.path.exists(FILM + 'final_nosfx.mp4'): return
    SC = 0.88; MX, MT, MB = 88, 64, 112; PAD = 24
    def png(c): return Image.open(io.BytesIO(subprocess.check_output(c)))
    def bbox(f):
        a = np.asarray(png(['ffmpeg', '-loglevel', 'error', '-c:v', 'libvpx-vp9', '-ss', '1.2', '-i', f, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-']).convert('RGBA'))[:, :, 3] > 200
        ys, xs = np.where(a); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    def frame(tt):
        tt = max(0, min(tt, TOT - 0.3))
        g = np.asarray(png(['ffmpeg', '-loglevel', 'error', '-ss', f'{tt:.3f}', '-i', FILM + 'cut_nocards.mp4', '-frames:v', '1', '-vf', 'scale=960:540,format=gray', '-f', 'image2pipe', '-vcodec', 'png', '-']), float)
        gy, gx = np.gradient(g); return np.hypot(gx, gy)
    items = [(n, wtime(i, k) - 0.45, d, f'{FILM}cards/{n}.webm') for n, i, k, l, t, s, d in CARDS]
    items.append(('subscribe', wtime('E10', 'सब्सक्राइब') - 0.45, 4.4, ROOT + 'ayodhya_film/cards/subscribe.webm'))
    items.sort(key=lambda x: x[1]); ins = []; fl = []; cur = '0:v'; n = 1; P = {}; used = []
    for name, t0, d, f in items:
        t0 = max(0.05, t0)
        if name == 'subscribe': x0, y0, x1, y1, iw, ih = 0, 0, 520, 150, 520, 150
        else: x0, y0, x1, y1 = bbox(f); iw, ih = 900, 220
        cx0, cy0, cx1, cy1 = max(0, x0 - PAD), max(0, y0 - PAD), min(iw, x1 + PAD), min(ih, y1 + PAD)
        pw, ph = (x1 - x0) * SC, (y1 - y0) * SC; px, py = (x0 - cx0) * SC, (y0 - cy0) * SC
        cand = {'TL': (MX, MT), 'TR': (1920 - MX - pw, MT), 'BL': (MX, 1080 - MB - ph)}; fr = [frame(t0 + d * (q + .5) / 6) for q in range(6)]; sc = {}
        for nm, (X, Y) in cand.items():
            if any(u[0] == nm and u[1] < t0 + d and u[2] > t0 for u in used): continue
            s = 0
            for g in fr: reg = g[int(Y / 2):int((Y + ph) / 2), int(X / 2):int((X + pw) / 2)]; s += reg.mean() + 0.5 * np.percentile(reg, 90)
            sc[nm] = s
        nm = min(sc, key=sc.get) if sc else 'TL'; X, Y = cand[nm]; used.append((nm, t0, t0 + d)); P[name] = dict(t=t0, dur=d, corner=nm)
        ins += ['-c:v', 'libvpx-vp9', '-i', f]
        fl.append(f'[{n}:v]format=yuva420p,crop={cx1-cx0}:{cy1-cy0}:{cx0}:{cy0},scale=iw*{SC}:ih*{SC},setpts=PTS-STARTPTS+{t0}/TB[c{n}]')
        fl.append(f"[{cur}][c{n}]overlay=x={int(X-px)}:y={int(Y-py)}:eof_action=pass:enable='between(t,{t0},{t0+d})'[o{n}]"); cur = f'o{n}'; n += 1
    json.dump(P, open(FILM + 'placement.json', 'w'), indent=1); ins += ['-loop', '1', '-i', ROOT + 'ayodhya_film/logo_circle.png']; fl.append(f'[{cur}][{n}:v]overlay=x=1794:y=954:shortest=1[vout]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', FILM + 'cut_nocards.mp4', *ins, '-filter_complex', ';'.join(fl), '-map', '[vout]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-r', '24', '-t', f'{TOT:.3f}', FILM + 'final_nosfx.mp4'], check=True)
# ---------------- sounds
SRC = {'river': ROOT + 'ayodhya_film/sfx/river.mp4', 'fire': ROOT + 'ayodhya_film/sfx/fire.mp4', 'birds': ROOT + 'ayodhya_film/sfx/birds.mp4', 'crick': ROOT + 'ayodhya_film/sfx/crick.mp4',
       'crowd': ROOT + 'ayodhya_film/sfx/crowd.mp4', 'train': ROOT + 'ayodhya_film/sfx/train.mp4'}
NEW = {'sea': 'sea waves shore beach'}
def sounds():
    for k, q in NEW.items():
        p = f'{AUTO}snd/{k}.mp4'
        if not os.path.exists(p):
            r = call('GET', '/v1/sounds?q=' + urllib.parse.quote(q) + '&kind=ambience&minSeconds=40&limit=3')['sounds']
            if not r: r = call('GET', '/v1/sounds?q=' + urllib.parse.quote(q) + '&limit=6')['sounds']
            for cand in r[:6]:
                sid = cand['id']; j = wait(call('POST', '/v1/video/trim', {'input': 'sound:' + sid, 'startSec': 0, 'durationSec': min(60, int(cand['seconds']) - 1), 'reencode': True, 'container': 'mp4', 'idempotencyKey': f'dw-snd-{k}-{sid}'})['id'])
                if j['status'] == 'succeeded': fetch(sign([out_key(j)])[out_key(j)], p); log('sound', k, sid, cand.get('name')); break
                log('sound candidate failed', k, sid)
        SRC[k] = p
    for k, flt in (('under', 'lowpass=f=450,volume=1.6'), ('storm', 'highpass=f=120,volume=1.4')):   # underwater = muffled sea, storm = harder sea
        p = f'{AUTO}snd/{k}2.mp4'
        if not os.path.exists(p): subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', SRC['sea'], '-af', flt, '-c:a', 'aac', '-b:a', '192k', p], check=True)
        SRC[k] = p
MAP = {'sea': 'A1 A2 A3 A6 B1 B8 C1 C8 C9 C12 C14 D1 D7 E1 E5 E10', 'under': 'A4 C2 C3 C4 C5', 'storm': 'B4 B5 B7 B6 C10 C16 E4', 'crowd': 'C11 C17 E2', 'train': 'B2 B3 D4', 'crick': 'E8 E9', 'birds': 'D3 E3'}
LV = dict(sea=-35, under=-34, storm=-31, river=-37, birds=-39, fire=-40, crowd=-37, train=-36, crick=-41)
def mix(voice, out_m4a, out_mp4):
    tm = json.load(open(FILM + 'timing.json')); win = {s: (tm['start'][i], tm['end'][i]) for i, s in enumerate(tm['shots'])}; segs = [(s, k) for k, v in MAP.items() for s in v.split() if s in win]
    sl = {k: lufs(SRC[k]) for k in SRC}; sd = {k: dur(SRC[k]) for k in SRC}; used = collections.defaultdict(float); ins = []; fl = []; lab = []
    for n, (s, k) in enumerate(segs):
        a, b = win[s]; d = b - a; off = used[k] % max(1, sd[k] - d - 0.1); used[k] += d + 3; ins += ['-ss', f'{off:.2f}', '-t', f'{d:.3f}', '-i', SRC[k]]
        g = LV[k] - sl[k] - (2 if sum(1 for v in MAP.values() if s in v.split()) > 1 else 0)
        fl.append(f'[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,afade=t=in:d=0.6,afade=t=out:st={max(0, d-0.6):.3f}:d=0.6,adelay={int(a*1000)}|{int(a*1000)}[b{n}]'); lab.append(f'[b{n}]')
    n = len(segs); fl.append(''.join(lab) + f'amix=inputs={n}:normalize=0:duration=longest,apad,atrim=0:{TOT}[bed]'); ins += ['-i', voice, '-stream_loop', '-1', '-i', ROOT + 'ayodhya_film/sfx/music.mp4']
    mg = -31 - lufs(ROOT + 'ayodhya_film/sfx/music.mp4')
    fl += [f'[{n}:a]aformat=channel_layouts=stereo,asplit=3[v0][v1][v2]', '[bed][v0]sidechaincompress=threshold=0.015:ratio=5:attack=30:release=500[bedd]',
           f'[{n+1}:a]aformat=channel_layouts=stereo,volume={mg:.2f}dB,atrim=0:{TOT},afade=t=in:d=3,afade=t=out:st={TOT-3}:d=3[m]', '[m][v1]sidechaincompress=threshold=0.015:ratio=4:attack=30:release=600[mm]',
           f'[v2][bedd][mm]amix=inputs=3:normalize=0:duration=first,atrim=0:{TOT}[out]']
    raw = AUTO + 'mix_raw.wav'; subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(fl), '-map', '[out]', '-c:a', 'pcm_s16le', raw], check=True)
    g = -15 - lufs(raw); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', f'volume={g:.2f}dB,alimiter=limit=0.89', '-c:a', 'aac', '-b:a', '192k', out_m4a], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', FILM + 'final_nosfx.mp4', '-i', out_m4a, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', f'{TOT+0.04:.3f}', '-movflags', '+faststart', out_mp4], check=True)
    log('mixed', out_mp4, 'LUFS', round(lufs(out_mp4), 1))
if __name__ == '__main__':
    which = sys.argv[1:] or ['all']
    if 'cut' in which or 'all' in which: cut(); log('cut done')
    if 'cards' in which or 'all' in which: cards(); comp(); log('cards and composite done')
    if 'mix' in which or 'all' in which:
        sounds(); mix(FILM + 'voiceover_master_sameer.mp3', FILM + 'Dhanushkodi_Hindi_Audio_Full_Mix.m4a', FILM + 'final_hindi.mp4')
    if 'mix_en' in which or 'all' in which:
        if os.path.exists(FILM + 'english/voiceover_master_oliver.mp3'): sounds(); mix(FILM + 'english/voiceover_master_oliver.mp3', FILM + 'english/Dhanushkodi_English_Audio_Full_Mix.m4a', FILM + 'final_english.mp4')
