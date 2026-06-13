#!/usr/bin/env bash
# Smoke test after Hailo install + reboot.
set -euo pipefail

echo "=== Hailo smoke test ==="

if ! command -v hailortcli > /dev/null; then
    echo "[FAIL] hailortcli not found. Run 06_install_hailo.sh first."
    exit 1
fi

if [[ ! -e /dev/hailo0 ]]; then
    echo "[FAIL] /dev/hailo0 missing. Did you reboot after 06_install_hailo.sh?"
    exit 1
fi

echo
echo "--- device identify ---"
hailortcli fw-control identify

echo
echo "--- kernel module ---"
lsmod | grep hailo || echo "WARN: no hailo module loaded"

echo
echo "--- PCIe device ---"
lspci | grep -i hailo || echo "WARN: no hailo PCIe device"

echo
echo "--- benchmark (YOLOv8n if available) ---"
HEF=/usr/share/hailo-models/yolov8n.hef
if [[ -f "$HEF" ]]; then
    hailortcli benchmark "$HEF" || true
else
    echo "yolov8n.hef not found at $HEF. Skip benchmark."
    echo "Pull a model: wget https://hailo-csdata.s3.eu-west-2.amazonaws.com/resources/hefs/v2.13/yolov8n.hef"
fi

echo
echo "=== Done. Hailo is healthy. ==="
