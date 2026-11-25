# Decisões do kit (2026-11-25)

Uma ferramenta por função. As alternativas ficam registradas para reavaliar quando o kit não bastar.

| Função | Escolhido | Por quê | Alternativas (quando considerar) |
|---|---|---|---|
| Planejar | skill `planejar` | Leve, sem dependências, e escolhe modelo/esforço por tarefa | [GitHub Spec Kit](https://github.github.com/spec-kit/) (projeto grande, várias pessoas); [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) (simular um time ágil completo); [Task Master](https://github.com/eyaltoledano/claude-task-master) |
| Executar | skill `executar` + agente `executor`; `ralph.sh` para modo autônomo | Mesmo `plano.json` nos dois modos; modelo barato onde dá | Agent teams do Claude Code; [Claude Squad](https://github.com/smtg-ai/claude-squad) (muitas sessões paralelas) |
| Verificar | agente `verificador` + skill `verificar` | Evidência obrigatória; independente de quem implementou | Plugin oficial `/code-review` (revisão de PR em paralelo) |
| Outros modelos | skill `consultar-modelos` via CLIs (Codex, Gemini, Copilot) | Usa assinaturas existentes, sem chave de API, somente leitura | [PAL MCP server](https://github.com/beehiveinnovations/zen-mcp-server) (50+ modelos via API/OpenRouter); protocolo A2A (agentes como produto) |
| Melhorar | skill `diagnostico` (histórico de sessões) + `claude plugin eval` | Mede uso real e o efeito das skills | [ccusage](https://github.com/ryoppippi/ccusage) (só custos); Langfuse/promptfoo (agentes em produção) |
| Instruções | `AGENTS.md` (+ `CLAUDE.md` com `@AGENTS.md`) | Padrão aberto lido pela maioria das ferramentas | [rulesync](https://github.com/dyoshikawa/rulesync) (se precisar de regras por ferramenta) |
| Distribuição | plugin + instalador mínimo | Skills/agentes num lugar só; projeto só recebe o que é dele | Copiar `.claude/` para cada projeto (offline) |

## Retirado na v3 (e por quê)
- `prd`, `ralph` (conversor), `orquestrar`, `handoff` → absorvidos por `planejar`/`executar` (o `plano.json` + `progresso.md` já são o handoff).
- `nova-regra`, `nova-skill`, `novo-agente` → uma skill `criar`.
- Agentes `planejador`, `pesquisador`, `revisor` → o Claude Code já tem `Plan`, `Explore` e `general-purpose`; revisão virou `verificador`.
- Biblioteca de regras e `aikit sync/new/add-rule` → regras ficam no `AGENTS.md` do projeto.

## Ferramentas úteis, fora do kit
- [Context7](https://github.com/upstash/context7) (MCP): documentação atualizada de bibliotecas.
- [Serena](https://github.com/oraios/serena) (MCP): navegação por símbolo em bases de código grandes.
- MCP de banco de dados: quando o projeto tiver banco, para o agente conferir números direto.
