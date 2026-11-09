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
def cut():
    if os.path.exists(FILM + 'cut_nocards.mp4'): return
    t = [0.0] + [max(0, ON[i] - 0.12) for i in SH[1:]]; bound = {'B1', 'C1', 'D1', 'E1'}
    Xf = [0.5 if SH[k + 1] in bound else 0.2 for k in range(len(SH) - 1)] + [0]
    S = [0.0] + [t[k] - Xf[k - 1] / 2 for k in range(1, len(SH))]; E = [t[k + 1] + Xf[k] / 2 for k in range(len(SH) - 1)] + [TOT]
    json.dump(dict(shots=SH, start=S, end=E, on=ON), open(FILM + 'timing.json', 'w')); CLIP = 124 / 24; ins = []; fl = []
    for k, s in enumerate(SH):
        d = E[k] - S[k]; ins += ['-i', f'{FILM}clips/{s}.mp4']; f = d / CLIP if d > CLIP else 1.0
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
 ('c01_dwarka', 'A4', 'द्वारका', 'Location', 'द्वारका, गुजरात', 'Dwarka, Gujarat', 3.8),
 ('c02_gold', 'A1', 'सोने', 'The legend', 'सोने का शहर', 'The city of gold', 3.4),
 ('c03_meaning', 'B2', 'द्वारका', 'The name', 'द्वारका यानी द्वार', 'Dwarka means gateway', 3.4),
 ('c04_prabhas', 'B4', 'प्रभास', 'Where it ended', 'प्रभास तीर्थ', 'The Yadavas fall', 3.4),
 ('c05_jara', 'B6', 'जरा', 'The hunter', 'जरा का तीर', "Jara's arrow", 3.2),
 ('c06_bhalka', 'B9', 'भालका', 'Where Krishna left', 'भालका तीर्थ', 'Near Somnath', 3.4),
 ('c07_dig', 'C2', 'पाँच', 'Underwater dig', '2005 से 2007', 'ASI and Navy divers', 3.6),
 ('c08_news', 'C5', 'पच्चीस', 'Latest news', 'नया सर्वे, 2025', 'ASI underwater team', 3.8),
 ('c09_dive', 'C7', 'मोदी', 'February 2024', 'समंदर में प्रार्थना', 'The Prime Minister dives', 3.8),
 ('c10_temple', 'C9', 'द्वारकाधीश', 'Landmark', 'द्वारकाधीश मंदिर', 'Five floors, 72 pillars', 3.8),
 ('c11_gomti', 'C11', 'गोमती', 'Landmark', 'गोमती घाट', 'Where the river meets the sea', 3.8),
 ('c12_rukmini', 'C12', 'रुक्मिणी', 'Landmark', 'रुक्मिणी मंदिर', 'Rukmini Temple', 3.6),
 ('c13_bet', 'C13', 'बेट', 'Landmark', 'बेट द्वारका', 'An island in the sea', 3.4),
 ('c14_setu', 'C13', 'सुदर्शन', 'Bridge', 'सुदर्शन सेतु', 'Opened February 2024', 3.4),
 ('c15_l1', 'C17', 'द्वारकाधीश', 'Place 1', 'द्वारकाधीश मंदिर', '', 1.7),
 ('c16_l2', 'C18', 'गोमती', 'Place 2', 'गोमती घाट', '', 1.7),
 ('c17_l3', 'C19', 'रुक्मिणी', 'Place 3', 'रुक्मिणी मंदिर', '', 1.7),
 ('c18_l4', 'C20', 'बेट', 'Place 4', 'बेट द्वारका', '', 1.7),
 ('c19_rail', 'D2', 'रेलवे', 'By rail', 'द्वारका रेलवे स्टेशन', '2 km from the temple', 3.8),
 ('c20_fee', 'D7', 'शुल्क', 'Entry', 'दर्शन शुल्क: कोई नहीं', 'Free', 3.0),
 ('c21_hours', 'D8', 'समय', 'Darshan hours', '6:30 to 1:00 · 5:00 to 9:30', 'Morning and evening', 4.6),
 ('c22_season', 'D11', 'अक्टूबर', 'Best season', 'अक्टूबर से मार्च', 'October to March', 3.8),
 ('c23_road', 'D10', 'बत्तीस', 'By road', 'बेट द्वारका: 32 किमी', 'Sudarshan Setu, no toll', 3.8),
 ('c24_plan1', 'E2', 'साढ़े', '6:30 AM', 'द्वारकाधीश मंदिर', 'First darshan', 3.4),
 ('c25_plan2', 'E3', 'आठ', '8:00 AM', 'गोमती घाट', 'A walk by the river', 3.0),
 ('c26_plan3', 'E5', 'दोपहर', 'Afternoon', 'बेट द्वारका', 'Cross the Sudarshan Setu', 3.4),
 ('c27_plan4', 'E6', 'शाम', 'Evening', 'द्वारकाधीश मंदिर', 'Evening aarti', 3.4)]
def cards():
    rows = [dict(name=n, variables=dict(label=l, title=t, sub=s, dur=d)) for n, i, k, l, t, s, d in CARDS if not os.path.exists(f'{FILM}cards/{n}.webm')]
    if rows:
        html = open(ROOT + 'ayodhya_film/../../private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/card_v2.html').read() if False else open('/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/card_v2.html').read()
        j = wait(call('POST', '/v1/motion-graphic/batch', {'html': html, 'rows': rows, 'format': 'webm', 'quality': 'high', 'fps': 24, 'idempotencyKey': 'dwarka-cards-v1-' + str(len(rows))})['id'], every=5, limit=3600)
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
    items.append(('subscribe', wtime('E12', 'सब्सक्राइब') - 0.45, 4.4, ROOT + 'ayodhya_film/cards/subscribe.webm'))
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
MAP = {'sea': 'A1 A5 A6 B1 B2 B13 C2 C5 C13 C18 C20 D10 D11 E1 E5 E10 E11 E12', 'under': 'A3 C3 C4 C7', 'storm': 'B4 B10 B12', 'river': 'C11 E3', 'birds': 'B5 B7 B9 D7 E2',
       'fire': 'A2 D8 E6 E12', 'crowd': 'D6', 'train': 'D2', 'crick': 'E10 E11'}
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
        sounds(); mix(FILM + 'voiceover_master_sameer.mp3', FILM + 'Dwarka_Hindi_Audio_Full_Mix.m4a', FILM + 'final_hindi.mp4')
    if 'mix_en' in which or 'all' in which:
        if os.path.exists(FILM + 'english/voiceover_master_oliver.mp3'): sounds(); mix(FILM + 'english/voiceover_master_oliver.mp3', FILM + 'english/Dwarka_English_Audio_Full_Mix.m4a', FILM + 'final_english.mp4')
