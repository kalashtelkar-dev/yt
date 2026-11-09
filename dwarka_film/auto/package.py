# -*- coding: utf-8 -*-
"""YouTube package for Dwarka: Hinglish titles, description with real chapters, tags (length counted), Hindi SRT, two clickbait thumbnails."""
import json, os, re, subprocess
from lib import *
Y = FILM + 'youtube/'; os.makedirs(Y + 'thumb', exist_ok=True)
T = json.load(open(FILM + 'voice_hi/timings.json')); TM = json.load(open(FILM + 'timing.json')); ON = TM['on']; S = script('hi'); ORD = order()
mmss = lambda t: f'{int(t // 60)}:{int(t % 60):02d}'
ch = [('A1', 'Samandar mein sone ka shehar?'), ('B1', 'Krishna aur Dwarka ki kahani'), ('B4', 'Yadavon ka ant aur Krishna ka dham'), ('B10', 'Jab samandar ne poora shehar nigal liya'), ('C1', 'Samandar ke neeche kya mila?'),
      ('C5', 'Latest khabar: ASI ki nayi khoj'), ('C9', 'Dwarkadhish Mandir, Gomti Ghat aur Bet Dwarka'), ('D1', 'Kaise pahunchein'), ('D7', 'Darshan ka time, free entry aur best season'), ('E1', 'Ek din ka full plan'),
      ('E7', 'Kya saath rakhein'), ('E10', 'Aakhri baat')]
chapters = '\n'.join(f'{mmss(0 if i == "A1" else max(0, ON[i] - 0.12))} {n}' for i, n in ch)
titles = ['Samandar Mein Sone Ka Shehar? 😱 Dwarka Ka Raaz, Krishna Ki Antim Katha Aur Latest Khoj',
          'Dwarka Ka Poora Sach 🔥 Krishna Ke Jaate Hi Samandar Ne Nigal Liya Shehar! Complete Guide',
          'Dwarka Underwater City Ka Asli Raaz 😳 ASI Ki Nayi Khoj + Poora Travel Plan',
          'Bhai Dwarka Ka Ye Raaz Kisi Ne Nahi Bataya 😱 Samandar Mein Doobi Sone Ki Nagri']
desc = f"""🔥 Samandar mein aaj bhi samaya hua hai ye shehar, jise sone ka shehar kehte hain... aur uski kahani sunke dil jhannat ho jayega! 😱

Sawaal ye hai: Dwarka sach mein samandar mein doob gayi? Krishna ke antim din kaise the? Underwater ASI ki nayi khoj mein kya mila? Aur Dwarka jaana ho toh kaise jaayein, kitna time lagega, kya dekhein? Sab kuch is video mein, ekdum chaukas tareeke se. 🚩

👇 Is video mein kya milega:
✅ Krishna ne Dwarka kyun basaya aur Yadavon ka ant kaise hua
✅ Jara ka teer aur Bhalka Tirth ki kahani
✅ Samandar mein doobi Dwarka: ab tak kya mila, aur scientists mein bahas kyun hai
✅ Latest khabar: 2025 mein ASI ki underwater team ka naya survey
✅ Dwarkadhish Mandir, Gomti Ghat, Rukmini Mandir aur Bet Dwarka
✅ Kaise pahunchein, darshan timing, free entry aur best season
✅ Ek din ka full plan

⏱️ CHAPTERS
{chapters}

📍 Location: Dwarka, Gujarat
⚠️ Time, rules aur raaste badalte rehte hain. Jaane se pehle official website pe ek baar zaroor check kar lena.

💬 Comment mein batao: tumhe kya lagta hai, Dwarka ki kahani sach hai ya sirf legend? 👇

🔔 GEO Dismantled ko subscribe karo aur bell dabao, taaki agla raaz sabse pehle tumhe mile. Video pasand aaye toh like aur share karna, bhai! 🙏

🤖 Visuals aur animation AI se bane hain. Kahaniyan Mahabharata ki kathaon par aadharit hain, aur khoj ki jaankari news reports se li gayi hai.

#Dwarka #Krishna #DwarkaUnderwater #Dwarkadhish #Mahabharata #BetDwarka #GujaratTourism #SudarshanSetu #BhalkaTirth #GEODismantled #IncredibleIndia #Travel
"""
tags = ['dwarka', 'dwarka travel guide', 'dwarka underwater city', 'dwarka mystery', 'dwarkadhish temple', 'dwarka krishna', 'krishna death', 'krishna dwarka story', 'dwarka sunk in sea', 'bet dwarka',
        'sudarshan setu', 'gomti ghat', 'rukmini temple', 'bhalka tirth', 'jara arrow krishna', 'mahabharata dwarka', 'dwarka ASI underwater survey', 'dwarka latest news', 'dwarka one day plan',
        'dwarka darshan timings', 'dwarka kaise jaye', 'gujarat tourism', 'india travel guide', 'hindi travel vlog', 'dwarka vlog', 'dwarka history', 'GEO Dismantled']
tg = ''
for t in tags:
    n = (tg + ', ' + t) if tg else t
    if len(n) > 480: break
    tg = n
open(Y + 'Dwarka_YouTube_Package.txt', 'w', encoding='utf-8').write('\n\n'.join(['TITLE OPTIONS (best = #1)\n' + '\n'.join(f'{k+1}. {t}  [{len(t)} chars]' for k, t in enumerate(titles)), 'DESCRIPTION\n' + desc, f'TAGS [{len(tg)} chars of 500]\n' + tg]))
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
open(Y + 'Dwarka_Hindi_Subtitles.srt', 'w', encoding='utf-8').write('\n'.join(f'{k+1}\n{ts(a)} --> {ts(b)}\n{wrap(c)}\n' for k, (a, b, c) in enumerate(cues)))
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
thumb('Dwarka_Thumbnail', 'A1', 3, 'SONE KA', 'SHEHAR SAMANDAR MEIN?!', 'DWARKA KA RAAZ 🔥', 'ASLI SACH')
thumb('Dwarka_Thumbnail_Alt', 'B12', 3, 'DOOB GAYA!', 'KRISHNA KE JAATE HI', 'DWARKA KI ANKAHI KAHANI 😱', 'LATEST KHOJ')
log('package done', len(tg), 'tag chars')
