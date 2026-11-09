# -*- coding: utf-8 -*-
"""Stitch the 9:16 reel: clips cut to the voice, 7 word-synced cards in quiet corners, logo, ambient music under the voice."""
import json, subprocess, io, os, numpy as np
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
POS = json.load(open('voice_hi/positions.json')); WORDS = json.load(open('voice_hi/words.json'))
TOT = POS['R13'][1]; FW, FH = 1080, 1920
def first(t0, t1=None):  # onset of the first spoken word at or after t0
    return next(w['start'] for w in WORDS if w['start'] >= t0 - 0.05)
on = {k: first(a) for k, (a, b) in POS.items()}
shots = ['R1', 'R2', 'R3', 'R4', 'R5', 'R5b', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13']
t = {s: max(0, on[s] - 0.12) for s in shots if s != 'R5b'}
t['R5b'] = next(w['start'] for w in WORDS if w['word'] == 'नक्काशी') - 0.12   # "ऐसी नक्काशी है": the second picture lands on the word
t['R1'] = 0.0
T = [t[s] for s in shots]; X = 0.2
S = [0.0] + [T[i] - X / 2 for i in range(1, len(T))]
E = [T[i + 1] + X / 2 for i in range(len(T) - 1)] + [TOT + 0.05]
CLIP = 124 / 24; ins = []; fl = []
for i, s in enumerate(shots):
    d = E[i] - S[i]; ins += ['-i', f'clips/{s}.mp4']; f = d / CLIP if d > CLIP else 1.0
    c = f"[{i}:v]scale={FW}:{FH}:flags=lanczos,setsar=1,fps=24,setpts=PTS-STARTPTS"
    if f > 1.0: c += f",setpts=PTS*{min(f, 2.0):.4f}" + (",minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if f > 1.25 else ",fps=24")
    fl.append(c + f",tpad=stop_mode=clone:stop_duration=4,trim=0:{d:.4f},setpts=PTS-STARTPTS[v{i}]")
cur = 'v0'
for i in range(len(shots) - 1):
    fl.append(f"[{cur}][v{i+1}]xfade=transition=fade:duration={X}:offset={S[i+1]:.4f}[x{i}]"); cur = f'x{i}'
n = len(shots)
# cards: (file, word, rendered duration)
w1 = lambda word, after=0: next(w['start'] for w in WORDS if w['word'] == word and w['start'] > after)
CARDS = [('n01_lakhs', w1('लाखों'), 3.6), ('n02_ayodhya_meaning', w1('अयोध्या', 5), 3.6), ('n10_pran', w1('बाईस'), 3.8), ('c03_hanumangarhi', w1('हनुमान'), 4.0),
         ('c05_paidi', w1('पैड़ी'), 4.0), ('c11_entry', w1('मुफ़्त'), 2.8), ('c13_season', w1('अक्टूबर'), 4.2)]
def png(cmd): return Image.open(io.BytesIO(subprocess.check_output(cmd)))
def bbox(f):
    a = np.asarray(png(['ffmpeg', '-loglevel', 'error', '-c:v', 'libvpx-vp9', '-ss', '1.2', '-i', f, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-']).convert('RGBA'))[:, :, 3] > 200
    ys, xs = np.where(a); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
def frame(tt):
    g = np.asarray(png(['ffmpeg', '-loglevel', 'error', '-ss', f'{tt:.3f}', '-i', 'cut.mp4', '-frames:v', '1', '-vf', 'scale=270:480,format=gray', '-f', 'image2pipe', '-vcodec', 'png', '-']), dtype=float)
    gy, gx = np.gradient(g); return np.hypot(gx, gy)
if not os.path.exists('cut.mp4'):
    ins2 = ins + ['-i', 'voice_hi/Reel_Hindi_Voiceover.mp3']
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-stats', *ins2, '-filter_complex', ';'.join(fl + [f'[{cur}]format=yuv420p[vout]']), '-map', '[vout]', '-map', f'{n}:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-r', '24', '-c:a', 'copy', '-t', f'{TOT:.3f}', 'cut.mp4'], check=True)
PAD = 24; SAFE_T, SAFE_B, MX = 280, 430, 64; place = {}; ins3 = []; fl3 = []; cur = '0:v'; k = 1
for name, wt, d in CARDS:
    f = f'../cards2/{name}.webm'; ct = round(wt - 0.45, 3)
    x0, y0, x1, y1 = bbox(f); iw, ih = 900, 220
    sc = min(1.0, 940 / (x1 - x0)); pw, ph = (x1 - x0) * sc, (y1 - y0) * sc
    cx0, cy0, cx1, cy1 = max(0, x0 - PAD), max(0, y0 - PAD), min(iw, x1 + PAD), min(ih, y1 + PAD)
    px, py = (x0 - cx0) * sc, (y0 - cy0) * sc
    cand = {'TL': (MX, SAFE_T), 'TR': (FW - MX - pw, SAFE_T), 'BL': (MX, FH - SAFE_B - ph)}
    fr = [frame(ct + d * (i + .5) / 6) for i in range(6)]; scs = {}
    for nm, (X0, Y0) in cand.items():
        s = 0
        for g in fr:
            reg = g[int(Y0 / 4):int((Y0 + ph) / 4), int(X0 / 4):int((X0 + pw) / 4)]; s += reg.mean() + 0.5 * np.percentile(reg, 90)
        scs[nm] = s
    nm = min(scs, key=scs.get); X0, Y0 = cand[nm]
    place[name] = dict(t=ct, dur=d, corner=nm, scores={a: round(b, 1) for a, b in scs.items()})
    ins3 += ['-c:v', 'libvpx-vp9', '-i', f]
    fl3.append(f"[{k}:v]format=yuva420p,crop={cx1-cx0}:{cy1-cy0}:{cx0}:{cy0},scale=iw*{sc}:ih*{sc},setpts=PTS-STARTPTS+{ct}/TB[c{k}]")
    fl3.append(f"[{cur}][c{k}]overlay=x={int(X0-px)}:y={int(Y0-py)}:eof_action=pass:enable='between(t,{ct},{ct+d})'[o{k}]"); cur = f'o{k}'; k += 1
ins3 += ['-loop', '1', '-i', '../logo_circle.png']
fl3.append(f"[{k}:v]scale=96:96[lg]"); fl3.append(f"[{cur}][lg]overlay=x={FW-24-96}:y=130:shortest=1[vout]")
json.dump(place, open('placement.json', 'w'), indent=1)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'cut.mp4', *ins3, '-filter_complex', ';'.join(fl3), '-map', '[vout]', '-map', '0:a', '-c:a', 'copy', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-r', '24', '-t', f'{TOT:.3f}', '-movflags', '+faststart', 'cards_nomusic.mp4'], check=True)
# music bed (same ambient pad as the film), ducked under the voice, soft fade at the end
def lufs(p):
    import re
    o = subprocess.run(['ffmpeg', '-nostats', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr; return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])
mg = -30 - lufs('../sfx/music.mp4')
fm = (f"[0:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];[1:a]aformat=channel_layouts=stereo,volume={mg:.2f}dB,atrim=0:{TOT},afade=t=in:d=1.5,afade=t=out:st={TOT-2.5}:d=2.5[m];"
      f"[m][v1]sidechaincompress=threshold=0.015:ratio=4:attack=30:release=600[mm];[v2][mm]amix=inputs=2:normalize=0:duration=first,atrim=0:{TOT}[out]")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'voice_hi/Reel_Hindi_Voiceover.wav', '-stream_loop', '-1', '-i', '../sfx/music.mp4', '-filter_complex', fm, '-map', '[out]', '-c:a', 'pcm_s16le', 'mix_raw.wav'], check=True)
g = -15 - lufs('mix_raw.wav')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'mix_raw.wav', '-af', f'volume={g:.2f}dB,alimiter=limit=0.89', '-c:a', 'aac', '-b:a', '192k', 'mix.m4a'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'cards_nomusic.mp4', '-i', 'mix.m4a', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', f'{TOT:.3f}', '-movflags', '+faststart', 'Ayodhya_Reel_Hindi_9x16.mp4'], check=True)
print('done', place, 'final lufs', lufs('Ayodhya_Reel_Hindi_9x16.mp4'))
