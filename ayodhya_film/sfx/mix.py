"""Stage 6 mix: per-shot sound beds + ambient music under the voice, ducked locally with ffmpeg.
Run from ayodhya_film/sfx. Writes mix.m4a and final.mp4 (../final.mp4)."""
import json, re, subprocess, collections

T = json.load(open('../timing.json'))
win = {s: (T['start'][i], T['end'][i]) for i, s in enumerate(T['shots'])}
TOT = 301.293
# source -> target loudness (LUFS) of the bed before ducking; all very soft, wind-like beds softest
LV = dict(river=-37, fire=-40, birds=-39, crick=-40, crowd=-37, road=-36, train=-36, jet=-31)
MAP = {
 'river': 'A1 A3 B4b C3 C7 C8 C9 C9b C14 C15 D9 E1 E2 E6 E6b E10 E12',
 'fire':  'B3 B5 B6 B9 C4 C6 E6',
 'birds': 'A2 C1 C2 C5 D6 D8 E3 E4 E9 B10',
 'crick': 'A5b D7b B4b E10 E12',
 'crowd': 'A6 D5',
 'road':  'D1 D3 D3b',
 'train': 'D2 D2b',
 'jet':   'D4',
}
segs = [(s, k) for k, v in MAP.items() for s in v.split()]
segs = [(s, k) for s, k in segs if s in win]

def lufs(f):
    o = subprocess.run(['ffmpeg', '-nostats', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])
src_l = {k: lufs(f'{k}.mp4') for k in LV}
srcdur = {'river': 34, 'fire': 14, 'birds': 64, 'crick': 60, 'crowd': 60, 'road': 60, 'train': 60, 'jet': 16}
used = collections.defaultdict(float)

ins, fl, lab = [], [], []
FADE = 0.6
for i, (s, k) in enumerate(segs):
    a, b = win[s]; d = b - a
    off = used[k] % max(1, srcdur[k] - d - 0.1); used[k] += d + 3
    if k == 'jet': off = 0
    ins += ['-ss', f'{off:.2f}', '-t', f'{d:.3f}', '-i', f'{k}.mp4']
    g = LV[k] - src_l[k]
    # layered shots keep each layer a little lower
    if sum(1 for kk, v in MAP.items() if s in v.split()) > 1: g -= 2
    fl.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,"
              f"afade=t=in:d={FADE},afade=t=out:st={max(0, d - FADE):.3f}:d={FADE},adelay={int(a*1000)}|{int(a*1000)}[b{i}]")
    lab.append(f'[b{i}]')
n = len(segs)
fl.append(''.join(lab) + f'amix=inputs={n}:normalize=0:duration=longest,apad,atrim=0:{TOT}[bed]')
ins += ['-i', '../voiceover_master_sameer.mp3']
vi = n
ins += ['-stream_loop', '-1', '-i', 'music.mp4']
mi = n + 1
fl.append(f'[{vi}:a]aformat=channel_layouts=stereo,asplit=3[v0][v1][v2]')
fl.append('[bed][v0]sidechaincompress=threshold=0.015:ratio=5:attack=30:release=500[bedd]')
mg = -31 - lufs('music.mp4')
fl.append(f"[{mi}:a]aformat=channel_layouts=stereo,volume={mg:.2f}dB,atrim=0:{TOT},afade=t=in:d=3,afade=t=out:st={TOT-3}:d=3[m]")
fl.append('[m][v1]sidechaincompress=threshold=0.015:ratio=4:attack=30:release=600[mm]')
fl.append(f'[v2][bedd][mm]amix=inputs=3:normalize=0:duration=first,atrim=0:{TOT}[out]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(fl), '-map', '[out]', '-c:a', 'pcm_s16le', 'mix_raw.wav'], check=True)
L = lufs('mix_raw.wav'); gain = -16 - L
print('segments', n, 'raw LUFS', L, 'gain', gain)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'mix_raw.wav', '-af', f'volume={gain:.2f}dB,alimiter=limit=0.89', '-c:a', 'aac', '-b:a', '192k', 'mix.m4a'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '../final_nosfx.mp4', '-i', 'mix.m4a', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-t', str(TOT + 0.04), '-movflags', '+faststart', '../final.mp4'], check=True)
print('final lufs', lufs('../final.mp4'))
