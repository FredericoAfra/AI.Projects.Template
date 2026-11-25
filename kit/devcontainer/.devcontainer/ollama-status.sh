#!/bin/bash
# Shows whether the Ollama server is running and which models are available.
if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama: running on :11434"
  ollama list
else
  echo "Ollama: not responding (log: /tmp/ollama.log)"
  exit 1
fi
