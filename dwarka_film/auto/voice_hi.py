# -*- coding: utf-8 -*-
"""Hindi voiceover (Sameer): per-line renders, automatic QA (missing words, sh-for-s), retakes, assembly, section files, word timings."""
import difflib, json, os, re, subprocess, numpy as np
from lib import *
HI = FILM + 'voice_hi/'; os.makedirs(HI + 'raw', exist_ok=True); os.makedirs(HI + 'trim', exist_ok=True)
S = script('hi'); ORD = order(); SEC = sections()
TAG = {'E11': '[playful] '}
SEEDS = [None, 101, 202, 303]
def body(i, seed):
    b = {'text': TAG.get(i, '') + S[i], 'voice': 'sameer', 'speed': 'normal', 'expressiveness': 'normal', 'format': 'wav', 'idempotencyKey': f'dw-hi-{i}-{seed or 0}-v1'}
    if seed: b['seed'] = seed
    return b
def render(ids, attempt):
    seed = SEEDS[attempt]; jobs = run_many('/v1/emotive-speech/speak', [body(i, seed) for i in ids]); keys = {}
    for i, j in zip(ids, jobs):
        if j['status'] != 'succeeded': log('speak failed', i, j.get('error')); continue
        keys[i] = out_key(j)
    urls = sign(list(keys.values()))
    for i, k in keys.items():
        raw = f'{HI}raw/{i}_{attempt}.wav'; fetch(urls[k], raw); trim_sil(raw, f'{HI}trim/{i}_{attempt}.wav')
def norm(w): return re.sub(r'[^ऀ-ॿ\w]', '', w.replace('़', ''))
def fric(x, t):  # centroid (Hz) of the frication just before a word the aligner starts at its vowel
    a = int(max(0, t - 0.15) * SR); b = int(max(0, t - 0.01) * SR); seg = x[a:b]
    if len(seg) < 800: return None
    f = np.fft.rfftfreq(2048, 1 / SR); n = int(0.015 * SR); best = None
    for k in range(0, max(1, len(seg) - n), int(0.005 * SR)):
        s = np.abs(np.fft.rfft(seg[k:k + n] * np.hanning(n), 2048)) ** 2
        if s.sum() < 1e-9: continue
        hf = s[f > 3500].sum() / s.sum(); c = float((f * s).sum() / s.sum())
        if hf > 0.5 and (best is None or True): best = c if best is None else max(best, c)
    return best
def judge(i, attempt):
    p = f'{HI}trim/{i}_{attempt}.wav'; w = words(p); x = load(p)
    sw = [norm(t) for t in re.split(r'\s+', S[i]) if norm(t)]; tw = [norm(a['word']) for a in w]
    got = sum(1 for t in sw if any(difflib.SequenceMatcher(None, t, u).ratio() >= 0.7 for u in tw)); cov = got / max(1, len(sw))
    bad = []
    for a in w:
        if norm(a['word']).startswith('स'):  # words starting with स
            c = fric(x, a['start'])
            if c is not None and c < 5800: bad.append((a['word'], round(c)))
    return cov, bad
best = {}; todo = list(ORD)
for attempt in range(len(SEEDS)):
    if not todo: break
    log('hindi voice attempt', attempt, len(todo), 'lines'); render(todo, attempt); nxt = []
    for i in todo:
        try: cov, bad = judge(i, attempt)
        except Exception as e: log('judge error', i, e); cov, bad = 0, []
        score = cov - 0.5 * len(bad)
        if i not in best or score > best[i][0]: best[i] = (score, attempt, cov, bad)
        if cov < 0.85 or bad: nxt.append(i); log('retake', i, 'coverage', round(cov, 2), 'sh-risk', bad)
    todo = nxt
json.dump({i: dict(attempt=a, coverage=c, shrisk=b) for i, (s, a, c, b) in best.items()}, open(HI + 'qa.json', 'w'), ensure_ascii=False, indent=1)
# assemble
def gap(i, nxt):
    if SEC[i] != SEC[nxt]: return 0.9
    if i in ('C16', 'C17', 'C18', 'C19'): return 0.28
    return 0.55
X = {i: load(f'{HI}trim/{i}_{best[i][1]}.wav') for i in ORD}; tg = np.median([np.sqrt(np.mean(v ** 2)) for v in X.values()])
t = 0.0; out = []; T = {}
for n, i in enumerate(ORD):
    x = X[i] * (tg / np.sqrt(np.mean(X[i] ** 2) + 1e-12)); fd = int(0.008 * SR); x[:fd] *= np.linspace(0, 1, fd); x[-fd:] *= np.linspace(1, 0, fd)
    T[i] = dict(start=round(t, 3), end=round(t + len(x) / SR, 3), sec=SEC[i]); g = gap(i, ORD[n + 1]) if n + 1 < len(ORD) else 0
    out += [x, np.zeros(int(g * SR), dtype=np.float32)]; t += len(x) / SR + g
y = np.concatenate(out); save_wav(HI + 'raw_master.wav', y)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'raw_master.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000', '-ac', '1', HI + 'voiceover_master_sameer.wav'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'voiceover_master_sameer.wav', '-c:a', 'libmp3lame', '-b:a', '192k', FILM + 'voiceover_master_sameer.mp3'], check=True)
yn = load(HI + 'voiceover_master_sameer.wav')
for s in 'ABCDE':
    ids = [i for i in ORD if SEC[i] == s]; a = int(max(0, T[ids[0]]['start'] - 0.2) * SR); b = int(min(len(yn) / SR, T[ids[-1]]['end'] + 0.3) * SR)
    save_wav(f'{HI}tmp.wav', yn[a:b]); subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{HI}tmp.wav', '-c:a', 'libmp3lame', '-b:a', '128k', f'{FILM}voice/{s}.mp3'] if os.makedirs(FILM + 'voice', exist_ok=True) is None else [], check=True)
W = words(HI + 'voiceover_master_sameer.wav')
json.dump(dict(total=round(len(yn) / SR, 3), lines=T), open(HI + 'timings.json', 'w'), indent=1); json.dump(W, open(HI + 'words.json', 'w'), ensure_ascii=False)
log('hindi voice done', round(len(yn) / SR, 1), 's;', sum(1 for v in best.values() if v[2] < 0.85 or v[3]), 'lines still flagged')
