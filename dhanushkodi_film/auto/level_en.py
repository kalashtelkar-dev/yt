import sys,subprocess,os;sys.path.insert(0,'.')
from lib import *
h=lufs(FILM+'voiceover_master_sameer.mp3');e=lufs(FILM+'english/voiceover_master_oliver.wav');g=h-e
if abs(g)>0.5:
    subprocess.run(['ffmpeg','-y','-v','error','-i',FILM+'english/voiceover_master_oliver.wav','-af',f'volume={g:.2f}dB,alimiter=limit=0.89','-ac','1','-ar','48000',FILM+'english/o.wav'],check=True);os.replace(FILM+'english/o.wav',FILM+'english/voiceover_master_oliver.wav')
    subprocess.run(['ffmpeg','-y','-v','error','-i',FILM+'english/voiceover_master_oliver.wav','-c:a','libmp3lame','-b:a','192k',FILM+'english/voiceover_master_oliver.mp3'],check=True)
log('english level matched', round(h,1), round(lufs(FILM+'english/voiceover_master_oliver.mp3'),1))
