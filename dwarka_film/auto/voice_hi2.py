# -*- coding: utf-8 -*-
"""Hindi voiceover v2: each BEAT is read as one passage (continuity, so tone and pronunciation stay the same inside a section), then cut into lines.
Risky lines are retaken inside their neighbours so the retake keeps the same voice. Same outputs as voice_hi.py."""
import difflib, json, os, re, shutil, subprocess, numpy as np
from lib import *
HI = FILM + 'voice_hi/'; os.makedirs(HI + 'v2', exist_ok=True)
S = script('hi'); ORD = order(); SEC = sections()
BEATS = [['A1'], ['A2', 'A3'], ['A4'], ['A5', 'A6'], ['B1', 'B2'], ['B3', 'B4'], ['B5', 'B6', 'B7', 'B8'], ['B9'], ['B10', 'B12'], ['B13'], ['C1', 'C2', 'C3', 'C4'], ['C5', 'C7'], ['C9', 'C10'], ['C11', 'C12', 'C13'],
         ['C16', 'C17', 'C18', 'C19', 'C20'], ['D1', 'D2'], ['D6', 'D7'], ['D8', 'D9'], ['D10', 'D11'], ['E1', 'E2', 'E3'], ['E5', 'E6'], ['E7', 'E8', 'E9'], ['E10'], ['E11', 'E12']]
assert [i for b in BEATS for i in b] == ORD
TAGS = {'A1': '[excited] ', 'A2': '[sad] ', 'A3': '[surprised] ', 'A4': '[proud] ', 'A5': '[excited] ', 'A6': '[happy] ', 'B4': '[sad] ', 'B6': '[surprised] ', 'B10': '[scared] ', 'B12': '[scared] ', 'B13': '[confused] ', 'C3': '[surprised] ', 'C5': '[excited] ', 'E11': '[playful] '}
LIST = {'C16', 'C17', 'C18', 'C19', 'C20'}
def txt(i): t = S[i]; return TAGS.get(i, '') + (t[:-1] + '।' if i in LIST and t.endswith(',') else t)
def norm(w): return re.sub(r'[^ऀ-ॿ\w]', '', w.replace('़', ''))
def render(sections_of_beats, tag):
    """sections_of_beats: list of lists of ids (one passage each). returns {passage_index: (wav path, [(id, start, end)])}"""
    bodies = [{'text': '\n'.join(txt(i) for i in ids), 'voice': 'sameer', 'speed': 'normal', 'expressiveness': 'high' if SEC[ids[0]] in 'ABC' else 'normal', 'format': 'wav', 'lineGapMs': 450, 'continuity': True, 'idempotencyKey': f'dw-hi3-{tag}-{k}-{ids[0]}-{len(ids)}'} for k, ids in enumerate(sections_of_beats)]
    jobs = run_many('/v1/emotive-speech/speak', bodies); res = {}; keys = {}
    for k, (ids, j) in enumerate(zip(sections_of_beats, jobs)):
        if j['status'] != 'succeeded': log('speak failed', ids[0], j.get('error')); continue
        keys[k] = out_key(j)
    urls = sign(list(keys.values()))
    for k, key in keys.items():
        p = f'{HI}v2/{tag}_{k}.wav'; fetch(urls[key], p); L = jobs[k]['result']['lines']
        res[k] = (p, [(i, l['startSec'], l['endSec']) for i, l in zip(sections_of_beats[k], L)])
    return res
def slice_line(p, a, b, dst):
    x = load(p); s = max(0, int((a - 0.04) * SR)); e = min(len(x), int((b + 0.06) * SR)); save_wav(dst, x[s:e]); return dst
def fric(x, t):
    a = int(max(0, t - 0.15) * SR); b = int(max(0, t - 0.01) * SR); seg = x[a:b]
    if len(seg) < 800: return None
    f = np.fft.rfftfreq(2048, 1 / SR); n = int(0.015 * SR); best = None
    for k in range(0, max(1, len(seg) - n), int(0.005 * SR)):
        s = np.abs(np.fft.rfft(seg[k:k + n] * np.hanning(n), 2048)) ** 2
        if s.sum() < 1e-9: continue
        if s[f > 3500].sum() / s.sum() > 0.5: c = float((f * s).sum() / s.sum()); best = c if best is None else max(best, c)
    return best
def judge(i, wav):
    w = words(wav); x = load(wav); sw = [norm(t) for t in re.split(r'\s+', S[i]) if norm(t)]; tw = [norm(a['word']) for a in w]
    cov = sum(1 for t in sw if any(difflib.SequenceMatcher(None, t, u).ratio() >= 0.7 for u in tw)) / max(1, len(sw)); bad = []
    for a in w:
        if norm(a['word']).startswith('स'):
            c = fric(x, a['start'])
            if c is not None and c < 5800: bad.append((a['word'], round(c)))
    return cov, bad
