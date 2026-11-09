# -*- coding: utf-8 -*-
"""YouTube package for Dwarka: Hinglish titles, description with real chapters, tags (length counted), Hindi SRT, two clickbait thumbnails."""
import json, os, re, subprocess
from lib import *
Y = FILM + 'youtube/'; os.makedirs(Y + 'thumb', exist_ok=True)
T = json.load(open(FILM + 'voice_hi/timings.json')); TM = json.load(open(FILM + 'timing.json')); ON = TM['on']; S = script('hi'); ORD = order()
mmss = lambda t: f'{int(t // 60)}:{int(t % 60):02d}'
ch = [('A1', 'Paani ke neeche chhupa pul'), ('B1', 'Dhanushkodi: kabhi chahal-pahal wala shehar'), ('B4', '1964 ka toofan aur veeran shehar'), ('C1', 'Ram Setu ka raaz'), ('C4', 'ISRO ka naksha aur ASI ki manzoori'),
      ('C7', 'Dhanushkodi mein kya dekhein'), ('D1', 'Kaise pahunchein'), ('D6', 'Timing aur best season'), ('E1', 'Ek din ka full plan'), ('E8', 'Aakhri baat')]
chapters = '\n'.join(f'{mmss(0 if i == "A1" else max(0, ON[i] - 0.12))} {n}' for i, n in ch)
titles = ['Dhanushkodi: Samandar Ke Neeche Chhupa Ram Setu Ka Raaz 😱 Ghost Town Ki Sachchai',
          'Bhai Ye Shehar 1964 Mein Doob Gaya! 🔥 Dhanushkodi Aur Ram Setu Ka Poora Sach',
          'Ram Setu Ko Dekhne Ka Nazariya Badal Jayega 😳 Dhanushkodi Complete Guide',
          'India Ka Sabse Veeran Shehar 🚩 Dhanushkodi Ghost Town + Ram Setu Mystery']
desc = f"""🔥 Inn lehron ke theek neeche ek prachin doobha hua pul maujood hai, jiske raaz ko vigyan aaj bhi poori tarah samajh nahi paaya! 😱

Hum India ke sabse rahasyamayi aur veeran shehron mein se ek, Dhanushkodi ki padtaal kar rahe hain, jahan samandar se judi pauranik kathayein asli paani ke neeche maujood avsheshon se milti hain. Aakhir paani ke neeche kya chhupa hai? Yahan kya-kya aaj bhi maujood hai? 🚩

👇 Is video mein kya milega:
✅ 1964 ke toofan ne Dhanushkodi ka kya kiya
✅ Toota railway station aur church ke khandhar
✅ Ram Setu (Adam's Bridge): Ramayana, ISRO ka naksha aur ASI ki 2021 ki manzoori
✅ Arichal Munai, Rameswaram ka mandir aur naya Pamban Bridge
✅ Kaise pahunchein, timing aur best season
✅ Ek din ka full plan

⏱️ CHAPTERS
{chapters}

📍 Location: Dhanushkodi, Rameswaram, Tamil Nadu
⚠️ Timing, bus aur rules badalte rehte hain. Jaane se pehle local jaankari ek baar zaroor check kar lena.

💬 Comment mein batao: tumhe kya lagta hai, Ram Setu insaan ne banaya ya prakriti ne? 👇

🔔 GEO Dismantled ko subscribe karo aur bell dabao, taaki agla raaz sabse pehle tumhe mile. Video pasand aaye toh like aur share karna, bhai! 🙏

🤖 Visuals aur animation AI se bane hain, kuch real clips bhi shaamil hain. Kahaniyan Ramayana ki kathaon par aadharit hain, aur khoj ki jaankari news reports se li gayi hai.

#Dhanushkodi #RamSetu #AdamsBridge #Rameswaram #GhostTown #ArichalMunai #PambanBridge #TamilNadu #GEODismantled #IncredibleIndia #Travel
"""
tags = ['dhanushkodi', 'dhanushkodi ghost town', 'ram setu', 'ram setu mystery', 'adams bridge', 'dhanushkodi travel guide', 'arichal munai', 'rameswaram', 'rameswaram tourist places', 'dhanushkodi 1964 cyclone',
        'pamban bridge', 'new pamban bridge', 'ramanathaswamy temple', 'dhanushkodi church ruins', 'dhanushkodi railway station', 'ram setu underwater', 'ram setu isro', 'ram setu asi', 'dhanushkodi kaise jaye',
        'rameswaram one day plan', 'tamil nadu tourism', 'india travel guide', 'hindi travel vlog', 'abandoned places india', 'GEO Dismantled']
tg = ''
for t in tags:
    n = (tg + ', ' + t) if tg else t
    if len(n) > 480: break
    tg = n
