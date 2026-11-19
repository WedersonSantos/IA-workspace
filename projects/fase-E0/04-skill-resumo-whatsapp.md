# T4: Skill `resumo-whatsapp`

Para: **Pesquisador** (confirmar a API na instância real) → **Executor** (implementar). Revisam: **Segurança**, **Revisor** e **QA/Teste**. **Infra** confirma onde a Evolution API roda.

## Objetivo

Ler as mensagens das últimas N horas em conversas e grupos escolhidos e gerar uma nota de resumo no vault: o que foi decidido, o que pediram ao Wederson, o que ele precisa responder e links compartilhados. **Só leitura. A skill nunca envia mensagem.**

Decisão D4 pendente: quais conversas e qual janela. Sugestão: lista fixa de 3 a 5 JIDs num arquivo de configuração e 24 h.

## API (Evolution API v2): o que a pesquisa encontrou

Autenticação: cabeçalho `apikey: [SEGREDO] em todas as chamadas.

1. **Listar conversas**: `POST /chat/findChats/{instance}`
   Devolve conversas individuais e grupos. O campo `isGroup` diferencia os dois. Usar para montar a lista de JIDs na primeira configuração.

2. **Buscar mensagens**: `POST /chat/findMessages/{instance}`
   ```json
   {
     "where": {
       "key": { "remoteJid": "[WHATSAPP_ID]" },
       "messageTimestamp": { "gte": "2026-11-18T10:00:00-03:00", "lte": "2026-11-19T10:00:00-03:00" }
     },
     "page": 1,
     "offset": 50
   }
   ```
   - O exemplo da documentação oficial mostra **só** `where.key.remoteJid`.
   - O filtro `messageTimestamp` com `gte` e `lte` foi adicionado num commit do repositório (o código converte as datas para epoch em segundos). **O Pesquisador precisa confirmar se a versão instalada tem esse filtro.** Se não tiver, buscar por páginas e filtrar no script.
   - Paginação: `page` + `offset` (é o que a v2 usa, segundo um PR de correção da documentação). Confirmar o formato da resposta na instância. Pode vir `{ messages: { records: [...] } }` ou uma lista simples. O script precisa tratar os dois casos.
   - Grupos: JID termina em `@g.us`. Conversas individuais terminam em `@s.whatsapp.net`.

3. Problema conhecido: `findContacts` às vezes não devolve `pushName`. Para nomear quem falou, usar o `pushName` que vem na própria mensagem e, se faltar, o número.

## Desenho sugerido

```
tools/whatsapp/
  buscar_mensagens.py   # chama a Evolution, normaliza, grava JSON temporário
  conversas.yaml        # lista de JIDs + apelido (sem dados sensíveis)
skills/resumo-whatsapp/SKILL.md
vault/diario/whatsapp/AAAA-MM-DD.md   # saída (o Arquivista confirma o caminho)
```

`buscar_mensagens.py`:
- Lê `EVOLUTION_URL`, `EVOLUTION_INSTANCE` e `EVOLUTION_APIKEY` do ambiente. **Nunca** imprime a chave nem lê o `.env` diretamente na skill.
- Para cada JID: busca a janela e normaliza cada mensagem para `{hora, autor, tipo, texto}`.
- Mídia sem texto vira um marcador: `[áudio 0:42]`, `[imagem]`, `[documento: nome.pdf]`. A legenda da imagem entra como texto.
- Grava em pasta temporária fora do vault e do git. Apaga no fim.

O resumo é feito pelo **próprio Claude dentro da skill** (custo zero, já está na assinatura). Não chamar outro LLM pago. Se o volume for grande, o script entrega por conversa e a skill resume uma por vez.

## Rascunho do SKILL.md

```markdown
---
name: resumo-whatsapp
description: Resume as conversas e grupos de WhatsApp escolhidos nas últimas horas (via Evolution API, só leitura) numa nota do vault com decisões, pedidos, pendências de resposta e links. Usar quando pedirem resumo do WhatsApp, o que perdi no zap, resumo dos grupos ou pendências de mensagens.
---

# Resumo do WhatsApp

## Antes de começar
1. Conferir se a Evolution responde (status da instância = open). Se não responder, parar e dizer qual serviço subir.
2. Conferir se `conversas.yaml` existe e tem pelo menos 1 JID.

## Passos
1. Rodar `buscar_mensagens.py --horas 24` (ou o período pedido).
2. Para cada conversa, extrair:
   - Decisões tomadas
   - Pedidos feitos ao Wederson (quem, o quê, prazo)
   - Perguntas sem resposta dele
   - Links e arquivos citados
3. Gravar em `vault/diario/whatsapp/AAAA-MM-DD.md` no modelo abaixo.
4. Mostrar no chat só a seção "Precisa de você".

## Modelo da nota
# WhatsApp: AAAA-MM-DD (janela: HH:MM–HH:MM)
## Precisa de você
- [ ] (conversa) pedido, quem pediu, prazo
## Por conversa
### Apelido da conversa
- Decisões:
- Assuntos:
- Links:

## Nunca
- Enviar, responder ou reagir a mensagens.
- Copiar mensagens inteiras para o vault. Só resumo.
- Incluir números de telefone completos na nota (usar o apelido).
```

## Checagens do Segurança

- [ ] A chave da Evolution está só em variável de ambiente e não aparece em log nem em output.
- [ ] O JSON temporário fica fora do vault e do repositório e é apagado ao final.
- [ ] `conversas.yaml` sem números reais no git (ou o arquivo está no `.gitignore`).
- [ ] A skill não tem nenhum caminho de envio (nenhum `sendText` etc.).
- Observação de risco: a Evolution usa conexão não oficial do WhatsApp (Baileys). Só leitura e baixo volume mantém o risco de bloqueio do número baixo, mas vale registrar.

## Pronto quando

- [ ] Rodando com 2 conversas reais, a nota sai no vault com as quatro seções.
- [ ] Mensagens de áudio e imagem aparecem como marcadores, sem quebrar o script.
- [ ] Com a Evolution desligada, a skill para com uma mensagem clara (QA/Teste).
- [ ] O Segurança marcou todas as checagens acima.
