# -*- coding: utf-8 -*-
"""Automatic review of each finished shot: fake lettering (OCR), look-alike stills, clip scene jumps and letterbox bars. A failing shot is redrawn with a changed prompt (max 2 redos)."""
import io, json, os, subprocess, numpy as np
from PIL import Image
from lib import *
Q = ROOT + 'queue/'; STATE = AUTO + 'qa_state.json'
VAR = [' Different composition: a low dramatic angle looking up.', ' Different composition: a wide aerial view from above.', ' Different composition: an intimate close-up with a shallow depth feel.',
       ' Different composition: a symmetrical straight-on view.', ' Different composition: seen from the water level looking toward the shore.']
def st(): return json.load(open(STATE)) if os.path.exists(STATE) else {}
def sig(path):
    im = Image.open(path).convert('RGB').resize((48, 27)); a = np.asarray(im, float); g = a.mean(2)
    hist = np.concatenate([np.histogram(a[:, :, c], bins=8, range=(0, 255))[0] for c in range(3)]).astype(float); hist /= hist.sum()
    return (g - g.mean()) / (g.std() + 1e-6), hist
def frame(clip, t):
    b = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', clip, '-frames:v', '1', '-vf', 'scale=320:180', '-f', 'image2pipe', '-vcodec', 'png', '-']); return np.asarray(Image.open(io.BytesIO(b)).convert('L'), float)
def ocr_text(still):
    try:
        j = wait(call('POST', '/v1/ocr/ocr', {'input': upload(still)})['id']); return (j['result'].get('text') or '').replace(' ', '').replace('\n', '')
    except Exception as e: return ''
def check(shot, others):
    p = FILM + 'stills/' + shot; p = p + '.png' if os.path.exists(p + '.png') else p + '.jpg'; probs = []
    t = ocr_text(p)
    if len(t) >= 6: probs.append('lettering:' + t[:20])
    g, h = sig(p)
    for o in others:
        q = FILM + 'stills/' + o; q = q + '.png' if os.path.exists(q + '.png') else q + '.jpg'
        if o == shot or not os.path.exists(q): continue
        g2, h2 = sig(q); ncc = float((g * g2).mean()); hi = float(np.minimum(h, h2).sum())
        if ncc > 0.82 and hi > 0.75: probs.append(f'lookalike:{o}:{ncc:.2f}')
    c = FILM + f'clips/{shot}.mp4'
    if os.path.exists(c):
        a, b, m = frame(c, 0.1), frame(c, 4.9), frame(c, 3.0)
        if float(np.corrcoef(a.ravel(), b.ravel())[0, 1]) < 0.30: probs.append('scene-jump')
        if m[:18].mean() < 8 and m[-18:].mean() < 8: probs.append('letterbox')
    return probs
def redo(shot, probs):
    S = st(); n = S.get(shot, {}).get('redo', 0) + 1; cfg = json.load(open(Q + 'dhanu.json')); s = next(x for x in cfg if x['shot'] == shot)
    if 'scene-jump' in probs or 'letterbox' in probs:
        s['idea'] = s['idea'].split(' Painterly')[0] + ' One single continuous shot, same framing, no scene change, no new building appears, no zoom out.' + ' Painterly hand-painted animation look, no cuts, no morphing, calm final shot.'
    else:
        base = s['prompt'].split(' Different composition:')[0].replace(' No text, no lettering, no signs, no watermark, no logo.', '')
        s['prompt'] = base + VAR[n % len(VAR)] + ' Absolutely no text, no letters, no writing, no signs anywhere. No text, no lettering, no signs, no watermark, no logo.'
    json.dump(cfg, open(Q + 'dhanu.json', 'w'), ensure_ascii=False, indent=1)
    for d, e in (('stills', 'png'), ('stills', 'jpg'), ('up', 'jpg'), ('clips', 'mp4')):
        f = f'{FILM}{d}/{shot}.{e}'
        if os.path.exists(f): os.remove(f)
    subprocess.run(['node', 'dhanu_requeue.mjs', shot], cwd=Q, check=True, capture_output=True)
    S[shot] = dict(redo=n, last=probs); json.dump(S, open(STATE, 'w')); log('QA redo', shot, probs)
def sweep(ids_done):
    """check every shot that has a clip and is not yet passed"""
    S = st(); stills_all = [s for s in ids_done]
    for shot in ids_done:
        if S.get(shot, {}).get('pass'): continue
        probs = check(shot, stills_all)
        if not probs: S[shot] = dict(S.get(shot, {}), **{'pass': True}); json.dump(S, open(STATE, 'w'))
        elif S.get(shot, {}).get('redo', 0) >= 2: S[shot] = dict(S.get(shot, {}), **{'pass': True, 'accepted_with': probs}); json.dump(S, open(STATE, 'w')); log('QA accepted after 2 redos', shot, probs)
        else: redo(shot, probs); S = st()
