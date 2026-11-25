#!/usr/bin/env bash
# Wrapper: chama aikit.py com o Python disponivel.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
[ -z "$PY" ] && { echo "erro: Python 3 nao encontrado" >&2; exit 1; }
exec "$PY" "$DIR/aikit.py" "$@"
