"""Monta um video vertical a partir de uma pasta de conteudo.

uso: python montar.py AAAA-MM-DD-slug [--so-narracao] [--voz-referencia caminho.wav]
Aceita tambem caminho absoluto da pasta.

Pasta de entrada:
  02-roteiro.md   texto a narrar (titulos '#', comentarios e marcacao markdown sao ignorados)
  04-midia\\       opcional: imagens e/ou videos, usados em ordem alfabetica
Saidas na mesma pasta:
  03-narracao.wav, 03-narracao.srt, 05-final.mp4

Nada e publicado nem enviado: tudo fica local.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import torch
import torchaudio as ta

from narrar import AQUI, carregar_modelo, narrar, parametros

CONTEUDO_DIR = Path(os.environ.get("CONTEUDO_DIR", "F:/AI-Workspace/conteudo"))


def resolver_pasta(entrada):
    """Resolve nome relativo a CONTEUDO_DIR ou preserva caminho absoluto."""
    pasta = Path(entrada)
    if not pasta.is_absolute():
        pasta = CONTEUDO_DIR / pasta
    return pasta.resolve()


LARGURA, ALTURA, FPS = 1080, 1920, 30
COR_FUNDO = "0x1e1e2e"
SILENCIO_S = 0.3
MAX_FRASES, MAX_CHARS = 3, 220
# Em legenda .srt o libass usa uma tela de referencia de 288 de altura:
# FontSize=16 ~ 107 px e MarginV=23 ~ 150 px a partir da base, num video de 1920.
ESTILO_LEGENDA = "FontSize=16,Alignment=2,MarginV=23"
LOUDNORM = "loudnorm=I=-14:LRA=7:TP=-1.5"
IMAGENS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEOS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
ENQUADRAR = (f"scale={LARGURA}:{ALTURA}:force_original_aspect_ratio=increase,"
             f"crop={LARGURA}:{ALTURA},setsar=1,fps={FPS},format=yuv420p")


def ffmpeg(args, cwd):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args]
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit(f"ffmpeg falhou ({r.returncode}): {' '.join(cmd)}")


def loudnorm_2_passadas(wav, cwd):
    """Mede o audio e devolve o filtro loudnorm com os valores medidos (modo linear)."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", wav,
           "-af", f"{LOUDNORM}:print_format=json", "-f", "null", "-"]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if r.returncode != 0 or not m:
        print("aviso: medicao do loudnorm falhou, usando uma passada")
        return LOUDNORM
    d = json.loads(m.group(0))
    return (f"{LOUDNORM}:measured_I={d['input_i']}:measured_LRA={d['input_lra']}"
            f":measured_TP={d['input_tp']}:measured_thresh={d['input_thresh']}"
            f":offset={d['target_offset']}:linear=true")


def limpar_markdown(md):
    md = re.sub(r"<!--.*?-->", " ", md, flags=re.S)
    linhas = []
    for ln in md.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or re.fullmatch(r"[-*_=]{3,}", s):
            linhas.append("")
            continue
        s = re.sub(r"^(>\s*|[-*+]\s+|\d+[.)]\s+)", "", s)
        s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links/imagens -> texto
        s = re.sub(r"[*_`~]+", "", s)
        linhas.append(s)
    return re.sub(r"\s+", " ", " ".join(linhas)).strip()


def dividir(texto):
    frases = [f.strip() for f in re.split(r"(?<=[.!?…])\s+", texto) if f.strip()]
    trechos, atual = [], []
    for f in frases:
        if atual and (len(atual) >= MAX_FRASES or len(" ".join(atual + [f])) > MAX_CHARS):
            trechos.append(" ".join(atual))
            atual = []
        atual.append(f)
    if atual:
        trechos.append(" ".join(atual))
    return trechos


def gerar_narracao(trechos, saida, voz_referencia):
    model = carregar_modelo()
    p = parametros()
    print(f"parametros: exaggeration={p['exaggeration']}, cfg_weight={p['cfg_weight']}, "
          f"temperature={p['temperature']}, language_id={model._language_id}")
    silencio = torch.zeros(1, int(SILENCIO_S * model.sr))
    partes = []
    for i, t in enumerate(trechos, 1):
        wav = narrar(model, t, ref=str(voz_referencia)).cpu()
        print(f"  trecho {i}/{len(trechos)}: {wav.shape[-1] / model.sr:.1f}s  {t[:70]}")
        if partes:
            partes.append(silencio)
        partes.append(wav)
    audio = torch.cat(partes, dim=-1)
    ta.save(str(saida), audio, model.sr)
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return audio.shape[-1] / ta.info(str(saida)).sample_rate


