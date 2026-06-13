#!/usr/bin/env bash
# Install the pi5-ai-server web UI as a systemd service on :8080.
# - FastAPI + HTMX, ~50 MB RAM, no node/npm required
# - Streams chat from Ollama via SSE
# - Sidebar shows live Pi temp / throttle / freq / Hailo status
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_USER="${SUDO_USER:-$USER}"
RUN_HOME=$(getent passwd "$RUN_USER" | cut -d: -f6)
VENV="$REPO_DIR/web/.venv"
SERVICE=/etc/systemd/system/pi5-ai-web.service

echo "[web] creating venv at $VENV"
python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -r "$REPO_DIR/web/requirements.txt"

echo "[web] writing $SERVICE"
sudo tee "$SERVICE" > /dev/null <<EOF
[Unit]
Description=pi5-ai-server web UI
After=network-online.target ollama.service
Wants=ollama.service

[Service]
ExecStart=$VENV/bin/python $REPO_DIR/web/app.py
User=$RUN_USER
Group=$RUN_USER
WorkingDirectory=$REPO_DIR/web
Restart=always
RestartSec=3
Environment="OLLAMA_URL=http://127.0.0.1:11434"
Environment="WEB_HOST=0.0.0.0"
Environment="WEB_PORT=8080"
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable pi5-ai-web.service
sudo systemctl restart pi5-ai-web.service

sleep 2
if curl -fsS "http://127.0.0.1:8080/api/health" > /dev/null; then
    IP=$(hostname -I | awk '{print $1}')
    echo "[web] OK. Open http://$IP:8080 in your browser."
else
    echo "[web] WARN: not responding yet. Check: journalctl -u pi5-ai-web -n 30"
    exit 1
fi
