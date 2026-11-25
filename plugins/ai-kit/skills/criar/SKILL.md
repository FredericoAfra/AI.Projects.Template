---
name: criar
description: "Cria uma regra, skill ou agente (subagente) a partir de uma descrição em linguagem natural, no projeto ou no kit. Use quando o usuário disser 'cria uma regra', 'sempre/nunca faça X', 'transforma isso em skill', 'automatiza esse processo', 'cria um agente/especialista para Y'."
---

# Criar regra, skill ou agente

## Qual criar?
| Pedido | Tipo | Onde (projeto) |
|---|---|---|
| "sempre / nunca…", convenção | **Regra** | linha na seção *Convenções* do `AGENTS.md`; se for longa ou só para certos arquivos, `.claude/rules/<nome>.md` |
| "como fazer X" (passo a passo repetível) | **Skill** | `.claude/skills/<nome>/SKILL.md` |
| "quem faz X" (especialista, contexto isolado) | **Agente** | `.claude/agents/<nome>.md` |

**Para todos os projetos:** crie no repositório do kit (`plugins/ai-kit/skills/` ou `plugins/ai-kit/agents/`), rode `python aikit.py validate` lá e lembre o usuário de fazer commit + `/plugin marketplace update`.

Antes de criar: procure algo parecido que já exista e **edite** em vez de duplicar. Pergunte no máximo 2 coisas se faltar informação.

## Formatos

**Regra** (`.claude/rules/<nome>.md`)
```markdown
---
description: <o que garante>
paths: ["**/*.sql"]      # opcional: só vale para esses arquivos
---
- <instrução imperativa e verificável> — <porquê, se não for óbvio>
```

**Skill** (`<nome>/SKILL.md`; `name` = nome da pasta, minúsculas e hífens)
```markdown
---
name: <nome>
description: "<o que faz> + <quando usar, com as palavras do usuário>"
---
# <Título>
## Passos
## Saída esperada
## Armadilhas
```
Scripts ficam em `<nome>/scripts/` e são chamados como `python "${CLAUDE_SKILL_DIR}/scripts/x.py"`.

**Agente** (`<nome>.md`; `name` = nome do arquivo)
```markdown
---
name: <nome>
description: "<especialidade>. Use quando <situação>."
tools: Read, Grep, Glob        # omita para herdar todas; só leitura é mais seguro
model: sonnet                  # haiku (barato) | sonnet | opus (difícil) | inherit
effort: medium                 # low | medium | high
---
Você é <papel>. <processo> <formato de resposta curto> <limites>
```

## Qualidade
- A `description` decide quando a skill/agente é usado: diga **o quê** e **quando**. Descrição vaga = nunca usado; ampla demais = usado sem necessidade.
- Curto: regras < 30 linhas, skills < 500 linhas (detalhes em arquivos de referência).
- Depois de criar, teste com um pedido real. Se não for acionado, ajuste a `description`. `/ai-kit:diagnostico` mostra o que nunca é usado.
