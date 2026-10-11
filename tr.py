import wave, numpy as np
from faster_whisper import WhisperModel
w=wave.open("seg.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel("small",compute_type="int8")
segs,_=m.transcribe(a,language="fr",word_timestamps=True)
with open("words.txt","w") as f:
    for s in segs:
        for x in s.words: f.write(f"{x.start:.2f}\t{x.end:.2f}\t{x.word}\n")
