#!/usr/bin/env bash
# Drop the mini-agent into $HOME and prepare its workdir.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DST="${HOME}/mini_agent.py"
WORK="${HOME}/agent-workdir"

cp "${REPO_DIR}/agent/mini_agent.py" "${DST}"
chmod +x "${DST}"
mkdir -p "${WORK}"

echo "[agent] installed -> ${DST}"
echo "[agent] workdir   -> ${WORK}"
echo "[agent] test:"
echo "         python3 ${DST} \"écris hello.txt avec 'hi pi' puis affiche son contenu\""
