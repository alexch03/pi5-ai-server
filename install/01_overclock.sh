#!/usr/bin/env bash
# Apply a stable 3.0 GHz overclock to the Pi 5.
# Validated on a Pi 5 16GB with an active alu cooling block: 60s stress-ng
# matrixprod stayed below 62°C (80°C is the throttle threshold), throttled=0x0,
# 1.00 V load. ~25% faster decode for small LLMs on CPU.
#
# Safe by design:
#  - Backs up /boot/firmware/config.txt to config.txt.bak.preoc once
#  - Block is delimited so this script is idempotent and reversible
#  - Sets arm_freq=3000, gpu_freq=1000, over_voltage_delta=60000
#  - Use install/rollback_overclock.sh to revert
set -euo pipefail

CFG=/boot/firmware/config.txt
BAK="${CFG}.bak.preoc"
MARK_BEGIN="# --- OC block pi5-ai-server ---"
MARK_END="# --- /OC block pi5-ai-server ---"

if [[ ! -f "$CFG" ]]; then
    echo "[oc] $CFG not found. Are you running this on a Pi with Bookworm/Trixie?"
    exit 1
fi

if [[ ! -f "$BAK" ]]; then
    sudo cp "$CFG" "$BAK"
    echo "[oc] backup -> $BAK"
fi

# Idempotent: drop any previous block then re-append
sudo sed -i "/$MARK_BEGIN/,/$MARK_END/d" "$CFG"

sudo tee -a "$CFG" > /dev/null <<'EOF'

# --- OC block pi5-ai-server ---
# Stable 3.0 GHz @ ~1.0 V load, validated 60s stress-ng matrixprod < 62°C
# REQUIRES ACTIVE COOLING (fan + heatsink). Rollback: install/rollback_overclock.sh
arm_freq=3000
gpu_freq=1000
over_voltage_delta=60000
# --- /OC block pi5-ai-server ---
EOF

echo "[oc] applied. Reboot to activate: sudo reboot"
echo "[oc] verify after reboot:"
echo "       vcgencmd measure_clock arm     # should report ~3000 MHz under load"
echo "       vcgencmd get_throttled         # should stay 0x0"
echo "[oc] rollback any time: bash install/rollback_overclock.sh"
