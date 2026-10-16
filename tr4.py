import wave, numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
w=wave.open("full.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
segs,_=m.transcribe(a,language="fr")
with open("full.txt","w") as f:
    for s in segs: f.write(f"[{s.start:.0f}] {s.text}\n")
