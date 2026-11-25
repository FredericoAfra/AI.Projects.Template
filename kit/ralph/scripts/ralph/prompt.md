# Ralph — tarefa {{TAREFA}}

Você é um agente autônomo executando **uma única tarefa** do plano. Não há humano para responder perguntas.

1. Leia `AGENTS.md`, `plano/plano.json` (tarefa **{{TAREFA}}**) e o fim de `plano/progresso.md` (aprendizados anteriores).
2. Confira a branch do plano (`branch`); crie/troque se necessário.
3. Implemente a tarefa {{TAREFA}} — só ela, a menor mudança que atende a todos os `criterios`.
4. Rode os comandos de `verificacao` da tarefa e corrija até passarem.
5. Verifique com evidência: se o agente `verificador` estiver disponível, delegue a ele; senão, confira cada critério você mesmo (comando + resultado).
6. Atualize `plano/plano.json` na tarefa {{TAREFA}}:
   - todos os critérios comprovados → `"status": "verificado"`;
   - não conseguiu → mantenha `"pendente"`, some 1 em `"tentativas"` e explique em `"notas"`; se `tentativas` chegar a 2, use `"status": "falhou"`.
7. Acrescente em `plano/progresso.md`:
   ```
   ## <data hora> {{TAREFA}} — <status>
   - Arquivos: ...
   - Verificação: <comando> → <resultado>
   - Aprendizados: <padrões, armadilhas úteis para as próximas tarefas>
   ```
8. Se a tarefa passou e o projeto usa git, faça commit: `feat: {{TAREFA}} - <título>`. Nunca faça push.

Regras: não altere outras tarefas; não marque `verificado` sem evidência; aprendizado permanente sobre o projeto → uma linha em `AGENTS.md`.
