"""Replace one spoken word inside a finished voice file with a better take of that word, keeping the exact length so nothing else moves."""
import json, subprocess, numpy as np, wave, shutil
SR = 48000

def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout, dtype=np.float32).copy()

def stretch(x, n):  # change duration to n samples, pitch kept
    r = len(x) / n
    b = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={r:.5f}', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'],
                       input=x.tobytes(), capture_output=True, check=True).stdout
    y = np.frombuffer(b, dtype=np.float32).copy()
    return np.pad(y, (0, max(0, n - len(y))))[:n]

rms = lambda a: float(np.sqrt(np.mean(a ** 2) + 1e-12))

def patch(master_in, offset, out_mp3, old_a, old_b, new_wav, new_a, new_b, br='192k'):
    M = load(master_in); N = load(new_wav); M0 = M.copy()
    a = int((old_a - offset) * SR); b = int((old_b - offset) * SR)
    seg = stretch(N[int(new_a * SR):int(new_b * SR)], b - a)
    def active(v):  # rms of the speech frames only
        n = int(0.02 * SR); fr = [v[i:i + n] for i in range(0, len(v) - n, n)]; fr = [rms(f) for f in fr if rms(f) > 0.05]
        return float(np.mean(fr)) if fr else rms(v)
    ctx = np.concatenate([M[max(0, a - int(0.8 * SR)):a], M[b:b + int(0.8 * SR)]])
    seg *= active(ctx) / active(seg)
    X = int(0.012 * SR); fi = np.linspace(0, 1, X); fo = 1 - fi
    M[a:a + X] = M[a:a + X] * fo + seg[:X] * fi
    M[a + X:b - X] = seg[X:-X]
    M[b - X:b] = M[b - X:b] * fi + seg[-X:] * fo
    assert len(M) == len(M0) and np.allclose(M[:a - 1], M0[:a - 1]) and np.allclose(M[b + 1:], M0[b + 1:])
    p = out_mp3.replace('.mp3', '.wav')
    with wave.open(p, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(M, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', p, '-c:a', 'libmp3lame', '-b:a', br, '-ar', str(SR), '-ac', '1', out_mp3], check=True)
    return a / SR, b / SR

if __name__ == '__main__':
    s = json.load(open('sam.json'))['s33'][1]
    oa, ob = 231.596 - 0.02, 231.856 + 0.02
    na, nb = s['start'] - 0.02, s['end'] + 0.02
    print(patch('../voiceover_master_sameer.mp3', 0, 'master_fixed.mp3', oa, ob, 's33.wav', na, nb, '192k'))
    print(patch('../voice/D.mp3', 170.169063, 'D_fixed.mp3', oa, ob, 's33.wav', na, nb, '64k'))
