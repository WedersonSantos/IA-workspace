"""Gera um episodio de podcast com dois apresentadores a partir de 03-roteiro.md.

uso:
  python podcast.py AAAA-MM-DD-slug                 gera (ou continua) o episodio completo
  python podcast.py AAAA-MM-DD-slug --estimar       so conta palavras e estima a duracao (sem modelo)
  python podcast.py AAAA-MM-DD-slug --amostra 60    gera so os primeiros ~60 s, para ouvir as vozes
  python podcast.py AAAA-MM-DD-slug --refazer 42 57 regera as falas das linhas 42 e 57 e remonta
  python podcast.py AAAA-MM-DD-slug --simular       testa o fluxo sem modelo (silencio no lugar da voz)

A pasta e relativa a CONTEUDO_DIR/podcast (padrao F:/AI-Workspace/conteudo/podcast)
ou um caminho absoluto.

Formato do roteiro (03-roteiro.md), uma fala por linha:
  # Bloco 1: titulo           vira capitulo (nao e falado)
  [A] fala do apresentador A
  [B] fala do apresentador B
  [PAUSA 1.5]                 silencio em segundos
Linhas vazias, comentarios <!-- --> e qualquer outra linha sao ignorados (com aviso).

Saidas na pasta do episodio:
  04-falas/        um WAV por fala (cache: rodar de novo so gera o que mudou)
  05-episodio.mp3  episodio final, loudnorm -16 LUFS, 128 kbps mono 44,1 kHz
  05-episodio.srt  legenda pelos tempos de cada fala
  05-capitulos.txt minutagem dos blocos (para a descricao)

Nada e publicado nem enviado: tudo fica local.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))  # narrar.py fica na mesma pasta
os.environ.setdefault("HF_HOME", str(AQUI / "modelos"))

CONTEUDO_DIR = Path(os.environ.get("CONTEUDO_DIR", "F:/AI-Workspace/conteudo")) / "podcast"
VOZES = {"A": AQUI / "vozes" / "apresentador-a.wav", "B": AQUI / "vozes" / "apresentador-b.wav"}
PALAVRAS_POR_MIN = 150
SILENCIO_ENTRE_FALAS = 0.3   # segundos entre falas de apresentadores diferentes
SILENCIO_MESMA_VOZ = 0.15    # segundos entre partes de uma fala longa ou falas seguidas da mesma voz
MAX_CHARS_PARTE = 250        # falas maiores sao divididas por frase antes do TTS
MAX_CHARS_LEGENDA = 84       # legenda de podcast: ate 2 linhas de ~42
LOUDNORM = "loudnorm=I=-16:LRA=11:TP=-1.5"
SR_SIMULADO = 24000

RE_FALA = re.compile(r"^\[(A|B)\]\s*(.+)$", re.I)
RE_PAUSA = re.compile(r"^\[PAUSA\s+(\d+(?:[.,]\d+)?)\]$", re.I)


# ---------------------------------------------------------------- roteiro

def ler_roteiro(caminho):
    """Devolve a lista de itens: ('fala', linha, voz, texto) | ('pausa', linha, s) | ('capitulo', linha, titulo)."""
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), texto, flags=re.S)
    itens, ignoradas = [], []
    for n, bruta in enumerate(texto.splitlines(), 1):
        s = bruta.strip()
        if not s:
            continue
        if s.startswith("#"):
            itens.append(("capitulo", n, s.lstrip("#").strip()))
        elif m := RE_FALA.match(s):
            fala = re.sub(r"[*_`~]+", "", m.group(2)).strip()
            if fala:
                itens.append(("fala", n, m.group(1).upper(), fala))
        elif m := RE_PAUSA.match(s):
            itens.append(("pausa", n, float(m.group(1).replace(",", "."))))
        else:
            ignoradas.append(n)
    if ignoradas:
        amostra = ", ".join(map(str, ignoradas[:10])) + (" ..." if len(ignoradas) > 10 else "")
        print(f"aviso: {len(ignoradas)} linha(s) fora do formato ignoradas: {amostra}")
    return itens


def dividir_fala(texto):
    """Divide fala longa em partes por frase, para o TTS nao ficar robotico."""
    if len(texto) <= MAX_CHARS_PARTE:
        return [texto]
    frases = [f.strip() for f in re.split(r"(?<=[.!?…])\s+", texto) if f.strip()]
    partes, atual = [], ""
    for f in frases:
        if atual and len(atual) + 1 + len(f) > MAX_CHARS_PARTE:
            partes.append(atual)
            atual = f
        else:
            atual = f"{atual} {f}".strip()
    if atual:
        partes.append(atual)
    return partes


def estimar(itens):
    falas = [i for i in itens if i[0] == "fala"]
    palavras = sum(len(i[3].split()) for i in falas)
    pausas = sum(i[2] for i in itens if i[0] == "pausa")
    seg = palavras / PALAVRAS_POR_MIN * 60 + pausas + len(falas) * SILENCIO_ENTRE_FALAS
    por_voz = {v: sum(len(i[3].split()) for i in falas if i[2] == v) for v in "AB"}
    return palavras, seg, por_voz, len(falas)


def hms(s):
    s = int(round(s))
    return f"{s // 3600}:{s % 3600 // 60:02}:{s % 60:02}" if s >= 3600 else f"{s // 60}:{s % 60:02}"


# ---------------------------------------------------------------- audio

class Motor:
    """Carrega o modelo so quando a primeira fala precisa ser gerada."""

    def __init__(self, simular):
        self.simular = simular
        self.model = None
        self.sr = SR_SIMULADO

    def gerar(self, texto, ref):
        import torch
        if self.simular:
            seg = max(0.5, len(texto.split()) / PALAVRAS_POR_MIN * 60)
            return torch.zeros(1, int(seg * self.sr))
        if self.model is None:
            from narrar import carregar_modelo
            self.model = carregar_modelo()
            self.sr = self.model.sr
        from narrar import narrar
        return narrar(self.model, texto, ref=str(ref)).cpu()

    def liberar(self):
        if self.model is not None:
            import torch
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def chave_cache(texto, voz, ref, simular):
    from narrar import parametros
    st = ref.stat() if ref.exists() else None
    base = json.dumps({
        "t": texto, "v": voz, "ref": str(ref), "ref_size": st.st_size if st else 0,
        "ref_mtime": int(st.st_mtime) if st else 0, "p": parametros(),
        "modelo": os.environ.get("MODELO", "mtl"), "sim": simular,
    }, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]


def arquivo_fala(dir_falas, linha, parte, voz, chave):
    return dir_falas / f"{linha:05d}-{parte:02d}-{voz}-{chave}.wav"


def limpar_versoes_antigas(dir_falas, linha, parte, manter):
    for f in dir_falas.glob(f"{linha:05d}-{parte:02d}-*.wav"):
        if f != manter:
            f.unlink(missing_ok=True)


def salvar_wav(caminho, wav, sr):
    """Grava tensor (1, n) ou (n,) como WAV mono 16-bit (soundfile, independe da versao do torchaudio)."""
    import soundfile as sf
    sf.write(str(caminho), wav.detach().cpu().reshape(-1).numpy(), int(sr), subtype="PCM_16")


def ler_wav(caminho):
    """Le WAV como tensor mono (1, n) float32 e devolve (tensor, taxa)."""
    import soundfile as sf
    import torch
    dados, sr = sf.read(str(caminho), dtype="float32", always_2d=True)
    return torch.from_numpy(dados.mean(axis=1)).unsqueeze(0), sr


def duracao_wav(caminho):
    import soundfile as sf
    info = sf.info(str(caminho))
    return info.frames / info.samplerate


def ffmpeg(args, cwd):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args]
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit(f"ffmpeg falhou ({r.returncode}): {' '.join(cmd)}")


def loudnorm_2_passadas(wav, cwd):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", wav,
           "-af", f"{LOUDNORM}:print_format=json", "-f", "null", "-"]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if r.returncode != 0 or not m:
        print("aviso: medicao do loudnorm falhou, usando uma passada")
        return LOUDNORM
    d = json.loads(m.group(0))
    if d.get("input_i") in ("-inf", None):  # audio silencioso (ex.: --simular)
        return LOUDNORM
    return (f"{LOUDNORM}:measured_I={d['input_i']}:measured_LRA={d['input_lra']}"
            f":measured_TP={d['input_tp']}:measured_thresh={d['input_thresh']}"
            f":offset={d['target_offset']}:linear=true")


# ---------------------------------------------------------------- legenda

def ts(s):
    h, m, sec = int(s // 3600), int(s % 3600 // 60), s % 60
    return f"{h:02}:{m:02}:{sec:06.3f}".replace(".", ",")


def blocos_legenda(texto):
    palavras, blocos, atual = texto.split(), [], []
    for p in palavras:
        if atual and len(" ".join(atual + [p])) > MAX_CHARS_LEGENDA:
            blocos.append(" ".join(atual))
            atual = []
        atual.append(p)
        if p.endswith((".", "!", "?", "…")) and len(" ".join(atual)) > MAX_CHARS_LEGENDA / 2:
            blocos.append(" ".join(atual))
            atual = []
    if atual:
        blocos.append(" ".join(atual))
    return blocos


def escrever_srt(segmentos, caminho):
    """segmentos: (inicio, fim, texto). Divide cada fala em blocos curtos, tempo proporcional ao tamanho."""
    n, linhas = 0, []
    for ini, fim, texto in segmentos:
        blocos = blocos_legenda(texto)
        total = sum(len(b) for b in blocos) or 1
        t = ini
        for b in blocos:
            d = (fim - ini) * len(b) / total
            n += 1
            linhas.append(f"{n}\n{ts(t)} --> {ts(t + d)}\n{b}\n")
            t += d
    caminho.write_text("\n".join(linhas), encoding="utf-8")


# ---------------------------------------------------------------- principal

def resolver_pasta(entrada):
    p = Path(entrada)
    return (p if p.is_absolute() else CONTEUDO_DIR / p).resolve()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--estimar", action="store_true", help="so estima palavras e duracao")
    ap.add_argument("--amostra", type=float, metavar="SEG", help="gera so os primeiros ~SEG segundos")
    ap.add_argument("--refazer", type=int, nargs="+", metavar="LINHA", help="regera estas linhas do roteiro")
    ap.add_argument("--simular", action="store_true", help="silencio no lugar da voz (testa o fluxo)")
    ap.add_argument("--voz-a", type=Path, default=VOZES["A"])
    ap.add_argument("--voz-b", type=Path, default=VOZES["B"])
    args = ap.parse_args()

    pasta = resolver_pasta(args.pasta)
    roteiro = pasta / "03-roteiro.md"
    if not roteiro.is_file():
        sys.exit(f"roteiro ausente: {roteiro}. Escreva o 03-roteiro.md com a skill podcast antes.")

    itens = ler_roteiro(roteiro)
    palavras, seg_est, por_voz, n_falas = estimar(itens)
    if not n_falas:
        sys.exit("roteiro sem falas [A]/[B]")
    print(f"roteiro: {n_falas} falas, {palavras} palavras (A {por_voz['A']}, B {por_voz['B']}), "
          f"duracao estimada {hms(seg_est)}")
    if args.estimar:
        caps = [i for i in itens if i[0] == "capitulo"]
        print(f"{len(caps)} capitulo(s): " + "; ".join(c[2] for c in caps))
        return

    refs = {"A": args.voz_a.resolve(), "B": args.voz_b.resolve()}
    if not args.simular:
        faltando = [f"{v}: {r}" for v, r in refs.items() if not r.is_file()]
        if faltando:
            sys.exit("voz de referencia ausente -> " + " | ".join(faltando) +
                     "\nGrave 10-20 s de fala limpa em WAV (voz propria ou com autorizacao do dono) "
                     "ou informe --voz-a/--voz-b.")
        if refs["A"] == refs["B"]:
            print("aviso: as duas vozes usam o mesmo arquivo de referencia")

    import torch

    dir_falas = pasta / "04-falas"
    dir_falas.mkdir(exist_ok=True)
    refazer = set(args.refazer or [])
    linhas_validas = {i[1] for i in itens if i[0] == "fala"}
    if refazer - linhas_validas:
        print(f"aviso: linhas sem fala, ignoradas em --refazer: {sorted(refazer - linhas_validas)}")

    motor = Motor(args.simular)
    segmentos, capitulos, pedacos = [], [], []
    t, voz_anterior, geradas, reaproveitadas = 0.0, None, 0, 0
    inicio_execucao = time.perf_counter()
    pendentes_total = n_falas

    for idx, item in enumerate(itens):
        if args.amostra and t >= args.amostra:
            break
        if item[0] == "capitulo":
            capitulos.append((t, item[2]))
            continue
        if item[0] == "pausa":
            if pedacos:
                pedacos.append(("silencio", item[2]))
                t += item[2]
            continue

        _, linha, voz, texto = item
        if pedacos:
            gap = SILENCIO_MESMA_VOZ if voz == voz_anterior else SILENCIO_ENTRE_FALAS
            pedacos.append(("silencio", gap))
            t += gap
        ini_fala = t
        for k, parte in enumerate(dividir_fala(texto)):
            chave = chave_cache(parte, voz, refs[voz], args.simular)
            arq = arquivo_fala(dir_falas, linha, k, voz, chave)
            if linha in refazer:
                arq.unlink(missing_ok=True)
            if arq.is_file():
                reaproveitadas += 1
            else:
                t0 = time.perf_counter()
                wav = motor.gerar(parte, refs[voz])
                salvar_wav(arq, wav, motor.sr)
                limpar_versoes_antigas(dir_falas, linha, k, arq)
                geradas += 1
                feitas = sum(1 for p in pedacos if p[0] == "fala") + 1
                restante = (time.perf_counter() - inicio_execucao) / max(geradas, 1) * max(pendentes_total - feitas, 0)
                print(f"  linha {linha} [{voz}] {wav.shape[-1] / motor.sr:.1f}s em "
                      f"{time.perf_counter() - t0:.1f}s | ~{hms(restante)} restantes | {parte[:60]}", flush=True)
            dur = duracao_wav(arq)
            if k:
                pedacos.append(("silencio", SILENCIO_MESMA_VOZ))
                t += SILENCIO_MESMA_VOZ
            pedacos.append(("fala", arq))
            t += dur
        segmentos.append((ini_fala, t, f"{texto}"))
        voz_anterior = voz

    motor.liberar()
    print(f"falas geradas: {geradas}, reaproveitadas do cache: {reaproveitadas}")

    # junta tudo num WAV temporario (todas as falas na mesma taxa)
    # o primeiro pedaco e sempre uma fala, entao a taxa ja esta definida antes do primeiro silencio
    sr = None
    audio = []
    for tipo, valor in pedacos:
        if tipo == "fala":
            wav, s = ler_wav(valor)
            if sr is None:
                sr = s
            elif s != sr:
                import torchaudio
                wav = torchaudio.functional.resample(wav, s, sr)
            audio.append(wav)
        else:
            audio.append(torch.zeros(1, int(valor * sr)))
    junto = torch.cat(audio, dim=-1)

    nome = "05-amostra" if args.amostra else "05-episodio"
    tmp_wav = pasta / f".{nome}.wav"
    salvar_wav(tmp_wav, junto, sr)
    duracao = junto.shape[-1] / sr
    ffmpeg(["-i", tmp_wav.name, "-af", loudnorm_2_passadas(tmp_wav.name, pasta),
            "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k", f"{nome}.mp3"], cwd=pasta)
    tmp_wav.unlink(missing_ok=True)

    escrever_srt(segmentos, pasta / f"{nome}.srt")
    if capitulos and not args.amostra:
        (pasta / "05-capitulos.txt").write_text(
            "\n".join(f"{hms(c[0])} {c[1]}" for c in capitulos) + "\n", encoding="utf-8")

    print(f"ok: {pasta / (nome + '.mp3')} ({hms(duracao)}; estimado {hms(seg_est if not args.amostra else duracao)})")
    if args.simular:
        print("SIMULACAO: o audio e silencio. Rode sem --simular para gerar as vozes.")


if __name__ == "__main__":
    main()
