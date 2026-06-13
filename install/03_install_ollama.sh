#!/usr/bin/env bash
# Install Ollama on the Pi 5 (arm64), enable as a systemd service, and
# expose the API on the LAN at port 11434.
#
# Why not the official one-line installer?
#  - It pulls from raw.githubusercontent.com which can be flaky behind some ISPs
#  - We want explicit control over the systemd override (LAN bind + CORS)
# But it still works if you prefer it — just skip step 1 here and run:
#     curl -fsSL https://ollama.com/install.sh | sh
set -euo pipefail

OLLAMA_BIN=/usr/local/bin/ollama
SERVICE=/etc/systemd/system/ollama.service
OVERRIDE_DIR=/etc/systemd/system/ollama.service.d
OVERRIDE=$OVERRIDE_DIR/override.conf
RUN_USER="${SUDO_USER:-$USER}"

# 1) Binary
if [[ ! -x "$OLLAMA_BIN" ]]; then
    echo "[ollama] installing binary via official installer..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "[ollama] binary already present: $($OLLAMA_BIN --version 2>/dev/null || echo unknown)"
fi

# 2) Service file (only write if missing — the installer might have created it)
if [[ ! -f "$SERVICE" ]]; then
    echo "[ollama] writing $SERVICE"
    sudo tee "$SERVICE" > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=$OLLAMA_BIN serve
User=$RUN_USER
Group=$RUN_USER
Restart=always
RestartSec=3
Environment="HOME=/home/$RUN_USER"

[Install]
WantedBy=multi-user.target
EOF
fi

# 3) LAN-bind override (idempotent)
sudo mkdir -p "$OVERRIDE_DIR"
sudo tee "$OVERRIDE" > /dev/null <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
EOF
echo "[ollama] override written -> $OVERRIDE"

# 4) Enable + start
sudo systemctl daemon-reload
sudo systemctl enable ollama.service
sudo systemctl restart ollama.service

sleep 2
if curl -fsS "http://127.0.0.1:11434/api/tags" > /dev/null; then
    IP=$(hostname -I | awk '{print $1}')
    echo "[ollama] OK. Reachable at http://127.0.0.1:11434 and http://$IP:11434"
else
    echo "[ollama] WARN: API not responding yet. Check: journalctl -u ollama -n 50"
    exit 1
fi
