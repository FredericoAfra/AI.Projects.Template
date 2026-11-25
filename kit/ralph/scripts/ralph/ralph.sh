#!/bin/bash
# Ralph - loop autonomo: executa plano/plano.json, uma tarefa por iteracao, com Claude Code.
# Cada iteracao usa o modelo e o esforco definidos na tarefa (sobe um nivel na 2a tentativa).
# Uso: bash scripts/ralph/ralph.sh [max_iteracoes]
# ATENCAO: roda com --dangerously-skip-permissions. Use no devcontainer ou numa branch descartavel.
set -e
MAX=${1:-10}
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
PLANO="$ROOT/plano/plano.json"
PROG="$ROOT/plano/progresso.md"
PY="$(command -v python3 || command -v python)"
[ -f "$PLANO" ] || { echo "erro: $PLANO nao existe. Crie o plano com /ai-kit:planejar."; exit 1; }
[ -f "$PROG" ] || printf '# Progresso\n\n' > "$PROG"
cd "$ROOT"

# Imprime "<id> <modelo> <esforco>" da proxima tarefa pronta, ou FIM / BLOQUEADO.
proxima() {
  "$PY" - "$PLANO" <<'PYEOF'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
t = p.get("tarefas", [])
ok = {x["id"] for x in t if x.get("status") == "verificado"}
if all(x.get("status") == "verificado" for x in t):
    print("FIM - -"); sys.exit()
subir = {"haiku": ("sonnet", "medium"), "sonnet": ("opus", "high"), "opus": ("opus", "high")}
for x in t:
    if x.get("status") == "pendente" and set(x.get("dependeDe", [])) <= ok:
        m, e = x.get("modelo", "sonnet"), x.get("esforco", "medium")
        if x.get("tentativas", 0) >= 1:
            m, e = subir.get(m, (m, e))
        print(x["id"], m, e); sys.exit()
print("BLOQUEADO - -")
PYEOF
}

echo "Ralph - plano: $PLANO - max $MAX iteracoes"
for i in $(seq 1 "$MAX"); do
  read -r ID MODELO ESFORCO <<<"$(proxima)"
  case "$ID" in
    FIM) echo "Todas as tarefas verificadas."; exit 0 ;;
    BLOQUEADO) echo "Nenhuma tarefa pronta (falhas ou dependencias). Veja $PROG."; exit 2 ;;
  esac
  echo ""
  echo "=== Ralph $i/$MAX: tarefa $ID (modelo $MODELO, esforco $ESFORCO) ==="
  PROMPT="$(sed "s/{{TAREFA}}/$ID/g" "$DIR/prompt.md")"
  CLAUDE_CODE_EFFORT_LEVEL="$ESFORCO" claude --dangerously-skip-permissions --model "$MODELO" -p "$PROMPT" || true
  sleep 2
done
echo "Limite de $MAX iteracoes atingido. Veja $PROG."
exit 1
