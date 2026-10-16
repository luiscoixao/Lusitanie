import subprocess, numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
for n in ["p1.mp3","p2.mp3"]:
    raw=subprocess.run(["ffmpeg","-v","error","-i","media/"+n,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(a,language="fr",word_timestamps=True)
    with open("media/"+n+".txt","w") as f:
        for s in segs:
            f.write(f"[{s.start:.1f}] {s.text}\n")
    with open("media/"+n+".words","w") as f:
        for s in segs:
            for x in s.words: f.write(f"{x.start:.2f}\t{x.end:.2f}\t{x.word}\n")
