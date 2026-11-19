# T2: Arquivos da marca

Para: **Mídia** (escreve o conteúdo) e **Arquivista** (cria as notas no vault e liga no índice). Revisa: **Revisor**.

## O que criar

```
vault/negocios/marca/
  voz-e-tom.md
  guia-de-edicao.md
  roteiros-aprovados/
    README.md
```

Sem esses três itens, `roteiro-reels` e `edicao-video` param logo no início.

## Regra principal

A **voz é do Wederson**. Os agentes montam a estrutura e fazem as perguntas. Não inventam o jeito dele falar. Onde faltar resposta, deixar `[A PREENCHER: pergunta]` e nunca um texto genérico no lugar.

Atalho bom: se ele já tiver vídeos gravados ou textos que escreveu (LinkedIn, posts), o Mídia pode extrair padrões deles e pedir confirmação.

---

## Modelo: voz-e-tom.md

```markdown
---
tipo: marca
atualizado: AAAA-MM-DD
---
# Voz e tom

## Quem fala
- Nome / como se apresenta:
- Para quem fala (público, nível técnico, o que essa pessoa quer):
- Promessa em uma frase (o que o público ganha seguindo):

## Personalidade (3 a 5 traços, cada um com "é / não é")
| Traço | É | Não é |
|-------|---|-------|
| Direto | vai ao ponto em 3 s | grosseiro |

## Jeito de falar
- Trata o público por: você / vocês / galera ...
- Expressões que usa:
- Expressões que nunca usa:
- Nível de gíria e de termo técnico:
- Tamanho das frases (curtas para fala; ideal ≤ 15 palavras):

## Estrutura padrão de um reels
1. Gancho (0–3 s):
2. Contexto ou problema:
3. Conteúdo (1 ideia por vídeo):
4. Fechamento / chamada (CTA):

## Temas
- Pilares (3 a 5):
- Fora de pauta:

## Exemplos
- 2 ou 3 trechos que soam como ele (copiar de roteiros aprovados).
- 1 trecho que NÃO soa como ele, com o motivo.
```

Questionário para o Wederson (o Mídia envia e aguarda as respostas):
1. Para quem são os vídeos? (ex.: devs juniores, donos de pequenos negócios, recrutadores)
2. Qual é o objetivo principal? (portfólio, clientes para ERP, audiência)
3. Cite 2 criadores cujo jeito de falar você gosta e o que gosta neles.
4. Três palavras que descrevem como você quer soar.
5. Algo que você nunca diria num vídeo?
6. Qual é o seu CTA padrão? (seguir, comentar, link na bio ...)

---

## Modelo: guia-de-edicao.md

Já preenchido com padrões técnicos pesquisados. O Mídia ajusta o gosto visual com o Wederson.

```markdown
---
tipo: marca
atualizado: AAAA-MM-DD
---
# Guia de edição

## Formato
- 1080x1920, 9:16, 30 fps, H.264 + AAC (é o que o montar.py já gera).
- Duração alvo: [A PREENCHER: 30–60 s?]

## Zonas seguras (Instagram Reels, 1080x1920)
Guia da Meta em porcentagem, convertido em pixels:
- Topo: 14% ≈ 270 px livres (usuário, rótulo de áudio).
- Base: 35% ≈ 670 px (legenda do post e trilha).
- Lateral direita na parte de baixo: coluna de curtir/comentar/compartilhar, cerca de 230 px.
- Laterais: 6% ≈ 65 px.
- Área central garantida: cerca de 950x980 px.
Na prática: texto de tela e legendas queimadas ficam entre y≈270 e y≈1250, com margem lateral de pelo menos 65 px.

## Legenda queimada (SRT do narrar)
- Fonte: [A PREENCHER], peso bold, tamanho [≈ 60–72 px].
- Cor e contorno: [branco com contorno preto 4 px?]
- No máximo 2 linhas e cerca de 32 caracteres por linha.
- Posição: centro vertical ou terço inferior, sempre acima de y≈1250.

## Ritmo
- Corte ou mudança visual a cada [2–4 s].
- Primeira imagem já é o gancho (nada de logo no início).

## Áudio
- Narração normalizada em [-14 LUFS?]. Música de fundo, se houver, 15–20 dB abaixo da voz.
- Só música livre de direitos.

## Marca visual
- Cores: [A PREENCHER]
- Logo / marca d'água: [sim/não, onde]
- Capa (thumbnail): 1080x1920 com o título dentro da área central.
```

Os números de zona segura vêm do guia da Meta para posicionamentos 9:16 (resumido pela Hopper HQ e pela Socialync). Fontes diferentes dão valores próximos, então fica a regra mais conservadora.

---

## Modelo: roteiros-aprovados/README.md

```markdown
# Roteiros aprovados
Um arquivo por roteiro que o Wederson aprovou e gravou: AAAA-MM-DD-tema.md
Cabeçalho: tema, duração real, link do post, desempenho (views/salvos após 7 dias).
A skill roteiro-reels usa estes arquivos como exemplos de voz. Só entra o que foi aprovado.
```

## Pronto quando

- [ ] Os três itens existem em `vault/negocios/marca/` e a nota índice do vault aponta para eles (Arquivista).
- [ ] `voz-e-tom.md` tem as respostas do Wederson. Os `[A PREENCHER]` que sobraram estão listados para ele.
- [ ] `roteiro-reels` roda até o fim com um tema de teste, sem parar por falta de arquivo.
- [ ] `edicao-video` encontra o `guia-de-edicao.md`.
