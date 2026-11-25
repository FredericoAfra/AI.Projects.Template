#!/bin/bash
# Waits for the Ollama server started in postStartCommand and optionally pulls models.
# Set OLLAMA_PULL_MODELS="llama3.2 qwen2.5-coder" (space separated) to pull on start.
# NOTE: init-firewall.sh blocks most outbound traffic; model pulls need the Ollama
# registry/CDN allowed, otherwise pull models on the host and mount /ollama.
set -u

for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama is up."
    break
  fi
  sleep 1
done

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "WARN: Ollama did not respond on :11434 (see /tmp/ollama.log)."
  exit 0
fi

for model in ${OLLAMA_PULL_MODELS:-}; do
  echo "Pulling $model ..."
  ollama pull "$model" || echo "WARN: could not pull $model (firewall?)"
done
exit 0
