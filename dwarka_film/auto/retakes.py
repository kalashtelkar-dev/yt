# -*- coding: utf-8 -*-
"""Fix exactly the lines the user marked Wrong (round 2), keep every line marked Right. Picks the best of several variants by measurement."""
import json, os, re, subprocess, numpy as np
from lib import *
HI = FILM + 'voice_hi/'; V = HI + 'v3/'; S = script('hi'); ORD = order(); SEC = sections(); OV = json.load(open(HI + 'overrides.json')) if os.path.exists(HI + 'overrides.json') else {}
LIST = {'C16', 'C17', 'C18', 'C19', 'C20'}
def body(ctx, tag_all, extra, seed=None, pr=None, final_tag=''):
    lines = []
    for n, i in enumerate(ctx):
        t = S[i]; t = t[:-1] + '।' if i in LIST and t.endswith(',') else t; tg = (tag_all if i != ctx[-1] else (final_tag or tag_all)); lines.append(tg + t)
    b = {'text': '\n'.join(lines), 'voice': 'sameer', 'speed': globals().get('SPEED', 'normal'), 'expressiveness': 'normal', 'format': 'wav', 'lineGapMs': 550, 'idempotencyKey': 'dw-fix2-' + ctx[-1] + '-' + str(abs(hash((tag_all, final_tag, seed, json.dumps(pr, sort_keys=True), globals().get('SPEED', 'normal')))) % 10 ** 8)}
    if seed: b['seed'] = seed
    if pr: b['pronounce'] = pr
    return b
def make(ids_variants):
    """ids_variants: list of (id, tag_all, final_tag, seed, pronounce); renders all through the ops queue, returns list of (id, wav path of the target line)"""
    bodies = []; meta = []
    for i, tag_all, final_tag, seed, pr in ids_variants:
        pos = ORD.index(i); ctx = ORD[max(0, pos - 1):pos + 1] if pos else [i]; bodies.append(body(ctx, tag_all, {}, seed, pr, final_tag)); meta.append((i, ctx))
    jobs = run_many('/v1/emotive-speech/speak', bodies); keys = {k: out_key(j) for k, j in enumerate(jobs) if j['status'] == 'succeeded'}; urls = sign(list(keys.values())); out = []
    for k, (i, ctx) in enumerate(meta):
        if k not in keys: out.append((i, None)); continue
        p = f'{V}fx_{i}_{k}_{len(os.listdir(V))}.wav'; fetch(urls[keys[k]], p); L = jobs[k]['result']['lines'][-1]; x = load(p)
        s = max(0, int((L['startSec'] - 0.04) * SR)); e = min(len(x), int((L['endSec'] + 0.06) * SR)); d = p.replace('.wav', '_line.wav'); save_wav(d, x[s:e]); out.append((i, d))
    return out
def tempo(src, dst, f):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', f'atempo={f:.3f}', '-ar', str(SR), '-ac', '1', dst], check=True); return dst
def trans(p): return words(p)
def has(ws, target, nukta=None):
    for w in ws:
        t = w['word']
        if target in t.replace('़', '').replace('ज़', 'ज'):
            if nukta is None or (('़' in t or 'ज़' in t) == nukta): return w
    return None
def f0(x, a, b):
    seg = x[int(a * SR):int(b * SR)]; n = int(0.04 * SR); out = []
    for k in range(0, len(seg) - n, int(0.01 * SR)):
        f = seg[k:k + n]
        if np.sqrt(np.mean(f ** 2)) < 0.02: continue
        r = np.correlate(f, f, 'full')[n - 1:]; lo, hi = int(SR / 300), int(SR / 70)
        if hi >= len(r): continue
        pk = lo + int(np.argmax(r[lo:hi]))
        if r[pk] > 0.3 * r[0]: out.append(SR / pk)
    return float(np.median(out)) if out else None
def pick_pron(i, variants, target, nukta=None, pause=None):
    cands = make([(i, '[playful] ' if i not in ('D10',) else '', '', None, pr) for pr in variants]); best = None
    for (ii, p), pr in zip(cands, variants):
        if not p: continue
        ws = trans(p); w = has(ws, target, nukta); sc = (2 if w else 0) + (w['score'] if w else 0)
        if pause:
            a = has(ws, pause[0]); b = has(ws, pause[1])
            if a and b: sc += 1 if b['start'] - a['end'] < 0.25 else 0
        log('variant', i, pr, round(sc, 2))
        if best is None or sc > best[0]: best = (sc, p)
    return best[1] if best else None
def plain(i, seed=None, tag=''): return make([(i, '', tag, seed, None)])[0][1]
log('retakes start')
# pronunciation lines
OV['B6'] = pick_pron('B6', [None, {'जरा': 'जर्रा'}, {'जरा': 'जराः'}], 'जरा', nukta=False)
for i in ('C13', 'C20', 'D10'): OV[i] = pick_pron(i, [None, {'बेट': 'बेट्'}, {'बेट': 'बेयट'}, {'बेट': 'बे ट'}], 'बेट')
OV['E3'] = pick_pron('E3', [None, {'आठ': 'आट्ठ'}, {'आठ': 'आठ्'}, {'आठ': 'आ ठ'}], 'आठ')
OV['E5'] = pick_pron('E5', [None, {'दोपहर': 'दो पहर'}, {'दोपहर': 'दोपहर्'}], 'दोपहर')
OV['E9'] = pick_pron('E9', [{'भीड़': 'भीड'}, {'भीड़': 'भीड़'}, {'भीड़': 'भीर'}], 'भीड')
OV['E1'] = pick_pron('E1', [None, {'अब': 'अब्'}, {'अब': 'ऐब'}], 'अब', pause=('अब', 'एक'))
# emotion lines: plain, then pace
for i in ('C7', 'C10', 'C11', 'C12', 'E10'): OV[i] = plain(i)
for i in ('D2', 'D6', 'D7', 'D8', 'D9'): OV[i] = tempo(plain(i), f'{V}fx_{i}_t.wav', 1.08)
OV['C9'] = tempo(plain('C9'), f'{V}fx_C9_t.wav', 0.95)
OV['A4'] = tempo(plain('A4', tag='[proud] '), f'{V}fx_A4_t.wav', 0.93)
# E12: pick the variant whose pitch falls most at the end
cands = make([('E12', '[playful] ', '[playful] ', s, None) for s in (None, 101, 202, 303)] + [('E12', '', '[calm] ', s, None) for s in (None, 101)]); bestd = None
for i, p in cands:
    if not p: continue
    x = load(p); d = len(x) / SR; a = f0(x, d - 0.45, d - 0.05); b = f0(x, d - 1.0, d - 0.5); drop = (b - a) if a and b else -99; log('E12 variant drop', round(drop, 1))
    if bestd is None or drop > bestd[0]: bestd = (drop, p)
OV['E12'] = bestd[1]
# pace only (kept takes)
def old(i): return OV.get(i) or f"{V}{i}_{json.load(open(HI + 'qa.json'))[i]['attempt']}.wav"
for i in ('B9', 'B10', 'B12'): OV[i] = tempo(old(i), f'{V}fx_{i}_t.wav', 1.10)
for i in ('C1', 'C2', 'C3'): OV[i] = tempo(old(i), f'{V}fx_{i}_t.wav', 0.90)
json.dump({k: v for k, v in OV.items() if v}, open(HI + 'overrides.json', 'w'), indent=1); log('retakes done', len(OV), 'lines')
