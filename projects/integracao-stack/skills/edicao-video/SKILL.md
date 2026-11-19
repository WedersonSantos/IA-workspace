---
name: "edicao-video"
description: "Monta, corta e legenda um reels com FFmpeg a partir da narração e das mídias da pasta do vídeo, seguindo o guia de edição da marca. Usar quando pedirem para editar ou montar o vídeo."
---

# Edição de vídeo

Monta o vídeo final com FFmpeg, aplicando as regras escritas no guia de edição. O estilo vem do guia, não de suposição: recurso que o guia não descreve não é usado.

## Antes de comecar

1. Exija o nome do produto. Se nao veio no pedido, liste as pastas existentes
   em `F:/AI-Workspace/vault/negocios/marca/produtos/` e pergunte qual usar. Nunca escolha um padrao.
2. Leia `F:/AI-Workspace/vault/negocios/marca/produtos/<produto>/briefing.md` e o campo `marca:` do frontmatter.
   Se o arquivo ou campo faltar, pare e informe arquivo e campo. Siga esse valor,
   sem inferir a marca.
3. Leia `F:/AI-Workspace/vault/negocios/marca/perfis/<marca>/voz-e-tom.md`,
   `F:/AI-Workspace/vault/negocios/marca/perfis/<marca>/visual.md` e `F:/AI-Workspace/vault/negocios/marca/_base/guia-tecnico.md`.
   Se o perfil apontado nao existir, ou qualquer arquivo necessario faltar,
   pare e informe o caminho e campo pendente.
4. Identifique os campos usados nesta etapa. Se algum deles tiver
   `[A PREENCHER]`, pare e informe o arquivo e o campo exato. Nao substitua
   dados em branco por suposicoes.
5. Em conflitos, aplique produto > marca > base. Regras de formato e zona
   segura de `_base/guia-tecnico.md` sao obrigatorias e nao podem ser
   sobrescritas pelos perfis de marca ou produto.

## Entradas

- Pasta do vídeo: `F:\AI-Workspace\conteudo\AAAA-MM-DD-<slug>\`

Se a pasta não for informada, perguntar.

## Fontes (onde consultar)

- `02-roteiro.md`: ordem das cenas e a fala de cada uma
- `03-narracao.wav`: áudio que define a duração do vídeo
- `04-midia\`: imagens e clipes, nomeados `cena-01.png`, `cena-02.mp4` e assim por diante

Se o guia não existir, ou se faltar narração ou mídia de alguma cena, parar e listar o que falta. Nunca trocar a mídia que falta por tela preta, imagem repetida ou material de terceiros.

## Passo a passo

1. Ativar o ambiente: `. F:\AI-Workspace\tools\midia\ativar.ps1`.
2. Conferir as fontes. Comparar as cenas de `02-roteiro.md` com os arquivos de `04-midia\` e parar se houver cena sem mídia.
3. Medir a narração com `ffprobe` e anotar a duração.
4. Transcrever `03-narracao.wav` com faster-whisper (`word_timestamps=True`) e gerar `legendas.srt`. Corrigir o texto da legenda pelo roteiro aprovado, mantendo os tempos.
5. Escrever `plano-de-edicao.md`: para cada cena, arquivo, início e fim (tirados dos tempos da legenda) e o recurso do guia aplicado (corte, zoom, B-roll).
6. Montar com FFmpeg conforme o plano. Padrão, se o guia não disser outra coisa: 1080x1920, 30 fps, H.264, AAC, imagens preenchendo a tela sem distorcer.
7. Queimar a legenda no estilo descrito no guia (fonte, tamanho, cor, posição).
8. Exportar `05-final.mp4`. Se o arquivo já existir, salvar como `05-final-v2.mp4`.
9. Conferir com `ffprobe`: resolução, taxa de quadros, presença de áudio e duração igual à da narração, com tolerância de 0,5 s. Fora disso, corrigir antes de entregar.
10. Escrever `publicar.json` e parar.

## Resultado esperado

Na pasta do vídeo: `05-final.mp4`, `legendas.srt`, `plano-de-edicao.md` e `publicar.json` neste modelo:

```json
{
  "arquivo": "05-final.mp4",
  "legenda": "",
  "hashtags": [],
  "contas": [],
  "data_hora": "",
  "status": "aguardando_aprovacao"
}
```

`legenda` e `hashtags` vêm de `02-roteiro.md`. `contas` e `data_hora` ficam vazios se o usuário não informou.

Na resposta ao usuário, informar o caminho do vídeo, a duração, os recursos do guia aplicados e qualquer regra do guia que não deu para cumprir.

## Aprovação humana

Esta skill nunca faz sozinha:

- Publicar ou agendar o vídeo, nem disparar o workflow `publicar-reels` do n8n. O usuário assiste, aprova e aperta o botão.
- Mudar o `status` de `publicar.json` para aprovado.
- Apagar ou alterar os originais em `04-midia\`, a narração ou o roteiro.
- Baixar trilha, fonte, imagem ou efeito da internet.
