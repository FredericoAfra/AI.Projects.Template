# AI.Projects.Template — ai-kit

Kit mínimo para programar com IA (webapps, painéis, bots, sistemas pequenos) **rápido e sem erros**: entender o pedido → planejar → executar → verificar, com **um modelo por papel** — Opus para pensar, Sonnet para o trabalho médio, Haiku para o simples.

```
plugins/ai-kit/                ← plugin do Claude Code (vale para todos os projetos)
  skills/  fazer · planejar · executar · verificar · consultar-modelos · diagnostico · criar
  agents/  arquiteto · depurador · verificador · mentor-rigoroso   (opus)
           executor · analista-dados                               (sonnet)
           executor-leve                                           (haiku)
kit/                           ← arquivos copiados para cada projeto pelo aikit
  core/          AGENTS.md, CLAUDE.md, .claude/settings.json
  ralph/         scripts/ralph/ (execução autônoma do plano)
  devcontainer/  .devcontainer/ (sandbox com firewall + Ollama)
aikit.py (.ps1/.sh)            ← install · update · status · validate
docs/decisoes.md               ← o que foi escolhido, por quê, e as alternativas
```

## Agentes e modelos (do mais complexo ao mais simples)

| Agente | Modelo / esforço | Papel |
|---|---|---|
| `arquiteto` | opus / high | Transforma o pedido em especificação (objetivo, exemplos, premissas, critérios) para você confirmar; monta o plano |
| `depurador` | opus / high | Bugs difíceis: reproduz, isola a causa raiz, corrige com teste de regressão |
| `verificador` | opus / high (final) · haiku / low (por tarefa) | Confere com evidência; não edita |
| `mentor-rigoroso` | opus / high | Crítica dura de planos e decisões |
| `executor` | sonnet / medium (opus em tarefa G) | Tarefas médias |
| `analista-dados` | sonnet / medium | Esquema, SQL, DAX, validação de números |
| `executor-leve` | haiku / low | Mudanças simples e bem especificadas |

Sessão principal: `opusplan` (configurado no `.claude/settings.json` do projeto) — Opus no modo plan, Sonnet no resto. Como o trabalho pesado já roda nos agentes Opus, a sessão pode ficar no Sonnet.

## O fluxo

```
/ai-kit:fazer <pedido> ─► triagem
   ├─ trivial ─────────► executor-leve (haiku) ─► verificador rápido (haiku)
   ├─ bug ─────────────► depurador (opus) ─► verificador rápido
   └─ funcionalidade ──► arquiteto (opus): especificação ─► VOCÊ CONFIRMA
                         ─► /ai-kit:planejar  → plano/plano.json (tarefa → agente + modelo)
                         ─► /ai-kit:executar  → P: executor-leve · M: executor · G: executor/opus
                                                 cada tarefa: verificador rápido; falhou → sobe um nível
                                                 (haiku → sonnet → opus → depurador)
                         ─► /ai-kit:verificar → verificador opus no conjunto + 2ª opinião opcional

/ai-kit:diagnostico ► custo, tokens, erros, skills nunca usadas → o que melhorar
/ai-kit:criar ──────► nova regra, skill ou agente
```

**Esforço automático:** cada tarefa recebe pontos (escopo, clareza, risco, verificação). 0–1 = **P** (haiku, low), 2–3 = **M** (sonnet, medium), 4–5 = **G** (opus, high), 6+ = dividir. Tarefas simples custam pouco; o modelo caro fica para o que é difícil.

**Execução autônoma:** com o perfil `ralph`, `bash scripts/ralph/ralph.sh 20` executa o mesmo `plano.json` sem supervisão, uma tarefa por sessão, com o modelo/esforço de cada tarefa. ⚠️ Roda com permissões liberadas: use no devcontainer ou numa branch descartável.

## Instalação

Requisito: Python 3.8+. Uma vez por máquina (dentro da pasta do kit):

```powershell
Add-Content $PROFILE "`nfunction aikit { & '$PWD\aikit.ps1' @args }"
```

Em cada projeto:

```powershell
aikit install .                          # perfil core; plugin vindo do GitHub
aikit install . --profile ralph          # + execução autônoma
aikit install . --marketplace local      # plugin vindo desta pasta (sem precisar dar push)
aikit update .                           # traz melhorias; o que você editou vira <arquivo>.aikit-new
aikit status .
```

Depois abra o Claude Code na pasta e aceite instalar o plugin `ai-kit` (ou `/plugin marketplace add FredericoAfra/AI.Projects.Template` e `/plugin install ai-kit@ai-projects-template`).

## Outros modelos

A skill `consultar-modelos` chama os CLIs em **modo somente leitura**, usando suas assinaturas (sem chave de API):

| Modelo | Instalar | Login |
|---|---|---|
| OpenAI Codex / ChatGPT | `npm i -g @openai/codex` | `codex` |
| Google Gemini | `npm i -g @google/gemini-cli` | `gemini` |
| GitHub Copilot | `npm i -g @github/copilot` | `copilot` → `/login` |

O caminho inverso (Copilot/Gemini/Codex consultando o Claude) está descrito no `AGENTS.md` instalado: `claude -p "..." --permission-mode plan`.

## Melhorando o kit

1. `/ai-kit:diagnostico` em um projeto (ou `--todos`) → relatório de custo, erros, skills nunca usadas, correções frequentes.
2. Ajuste a skill/agente no kit, `python aikit.py validate`, suba a versão (`VERSION` + `plugin.json` + `marketplace.json`), registre no `CHANGELOG.md`, commit.
3. Nos projetos: `/plugin marketplace update` (skills/agentes) e `aikit update` (arquivos).
4. Para medir se uma skill ajuda de verdade: `claude plugin eval init` e `claude plugin eval` dentro de `plugins/ai-kit`.
