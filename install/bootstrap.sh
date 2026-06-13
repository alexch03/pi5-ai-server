#!/usr/bin/env bash
# One-shot bootstrap: clones the repo on the Pi then runs install_all.sh.
# Usage on a fresh Pi:
#     curl -fsSL https://raw.githubusercontent.com/alexch03/pi5-ai-server/main/install/bootstrap.sh | bash
set -euo pipefail

REPO=${REPO:-https://github.com/alexch03/pi5-ai-server.git}
DEST=${DEST:-$HOME/pi5-ai-server}

if [[ ! -d "$DEST/.git" ]]; then
    echo "[bootstrap] cloning $REPO -> $DEST"
    git clone "$REPO" "$DEST"
else
    echo "[bootstrap] $DEST already exists, pulling latest"
    git -C "$DEST" pull --ff-only
fi

cd "$DEST"
chmod +x install/*.sh bench/*.sh
bash install/install_all.sh
