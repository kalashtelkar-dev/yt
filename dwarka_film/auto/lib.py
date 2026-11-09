# -*- coding: utf-8 -*-
"""Shared helpers for the Dwarka overnight pipeline (EngineX REST, audio math). No Claude involved at run time."""
import json, os, re, subprocess, time, urllib.request, wave, numpy as np
ROOT = '/Users/kalash/Projects/yt/'; FILM = ROOT + 'dwarka_film/'; AUTO = FILM + 'auto/'
SCR = '/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/dwarka/'
for l in open(ROOT + '.env'):
    m = re.match(r'\s*([A-Z_]+)\s*=\s*(.*)', l)
    if m: os.environ.setdefault(m.group(1), m.group(2).strip('"\''))
O = 'https://enginex.run'; H = {'Authorization': 'Bearer ' + os.environ['AUTH_KEY'], 'content-type': 'application/json'}
SR = 48000
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); open(AUTO + 'autopilot.log', 'a').write(s + '\n')
GW = 'http://127.0.0.1:3940'; DONE = {}
def ensure_gateway():
    try: urllib.request.urlopen(GW, timeout=5); return
    except Exception:
        subprocess.Popen('nohup node gateway.mjs >> gateway.log 2>&1 &', shell=True, cwd=ROOT + 'queue'); time.sleep(4)
def gw(path, body):
    ensure_gateway(); r = urllib.request.Request(GW + '/run', json.dumps({'path': path, 'body': body}).encode(), {'content-type': 'application/json'})
    j = json.load(urllib.request.urlopen(r, timeout=4000))
    if 'error' in j and 'id' not in j: raise RuntimeError(str(j['error'])[:300])
    DONE[j['id']] = j; return {'id': j['id']}
def call(method, path, body=None, tries=6):
    if method == 'POST' and path.startswith('/v1/') and not path.startswith(('/v1/uploads', '/v1/outputs')): return gw(path, body)  # every engine job goes through the ops queue
    for a in range(tries):
        try:
            r = urllib.request.Request(O + path, json.dumps(body).encode() if body is not None else None, H, method=method)
            return json.load(urllib.request.urlopen(r, timeout=120))
        except urllib.error.HTTPError as e:
            t = e.read().decode()[:300]
            if e.code == 403 and 'account_paused' in t: log('account paused, waiting 5 min'); time.sleep(300); continue
            if e.code in (429, 500, 502, 503, 504): time.sleep(5 + 10 * a); continue
            raise RuntimeError(f'{method} {path} {e.code} {t}')
        except Exception: time.sleep(5 + 10 * a)
    raise RuntimeError(f'{method} {path} failed')
def wait(jid, every=3, limit=1800):
    if jid in DONE: return DONE[jid]
    t0 = time.time()
    while time.time() - t0 < limit:
        j = call('GET', '/v1/jobs/' + jid)
        if j['status'] in ('succeeded', 'failed', 'cancelled', 'canceled'): return j
        time.sleep(every)
    raise RuntimeError('timeout ' + jid)
def sign(keys):
    return call('POST', '/v1/outputs/sign', {'keys': keys})['urls']
def fetch(url, path):
    for a in range(4):
        try: open(path, 'wb').write(urllib.request.urlopen(url, timeout=180).read()); return
        except Exception: time.sleep(3 + 5 * a)
    raise RuntimeError('download failed ' + path)
def upload(path, name=None):
    d = open(path, 'rb').read(); name = name or os.path.basename(path)
    u = call('POST', '/v1/uploads', {'filename': name})
    urllib.request.urlopen(urllib.request.Request(u['url'], d, {'content-type': 'application/octet-stream'}, method='PUT'), timeout=300)
    call('POST', '/v1/uploads/complete', {'key': u['key'], 'filename': name, 'bytes': len(d)}); return u['key']
def run_many(path, bodies):
    """submit many jobs, then wait for all; returns the finished jobs in order"""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as ex: ids = list(ex.map(lambda b: call('POST', path, b)['id'], bodies))
    return [wait(i) for i in ids]
def out_key(j, ext=None):
    for o in j['result']['outputs']:
        if ext is None or o['key'].endswith(ext): return o['key']
def load(p, sr=SR):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout, dtype=np.float32).copy()
def save_wav(p, x, sr=SR):
    with wave.open(p, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
def lufs(p):
    o = subprocess.run(['ffmpeg', '-nostats', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def trim_sil(src, dst):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse', '-ar', str(SR), '-ac', '1', dst], check=True)
def words(path):
    """word timings of an audio file via regional transcription (Hindi)"""
    j = wait(call('POST', '/v1/transcribe-regional/words', {'input': upload(path), 'language': 'hi'})['id'])
    return j['result']['words']
def script(lang='hi'):
    if lang == 'en': return json.load(open(AUTO + 'script_en.json'))
    d = json.load(open(SCR + 'script_draft.json'))['sections']; return {i: t for v in d.values() for i, t in v}
def order():
    d = json.load(open(SCR + 'script_draft.json'))['sections']; return [i for v in d.values() for i, _ in v]
def sections():
    d = json.load(open(SCR + 'script_draft.json'))['sections']; return {i: s for s, v in d.items() for i, _ in v}
