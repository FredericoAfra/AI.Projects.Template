# AI.Projects.Template (manutenção do kit)

Este repositório **é o kit**. Princípio: o mínimo suficiente — uma ferramenta por função (ver `docs/decisoes.md`). Antes de adicionar algo, verifique se não duplica uma skill/agente existente ou um recurso nativo do Claude Code.

- Skills/agentes: `plugins/ai-kit/`. Scripts de skill em `skills/<nome>/scripts/`, chamados via `${CLAUDE_SKILL_DIR}`; só biblioteca padrão do Python.
- Arquivos para projetos: `kit/<perfil>/` (caminho relativo = destino). `{{PROJECT_NAME}}` em `.md` é substituído.
- Formato do plano (`plano/plano.json`) é contrato entre `planejar`, `executar`, `verificar` e `ralph.sh`: mudou um, ajuste os outros.
- Antes de commitar: `python aikit.py validate` e um `install` numa pasta temporária.
- Versão em `VERSION`, `plugins/ai-kit/.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json` + `CHANGELOG.md`.
- Conteúdo em português (BR); mensagens dos scripts sem acentos (console do Windows).
