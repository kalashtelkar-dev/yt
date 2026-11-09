# -*- coding: utf-8 -*-
"""English voiceover (Oliver, short chunks) placed on the Hindi timeline, plus the English SRT."""
import json, os, re, subprocess, numpy as np
from lib import *
EN = FILM + 'english/'; os.makedirs(EN + 'lines', exist_ok=True); os.makedirs(EN + 'trim', exist_ok=True)
S = script('en'); ORD = [i for i in order() if i in S]; HI = FILM + 'voice_hi/'
T = json.load(open(HI + 'timings.json')); WORDS = json.load(open(HI + 'words.json')); TOT = T['total']
def onset(i):
    a, b = T['lines'][i]['start'], T['lines'][i]['end']; return next((w['start'] for w in WORDS if a - 0.05 <= w['start'] <= b), a)
ON = {i: onset(i) for i in ORD}
have = all(os.path.exists(f'{EN}trim/{i}.wav') for i in ORD)
keys = {i: True for i in ORD} if have else {}
if not have:
    jobs = run_many('/v1/emotive-speech/speak', [{'text': ('[playful] ' if i == 'E11' else '') + S[i], 'voice': 'oliver', 'speed': 'normal', 'expressiveness': 'normal', 'format': 'wav', 'idempotencyKey': f'dw-en-{i}-v1'} for i in ORD])
    keys = {i: out_key(j) for i, j in zip(ORD, jobs) if j['status'] == 'succeeded'}; urls = sign(list(keys.values()))
    for i, k in keys.items(): fetch(urls[k], f'{EN}lines/{i}.wav'); trim_sil(f'{EN}lines/{i}.wav', f'{EN}trim/{i}.wav')
def fit(x, f):
    if f <= 1.001: return x
    b = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={f:.4f}', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'], input=x.tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(b, dtype=np.float32).copy()
rms = lambda a: float(np.sqrt(np.mean(a ** 2) + 1e-12))
L = {i: load(f'{EN}trim/{i}.wav') for i in ORD if i in keys}; tg = np.median([rms(v) for v in L.values()])
out = np.zeros(int((TOT + 1) * SR), dtype=np.float32); placed = {}; nxt = {ORD[k]: (ON[ORD[k + 1]] if k + 1 < len(ORD) else TOT) for k in range(len(ORD))}
last_end = 0.0   # natural delivery: no speed-up; a line that would overlap the previous one starts just after it
for i in ORD:
    if i not in L: continue
    x = (L[i] * (tg / rms(L[i]))).astype(np.float32); start = max(ON[i], last_end + 0.12); late = start - ON[i]
    if late > 0.6: x = fit(x, min(1.08, 1 + (late - 0.6) / (len(x) / SR)))   # only when it would drift more than 0.6 s behind the picture
    fd = int(0.01 * SR); x[:fd] *= np.linspace(0, 1, fd); x[-fd:] *= np.linspace(1, 0, fd); a = int(start * SR); out[a:a + len(x)] += x[:max(0, len(out) - a)]
    placed[i] = (start, start + len(x) / SR); last_end = start + len(x) / SR
out = out[:int(TOT * SR)]; save_wav(EN + 'voice_raw.wav', out); tgt = lufs(FILM + 'voiceover_master_sameer.mp3')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', EN + 'voice_raw.wav', '-af', f'loudnorm=I={tgt}:TP=-1.5:LRA=7,aresample=48000', '-ac', '1', EN + 'voiceover_master_oliver.wav'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', EN + 'voiceover_master_oliver.wav', '-c:a', 'libmp3lame', '-b:a', '192k', EN + 'voiceover_master_oliver.mp3'], check=True)
json.dump(placed, open(EN + 'placed.json', 'w'))
def wrap(s, w=40):
    if len(s) <= w: return s
    ws = s.split(); b = None
    for k in range(1, len(ws)):
        a, c = ' '.join(ws[:k]), ' '.join(ws[k:]); sc = abs(len(a) - len(c))
        if b is None or sc < b[0]: b = (sc, a, c)
    return b[1] + '\n' + b[2]
cues = []
for i, (a, b) in placed.items():
    parts = [p.strip() for p in re.split(r'(?<=[,.?!])\s+', S[i]) if p.strip()]; ch = []; cur = ''
    for p in parts:
        if cur and len(cur) + len(p) + 1 > 70: ch.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    if cur: ch.append(cur)
    tot = sum(len(c) for c in ch); t = a
    for c in ch: e = t + (b - a) * len(c) / tot; cues.append([t, e, c]); t = e
for k in range(len(cues) - 1): cues[k][1] = min(cues[k][1], cues[k + 1][0] - 0.02)
ts = lambda t: f'{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round((t%1)*1000))%1000:03d}'
os.makedirs(FILM + 'youtube', exist_ok=True)
open(FILM + 'youtube/Dwarka_English_Subtitles.srt', 'w', encoding='utf-8').write('\n'.join(f'{k+1}\n{ts(a)} --> {ts(b)}\n{wrap(c)}\n' for k, (a, b, c) in enumerate(cues)))
log('english voice done', len(placed), 'lines')
