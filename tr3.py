import subprocess, numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
out=open("media/check.txt","w")
for n in ["beatriz.mp3","olinda.mp3"]:
    raw=subprocess.run(["ffmpeg","-v","error","-i","media/"+n,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    for lang in ["fr","pt"]:
        segs,_=m.transcribe(a,language=lang)
        out.write(f"{n} {lang}: "+" ".join(s.text for s in segs)+"\n")
