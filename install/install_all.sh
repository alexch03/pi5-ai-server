#!/usr/bin/env bash
# Orchestrator — run on the Pi 5. Idempotent.
# Steps: cooling check -> overclock -> Ollama -> models -> mini-agent.
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Pi 5 AI server installer ==="
echo
echo "This will:"
echo "  1. Verify active cooling is present (refuse to OC otherwise)"
echo "  2. Apply a stable 3.0 GHz overclock (with backup + easy rollback)"
echo "  3. Install Ollama and expose it on the LAN"
echo "  4. Pull qwen3:1.7b (fast) and qwen3:4b (better quality)"
echo "  5. Install the mini-agent (~/mini_agent.py)"
echo
read -rp "Continue? [y/N] " ans
[[ "${ans,,}" == "y" ]] || { echo "Aborted."; exit 1; }

bash ./02_active_cooling_check.sh
bash ./01_overclock.sh
bash ./03_install_ollama.sh
bash ./04_pull_models.sh
bash ./05_install_mini_agent.sh

echo
echo "=== Done. ==="
echo "Ollama API: http://$(hostname -I | awk '{print $1}'):11434"
echo "Try the agent: python3 ~/mini_agent.py \"écris hello.txt avec 'hi pi'\""
echo "Reboot is recommended for the overclock to take effect: sudo reboot"
