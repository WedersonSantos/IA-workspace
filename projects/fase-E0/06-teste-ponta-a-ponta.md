# T6: Teste ponta a ponta

Para: **QA/Teste**. Revisa: **Revisor**. Depende de T1, T2, T3 e T5.

## Roteiro do teste

Tema de teste curto (30 s), algo que o Wederson não se importe de descartar.

| Passo | Pedido em linguagem natural | Esperado |
|-------|------------------------------|----------|
| 1 | "Escreve um roteiro de reels sobre X, 30 segundos" | `roteiro-reels` cria `conteudo\AAAA-MM-DD-x\02-roteiro.md` na voz do voz-e-tom.md |
| 2 | Wederson aprova ou ajusta o roteiro | — |
| 3 | "Narra esse roteiro" | `narrar` gera `03-narracao.wav` + `.srt` |
| 4 | Wederson ouve e aprova | — |
| 5 | "Monta o vídeo" | `edicao-video` gera `05-final.mp4` seguindo o guia-de-edicao.md |
| 6 | Conferência visual | Legenda dentro da zona segura (entre y≈270 e y≈1250); 1080x1920; 30 fps |
| 7 | "Prepara para publicar" | `publicar-reels` cria **rascunho** nas 2 contas |
| 8 | Wederson decide | Publica ou descarta. Nada sai sozinho. |

## Casos de falha que precisam de mensagem clara

- [ ] Sem `voz-e-tom.md` → roteiro-reels explica o que falta.
- [ ] Sem `02-roteiro.md` → narrar oferece criar o roteiro.
- [ ] Sem `voz-referencia.wav` → narrar explica como gravar.
- [ ] Sem `04-midia\` → vídeo sai com fundo liso (comportamento atual) e avisa.
- [ ] Zernio ou n8n fora do ar → workflow avisa e não perde o vídeo.

## Conferências técnicas

- `ffprobe 05-final.mp4` → 1080x1920, 30 fps, h264, aac.
- Duração do vídeo ≈ duração do WAV (diferença até 0,5 s).
- Abrir o SRT e conferir 3 marcações contra o áudio.

## Pronto quando

Os 8 passos rodam sem intervenção técnica (só as aprovações do Wederson), e todos os casos de falha estão marcados.
