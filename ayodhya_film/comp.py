import json,subprocess,numpy as np,io
from PIL import Image
C=json.load(open('cards/cardtimes.json'))
def size(f):
    o=subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height','-of','csv=p=0',f]).decode().strip().split(',');return int(o[0]),int(o[1])
def frame(t):
    b=subprocess.check_output(['ffmpeg','-loglevel','error','-ss',f'{t:.3f}','-i','cut_nocards.mp4','-frames:v','1','-vf','scale=480:270,format=gray','-f','image2pipe','-vcodec','png','-'])
    return np.asarray(Image.open(io.BytesIO(b)),dtype=float)
P={};ins=[];fl=[];cur='0:v';n=1
for k,v in C.items():
    f=f'cards/{k}.webm';w,h=size(f);t,d=v['t'],v['dur']
    if k=='tiles': x,y=(1920-w)//2,1080-h-60;sc={}
    else:
        cand={'TL':(96,72),'TR':(1920-96-w,72),'BL':(96,1080-120-h)}
        fr=[frame(t+d*(i+.5)/6) for i in range(6)];sc={}
        for nm,(x0,y0) in cand.items():
            s=0
            for g in fr:
                gy,gx=np.gradient(g);m=np.hypot(gx,gy)[int(y0/4):int((y0+h)/4),int(x0/4):int((x0+w)/4)];s+=m.mean()
            sc[nm]=s
        nm=min(sc,key=sc.get);x,y=cand[nm]
    P[k]=dict(t=t,dur=d,x=x,y=y,w=w,h=h,scores={a:round(b,1) for a,b in sc.items()})
    ins+=['-c:v','libvpx-vp9','-i',f];fl.append(f"[{n}:v]format=yuva420p,setpts=PTS-STARTPTS+{t}/TB[c{n}]")
    fl.append(f"[{cur}][c{n}]overlay=x={x}:y={y}:eof_action=pass:enable='between(t,{t},{t+d})'[o{n}]");cur=f'o{n}';n+=1
json.dump(P,open('placement.json','w'),indent=1)
ins+=['-loop','1','-i','logo_circle.png']
fl.append(f"[{cur}][{n}:v]overlay=x=1794:y=954:shortest=1[vout]")
subprocess.run(['ffmpeg','-y','-loglevel','error','-stats','-i','cut_nocards.mp4',*ins,'-filter_complex',';'.join(fl),'-map','[vout]','-map','0:a','-c:a','copy','-c:v','libx264','-preset','medium','-crf','21','-r','24','-t','301.293','-movflags','+faststart','final_nosfx.mp4'])
