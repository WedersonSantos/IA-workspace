# Fase E0: preparar a automação de conteúdo

Para: **Cérebro (Maestro)**. Este arquivo é o plano da fase. Os outros arquivos desta pasta são os briefings de cada tarefa.

Origem: o levantamento de 19/11/2026 ("Skills que temos / O que ainda falta") e pesquisa na web feita no mesmo dia.

## Objetivo da fase

Deixar o fluxo **roteiro → narração → edição → publicação** funcionando de ponta a ponta, e criar o **resumo-whatsapp**. Tudo com custo zero além da assinatura Claude, e com a publicação sempre aprovada pelo Wederson.

## Decisões que só o Wederson pode tomar (pedir antes de começar)

| # | Decisão | Bloqueia | Recomendação |
|---|---------|----------|--------------|
| D1 | Pasta única de conteúdo | T1, T3, T4 | `F:\AI-Workspace\conteudo\` (ver 01-caminhos.md) |
| D2 | Respostas do questionário de voz e tom | T2 | Ele responde. Os agentes não inventam a voz dele. |
| D3 | As duas contas sociais do Zernio | T5 | O plano grátis do Zernio cobre exatamente 2 contas. Instagram precisa ser conta Business ou Creator. |
| D4 | Quais conversas e grupos entram no resumo do WhatsApp, e a janela de tempo | T4 | Começar com uma lista fixa de 3 a 5 conversas e janela de 24 h |

## Tarefas, ordem e responsáveis

| Tarefa | Briefing | Faz | Revisa | Depende de |
|--------|----------|-----|--------|------------|
| T1 Acertar caminhos | 01-caminhos.md | Infra + Executor | Revisor | D1 |
| T2 Arquivos da marca | 02-arquivos-da-marca.md | Mídia + Arquivista | Revisor | D2 |
| T3 Skill `narrar` | 03-skill-narrar.md | Executor | Revisor + QA/Teste (Mídia ouve o áudio) | T1 |
| T4 Skill `resumo-whatsapp` | 04-skill-resumo-whatsapp.md | Pesquisador → Executor | Segurança + Revisor + QA/Teste | D4 |
| T5 Workflow `publicar-reels` | 05-workflow-publicar-reels.md | Infra + Executor | Segurança + Revisor | D3, T1 |
| T6 Teste ponta a ponta | 06-teste-ponta-a-ponta.md | QA/Teste | Revisor | T1–T3, T5 |

T1 e T2 podem andar em paralelo. T4 é independente do fluxo de vídeo e pode andar em paralelo também.

## Regras que valem para todas as tarefas

- Ler `AGENTS.md` antes de agir (como já está definido para cada agente).
- Nunca ler, imprimir nem commitar `.env`. Chaves (Evolution, Zernio) entram só por variável de ambiente.
- Nada é publicado nem enviado sem aprovação explícita do Wederson. Skills e workflows param num rascunho.
- Toda skill nova segue o formato SKILL.md com frontmatter `name` + `description`. A `description` diz **o que faz e quando usar**, com as palavras que o Wederson usaria para pedir.
- Toda skill nova tem uma seção "Antes de começar" que verifica os pré-requisitos e para com uma mensagem clara se faltar algo (o problema atual de roteiro-reels e edicao-video é parar sem dizer o que fazer).

## Fora desta fase

- Transcrever áudios do WhatsApp (dá para fazer depois com Whisper local).
- Postar em mais de 2 contas (sai do plano grátis do Zernio).
- YouTube Shorts (a documentação do Zernio não trata Shorts de forma específica).
