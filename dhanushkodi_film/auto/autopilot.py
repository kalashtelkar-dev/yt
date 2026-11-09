# -*- coding: utf-8 -*-
"""Overnight driver: keeps the queue workers alive, reviews each finished shot, redraws failures, then voices, cuts, cards, mixes and packages the film. Run: nohup python3 autopilot.py &"""
import json, os, subprocess, sys, time
from lib import *
import qa
Q = ROOT + 'queue/'; ORD = order(); stage = AUTO + 'stage.json'
def done_stage(n): s = json.load(open(stage)) if os.path.exists(stage) else {}; s[n] = time.strftime('%H:%M:%S'); json.dump(s, open(stage, 'w'))
def has(n): return os.path.exists(stage) and n in json.load(open(stage))
def workers():
    n = int(subprocess.run("pgrep -f 'node dhanu_worker.mjs' | wc -l", shell=True, capture_output=True, text=True).stdout.strip() or 0)
    while n < 2:
        subprocess.Popen('CONCURRENCY=1 nohup node dhanu_worker.mjs >> dhanu_auto.log 2>&1 &', shell=True, cwd=Q); n += 1; log('restarted a worker')
def retry_failed():
    r = subprocess.run(['node', 'dhanu_status.mjs', 'retry'], cwd=Q, capture_output=True, text=True)
    if 'retried 0' not in r.stdout and 'retried' in r.stdout: log('retried failed jobs:', r.stdout.split('retried')[-1].strip())
def run(script, *a):
    r = subprocess.run([sys.executable, AUTO + script, *a], cwd=AUTO, capture_output=True, text=True)
    if r.returncode: log('FAILED', script, r.stderr[-600:]); return False
    return True
log('autopilot started')
# 1. Hindi voice (started separately; wait for its timings, or run it)
if not os.path.exists(FILM + 'voice_hi/timings.json'):
    if subprocess.run("pgrep -f voice_hi3.py | wc -l", shell=True, capture_output=True, text=True).stdout.strip() == '0': run('voice_hi3.py')
    while not os.path.exists(FILM + 'voice_hi/timings.json'): time.sleep(30)
done_stage('voice_hi'); log('hindi voice ready')
# 2. English voice
if not os.path.exists(FILM + 'english/voiceover_master_oliver.mp3'): run('voice_en.py'); run('level_en.py')
done_stage('voice_en')
# 3. visuals: keep workers alive, review finished shots, redraw failures
last = time.time(); prev = -1
while True:
    workers(); retry_failed(); ready = [i for i in ORD if os.path.exists(f'{FILM}clips/{i}.mp4')]
    if ready:
        try: qa.sweep(ready)
        except Exception as e: log('qa error', e)
    S = qa.st(); passed = [i for i in ORD if S.get(i, {}).get('pass')]
    if len(passed) != prev: prev = len(passed); last = time.time(); log('visuals passed', len(passed), 'of', len(ORD))
    if len(passed) == len(ORD): break
    if time.time() - last > 5400: log('no progress for 90 min, still waiting'); last = time.time()
    time.sleep(180)
done_stage('visuals')
# 4. film
for step in (['cut'], ['cards'], ['mix'], ['mix_en']):
    ok = False
    for attempt in range(2):
        if run('assemble.py', *step): ok = True; break
        time.sleep(30)
    if not ok: log('STOPPED: step', step[0], 'failed twice, see FAILED above'); sys.exit(1)
    done_stage(step[0])
run('package.py'); done_stage('package')
log('ALL DONE')
