---
name: executar
description: "Executa o plano em plano/plano.json orquestrando subagentes: entrega cada tarefa ao agente e modelo definidos no plano (executor-leve/haiku, executor/sonnet, executor/opus), roda tarefas independentes em paralelo, confere cada uma com o verificador em modo rápido (haiku), escala quando falha e faz a revisão final em opus. Use quando o usuário pedir para executar, implementar ou continuar o plano."
---

# Executar o plano

Você é o **orquestrador**: decide, delega e confere. Não implemente tarefas você mesmo.

## Antes de começar
- Leia `plano/plano.json` e as últimas entradas de `plano/progresso.md`. Sem plano → `/ai-kit:planejar`.
- Confira/crie a branch do plano, se o projeto usa git.

## Ciclo
1. **Prontas:** `status: "pendente"` com todas as `dependeDe` em `verificado`.
2. **Paralelo:** prontas sem arquivos em comum → várias chamadas de agente na mesma mensagem.
3. **Delegar:** agente = `tarefa.agente` (padrão pelo tamanho: P `executor-leve`, M/G `executor`), passando **`model` = `tarefa.modelo`** e **`effort` = `tarefa.esforco`**. Brief autossuficiente: id, descrição, arquivos, critérios, comandos de verificação, aprendizados anteriores relevantes.
4. **Checagem rápida:** `verificador` com **`model: haiku`, `effort: low`**, passando critérios, arquivos e comandos. Ele roda os comandos e confere os critérios.
5. **Resultado:**
   - APROVADO → `status: "verificado"`.
   - REPROVADO / BLOQUEADA → some 1 em `tentativas` e escale com os problemas apontados:
     `executor-leve (haiku)` → `executor (sonnet)` → `executor (opus/high)` → `depurador (opus)`.
   - Falhou também no `depurador` → `status: "falhou"`, motivo em `notas`, pare e pergunte ao usuário.
6. **Registrar** a cada tarefa: `status`/`tentativas`/`notas` em `plano/plano.json`; em `plano/progresso.md`: `## <data hora> T0X — <status> (<agente>/<modelo>)` + arquivos, evidência, aprendizados. Aprendizado permanente → proponha uma linha no `AGENTS.md`.
7. Repita até não haver tarefas prontas.

## Revisão final (obrigatória)
1. Rode `verificacaoGeral`.
2. `verificador` com o modelo padrão (**opus**) sobre o conjunto das mudanças (`git diff` da branch) e os critérios do plano.
3. Problemas ALTA → volte ao ciclo com tarefas de correção.
4. Resuma: verificadas / escaladas (quais e por quê) / falhas, o que **não** foi verificado. Escalações frequentes indicam estimativa errada — mencione.

## Regras
- Nunca marque `verificado` sem veredito do `verificador`.
- Tarefa maior que o estimado → pare e peça ao `arquiteto` para replanejar só aquele trecho.
- Sem commit/push sem o usuário pedir.
