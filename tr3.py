import wave, numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
out=open("check2.txt","w")
for n in ["beatriz.wav","olinda.wav"]:
    w=wave.open(n); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    for lang in ["fr","pt"]:
        segs,_=m.transcribe(a,language=lang)
        out.write(f"{n} {lang}: "+" ".join(s.text for s in segs)+"\n")