open(Y + 'Dhanushkodi_YouTube_Package.txt', 'w', encoding='utf-8').write('\n\n'.join(['TITLE OPTIONS (best = #1)\n' + '\n'.join(f'{k+1}. {t}  [{len(t)} chars]' for k, t in enumerate(titles)), 'DESCRIPTION\n' + desc, f'TAGS [{len(tg)} chars of 500]\n' + tg]))
open(Y + 'tags.txt', 'w', encoding='utf-8').write(tg)
# Hindi SRT from approved text and real timings
def wrap(s, w=34):
    if len(s) <= w: return s
    ws = s.split(); b = None
    for k in range(1, len(ws)):
        a, c = ' '.join(ws[:k]), ' '.join(ws[k:]); sc = abs(len(a) - len(c))
        if b is None or sc < b[0]: b = (sc, a, c)
    return b[1] + '\n' + b[2]
cues = []
for i in ORD:
    t0 = ON[i]; t1 = T['lines'][i]['end']; parts = [p.strip() for p in re.split(r'(?<=[,।?!])\s+', S[i]) if p.strip()]; chs = []; cur = ''
    for p in parts:
        if cur and len(cur) + len(p) + 1 > 62: chs.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    if cur: chs.append(cur)
    tot = sum(len(c) for c in chs); a = t0
    for c in chs: b = a + (t1 - t0) * len(c) / tot; cues.append([a, b, c]); a = b
for k in range(len(cues) - 1): cues[k][1] = min(cues[k][1], cues[k + 1][0] - 0.02)
ts = lambda t: f'{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round((t%1)*1000))%1000:03d}'
open(Y + 'Dhanushkodi_Hindi_Subtitles.srt', 'w', encoding='utf-8').write('\n'.join(f'{k+1}\n{ts(a)} --> {ts(b)}\n{wrap(c)}\n' for k, (a, b, c) in enumerate(cues)))
# thumbnails from raw clip frames
CSS = """<!doctype html><meta charset="utf-8"><style>*{margin:0;box-sizing:border-box}body{width:1280px;height:720px;position:relative;overflow:hidden;background:#000;font-family:Impact,"Arial Black","Helvetica Neue",sans-serif}
img.bg{position:absolute;inset:0;width:1280px;height:720px;filter:contrast(1.18) saturate(1.3) brightness(1.04)}.shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(2,10,20,.85) 0%,rgba(2,10,20,.6) 40%,rgba(2,10,20,0) 68%),linear-gradient(0deg,rgba(0,0,0,.45),rgba(0,0,0,0) 35%)}
.t{position:absolute;left:44px;line-height:.98;-webkit-text-stroke:12px #000;paint-order:stroke fill;text-shadow:0 10px 0 rgba(0,0,0,.45);letter-spacing:1px}.a{top:38px;font-size:190px;color:#ffd600}.b{top:230px;font-size:100px;color:#fff;white-space:nowrap}
.tag{position:absolute;left:44px;top:420px;background:#e11616;color:#fff;font-size:66px;padding:4px 30px 10px;border-radius:18px;border:6px solid #fff;transform:rotate(-2deg);box-shadow:0 8px 0 rgba(0,0,0,.45);white-space:nowrap}
.sticker{position:absolute;right:36px;top:34px;background:#00c853;color:#fff;font-size:52px;padding:6px 24px 12px;border-radius:50px;border:6px solid #fff;transform:rotate(5deg);box-shadow:0 8px 0 rgba(0,0,0,.45);white-space:nowrap}
img.logo{position:absolute;inset:auto;right:30px;bottom:26px;width:96px;height:96px;border-radius:50%;border:5px solid #fff;filter:none}</style>"""
def thumb(name, clip, at, a, b, tag, stick):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(at), '-i', f'{FILM}clips/{clip}.mp4', '-frames:v', '1', '-vf', 'scale=1280:720:flags=lanczos', f'{Y}thumb/{name}.png'], check=True)
    open(f'{Y}thumb/{name}.html', 'w').write(CSS + f'<img class="bg" src="{name}.png"><div class="shade"></div><div class="t a">{a}</div><div class="t b">{b}</div><div class="tag">{tag}</div><div class="sticker">{stick}</div><img class="logo" src="{ROOT}ayodhya_film/logo_circle.png">')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720', f'--screenshot={Y}thumb/{name}_t.png', f'file://{Y}thumb/{name}.html'], capture_output=True)
    os.replace(f'{Y}thumb/{name}_t.png', Y + name + '.png')
thumb('Dhanushkodi_Thumbnail', 'A1', 3, 'RAM SETU', 'PAANI KE NEECHE CHHUPA?!', 'DHANUSHKODI KA RAAZ 🔥', 'ASLI SACH')
thumb('Dhanushkodi_Thumbnail_Alt', 'B5', 3, 'DOOB GAYA!', '1964 KA TOOFAN', 'VEERAN SHEHAR KI KAHANI 😱', 'LATEST KHOJ')
log('package done', len(tg), 'tag chars')
