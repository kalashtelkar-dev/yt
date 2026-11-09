# -*- coding: utf-8 -*-
"""Re-join the Hindi line takes with tighter, deliberate pauses (no new renders)."""
import json, os, subprocess, sys, numpy as np
from lib import *
HI = FILM + 'voice_hi/'; ORD = order(); SEC = sections(); QA = json.load(open(HI + 'qa.json'))
BEAT_END = {'A1', 'A3', 'A4', 'A6', 'B2', 'B4', 'B8', 'B9', 'B12', 'B13', 'C4', 'C7', 'C10', 'C13', 'C20', 'D2', 'D7', 'D9', 'D11', 'E3', 'E6', 'E9', 'E10'}
GAPX = {}
IN, BEAT, SECG = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
def gap(i, nxt):
    if i in GAPX: return GAPX[i]
    if i in ('C16', 'C17', 'C18', 'C19'): return 0.28
    if SEC[i] != SEC[nxt]: return SECG
    return BEAT if i in BEAT_END else IN
OVR = json.load(open(HI + 'overrides.json')) if os.path.exists(HI + 'overrides.json') else {}
X = {i: load(OVR.get(i) or f"{HI}v3/{i}_{QA[i]['attempt']}.wav") for i in ORD}; tg = np.median([np.sqrt(np.mean(v ** 2)) for v in X.values()]); t = 0.0; out = []; T = {}
for n, i in enumerate(ORD):
    x = X[i] * (tg / np.sqrt(np.mean(X[i] ** 2) + 1e-12)); fd = int(0.008 * SR); x[:fd] *= np.linspace(0, 1, fd); x[-fd:] *= np.linspace(1, 0, fd)
    g = gap(i, ORD[n + 1]) if n + 1 < len(ORD) else 0; T[i] = dict(start=round(t, 3), end=round(t + len(x) / SR, 3), sec=SEC[i]); out += [x, np.zeros(int(g * SR), dtype=np.float32)]; t += len(x) / SR + g
y = np.concatenate(out); save_wav(HI + 'raw_master.wav', y)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'raw_master.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000', '-ac', '1', HI + 'voiceover_master_sameer.wav'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'voiceover_master_sameer.wav', '-c:a', 'libmp3lame', '-b:a', '192k', FILM + 'voiceover_master_sameer.mp3'], check=True)
yn = load(HI + 'voiceover_master_sameer.wav')
for s in 'ABCDE':
    ids = [i for i in ORD if SEC[i] == s]; a = int(max(0, T[ids[0]]['start'] - 0.2) * SR); b = int(min(len(yn) / SR, T[ids[-1]]['end'] + 0.3) * SR); save_wav(HI + 'tmp.wav', yn[a:b])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', HI + 'tmp.wav', '-c:a', 'libmp3lame', '-b:a', '128k', f'{FILM}voice/{s}.mp3'], check=True)
W = words(HI + 'voiceover_master_sameer.wav'); json.dump(dict(total=round(len(yn) / SR, 3), lines=T), open(HI + 'timings.json', 'w'), indent=1); json.dump(W, open(HI + 'words.json', 'w'), ensure_ascii=False)
log('hindi reassembled', round(len(yn) / SR, 1), 's')
