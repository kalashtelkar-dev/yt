# stitch: cut_nocards.mp4 from clips + lines3.json. Run when all 63 clips exist.
import json,subprocess,os
W='/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/'
L=json.load(open(W+'lines3.json')); TOT=L['total']; lines=L['lines']
on=json.load(open(W+'onsets.json'))
start={x['id']:max(0,on[x['id']]-0.12) for x in lines}
ids=[x['id'] for x in lines]
shots=[]
for i in ids:
    shots.append(i)
    if i=='A4': shots.append('A4p')
t=[]
for s in shots:
    if s=='A4p': t.append((start['A4']+start['A5'])/2 if False else start['A4']+1.45)
    else: t.append(start[s])
t[0]=0.0
bound={'B1','C1','D1','E1'}
X=[0.5 if shots[i+1] in bound else 0.2 for i in range(len(shots)-1)]+[0]
S=[0.0]+[t[i]-X[i-1]/2 for i in range(1,len(shots))]
E=[t[i+1]+X[i]/2 for i in range(len(shots)-1)]+[TOT]
json.dump(dict(shots=shots,t=t,start=S,end=E),open('timing.json','w'))
if os.environ.get('DRY'):
    d=[round(E[i]-S[i],2) for i in range(len(shots))];print(max(d),min(d),[ (shots[i],d[i]) for i in range(len(d)) if d[i]>6.2 or d[i]<2.4]);raise SystemExit
CLIP=124/24;fl=[];ins=[]
for i,s in enumerate(shots):
    d=E[i]-S[i]; ins+=['-i',f'clips/{s}.mp4']
    f=d/CLIP if d>CLIP else 1.0
    c=f"[{i}:v]scale=1920:1080:flags=lanczos,setsar=1,fps=24,setpts=PTS-STARTPTS"
    if f>1.0: c+=f",setpts=PTS*{min(f,2.1):.4f}"+(",minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if f>1.25 else ",fps=24")
    c+=f",tpad=stop_mode=clone:stop_duration=4,trim=0:{d:.4f},setpts=PTS-STARTPTS[v{i}]"
    fl.append(c)
cur='v0'
for i in range(len(shots)-1):
    fl.append(f"[{cur}][v{i+1}]xfade=transition={'fadeblack' if X[i]>.3 else 'fade'}:duration={X[i]}:offset={S[i+1]:.4f}[x{i}]"); cur=f'x{i}'
fl.append(f"[{cur}]format=yuv420p[vout]")
ins+=['-i','voiceover_master_sameer.mp3']
subprocess.run(['ffmpeg','-y','-loglevel','error','-stats',*ins,'-filter_complex',';'.join(fl),'-map','[vout]','-map',f'{len(shots)}:a','-c:v','libx264','-preset','medium','-crf','18','-r','24','-c:a','copy','-t',str(TOT),'cut_nocards.mp4'])
