# T1: Acertar os caminhos de conteúdo

Para: **Infra** (decide a estrutura) e **Executor** (aplica). Revisa: **Revisor**.

## Problema

- As skills `roteiro-reels` e `edicao-video` procuram `F:\AI-Workspace\conteudo\`, que não existe.
- Os scripts `narrar.py` e `montar.py` estão em `F:\AI-Workspace\tools\midia\` e o exemplo de uso grava em `tools\midia\conteudo\`.

## Recomendação (confirmar com o Wederson, decisão D1)

Usar **`F:\AI-Workspace\conteudo\`** como pasta única dos vídeos.

Motivos:
1. Separa ferramenta (`tools\midia\`, com `.venv`) de produção (os vídeos). Backup, `.gitignore` e limpeza ficam simples.
2. As skills já apontam para lá, então o ajuste é só nos scripts e na documentação.
3. O `montar.py` já recebe a pasta como argumento. Basta passar o caminho absoluto, sem mexer na lógica.

## O que fazer

1. Criar `F:\AI-Workspace\conteudo\` com um `README.md` curto explicando a estrutura de cada vídeo:
   ```
   conteudo\AAAA-MM-DD-tema\
     01-referencias.md      (opcional: links de vídeos de referência)
     02-roteiro.md          (texto falado; # e comentários são ignorados)
     03-narracao.wav / .srt (gerado)
     04-midia\              (cena-01.png, cena-02.mp4 ... em ordem alfabética)
     05-final.mp4           (gerado, 1080x1920, 30 fps)
     06-legenda-post.md     (texto do post, para o publicar-reels)
   ```
2. Se `tools\midia\conteudo\` tiver vídeos, **mover** (não apagar) para `conteudo\`.
3. Nos scripts: se houver caminho fixo ou relativo a `tools\midia\`, trocar por uma variável `CONTEUDO_DIR` com padrão `F:\AI-Workspace\conteudo`. Aceitar tanto o nome da pasta (`2026-11-20-tema`) quanto o caminho completo.
4. Atualizar o `ativar.ps1` para exportar `CONTEUDO_DIR`.
5. Atualizar `roteiro-reels` e `edicao-video` para usar o mesmo caminho e para conferir se ele existe na seção "Antes de começar".
6. Conferir com o Segurança se `conteudo\` precisa entrar no `.gitignore`. Vídeos e WAV não devem ir para o git.

## Pronto quando

- [ ] `python montar.py 2026-11-20-teste` (só o nome) e `python montar.py F:\AI-Workspace\conteudo\2026-11-20-teste` geram o mesmo resultado.
- [ ] Nenhum arquivo do repositório cita `tools\midia\conteudo` (conferir com `rg "midia.conteudo"`).
- [ ] As duas skills e os dois scripts usam o mesmo caminho.
- [ ] `conteudo\` está no `.gitignore` (ou o Segurança registrou por que não).
