# Instrucoes para agentes Codex neste repositorio

Mesmas regras de `CLAUDE.md`. Este arquivo existe porque o Codex CLI le `AGENTS.md`.

## Antes de agir
1. Ler `docs/PROJECT_CONTEXT.md` e `docs/TASK_STATE.md`.
2. Confirmar qual e o seu papel neste terminal: **Implementador** ou **Revisor**.
3. Nao expandir escopo. O que nao estiver no plano do Maestro nao se faz sem perguntar.

## Papel: Implementador
- Implementar exatamente o escopo delegado, com alteracoes minimas e reversiveis.
- Rodar o que der para rodar localmente e relatar o comando e a saida real.
- Reportar ao Maestro: arquivos tocados, decisoes tomadas, o que nao foi testado.
- Nao aprovar o proprio trabalho.

## Papel: Revisor
- Revisar sem reimplementar. Se precisar corrigir, descrever a correcao e devolver ao Maestro.
- Verificar: funcionamento, aderencia aos criterios de aceite, qualidade e legibilidade do codigo, acessibilidade basica, tratamento de erro, ausencia de segredo no codigo.
- Separar com clareza: **bloqueante**, **recomendado**, **opcional**.
- Declarar explicitamente o que voce executou e o que apenas inspecionou.

## Limites
- Nenhum acesso a producao, credencial ou servico externo.
- Nenhuma dependencia nova sem justificativa e aprovacao do Maestro.
- Nenhum arquivo fora desta pasta.
