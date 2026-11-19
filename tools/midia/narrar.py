import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(AQUI / "modelos"))

import torch
import torchaudio as ta


def parametros():
    return dict(
        exaggeration=float(os.environ.get("EXAGGERATION", 0.9)),
        cfg_weight=float(os.environ.get("CFG_WEIGHT", 0.2)),
        temperature=float(os.environ.get("TEMPERATURE", 0.6)),
    )


def carregar_modelo():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    t0 = time.perf_counter()
    modelo = os.environ.get("MODELO", "mtl")
    if modelo == "pt":
        # fine-tune gorack/Chatterbox-TTS-Portuguese (arquitetura do Chatterbox original, sem language_id)
        from chatterbox.tts import ChatterboxTTS
        model = ChatterboxTTS.from_local(AQUI / "modelos" / "chatterbox-pt", device)
        model._language_id = None
    else:
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        model._language_id = "pt"
    print(f"modelo {modelo} carregado em {time.perf_counter() - t0:.1f}s ({device})")
    return model


def narrar(model, texto, ref=None):
    """Gera a fala de `texto` e devolve o tensor de audio (taxa em model.sr)."""
    kw = dict(audio_prompt_path=ref or str(AQUI / "voz-referencia.wav"), **parametros())
    if model._language_id:
        kw["language_id"] = model._language_id
    return model.generate(texto, **kw)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('uso: python narrar.py "texto" saida.wav [voz-referencia.wav]')
    texto, saida = sys.argv[1], sys.argv[2]
    ref = sys.argv[3] if len(sys.argv) > 3 else None
    model = carregar_modelo()
    t1 = time.perf_counter()
    wav = narrar(model, texto, ref)
    p = parametros()
    print(f"audio gerado em {time.perf_counter() - t1:.1f}s ({wav.shape[-1] / model.sr:.1f}s de audio, "
          f"exaggeration={p['exaggeration']}, cfg_weight={p['cfg_weight']}, temperature={p['temperature']})")
    Path(saida).resolve().parent.mkdir(parents=True, exist_ok=True)
    ta.save(saida, wav, model.sr)
    print(f"ok: {saida}")