def preparar_fundo(pasta, duracao):
    """Devolve os argumentos de entrada do ffmpeg para o video de fundo."""
    midia_dir = pasta / "04-midia"
    midias = sorted(f for f in midia_dir.iterdir()
                    if f.suffix.lower() in IMAGENS | VIDEOS) if midia_dir.is_dir() else []
    if not midias:
        print("sem midia em 04-midia: usando fundo solido")
        return ["-f", "lavfi", "-i", f"color=c={COR_FUNDO}:s={LARGURA}x{ALTURA}:r={FPS}:d={duracao:.3f}"]

    tmp = pasta / ".tmp-montagem"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    cada = duracao / len(midias)
    print(f"{len(midias)} midia(s) em 04-midia, {cada:.1f}s cada")
    lista = []
    for i, m in enumerate(midias):
        seg = tmp / f"seg{i:03}.mp4"
        entrada = (["-loop", "1"] if m.suffix.lower() in IMAGENS else ["-stream_loop", "-1"])
        ffmpeg([*entrada, "-t", f"{cada:.3f}", "-i", str(m), "-vf", ENQUADRAR, "-an",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(seg)], cwd=pasta)
        lista.append(f"file '{seg.name}'")
    (tmp / "lista.txt").write_text("\n".join(lista) + "\n", encoding="utf-8")
    ffmpeg(["-f", "concat", "-safe", "0", "-i", "lista.txt", "-c", "copy", "fundo.mp4"], cwd=tmp)
    return ["-i", str(tmp / "fundo.mp4")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pasta", help="nome dentro de CONTEUDO_DIR ou caminho absoluto")
    parser.add_argument("--so-narracao", action="store_true",
                        help="gera somente WAV e SRT, sem montar video")
    parser.add_argument("--voz-referencia", type=Path, default=AQUI / "voz-referencia.wav",
                        help="WAV de referencia do Wederson (padrao: junto dos scripts)")
    args = parser.parse_args()
    pasta = resolver_pasta(args.pasta)
    roteiro = pasta / "02-roteiro.md"
    if not roteiro.is_file():
        sys.exit(f"roteiro ausente: {roteiro}; crie 02-roteiro.md com a skill roteiro-reels antes de narrar")

    texto = limpar_markdown(roteiro.read_text(encoding="utf-8"))
    trechos = dividir(texto)
    if not trechos:
        sys.exit("roteiro vazio")
    voz_referencia = args.voz_referencia.resolve()
    if not voz_referencia.is_file():
        sys.exit(f"voz de referencia ausente: {voz_referencia}; informe um WAV existente do Wederson "
                 "com --voz-referencia (10-20 s, ambiente silencioso)")
    palavras = len(texto.split())
    print(f"estimativa: {palavras} palavras, {palavras / 150 * 60:.1f}s a 150 palavras/min", flush=True)
    print(f"{len(trechos)} trecho(s) a narrar")

    wav = pasta / "03-narracao.wav"
    srt = pasta / "03-narracao.srt"
    duracao = gerar_narracao(trechos, wav, voz_referencia)
    print(f"narracao: {wav.name} ({duracao:.1f}s)")

    ref = pasta / ".roteiro-limpo.txt"
    ref.write_text(texto, encoding="utf-8")
    r = subprocess.run([sys.executable, str(AQUI / "legendar.py"), str(wav), str(srt), str(ref)])
    ref.unlink(missing_ok=True)
    if r.returncode != 0:
        sys.exit("legendar.py falhou")
    print(f"legenda: {srt.name}")

    if args.so_narracao:
        print(f"ok: {wav} e {srt} (somente narracao; nenhum video montado)")
        return

    fundo = preparar_fundo(pasta, duracao)
    # caminhos relativos (cwd=pasta) evitam o escape de 'F:\' no filtro subtitles
    vf = (f"tpad=stop_mode=clone:stop_duration=2,"
          f"subtitles={srt.name}:force_style='{ESTILO_LEGENDA}'")
    ffmpeg([*fundo, "-i", wav.name, "-map", "0:v", "-map", "1:a",
            "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-af", loudnorm_2_passadas(wav.name, pasta), "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
            "-t", f"{duracao:.3f}", "-movflags", "+faststart", "05-final.mp4"], cwd=pasta)
    shutil.rmtree(pasta / ".tmp-montagem", ignore_errors=True)
    print(f"ok: {pasta / '05-final.mp4'}")


if __name__ == "__main__":
    main()
