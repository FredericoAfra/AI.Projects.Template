---
name: verificar
description: "Verifica se o trabalho feito realmente funciona: confere critérios do plano ou a mudança atual (git diff) com evidência, usando o agente verificador e, opcionalmente, uma segunda opinião de outro modelo (Codex/ChatGPT, Gemini, Copilot). Use quando o usuário pedir para verificar, revisar, validar, testar ou conferir uma entrega."
---

# Verificar

## 1. Definir o alvo
- Plano: tarefas com `status: "feito"` em `plano/plano.json` (ou as que o usuário indicar).
- Sem plano: a mudança atual (`git diff` + arquivos novos) e o objetivo que o usuário descreveu.

## 2. Verificação principal
Delegue ao agente `verificador` com: o que deveria acontecer (critérios), arquivos alterados e comandos de verificação conhecidos (testes, build, scripts).
- **Revisão de entrega** (padrão desta skill): `verificador` no modelo dele (**opus**), sobre o conjunto das mudanças.
- **Checagem rápida** de uma tarefa pequena: `verificador` com `model: haiku`, `effort: low`.
- Problema encontrado e causa não óbvia → ofereça o `depurador`.

## 3. Segunda opinião (quando valer o custo)
Use `/ai-kit:consultar-modelos` com outro modelo se: a mudança for G ou de risco alto, o verificador marcou itens como NÃO VERIFICADO, ou o usuário pedir. Peça ao outro modelo uma **revisão independente** (não mostre a conclusão do verificador, para não enviesar).

## 4. Consolidar
```
Resultado: APROVADO | REPROVADO | INCOMPLETO
Por critério/tarefa: <status + evidência>
Problemas (gravidade, arquivo:linha, cenário)
Divergências entre modelos (se houve consulta)
Não verificado: <lista e por quê>
```
Atualize `plano/plano.json` (`verificado`/`falhou`) e `plano/progresso.md`, se houver plano. Não corrija nada sem o usuário pedir — ofereça a correção.
