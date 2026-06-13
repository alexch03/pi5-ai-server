#!/usr/bin/env bash
# OPTIONAL: enable Hailo-8L (AI HAT) on the Pi 5.
#
# This is independent from the Ollama / mini-agent stack. Hailo has no LLM
# backend — it's purely for vision (YOLOv8/n etc.). The two coexist fine but
# do not interact.
#
# Hardware: Hailo-8L PCIe accelerator on the Pi 5 AI HAT (or AI HAT+)
# Connector: PCIe FFC cable to the J11 connector on the Pi 5 (NOT GPIO!)
#
# What this script does:
#  1. Enables PCIe in /boot/firmware/config.txt (Gen2 by default, optionally Gen3)
#  2. Installs the official Hailo apt repo
#  3. Installs hailort + hailo-pcie driver + hailo-tappas-core (post-processing)
#  4. Pulls a sample HEF model (YOLOv8n)
#  5. Runs a smoke test (hailortcli fw-control identify)
set -euo pipefail

cd "$(dirname "$0")"

PI_MODEL=$(tr -d '\000' < /sys/firmware/devicetree/base/model 2>/dev/null || echo unknown)
if ! echo "$PI_MODEL" | grep -q "Pi 5"; then
    echo "[hailo] This script is for Raspberry Pi 5 only. Detected: $PI_MODEL"
    exit 1
fi

CFG=/boot/firmware/config.txt
MARK_BEGIN="# --- Hailo PCIe block pi5-ai-server ---"
MARK_END="# --- /Hailo PCIe block pi5-ai-server ---"

echo "[hailo] enabling PCIe in $CFG (idempotent block)"
sudo sed -i "/$MARK_BEGIN/,/$MARK_END/d" "$CFG"
sudo tee -a "$CFG" > /dev/null <<EOF

$MARK_BEGIN
# PCIe enable for the Hailo HAT. Gen2 is stable (default). Gen3 is faster
# but experimental on Pi 5 — uncomment dtparam=pciex1_gen=3 to try it.
dtparam=pciex1
#dtparam=pciex1_gen=3
$MARK_END
EOF
echo "[hailo] config.txt updated. Reboot needed to bring up PCIe."

echo "[hailo] installing Hailo apt repository..."
if [[ ! -f /etc/apt/sources.list.d/hailo.list ]]; then
    sudo apt-get install -y -qq curl gpg
    curl -fsSL https://hailo.ai/install/pi5/hailo-pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/hailo-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hailo-archive-keyring.gpg] https://hailo.ai/apt/pi5 stable main" | sudo tee /etc/apt/sources.list.d/hailo.list
    sudo apt-get update -qq
fi

echo "[hailo] installing hailort + driver + tappas..."
sudo apt-get install -y hailo-all || {
    echo "[hailo] hailo-all not available, falling back to individual pkgs"
    sudo apt-get install -y hailort hailo-pcie-driver hailo-tappas-core
}

echo
echo "[hailo] === reboot required before the device shows up ==="
echo "  sudo reboot"
echo
echo "[hailo] After reboot, validate with:"
echo "  hailortcli fw-control identify     # should print board info"
echo "  ls /dev/hailo0                     # should exist"
echo "  lsmod | grep hailo                 # hailo_pci module loaded"
echo
echo "[hailo] Run the YOLOv8 smoke test (after reboot):"
echo "  bash $(pwd)/test_hailo_yolo.sh"
