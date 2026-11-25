---
name: diagnostico
description: "Analisa o desempenho dos agentes a partir do histórico de sessões (custo, tokens por modelo, ferramentas que falham, skills/agentes nunca usados, correções do usuário) e propõe melhorias concretas para o projeto e para o kit. Use quando o usuário perguntar o que melhorar, por que está gastando muito, se as skills funcionam, ou pedir diagnóstico/retrospectiva."
allowed-tools: Bash(python "${CLAUDE_SKILL_DIR}/scripts/analisar_sessoes.py" *)
---

# Diagnóstico de desempenho

## 1. Coletar
```bash
python "${CLAUDE_SKILL_DIR}/scripts/analisar_sessoes.py" --dias 30            # projeto atual
python "${CLAUDE_SKILL_DIR}/scripts/analisar_sessoes.py" --todos --dias 30    # todos os projetos
```
O script só lê `~/.claude/projects/*/*.jsonl` e imprime um relatório em Markdown.

## 2. Interpretar
| Sinal | Provável causa | Ação |
|---|---|---|
| Custo concentrado no modelo principal, poucos agentes | tudo feito sem delegar | usar `planejar` + `executar` (tarefas P/M em haiku/sonnet) |
| Ferramenta com % de erro alto | comando/caminho errado recorrente (ex.: shell do Windows) | registrar o contorno no `AGENTS.md` |
| Muitas correções do usuário com o mesmo tema | convenção não escrita | criar regra (skill `criar`) |
| Compactações de contexto | sessões longas lendo muito | plano + progresso em arquivo; subagentes para leitura |
| Skill do kit nunca usada | `description` não dispara, ou a skill é desnecessária | reescrever a description ou remover do kit |
| Tarefas reprovadas pelo verificador (ver `plano/progresso.md`) | tarefas grandes ou critérios vagos | dividir tarefas; critérios verificáveis |

Leia também `plano/progresso.md` (se existir) para ver tarefas que falharam ou subiram de modelo — sinal de estimativa de esforço errada.

## 3. Propor
Apresente no máximo 5 melhorias, ordenadas por impacto, cada uma com: evidência (número do relatório), mudança concreta (arquivo e texto) e onde aplicar (**projeto** ou **kit**). Aplique só com o "ok" do usuário.

## 4. Testar skills do kit (opcional, consome uso do plano)
Para medir se uma skill realmente melhora o resultado, use os evals oficiais do Claude Code no repositório do kit:
```bash
claude plugin eval init     # dentro de plugins/ai-kit: cria casos de teste
claude plugin eval          # roda com e sem o plugin e compara
```
Um ganho perto de zero ou "skill não usada" indica que a `description` precisa ser reescrita.
