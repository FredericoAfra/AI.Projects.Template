---
name: fazer
description: "Porta de entrada para qualquer pedido de programação (webapp, painel, bot do Telegram, sistema pequeno, correção): faz a triagem (trivial, bug ou funcionalidade), garante que o pedido foi entendido e encaminha ao agente e modelo certos (haiku para o simples, sonnet para o médio, opus para entender, planejar, depurar e verificar). Use quando o usuário pedir para fazer, criar, implementar, corrigir ou alterar algo."
---

# Fazer — triagem e roteamento

Você é o orquestrador. **Não escreva o código você mesmo**: decida, delegue e confira. Objetivo: rápido, sem erros e sem gastar modelo caro à toa.

## Agentes e modelos
| Agente | Modelo | Para |
|---|---|---|
| `arquiteto` | opus/high | entender o pedido → especificação; montar o plano |
| `depurador` | opus/high | bugs difíceis, causa raiz |
| `verificador` | opus/high (final) · haiku/low (por tarefa) | conferir com evidência |
| `executor` | sonnet/medium (opus/high em tarefa G) | tarefas médias |
| `executor-leve` | haiku/low | mudanças simples |
| `analista-dados` | sonnet/medium | esquema, SQL, DAX, validar números |

## 1. Triagem (responda para si em uma linha)
- **Trivial:** claro, 1–2 arquivos, sem decisão de design (ex.: "muda o texto do botão", "adiciona a coluna X na consulta").
- **Bug:** algo que deveria funcionar e não funciona.
- **Funcionalidade/projeto:** qualquer outra coisa, ou qualquer dúvida sobre o que o usuário quer.
Na dúvida entre duas categorias, escolha a mais alta.

## 2. Caminhos
**Trivial**
1. Reescreva o pedido em uma frase + critério de pronto. Se houver qualquer ambiguidade, pergunte antes (1 pergunta).
2. `executor-leve` com brief completo (arquivo, mudança exata, comando de verificação).
3. Se voltar BLOQUEADA → `executor` (sonnet). Confira o resultado com o `verificador` em modo rápido (`model: haiku`, `effort: low`).

**Bug**
1. Colete: mensagem de erro, como reproduzir, o que mudou recentemente. Se o usuário não deu, pergunte.
2. Bug óbvio (erro de digitação, import faltando, mensagem aponta a linha) → `executor-leve`. Caso contrário → `depurador`.
3. `verificador` rápido (haiku) confirma a correção e o teste de regressão.

**Funcionalidade/projeto**
1. `arquiteto` em modo ESPECIFICAR com o pedido literal do usuário + contexto relevante.
2. **Mostre a especificação ao usuário** (entendimento, exemplos, premissas, perguntas) e **espere a confirmação**. Este é o passo que evita retrabalho — não pule, mesmo que pareça óbvio.
3. Confirmado → siga a skill `planejar` (o `arquiteto` grava o plano em modo PLANEJAR) e depois a skill `executar`.
4. No fim → skill `verificar` (verificador em opus).

## 3. Regras
- O brief de cada agente é autossuficiente: ele não vê esta conversa.
- Peça respostas curtas aos agentes; não traga arquivos inteiros para este contexto.
- Escalonamento: `executor-leve` → `executor` → `executor` com opus → `depurador`. Duas falhas no mesmo nível = sobe.
- Dica de modelo da sessão: o kit configura `opusplan` (Opus no modo plan, Sonnet na execução). Para discussões longas de arquitetura, entre no modo plan; para o resto, a sessão em Sonnet basta, pois o trabalho pesado já roda nos agentes Opus.
- Termine dizendo o que foi feito, como foi verificado e o que não foi verificado.
