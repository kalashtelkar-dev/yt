# -*- coding: utf-8 -*-
"""Round 3 of voice fixes: sad-but-straight A2 and A3, majestic A4, जरा and बेट द्वारका spliced from takes the user already accepted, slower C1 to C3, आठ in E3."""
import difflib
exec(open('retakes.py').read().split("log('retakes start')")[0])
log('fixes2 start')
def old(i): return OV.get(i) or f"{V}{i}_{json.load(open(HI + 'qa.json'))[i]['attempt']}.wav"
def sim(a, b): return difflib.SequenceMatcher(None, re.sub('[^ऀ-ॿ]', '', a.replace('़', '').replace('ज़', 'ज')), b).ratio()
def find_seq(ws, seq):
    for k in range(len(ws) - len(seq) + 1):
        if all(sim(ws[k + n]['word'], seq[n]) >= 0.6 for n in range(len(seq))): return ws[k]['start'], ws[k + len(seq) - 1]['end']
    return None
def splice(tgt, tseq, donor, dseq, out, pre=0.06, post=0.03):
    tw, dw = words(tgt), words(donor); t = find_seq(tw, tseq); d = find_seq(dw, dseq)
    if not t or not d: log('splice miss', tgt, tseq, bool(t), bool(d)); return tgt
    X, Dn = load(tgt), load(donor); a, b = int(max(0, t[0] - pre) * SR), int(min(len(X) / SR, t[1] + post) * SR); seg = Dn[int(max(0, d[0] - pre) * SR):int(min(len(Dn) / SR, d[1] + post) * SR)]
    f = min(1.25, max(0.8, len(seg) / max(1, b - a)))
    if abs(f - 1) > 0.02: seg = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={f:.4f}', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'], input=seg.tobytes(), capture_output=True, check=True).stdout, dtype=np.float32).copy()
    rms = lambda v: float(np.sqrt(np.mean(v ** 2) + 1e-12)); seg = seg * (rms(X[a:b]) / rms(seg)); xf = int(0.012 * SR); fi = np.linspace(0, 1, xf)
    pre = X[:a].copy(); post = X[b:].copy()
    if len(pre) >= xf: pre[-xf:] = pre[-xf:] * (1 - fi) + seg[:xf] * fi
    if len(post) >= xf: post[:xf] = post[:xf] * fi + seg[-xf:] * (1 - fi)
    Y = np.concatenate([pre, seg[xf:-xf], post])
    save_wav(out, Y); return out
# 1. A2, A3: straight and a little sad
OV['A2'] = make([('A2', '[playful] ', '[sad] ', None, None)])[0][1]
OV['A3'] = make([('A3', '[sad] ', '', None, None)])[0][1]
# 2. A4: majestic = lower and slower, pick the lowest pitch among variants
c = make([('A4', '', '[proud] ', s, None) for s in (None, 101, 202)] + [('A4', '', '[low voice] ', s, None) for s in (None, 101)]); bd = None
for i, p in c:
    if not p: continue
    x = load(p); fz = f0(x, 0.05, len(x) / SR - 0.05) or 999; log('A4 variant f0', round(fz))
    if bd is None or fz < bd[0]: bd = (fz, p)
OV['A4'] = tempo(bd[1], f'{V}fx3_A4_t.wav', 0.92)
# 3. जरा from B7, बेट द्वारका from C5 (both accepted by the user)
OV['B6'] = splice(f"{V}B6_{json.load(open(HI + 'qa.json'))['B6']['attempt']}.wav", ['जरा'], old('B7'), ['जरा'], f'{V}fx3_B6.wav')
for i in ('C13', 'C20', 'D10', 'E5'): OV[i] = splice(old(i), ['बेट', 'द्वारका'], old('C5'), ['बेट', 'द्वारका'], f'{V}fx3_{i}.wav')
# 4. C1 to C3: slower reading
SPEED = 'slow'
for i in ('C1', 'C2', 'C3'):
    p = make([(i, '[playful] ', '', None, None)])[0][1]; OV[i] = tempo(p, f'{V}fx3_{i}_t.wav', 1.10)
SPEED = 'normal'
# 5. E3: choose the variant whose word end is least hissy (a soft ठ, not च)
cands = make([('E3', '[playful] ', '', None, pr) for pr in (None, {'आठ': 'आट'}, {'आठ': 'आठ्ठ'}, {'आठ': 'आठह'}, {'आठ': 'अाठ'}, {'आठ': 'आथ'})]); bst = None
for i, p in cands:
    if not p: continue
    ws = words(p); w = next((a for a in ws if sim(a['word'], 'आठ') >= 0.6), None)
    if not w: continue
    x = load(p); seg = x[int(max(0, w['end'] - 0.12) * SR):int(w['end'] * SR)]; sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 2048)) ** 2; fr = np.fft.rfftfreq(2048, 1 / SR); hf = float(sp[fr > 3500].sum() / (sp.sum() + 1e-9)); log('E3 variant hf', round(hf, 3))
    if bst is None or hf < bst[0]: bst = (hf, p)
if bst: OV['E3'] = bst[1]
json.dump({k: v for k, v in OV.items() if v}, open(HI + 'overrides.json', 'w'), indent=1); log('fixes2 done')
