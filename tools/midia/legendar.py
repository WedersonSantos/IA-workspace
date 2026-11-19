import sys
from pathlib import Path

from faster_whisper import WhisperModel

# uso: python legendar.py audio.wav saida.srt [texto-de-referencia.txt]
# O texto de referencia (opcional) orienta o vocabulario do Whisper.
# Os blocos de legenda sao curtos (ate MAX_CHARS), bons para video vertical.
MAX_CHARS = 32
PONTUACAO_FINAL = (".", "!", "?", "…")

audio, srt = sys.argv[1], sys.argv[2]
prompt = Path(sys.argv[3]).read_text(encoding="utf-8") if len(sys.argv) > 3 else None
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = model.transcribe(audio, language="pt", initial_prompt=prompt, word_timestamps=True)


def t(s):
    h, m, sec = int(s // 3600), int(s % 3600 // 60), s % 60
    return f"{h:02}:{m:02}:{sec:06.3f}".replace(".", ",")


blocos, atual = [], []
for seg in segs:
    for w in seg.words or []:
        palavra = w.word.strip()
        if not palavra:
            continue
        texto = " ".join(p for p, _, _ in atual + [(palavra, 0, 0)])
        if atual and len(texto) > MAX_CHARS:
            blocos.append(atual)
            atual = []
        atual.append((palavra, w.start, w.end))
        if palavra.endswith(PONTUACAO_FINAL):
            blocos.append(atual)
            atual = []
if atual:
    blocos.append(atual)

with open(srt, "w", encoding="utf-8") as f:
    for i, b in enumerate(blocos, 1):
        f.write(f"{i}\n{t(b[0][1])} --> {t(b[-1][2])}\n{' '.join(p for p, _, _ in b)}\n\n")
