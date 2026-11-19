---
name: "roteiro-reels"
description: "Escreve um roteiro novo de reels a partir de vídeos de referência, do tema e da duração alvo, seguindo a voz da marca. Usar quando pedirem roteiro de reels ou de vídeo curto."
---

# Roteiro de reels

Estuda a estrutura de vídeos de referência e escreve um roteiro original. Os vídeos de referência são de outras pessoas: servem para entender gancho, estrutura e ritmo. Nenhum trecho de fala, texto, áudio ou imagem deles entra no roteiro.

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

Perguntar antes de começar se faltar qualquer uma:

- Pasta do vídeo: `F:\AI-Workspace\conteudo\AAAA-MM-DD-<slug>\`
- Links de referência (até 7), ou as transcrições já prontas em `01-referencias\`
- Tema do vídeo novo
- Duração alvo em segundos
- Chamada para ação desejada (opcional; se não vier, propor uma e marcar como sugestão)

## Fontes (onde consultar)

- `01-referencias\` na pasta do vídeo: transcrições dos links (`ref-01.txt` a `ref-07.txt`)
- `F:\AI-Workspace\vault\negocios\marca\roteiros-aprovados\`: de 3 a 5 roteiros que performaram, usados como modelo de formato

Se `voz-e-tom.md` não existir ou estiver vazio, parar e avisar. Nunca inventar dado, número, depoimento ou resultado de cliente.

## Publicidade e alegacoes

Antes de escrever, extraia do briefing do produto o aviso de publicidade
obrigatorio e as promessas proibidas. Se algum campo usado estiver
`[A PREENCHER]` ou sem resposta, pare informando arquivo e campo. Inclua o
aviso obrigatorio no roteiro e na legenda do post. Revise falas, textos na tela,
CTA e legenda contra cada promessa proibida; remova ou reescreva qualquer
alegacao vedada. Nao invente resultados, depoimentos, numeros ou beneficios.

## Passo a passo

1. Conferir produto, briefing, marca, perfil, base e campos usados conforme Antes de comecar. Faltou algo: parar e listar arquivo e campo.
2. Se as transcrições não existirem, ativar o ambiente com `. F:\AI-Workspace\tools\midia\ativar.ps1`, salvar os links em `01-referencias\links.txt` e baixar só o áudio:
   `yt-dlp -x --audio-format wav -o "01-referencias\ref-%(autonumber)02d.%(ext)s" -a 01-referencias\links.txt`
   Transcrever cada arquivo com faster-whisper (modelo `small`, `device="cpu"`, `compute_type="int8"`) e salvar como `ref-NN.txt`.
3. Escrever `01-referencias\analise.md` com uma linha por referência: tipo de gancho, estrutura em blocos, duração, palavras por segundo e tipo de chamada final. Descrever com palavras próprias, sem copiar frases.
4. Escolher a estrutura que melhor serve ao produto e ao tema e justificar em duas linhas no topo do roteiro.
5. Escrever o roteiro no modelo abaixo, na voz descrita em `voz-e-tom.md`.
6. Conferir a duração: contar as palavras das falas e dividir por 2,3 (palavras por segundo em português falado). Ajustar até ficar dentro de 10% da duração alvo.
7. Conferir a originalidade: nenhuma sequência de 6 ou mais palavras pode coincidir com uma transcrição de referência. Reescrever o que coincidir.
8. Salvar em `02-roteiro.md` e parar.

## Resultado esperado

Arquivo `02-roteiro.md` na pasta do vídeo:

```markdown
# <título de trabalho>

- Tema:
- Duração alvo: NN s | Duração estimada: NN s (NNN palavras)
- Estrutura escolhida e motivo:
- Status: aguardando aprovação

## Gancho (0 a 3 s)
Fala:
Prompt visual:

## Cena 01
Fala:
Prompt visual:
Tipo de mídia: imagem | clipe

## Cena 02
...

## Chamada para ação
Fala:
Prompt visual:

## Legenda do post
Texto e hashtags sugeridas.
```

Cada prompt visual descreve uma cena original, sem citar pessoas reais, marcas ou personagens de terceiros.

## Aprovação humana

Esta skill nunca faz sozinha:

- Narrar o texto: a narração só começa depois que o usuário aprovar `02-roteiro.md`.
- Publicar, agendar ou enviar o roteiro a qualquer serviço externo.
- Apagar ou sobrescrever um roteiro já aprovado; uma nova versão vira `02-roteiro-v2.md`.

Ao terminar, responder com o caminho do arquivo, a duração estimada e as dúvidas em aberto.
