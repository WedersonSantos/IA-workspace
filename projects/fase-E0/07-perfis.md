# T7: Sistema de perfis (marca + produto)

Pedido do Wederson em 2026-11-19 (Maestri Chat): transformar o questionário de voz e visual em perfis reutilizáveis, porque haverá projetos de afiliado com configuração diferente por produto. Substitui a estrutura de arquivo único da T2 (`voz-e-tom.md` + `guia-de-edicao.md`).

## Estrutura (dentro de `F:\AI-Workspace\vault\negocios\marca\`, pasta já liberada pelo ADR-007)

```
marca/
  _base/
    guia-tecnico.md          padrões técnicos que valem para tudo
  _modelos/
    perfil-marca/
      voz-e-tom.md           modelo em branco
      visual.md              modelo em branco
    produto/
      briefing.md            modelo em branco
  perfis/
    wederson/
      voz-e-tom.md           quem fala
      visual.md              como aparece
  produtos/
    marca-pessoal/
      briefing.md            o que se vende (marca: wederson)
  roteiros-aprovados/        (já existe; mantém)
  _legado/                   voz-e-tom.md e guia-de-edicao.md antigos, MOVIDOS para cá (nunca apagados)
```

## O que vai em cada arquivo

### `_base/guia-tecnico.md` (vale para todo perfil e produto)
Tirado das partes técnicas do `guia-de-edicao.md` atual: formato 1080x1920, 9:16, 30 fps, H.264 + AAC; zonas seguras (topo 270 px, base 670 px, coluna direita 230 px, laterais 65 px, área útil y 270–1250); limites de legenda (no máximo 2 linhas, ~32 caracteres por linha, sempre acima de y 1250); ritmo padrão de corte a cada 2–4 s; áudio a -14 LUFS, música 15–20 dB abaixo da voz, só música livre de direitos; capa 1080x1920 com título na área central. Nada de gosto pessoal aqui.

### `perfis/<marca>/` — quem fala
- `voz-e-tom.md`: perguntas 1 (como se apresenta), 5 (três traços, cada um com "é / não é"), 6 (como chama o público, nível de gíria e de termo técnico), 7 (expressões que usa e que nunca usa), 8 (dois criadores de referência e o que gosta neles). Mais a seção "Exemplos" (trechos de roteiros aprovados), preenchida depois.
- `visual.md`: perguntas 12 (fonte, tamanho 60/66/72 px, cor e contorno, posição da legenda), 13 (cores da marca, fundo sem mídia), 14 (logo ou marca d'água: arquivo, canto, opacidade).
- Frontmatter: `tipo: perfil-marca`, `marca: <slug>`, `atualizado:`.

### `produtos/<produto>/briefing.md` — o que se vende
- Perguntas 2 (público, nível técnico, o que quer), 3 (objetivo principal), 4 (promessa em uma frase), 9 (gancho de abertura e CTA padrão), 10 (pilares de conteúdo e fora de pauta), 11 (duração alvo).
- Campos de afiliado: plataforma; link de afiliado; comissão; aviso de publicidade obrigatório (texto exato a usar no vídeo e na legenda); promessas proibidas (regras do produtor e regras da plataforma, com a fonte de cada regra); material do produtor liberado (o que pode usar e onde está); testei o produto (sim/não, quando, o que achei).
- Frontmatter: `tipo: produto`, `produto: <slug>`, `marca: <slug do perfil de marca>` (obrigatório), `atualizado:`.
- Para `marca-pessoal`, os campos de afiliado ficam `não se aplica`.

## Regras para as skills
1. `roteiro-reels`, `edicao-video` e `podcast` recebem o **nome do produto** (ex.: `marca-pessoal`). A skill lê `produtos/<produto>/briefing.md`, segue o campo `marca:` até `perfis/<marca>/` e lê `_base/guia-tecnico.md`.
2. Se o pedido não disser o produto, a skill **lista os produtos existentes e pergunta**. Nunca escolhe sozinha nem usa um perfil padrão escondido.
3. Se faltar arquivo, se o `marca:` apontar para um perfil inexistente ou se houver `[A PREENCHER]` em campo que a skill usa, a skill para e diz qual arquivo e qual campo preencher.
4. Ordem de precedência quando houver conflito: produto > marca > base, exceto as regras técnicas de zona segura e formato da base, que não podem ser sobrescritas.
5. Aviso de publicidade e promessas proibidas do produto são obrigatórios: o roteiro inclui o aviso e confere que nenhuma promessa proibida aparece. A legenda do post também leva o aviso.
6. `publicar-reels` ainda não existe (é o workflow n8n da T5, bloqueado). Quando for feito, recebe o mesmo nome de produto e usa o aviso de publicidade na legenda. Por ora, só registrar essa regra no briefing da T5.

## Restrições
- Comissão, preço e link de afiliado não vão para Pesquisador nem QA/Teste (Gemini), como já está no `AGENTS.md`.
- Os agentes não preenchem respostas pessoais. Campos sem resposta ficam `[A PREENCHER: pergunta]`.
- `podcast` é skill sincronizada do claude.ai (como roteiro-reels e edicao-video): a versão corrigida vai para `skills/podcast/SKILL.md` no repositório, e o Wederson reenvia.

## Pronto quando
- [ ] Estrutura acima existe; arquivos antigos estão em `_legado/`, não apagados; índice `negocios/CLAUDE.md` atualizado (backup antes).
- [ ] Modelos em `_modelos/` em branco, com as perguntas certas em cada nível e os campos de afiliado no modelo de produto.
- [ ] `perfis/wederson/` e `produtos/marca-pessoal/` criados a partir dos modelos, com `marca: wederson`.
- [ ] As três skills recebem o produto, perguntam quando falta, seguem `marca:` e param com mensagem clara quando falta algo.
- [ ] Revisor aprova; Segurança confere que nenhum dado de afiliado vai para agente Gemini nem para o git.
