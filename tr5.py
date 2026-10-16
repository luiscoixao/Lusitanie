import wave, numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
for n in ["p1","p2"]:
    w=wave.open(n+".wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    segs=list(m.transcribe(a,language="fr",word_timestamps=True)[0])
    with open(n+".words","w") as f:
        for s in segs:
            for x in s.words: f.write(f"{x.start:.2f}\t{x.end:.2f}\t{x.word}\n")
