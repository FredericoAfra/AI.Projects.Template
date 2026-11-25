---
name: planejar
description: "Planeja um projeto ou funcionalidade: faz perguntas de esclarecimento, quebra em tarefas verificáveis, classifica o esforço de cada uma (P/M/G) e escolhe modelo e nível de esforço automaticamente. Gera plano/PLANO.md e plano/plano.json. Use quando o usuário quiser planejar, especificar, criar um PRD, estimar esforço ou começar algo novo."
---

# Planejar

Produz um plano que um humano entende (`plano/PLANO.md`) e que a skill `executar` ou o loop Ralph executam (`plano/plano.json`). **Não implemente nada aqui.**

## 1. Entender (máx. 5 perguntas)
Leia `AGENTS.md` e explore o código/dados relevantes (para varreduras grandes, delegue ao agente `Explore`). Depois faça só as perguntas que mudam o escopo, com alternativas numeradas para resposta rápida (`1A, 2C`):
- Qual problema resolve e para quem? O que fica **fora**?
- De onde vêm os dados / com o que integra?
- Como saberemos que deu certo (comando, número, tela)?

## 2. Quebrar em tarefas
Cada tarefa deve caber em **uma sessão de agente**: descrevível em 2–3 frases, critérios **verificáveis** (nada de "funciona bem"), ordem por dependência (dados → lógica → interface → relatórios).

## 3. Classificar o esforço (automático)
Some os pontos de cada tarefa:

| Fator | 0 | 1 | 2 |
|---|---|---|---|
| **Escopo** | 1 arquivo | 2–4 arquivos | 5+ arquivos → **divida a tarefa** |
| **Clareza** | segue um padrão existente | exige decisão de design | ambígua / exige pesquisa |
| **Risco** | local e reversível | mexe em dados ou integrações | segurança, produção ou irreversível |
| **Verificação** | teste/comando automático | conferência manual | difícil de verificar |

| Pontos | Tamanho | `modelo` | `esforco` |
|---|---|---|---|
| 0–1 | **P** | `haiku` | `low` |
| 2–3 | **M** | `sonnet` | `medium` |
| 4–5 | **G** | `opus` | `high` |
| 6+ | — | **divida** a tarefa ou faça um *spike* de pesquisa antes |

Registre o motivo em uma linha (`"motivoEsforco": "3 arquivos + decisão de esquema"`).

## 4. Gravar
`plano/plano.json`:
```json
{
  "projeto": "nome",
  "objetivo": "resultado final verificável",
  "branch": "feat/nome-kebab",
  "verificacaoGeral": ["comando que valida o projeto todo, ex.: pytest"],
  "tarefas": [
    {
      "id": "T01",
      "titulo": "Criar tabela de turnos",
      "descricao": "O que fazer e por quê, em 2–3 frases.",
      "dependeDe": [],
      "arquivos": ["db/schema.sql"],
      "pontos": 2,
      "tamanho": "M",
      "modelo": "sonnet",
      "esforco": "medium",
      "motivoEsforco": "decisão de esquema",
      "criterios": ["Tabela turnos com colunas equipe_id, data, inicio, fim", "Script de carga roda sem erro"],
      "verificacao": ["python scripts/carga.py --teste"],
      "status": "pendente",
      "notas": ""
    }
  ]
}
```
`status`: `pendente` → `feito` → `verificado` (ou `falhou`).

`plano/PLANO.md`: objetivo, fora de escopo, tabela das tarefas (id, título, tamanho, modelo, depende de), riscos e questões em aberto. Termine com o **resumo de esforço**: quantas P/M/G, quais tarefas podem rodar em paralelo (sem dependência e sem arquivos em comum) e a recomendação:
- poucas tarefas ou com decisões no meio → `/ai-kit:executar` (supervisionado);
- muitas tarefas P/M bem especificadas → loop Ralph (`bash scripts/ralph/ralph.sh 20`), se o projeto tiver o perfil ralph.

Se já existir um `plano/plano.json` de outro objetivo, mova-o para `plano/arquivo/AAAA-MM-DD-<branch>/` antes de gravar.

## 5. Revisão opcional
Para planos com tarefas G ou risco 2, ofereça uma segunda opinião de outro modelo com `/ai-kit:consultar-modelos` ("revise este plano: riscos, tarefas faltando, estimativas").
