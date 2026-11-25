# {{PROJECT_NAME}}

> Instruções para qualquer agente de IA (Claude Code, Codex, Copilot, Gemini, Cursor…).
> Mantenha **curto e atual**: é lido em toda sessão.

## Visão geral
<!-- 2–4 frases: o que o projeto faz, para quem, estado atual. -->

## Comandos
```
# instalar:
# rodar:
# testar/verificar:
```

## Convenções
- Documentação e mensagens em português (BR).
- Antes de criar algo, procure se já existe; reutilize.
- Trabalho repetitivo ou com dados → script versionado, não passos manuais.
- Nunca diga que algo funciona sem ter rodado; diga o que não foi verificado.
- Não invente nomes de colunas, APIs, versões ou números: confira na fonte.
- Segredos só em `.env` (fora do git). Não apague/sobrescreva dados nem faça push sem confirmação.
<!-- Acrescente aqui as regras do projeto (uma linha cada). -->

## Como trabalhar
- Planejamento e estado: `plano/PLANO.md`, `plano/plano.json` (tarefas, esforço, status) e `plano/progresso.md`. Ao retomar, leia-os primeiro.
- Entrada (Claude Code + plugin ai-kit): `/ai-kit:fazer <pedido>` — triagem e roteamento. Etapas avulsas: `/ai-kit:planejar` → `/ai-kit:executar` → `/ai-kit:verificar`.
- **Entender antes de fazer:** pedido não trivial vira especificação (objetivo, exemplos, premissas, critérios) confirmada pelo usuário antes de qualquer código.
- Modelo por papel: entender/planejar, bugs difíceis e revisão final em **opus** (`arquiteto`, `depurador`, `verificador`); tarefas médias em **sonnet** (`executor`); tarefas simples e checagens rápidas em **haiku** (`executor-leve`, `verificador` rápido).
- Uma tarefa só está pronta quando seus critérios foram **verificados com evidência**.

## Consultar outro modelo
Outros agentes podem pedir uma segunda opinião ao Claude em modo somente leitura:
`claude -p "<pergunta autossuficiente>" --permission-mode plan`
