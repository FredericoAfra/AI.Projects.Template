# Changelog

## 3.1.0 — 2026-11-25 (modelo por papel)
- Cada agente tem modelo e esforço fixos: `arquiteto`, `depurador`, `verificador`, `mentor-rigoroso` em opus/high; `executor`, `analista-dados` em sonnet/medium; `executor-leve` em haiku/low.
- Novos agentes: `arquiteto` (pedido → especificação confirmada → plano), `depurador` (causa raiz + teste de regressão), `executor-leve`.
- Nova skill `fazer`: porta de entrada com triagem (trivial / bug / funcionalidade) e roteamento por modelo; exige confirmação da especificação antes de programar.
- `planejar` delega ao `arquiteto`; tarefas ganham `agente` + `modelo`.
- `executar`: checagem rápida por tarefa com verificador em haiku; escalonamento haiku → sonnet → opus → depurador; revisão final em opus.
- Projetos instalados usam `"model": "opusplan"` na sessão principal.
- Ralph sobe um nível de modelo a cada tentativa falha.

## 3.0.0 — 2026-11-25 (enxugamento)
- Fluxo único **planejar → executar → verificar** com `plano/plano.json` como estado.
  - `planejar` classifica o esforço de cada tarefa (P/M/G) e define modelo e nível de esforço.
  - `executar` delega ao agente `executor` com esse modelo/esforço, em paralelo quando não há arquivos em comum, e sobe um nível quando a verificação falha.
  - Agente `verificador` (somente leitura) exige evidência por critério.
- `consultar-modelos`: Codex/ChatGPT, Gemini e Copilot pelos CLIs, somente leitura, em paralelo.
- `diagnostico`: relatório do histórico de sessões (custo, tokens, erros, skills nunca usadas, correções).
- `criar`: uma skill para regra, skill ou agente.
- Ralph usa `plano/plano.json`, modelo/esforço por tarefa e escalonamento automático.
- Removidos: prd, ralph (conversor), orquestrar, handoff, nova-*, planejador, pesquisador, revisor, biblioteca de regras, templates, `aikit sync/new/add-rule/list`, modo copy. Ver `docs/decisoes.md`.

## 2.0.0 — 2026-11-25
- Marketplace de plugins, CLI `aikit`, várias skills/agentes e biblioteca de regras (substituído na 3.0).

## 1.0 — versão inicial
- Agente mentor-rigoroso, skills PRD/Ralph, Ralph loop e devcontainer.
