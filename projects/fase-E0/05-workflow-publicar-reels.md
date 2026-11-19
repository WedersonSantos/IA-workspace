# T5: Workflow `publicar-reels` (n8n + Zernio)

Para: **Infra** (n8n, node e credencial) + **Executor** (workflow). Revisam: **Segurança** e **Revisor**.

Bloqueado por **D3**: o Wederson escolhe as duas contas sociais.

## Por que cabe no custo zero

O plano grátis do Zernio dá **2 contas conectadas**, posts ilimitados e acesso completo à API, sem cartão. Acima de 2 contas, cobra US$ 6 por conta por mês. Limite grátis: 60 requisições por minuto. As "duas contas" do plano batem com o plano grátis. Não conectar uma terceira.

## Peças

- **Node do n8n:** `n8n-nodes-zernio` (nó comunitário verificado, licença MIT). Também existe como `n8n-nodes-late`, por compatibilidade, porque o Zernio se chamava Late. Instalar pelo painel de Community Nodes.
- **Credencial:** chave de API do painel do Zernio, guardada só na credencial do n8n.
- **API direta** (se preferir o nó HTTP): base `https://zernio.com/api/v1`, cabeçalho `Authorization: Bearer <chave>`.

## Fluxo da API (resumo do llms.txt oficial do Zernio)

1. **Enviar o vídeo:** `POST /v1/media/presign` com `filename` e `contentType` → resposta traz `uploadUrl` e `publicUrl` → `PUT` do arquivo no `uploadUrl` com o mesmo `Content-Type`.
   Isso resolve o fato de o `05-final.mp4` estar no disco local: o Zernio exige URL pública HTTPS, e o presign entrega essa URL.
2. **Criar o post:** `POST /v1/posts`
   ```json
   {
     "content": "<texto de 06-legenda-post.md>",
     "mediaItems": [{ "type": "video", "url": "<publicUrl>" }],
     "platforms": [
       { "platform": "instagram", "accountId": "<ID>" },
       { "platform": "tiktok", "accountId": "<ID>" }
     ],
     "profileId": "<PROFILE_ID>",
     "isDraft": true,
     "timezone": "America/Sao_Paulo"
   }
   ```
   Para agendar: `scheduledFor` (ISO 8601) no lugar de `isDraft`. Para publicar na hora: `publishNow: true`.
3. **Acompanhar:** não há webhook de status de post. Consultar `GET /v1/posts/{postId}` (status `draft`, `scheduled`, `published` ou `failed`). Em caso de falha: `POST /v1/posts/{postId}/retry`.

## Detalhes por plataforma (a Infra confirma no painel)

- **Instagram:** exige conta **Business**. A documentação não tem campo específico de Reels. Vídeo vertical vira Reels. A capa pode ir em `instagramThumbnail`. Testar com 1 post em rascunho antes.
- **TikTok:** objeto `tiktokSettings` com `privacy_level`, `allow_comment`, `allow_duet` e `allow_stitch` (obrigatórios), mais `video_made_with_ai`. **Como a voz é clonada por IA, marcar `video_made_with_ai: true`.** Contas conectadas pelo TikTok for Business só publicam como público. Para revisar no app antes, usar `draft: true`. Limite de 15 vídeos por 24 h.
- **YouTube Shorts:** a documentação não trata Shorts. Fica fora desta fase.

## Desenho do workflow (aprovação humana obrigatória)

```
[Gatilho manual ou webhook local com: pasta do vídeo]
  → ler 05-final.mp4 e 06-legenda-post.md
  → presign + upload
  → POST /v1/posts com isDraft: true      ← nunca publishNow nesta fase
  → avisar o Wederson (link do rascunho no painel Zernio)
  → [Wederson aprova no painel ou responde "publica"]
  → (opcional) PUT no post com scheduledFor
  → consultar status até published/failed → registrar no vault
```

Regra do projeto: "publicar é sempre com você". O workflow **nunca** publica direto. Sempre cria rascunho ou agendamento que o Wederson confirma.

## Checagens do Segurança

- [ ] A chave do Zernio está só na credencial do n8n. Não está em JSON exportado do workflow nem no git.
- [ ] Workflow exportado para o repositório sem credenciais (o n8n exporta só a referência; conferir).
- [ ] Nenhum caminho do workflow usa `publishNow: true`.
- [ ] Só 2 contas conectadas no Zernio (para não sair do plano grátis).

## Pronto quando

- [ ] Um vídeo de teste aparece como **rascunho** nas 2 contas escolhidas.
- [ ] O status é consultado e registrado.
- [ ] O Wederson confirmou que o fluxo de aprovação é confortável.
