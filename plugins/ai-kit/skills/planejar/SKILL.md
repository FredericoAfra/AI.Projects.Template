---
name: planejar
description: "Planeja um projeto ou funcionalidade com o agente arquiteto (opus): transforma o pedido em especificação confirmada pelo usuário, quebra em tarefas verificáveis, classifica o esforço de cada uma (P/M/G) e define agente e modelo. Gera plano/PLANO.md e plano/plano.json. Use quando o usuário quiser planejar, especificar, criar um PRD, estimar esforço ou começar algo novo."
---

# Planejar

Esta skill só **coordena**: o raciocínio pesado é do agente `arquiteto` (opus). Nada é implementado aqui.

## 1. Especificar e confirmar
Se ainda não houver uma especificação confirmada nesta conversa (a skill `fazer` pode já ter feito isso):
1. Chame o `arquiteto` em modo ESPECIFICAR com o pedido literal do usuário.
2. Mostre ao usuário a especificação e as perguntas; registre as respostas. Repita até não haver dúvida que mude o resultado.

## 2. Gerar o plano
Chame o `arquiteto` em modo PLANEJAR, passando a especificação confirmada e as regras abaixo. Ele grava `plano/plano.json` e `plano/PLANO.md`.

### Classificação de esforço (pontos por tarefa)
| Fator | 0 | 1 | 2 |
|---|---|---|---|
| Escopo | 1 arquivo | 2–4 arquivos | 5+ → **dividir** |
| Clareza | segue padrão existente | exige decisão de design | ambígua / exige pesquisa |
| Risco | local e reversível | dados ou integrações | segurança, produção, irreversível |
| Verificação | teste/comando automático | conferência manual | difícil de verificar |

| Pontos | Tamanho | `agente` | `modelo` | `esforco` |
|---|---|---|---|---|
| 0–1 | P | `executor-leve` | `haiku` | `low` |
| 2–3 | M | `executor` | `sonnet` | `medium` |
| 4–5 | G | `executor` | `opus` | `high` |
| 6+ | — | dividir, ou criar uma tarefa de investigação para o `arquiteto` | | |

Tarefas de dados (esquema, SQL, DAX) de tamanho M/G podem usar `agente: "analista-dados"`.

### Formato de `plano/plano.json`
```json
{
  "projeto": "nome",
  "objetivo": "resultado final verificável",
  "branch": "feat/nome-kebab",
  "verificacaoGeral": ["comando que valida o projeto todo"],
  "tarefas": [
    {
      "id": "T01",
      "titulo": "Criar tabela de turnos",
      "descricao": "O que fazer, onde e por quê — sem precisar adivinhar.",
      "dependeDe": [],
      "arquivos": ["db/schema.sql"],
      "pontos": 2, "tamanho": "M",
      "agente": "executor", "modelo": "sonnet", "esforco": "medium",
      "motivoEsforco": "decisão de esquema",
      "criterios": ["Tabela turnos com colunas equipe_id, data, inicio, fim"],
      "verificacao": ["python scripts/carga.py --teste"],
      "status": "pendente", "tentativas": 0, "notas": ""
    }
  ]
}
```
`status`: `pendente` → `feito` → `verificado` (ou `falhou`). Plano anterior de outro objetivo → mover para `plano/arquivo/AAAA-MM-DD-<branch>/`.

`plano/PLANO.md`: especificação confirmada, tabela de tarefas (id, título, tamanho, agente/modelo, depende de), riscos e o resumo de esforço (quantas P/M/G, o que roda em paralelo, recomendação: `/ai-kit:executar` supervisionado ou `scripts/ralph/ralph.sh` autônomo).

## 3. Revisar
Mostre o resumo ao usuário. Para planos com tarefas G ou risco 2, ofereça segunda opinião de outro modelo (`/ai-kit:consultar-modelos`).
