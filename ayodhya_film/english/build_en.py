import json,subprocess,numpy as np,wave
SR=48000;W='/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/work/'
L=json.load(open(W+'lines3.json'))['lines'];on=json.load(open(W+'onsets.json'));S=json.load(open('script_en.json'))
nxt={L[i]['id']:(L[i+1]['start'] if i+1<len(L) else 301.29) for i in range(len(L))}
def load(p): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout,dtype=np.float32).copy()
def fit(x,f):
    if f<=1.001: return x
    b=subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af',f'atempo={f:.4f}','-f','f32le','-ar',str(SR),'-ac','1','-'],input=x.tobytes(),capture_output=True,check=True).stdout
    return np.frombuffer(b,dtype=np.float32).copy()
rms=lambda a:float(np.sqrt(np.mean(a**2)+1e-12))
TOT=301.293479;out=np.zeros(int((TOT+1)*SR),dtype=np.float32);placed={};fast=[]
lines={l['id']:load(f"trim/{l['id']}.wav") for l in L}
tgt=np.median([rms(v) for v in lines.values()])
for l in L:
    k=l['id'];x=lines[k];x*=tgt/rms(x)
    mx=nxt[k]-on[k]-0.15;f=min(1.25 if k in('C11','C12','C13','C14','C15') else 1.15,max(1.0,len(x)/SR/mx))
    if f>1.0: fast.append((k,round(f,2)))
    x=fit(x,f);fd=int(0.01*SR);x[:fd]*=np.linspace(0,1,fd);x[-fd:]*=np.linspace(1,0,fd)
    a=int(on[k]*SR);out[a:a+len(x)]+=x;placed[k]=(on[k],on[k]+len(x)/SR)
out=out[:int(TOT*SR)]
with wave.open('voice_raw.wav','wb') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
# match the Hindi master's loudness
r=subprocess.run(['ffmpeg','-nostats','-i','../voiceover_master_sameer.mp3','-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
import re;target=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1])
subprocess.run(['ffmpeg','-y','-v','error','-i','voice_raw.wav','-af',f'loudnorm=I={target}:TP=-1.5:LRA=7,aresample=48000','-ac','1','-ar','48000','voiceover_master_oliver_n.wav'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','voiceover_master_oliver_n.wav','-c:a','libmp3lame','-b:a','192k','voiceover_master_oliver.mp3'],check=True)
json.dump(placed,open('placed.json','w'));print('speed-ups',fast);print('target LUFS',target)
# overlaps
ks=[l['id'] for l in L];print('overlaps',[(a,b,round(placed[a][1]-placed[b][0],2)) for a,b in zip(ks,ks[1:]) if placed[a][1]>placed[b][0]+0.02])
