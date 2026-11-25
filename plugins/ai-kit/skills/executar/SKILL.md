---
name: executar
description: "Executa o plano em plano/plano.json orquestrando subagentes: delega cada tarefa ao agente executor com o modelo e o esforço definidos no plano, roda tarefas independentes em paralelo, verifica cada uma com o agente verificador e registra o progresso. Use quando o usuário pedir para executar, implementar ou continuar o plano."
---

# Executar o plano

Você é o **orquestrador**: decide, delega e confere. Não implemente tarefas você mesmo (exceto ajustes triviais de integração) — isso mantém seu contexto limpo para coordenar.

## Antes de começar
- Leia `plano/plano.json` e as últimas entradas de `plano/progresso.md`. Sem plano? Sugira `/ai-kit:planejar`.
- Confira a branch do plano (`branch`); crie-a se não existir e o projeto usar git.

## Ciclo
1. **Escolher** as tarefas prontas: `status: "pendente"` e todas as `dependeDe` já `verificado`.
2. **Agrupar**: tarefas prontas **sem arquivos em comum** rodam em paralelo (várias chamadas ao agente na mesma mensagem). As demais, uma de cada vez.
3. **Delegar** cada tarefa ao agente `executor`, passando **`model` = `tarefa.modelo` e `effort` = `tarefa.esforco`**. O brief deve ser autossuficiente (o executor não vê esta conversa):
   `id · descrição · arquivos · critérios · comandos de verificação · decisões/aprendizados anteriores relevantes`.
4. **Verificar** cada tarefa concluída com o agente `verificador` (passe os critérios e a lista de arquivos).
   - APROVADO → `status: "verificado"`.
   - REPROVADO/INCOMPLETO → devolva ao `executor` com os problemas apontados, **subindo um nível** (P→M: sonnet/medium; M→G: opus/high). Segunda falha → `status: "falhou"`, anote o motivo em `notas` e pare para perguntar ao usuário.
5. **Registrar** ao fim de cada tarefa:
   - atualize `status` e `notas` em `plano/plano.json`;
   - acrescente em `plano/progresso.md`: `## <data hora> T0X — <status>` + arquivos, evidência da verificação, aprendizados.
   - aprendizado permanente sobre o projeto (convenção, comando, armadilha) → proponha uma linha no `AGENTS.md`.
6. Repita até não haver tarefas prontas.

## Ao terminar
- Rode `verificacaoGeral` do plano.
- Resuma: tarefas verificadas / falhas / bloqueadas, o que **não** foi verificado, próximos passos.
- Para mudanças grandes, ofereça uma revisão cruzada com outro modelo (`/ai-kit:consultar-modelos`).
- Não faça commit/push sem o usuário pedir.

## Regras
- Nunca marque `verificado` sem o veredito do `verificador`.
- Se uma tarefa se revelar maior que o estimado, pare e replaneje só aquele trecho (atualize `pontos`/`tamanho`/`modelo`).
- Sessão longa? O próprio `plano.json` + `progresso.md` são o estado: outra sessão continua com `/ai-kit:executar`.
