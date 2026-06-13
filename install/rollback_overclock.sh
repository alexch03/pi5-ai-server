#!/usr/bin/env bash
# Revert the overclock block applied by 01_overclock.sh.
set -euo pipefail

CFG=/boot/firmware/config.txt
BAK="${CFG}.bak.preoc"
MARK_BEGIN="# --- OC block pi5-ai-server ---"
MARK_END="# --- /OC block pi5-ai-server ---"

if [[ -f "$BAK" ]]; then
    sudo cp "$BAK" "$CFG"
    echo "[oc-rollback] restored $CFG from $BAK"
else
    sudo sed -i "/$MARK_BEGIN/,/$MARK_END/d" "$CFG"
    echo "[oc-rollback] no backup found, just removed the OC block"
fi
echo "[oc-rollback] reboot to drop back to stock: sudo reboot"
