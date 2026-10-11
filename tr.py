from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
segs,_=m.transcribe("seg.wav",language="fr",word_timestamps=True)
with open("words.txt","w") as f:
    for s in segs:
        for w in s.words: f.write(f"{w.start:.2f}\t{w.end:.2f}\t{w.word}\n")
