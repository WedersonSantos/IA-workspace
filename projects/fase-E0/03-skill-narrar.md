# T3: Skill `narrar`

Para: **Executor**. Revisa: **Revisor**. Testa: **QA/Teste**, com o **Mídia** ouvindo o resultado.

## Contexto

A geração de voz já funciona por script (`narrar.py` e `montar.py`, Chatterbox local, voz clonada de `tools\midia\voz-referencia.wav`). Nenhuma skill chama esses scripts. A skill `narrar` serve de ponte, para que pedir "narra o roteiro de amanhã" funcione.

## O que já se sabe dos scripts (confirmar lendo o código)

- Ativação: `cd F:\AI-Workspace\tools\midia` e depois `. .\ativar.ps1`
- Uma frase: `python narrar.py "texto" saida.wav`
- Vídeo inteiro: `python montar.py <pasta>` gera `03-narracao.wav`, `03-narracao.srt` e `05-final.mp4`
- Variáveis: `EXAGGERATION` (padrão 0.9), `CFG_WEIGHT` (padrão 0.2), `MODELO=pt` (modelo afinado para português em vez do multilíngue)

**Pergunta para o Executor resolver no código:** existe um modo de gerar só a narração e o SRT, sem montar o vídeo? Se não existir, adicionar uma flag `--so-narracao` ao `montar.py` (ou um `narrar_roteiro.py`). Assim a skill `narrar` não depende de mídia e a `edicao-video` fica com a montagem.

## Referência de ajuste da voz (pesquisa no README do Chatterbox)

| Parâmetro | Efeito | Referência oficial |
|-----------|--------|--------------------|
| `exaggeration` | Mais emoção e intensidade. Valores altos também **aceleram** a fala. | Padrão do modelo 0.5; dramático ≥ 0.7 |
| `cfg_weight` | Ritmo e aderência à referência. Mais baixo deixa a fala mais pausada. | Padrão 0.5; locutor rápido ≈ 0.3; `0` reduz o sotaque quando a referência está em outra língua |

Os padrões atuais do Wederson (0.9 / 0.2) já são uma combinação "expressiva com ritmo compensado". Manter, mas registrar na skill como ajustar:

- Fala atropelada → baixar `EXAGGERATION` para 0.6–0.7.
- Fala arrastada ou robótica → subir `CFG_WEIGHT` para 0.3–0.4.
- Sotaque estranho ou palavras em inglês mal pronunciadas → testar `MODELO=pt`.
- Saída de 24 kHz, mono (padrão do Chatterbox).

## Rascunho do SKILL.md (o Executor completa)

```markdown
---
name: narrar
description: Gera a narração com a voz clonada do Wederson (Chatterbox local) a partir do 02-roteiro.md de um vídeo, produzindo 03-narracao.wav e 03-narracao.srt. Usar quando pedirem para narrar, gerar a voz, gravar o áudio ou testar a voz de um roteiro.
---

# Narrar

## Antes de começar
1. Confirmar que `tools\midia\voz-referencia.wav` existe. Se não existir, parar e explicar como gravar (10–20 s, lugar silencioso, WAV).
2. Confirmar que a pasta do vídeo existe em `CONTEUDO_DIR` e tem `02-roteiro.md` com texto. Se não tiver, oferecer a skill roteiro-reels.
3. Confirmar que o ambiente ativa (`ativar.ps1`) e que `python -c "import chatterbox"` funciona.

## Passos
1. Ler o roteiro e mostrar a contagem de palavras e a duração estimada (≈ 150 palavras/min em PT-BR) antes de gerar.
2. Gerar a narração e o SRT [comando definido pelo Executor].
3. Informar a duração real do WAV e o caminho dos arquivos.
4. Pedir ao Wederson que ouça. Se ele não aprovar, perguntar o problema e aplicar a tabela de ajuste.

## Teste rápido
`python narrar.py "Olá, teste" teste.wav`, para checar a voz sem gerar o vídeo.

## Nunca
- Sobrescrever `voz-referencia.wav`.
- Usar uma voz de referência que não seja do Wederson.
```

## Pronto quando

- [ ] Pedir "narra o vídeo 2026-11-20-teste" gera WAV + SRT na pasta certa, sem montar o vídeo.
- [ ] A skill para com uma mensagem clara quando falta o roteiro ou a voz de referência (QA/Teste testa os dois casos).
- [ ] O SRT bate com o áudio (QA/Teste confere 3 pontos: início, meio e fim).
- [ ] O Mídia ouviu e aprovou, ou registrou os ajustes de parâmetro que funcionaram.
- [ ] `edicao-video` passa a chamar `narrar` em vez de duplicar essa lógica (ou o Revisor registra por que não).
