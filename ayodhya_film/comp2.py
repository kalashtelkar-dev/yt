"""Place cards in the quietest corner (never bottom-right: the logo lives there), anchored to the real panel edges.
Needs cards2/*.webm, cardtimes_v2.json, cut_nocards.mp4. Writes placement2.json and final_nosfx.mp4."""
import json, subprocess, io, numpy as np
from PIL import Image

W = '/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/'
C = json.load(open(W + 'cardtimes_v2.json'))
SC = 0.88            # cards shown slightly smaller so they block less
MX, MT, MB = 88, 64, 112   # side margin, top margin, bottom margin
OVR = {'c12_hours': 'BR', 'c10_airport': 'BL'}   # user-chosen corners
PAD = 24             # transparent pad kept around the panel (shadow, exit slide)

def png(cmd):
    return Image.open(io.BytesIO(subprocess.check_output(cmd)))

def panel_bbox(f):
    im = png(['ffmpeg', '-loglevel', 'error', '-c:v', 'libvpx-vp9', '-ss', '1.2', '-i', f, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-']).convert('RGBA')
    a = np.asarray(im)[:, :, 3] > 200
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1, im.size

def frame(t):
    im = png(['ffmpeg', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', 'cut_nocards.mp4', '-frames:v', '1', '-vf', 'scale=960:540,format=gray', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    g = np.asarray(im, dtype=float); gy, gx = np.gradient(g); return np.hypot(gx, gy)

P, ins, fl, cur, n = {}, [], [], '0:v', 1
for k, v in C.items():
    f = f'cards2/{k}.webm' if k not in ('tiles', 'subscribe') else f'cards/{k}.webm'
    t, d = v['t'], v['dur']
    if k == 'tiles':
        w, h = [int(x) for x in subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', f]).decode().split(',')]
        x, y, cw, ch, sc = (1920 - w) // 2, 1080 - h - 60, w, h, {}
        crop = None
    else:
        x0, y0, x1, y1, (iw, ih) = panel_bbox(f) if k != 'subscribe' else (0, 0, 520, 150, (520, 150))
        cx0, cy0 = max(0, x0 - PAD), max(0, y0 - PAD); cx1, cy1 = min(iw, x1 + PAD), min(ih, y1 + PAD)
        crop = f'crop={cx1-cx0}:{cy1-cy0}:{cx0}:{cy0},scale=iw*{SC}:ih*{SC}'
        pw, ph = (x1 - x0) * SC, (y1 - y0) * SC; ow, oh = (cx1 - cx0) * SC, (cy1 - cy0) * SC
        px, py = (x0 - cx0) * SC, (y0 - cy0) * SC   # panel offset inside the cropped card
        fr = [frame(t + d * (i + .5) / 6) for i in range(6)]
        cand = {'TL': (MX, MT), 'TR': (1920 - MX - pw, MT), 'BL': (MX, 1080 - MB - ph), 'BR': (1920 - MX - pw, 940 - ph)}  # BR sits just above the logo; only used when forced
        sc = {}
        for nm, (X, Y) in cand.items():
            if nm == 'BR':
                sc[nm] = 0; continue
            s = 0
            for g in fr:
                reg = g[int(Y / 2):int((Y + ph) / 2), int(X / 2):int((X + pw) / 2)]
                s += reg.mean() + 0.5 * np.percentile(reg, 90)
            sc[nm] = s
        sc.pop('BR')
        nm = OVR.get(k) or min(sc, key=sc.get); X, Y = cand[nm]
        x, y, w, h = int(X - px), int(Y - py), ow, oh
    P[k] = dict(t=t, dur=d, x=x, y=y, corner=(nm if k != 'tiles' else 'bottom'), scores={a: round(b, 1) for a, b in sc.items()})
    ins += ['-c:v', 'libvpx-vp9', '-i', f]
    chain = f"[{n}:v]format=yuva420p," + (crop + ',' if crop else '') + f"setpts=PTS-STARTPTS+{t}/TB[c{n}]"
    fl.append(chain)
    fl.append(f"[{cur}][c{n}]overlay=x={x}:y={y}:eof_action=pass:enable='between(t,{t},{t+d})'[o{n}]"); cur = f'o{n}'; n += 1
json.dump(P, open('placement2.json', 'w'), indent=1)
ins += ['-loop', '1', '-i', 'logo_circle.png']
fl.append(f"[{cur}][{n}:v]overlay=x=1794:y=954:shortest=1[vout]")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'cut_nocards.mp4', *ins, '-filter_complex', ';'.join(fl), '-map', '[vout]', '-map', '0:a', '-c:a', 'copy', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-r', '24', '-t', '301.293', '-movflags', '+faststart', 'final_nosfx.mp4'], check=True)
print('done')
