#!/usr/bin/env bash
# Pull the two models that actually run well on a Pi 5 CPU.
# qwen3:1.7b -> ~1.4 GB, ~11 tok/s decode, agentic-capable (tool calls work)
# qwen3:4b   -> ~2.5 GB, ~4 tok/s decode, better quality but slow with tools
set -euo pipefail

# Skip if API isn't up yet
if ! curl -fsS "http://127.0.0.1:11434/api/tags" > /dev/null; then
    echo "[models] Ollama API not responding at :11434. Run 03_install_ollama.sh first."
    exit 1
fi

pull_if_missing() {
    local model="$1"
    if ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "$model"; then
        echo "[models] $model already pulled."
    else
        echo "[models] pulling $model ..."
        ollama pull "$model"
    fi
}

pull_if_missing "qwen3:1.7b"
pull_if_missing "qwen3:4b"

echo "[models] installed:"
ollama list