# 1. beats as passages
log('hindi v2: rendering', len(BEATS), 'beats'); R = render(BEATS, 'b'); LINE = {}   # id -> wav path of the line slice
for k, (p, segs) in R.items():
    for i, a, b in segs: LINE[i] = (slice_line(p, a, b, f'{HI}v2/{i}_0.wav'), a, b, k)
# 2. QA, retake inside neighbours
best = {}; todo = list(ORD)
for attempt in range(3):
    flagged = []
    for i in todo:
        try: cov, bad = judge(i, LINE[i][0])
        except Exception as e: log('judge error', i, e); cov, bad = 0, []
        sc = cov - 0.5 * len(bad)
        if i not in best or sc > best[i][0]: best[i] = (sc, LINE[i][0], cov, bad, attempt)
        if cov < 0.85 or bad: flagged.append(i); log('retake', i, 'coverage', round(cov, 2), 'sh-risk', bad)
    if not flagged or attempt == 2: break
    passages = []; targets = []
    for i in flagged:
        pos = ORD.index(i); ctx = [j for j in ORD[max(0, pos - 2):pos + 1]]; passages.append(ctx); targets.append(i)
    R2 = render(passages, f'r{attempt}')
    for k, (p, segs) in R2.items():
        i, a, b = segs[-1]; assert i == targets[k]; LINE[i] = (slice_line(p, a, b, f'{HI}v2/{i}_{attempt+1}.wav'), a, b, -1)
    todo = flagged
json.dump({i: dict(attempt=v[4], coverage=v[2], shrisk=v[3]) for i, v in best.items()}, open(HI + 'qa.json', 'w'), ensure_ascii=False, indent=1)
# 3. assemble with the engine's own pauses (kept between 0.3 and 1.4 s), loudnorm, sections, words
gaps = {}
for k, (p, segs) in R.items():
    for n in range(len(segs) - 1): gaps[segs[n][0]] = min(1.4, max(0.3, segs[n + 1][1] - segs[n][2]))
GAPX = {'A1': 0.95, 'A2': 0.7, 'A3': 1.35, 'A4': 0.55, 'A5': 0.75, 'B12': 1.0, 'B13': 1.15, 'C4': 0.9}
def gap(i, nxt):
    if i in GAPX: return GAPX[i]
    if SEC[i] != SEC[nxt]: return 1.0
    if BEATS_NEXT.get(i): return 0.85
    return gaps.get(i, 0.5)
BEATS_NEXT = {b[-1]: True for b in BEATS[:-1]}
X = {i: load(best[i][1]) for i in ORD}; tg = np.median([np.sqrt(np.mean(v ** 2)) for v in X.values()]); t = 0.0; out = []; T = {}
for n, i in enumerate(ORD):
    x = X[i] * (tg / np.sqrt(np.mean(X[i] ** 2) + 1e-12)); fd = int(0.008 * SR); x[:fd] *= np.linspace(0, 1, fd); x[-fd:] *= np.linspace(1, 0, fd)
    g = gap(i, ORD[n + 1]) if n + 1 < len(ORD) else 0; T[i] = dict(start=round(t, 3), end=round(t + len(x) / SR, 3), sec=SEC[i]); out += [x, np.zeros(int(g * SR), dtype=np.float32)]; t += len(x) / SR + g
y = np.concatenate(out); save_wav(HI + 'raw_master.wav', y)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'raw_master.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000', '-ac', '1', HI + 'voiceover_master_sameer.wav'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'voiceover_master_sameer.wav', '-c:a', 'libmp3lame', '-b:a', '192k', FILM + 'voiceover_master_sameer.mp3'], check=True)
yn = load(HI + 'voiceover_master_sameer.wav'); os.makedirs(FILM + 'voice', exist_ok=True)
for s in 'ABCDE':
    ids = [i for i in ORD if SEC[i] == s]; a = int(max(0, T[ids[0]]['start'] - 0.2) * SR); b = int(min(len(yn) / SR, T[ids[-1]]['end'] + 0.3) * SR); save_wav(HI + 'tmp.wav', yn[a:b])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'tmp.wav', '-c:a', 'libmp3lame', '-b:a', '128k', f'{FILM}voice/{s}.mp3'], check=True)
W = words(HI + 'voiceover_master_sameer.wav'); json.dump(dict(total=round(len(yn) / SR, 3), lines=T), open(HI + 'timings.json', 'w'), indent=1); json.dump(W, open(HI + 'words.json', 'w'), ensure_ascii=False)
log('hindi v2 done', round(len(yn) / SR, 1), 's;', sum(1 for v in best.values() if v[2] < 0.85 or v[3]), 'lines still flagged')
