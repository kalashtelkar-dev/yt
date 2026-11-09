# -*- coding: utf-8 -*-
"""Builds the Ayodhya YouTube package: Hinglish title options, description with real chapters, tags (length counted), Hindi SRT from the approved script."""
import json, re, os
W = '/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
L = json.load(open(W + 'lines3.json'))['lines']; on = json.load(open(W + 'onsets.json'))
S = json.load(open(W + 'script.json'))['sections']
text = {r[0]: r[1] for v in S.values() for r in v}
start = {l['id']: l for l in L}
mmss = lambda t: f'{int(t // 60)}:{int(t % 60):02d}'

# ---------- chapters (from real line starts)
ch = [('A1', 'Diwali pe Ayodhya ka bhaukaal'), ('B1', 'Ayodhya ka itihaas: Kosal se Ram janm tak'), ('B5', 'Bhoomipujan se Pran Pratishtha tak'),
      ('B7', 'Naya Ram Mandir: nakkashi aur khaasiyat'), ('C2', 'Hanuman Garhi'), ('C5', 'Kanak Bhawan'), ('C7', 'Ram ki Paidi aur Guptar Ghat'),
      ('D1', 'Kaise pahunchein: train, road, flight'), ('D6', 'Darshan ka time, kharcha aur best season'),
      ('E1', 'Ek din ka full plan'), ('E7', 'Kya saath rakhein aur kya nahi'), ('E12', 'Aakhri baat')]
chapters = '\n'.join(f'{mmss(max(0, on[i] - 0.12) if i != "A1" else 0)} {name}' for i, name in ch)

# ---------- title options (all claims are in the film)
titles = [
 'Ayodhya Ka Bhaukaal 🔥 Lakhon Diye Ek Saath! Poora Guide, Free Darshan Aur Ek Din Ka Plan',
 'Bhai Ayodhya Ne Toh Gadar Macha Diya 🚩 Ram Mandir Ka Poora Plan, Kharcha Aur Timing',
 'Ayodhya Jaane Se Pehle Ye Dekh Lo 😱 Free Darshan, Chaukas Plan, Sab Kuch Ek Video Mein',
 'Ram Mandir Jaana Hai? Ruk Ja Bhai! 😱 Ayodhya Ka Jhakaas Travel Guide',
]
best = 0

desc = f"""🔥 Diwali ki raat Ayodhya mein lakhon diye ek saath jal uthte hain... aur bhai, wo nazaara dekh ke dil jhannat ho jaata hai! 😱

Sawaal ye hai: Ayodhya jaana ho toh kya dekhein, kaise pahunchein, kitna kharcha, aur ek din mein sab kaise nipta lein? Sab kuch is video mein, ekdum chaukas tareeke se. 🚩

👇 Is video mein kya milega:
✅ "Ayodhya" naam ka matlab: jisse koi yuddh na kar sake
✅ Kosal rajya se Ram Mandir tak ka seedha itihaas
✅ Ram Janmabhoomi, Hanuman Garhi, Kanak Bhawan, Ram ki Paidi, Guptar Ghat
✅ Train, road aur flight se kaise pahunchein
✅ Darshan FREE hai! Timing aur best season
✅ Ek din ka full plan, subah se shaam tak

⏱️ CHAPTERS
{chapters}

📍 Location: Ayodhya, Uttar Pradesh
⚠️ Time, ticket aur rules badalte rehte hain. Jaane se pehle official website pe ek baar zaroor check kar lena.

💬 Comment mein batao: tumhe Ayodhya mein sabse zyada kya dekhna hai, Ram Mandir ya Ram ki Paidi ki aarti? Hum next video usi ka banayenge! 👇

🔔 Channel GEO Dismantled ko subscribe karo aur bell dabao, taaki agla jagah ka guide sabse pehle tumhe mile. Video pasand aaye toh like aur share zaroor karna, bhai! 🙏

🤖 Visuals aur animation AI se bane hain. Kuch tasveerein asli photos hain. Jaankari sirf general guide ke liye hai.

📸 Photo credits (Wikimedia Commons):
• Prime Minister's Office, GODL-India (Ram Mandir, Ram Lalla)
• Prashant Kharote, CC BY-SA 4.0 (Hanuman Garhi) and CC BY 4.0 (Ram ki Paidi)
• Aliva Sahoo, CC BY-SA 3.0 (Kanak Bhawan, Ayodhya)
• Vanshiikaa, CC0 (Ram ki Paidi)
• Narendra Modi / PMO, CC BY 3.0

#Ayodhya #RamMandir #AyodhyaTravelGuide #AyodhyaDham #RamLalla #HanumanGarhi #KanakBhawan #RamKiPaidi #UttarPradeshTourism #GEODismantled #Travel #IncredibleIndia
"""

tags = ['ayodhya', 'ayodhya travel guide', 'ram mandir', 'ayodhya ram mandir', 'ayodhya dham', 'ayodhya darshan', 'ayodhya tourist places', 'ayodhya one day plan',
        'ram janmabhoomi', 'hanuman garhi', 'kanak bhawan', 'ram ki paidi', 'guptar ghat', 'saryu river', 'ayodhya deepotsav', 'ayodhya diwali', 'ram lalla',
        'ayodhya kaise jaye', 'lucknow to ayodhya', 'ayodhya train', 'ayodhya airport', 'ayodhya free darshan', 'ayodhya best time to visit', 'uttar pradesh tourism',
        'india travel guide', 'hindi travel vlog', 'ayodhya vlog', 'ayodhya history', 'GEO Dismantled']
tagstr = ''
for t in tags:
    nxt = (tagstr + ', ' + t) if tagstr else t
    if len(nxt) > 480: break
    tagstr = nxt
txt = '\n\n'.join(['TITLE OPTIONS (best = #%d)\n' % (best + 1) + '\n'.join(f'{i+1}. {t}  [{len(t)} chars]' for i, t in enumerate(titles)), 'DESCRIPTION\n' + desc, f'TAGS [{len(tagstr)} chars of 500]\n' + tagstr])
open(OUT + 'Ayodhya_YouTube_Package.txt', 'w', encoding='utf-8').write(txt)
open(OUT + 'tags.txt', 'w', encoding='utf-8').write(tagstr)

# ---------- Hindi SRT from the approved script text and the real line times
def wrap(s, w=34):
    if len(s) <= w: return s
    words = s.split(); best = None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        sc = abs(len(a) - len(b))
        if best is None or sc < best[0]: best = (sc, a, b)
    return best[1] + '\n' + best[2]
cues = []
for l in L:
    t0 = on[l['id']]; t1 = l['end']; s = text[l['id']]
    parts = [p.strip() for p in re.split(r'(?<=[,।?!])\s+', s) if p.strip()]
    chunks, cur = [], ''
    for p in parts:   # merge short parts, keep each cue under 62 chars
        if cur and len(cur) + len(p) + 1 > 62: chunks.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    if cur: chunks.append(cur)
    tot = sum(len(c) for c in chunks); a = t0
    for c in chunks:
        b = a + (t1 - t0) * len(c) / tot; cues.append([a, b, c]); a = b
for i in range(len(cues) - 1): cues[i][1] = min(cues[i][1], cues[i + 1][0] - 0.02)
ts = lambda t: f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)) % 1000:03d}'
open(OUT + 'Ayodhya_Hindi_Subtitles.srt', 'w', encoding='utf-8').write('\n'.join(f'{i+1}\n{ts(a)} --> {ts(b)}\n{wrap(c)}\n' for i, (a, b, c) in enumerate(cues)))
print('tags', len(tagstr), 'cues', len(cues), 'titles', [len(t) for t in titles])
