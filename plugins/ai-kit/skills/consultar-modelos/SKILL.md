---
name: consultar-modelos
description: "Consulta agentes de outros modelos (OpenAI Codex/ChatGPT, Google Gemini, GitHub Copilot) pelos CLIs deles, em modo somente leitura, para segunda opinião, revisão cruzada de código/plano ou comparar respostas. Use quando o usuário pedir opinião de outro modelo, revisão cruzada, 'pergunta pro Gemini/ChatGPT/Copilot', ou quando uma verificação importante merecer um olhar independente."
allowed-tools: Bash(python "${CLAUDE_SKILL_DIR}/scripts/consultar.py" *)
---

# Consultar outros modelos

O Claude continua sendo o orquestrador; os outros modelos atuam como **revisores/consultores independentes**, sem alterar arquivos. As consultas usam as assinaturas já logadas em cada CLI (sem chave de API).

## Uso
```bash
python "${CLAUDE_SKILL_DIR}/scripts/consultar.py" --listar
python "${CLAUDE_SKILL_DIR}/scripts/consultar.py" --para todos --pergunta "<pedido>" [--diff] [--arquivos a b] [--modelo gemini=<modelo>]
```
- `--para`: `codex`, `gemini`, `copilot`, `claude` (separados por vírgula) ou `todos` (os instalados).
- A pergunta é gravada em `.ai-kit/consultas/<data>/pergunta.md`; as respostas ficam ao lado (`codex.md`, `gemini.md`…). As consultas rodam em paralelo.

## Como escrever a pergunta
- Autossuficiente: o outro agente não vê esta conversa. Diga o objetivo, onde olhar (`--arquivos`, `--diff`) e o formato da resposta.
- Para revisão independente, **não** inclua sua conclusão (evita viés). Ex.: *"Revise as mudanças: bugs, casos de borda e riscos. Liste por gravidade com arquivo:linha."*

## Depois
Compare as respostas com a sua análise: o que todos apontam (alta confiança), divergências (investigue lendo o código) e o que só um viu. Apresente ao usuário um resumo consolidado — não cole as respostas inteiras.

## Instalação dos CLIs (uma vez, fora daqui; cada um pede login)
| CLI | Instalação | Login |
|---|---|---|
| Codex (ChatGPT) | `npm i -g @openai/codex` | `codex` → entrar com conta ChatGPT |
| Gemini | `npm i -g @google/gemini-cli` | `gemini` → conta Google |
| Copilot | `npm i -g @github/copilot` | `copilot` → `/login` |

Requer Node.js. Se um CLI falhar por permissão de leitura do arquivo da pergunta, rode o comando dele uma vez manualmente na pasta do projeto e aceite a confiança na pasta.

## O caminho inverso
Para que Codex/Gemini/Copilot consultem o Claude, o `AGENTS.md` do projeto ensina: `claude -p "<pergunta>" --permission-mode plan`.
