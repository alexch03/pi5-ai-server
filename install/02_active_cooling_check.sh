#!/usr/bin/env bash
# Cooling sanity check before overclocking.
# A passive heatsink alone is NOT enough at 3.0 GHz. This script measures the
# idle temperature and aborts if it's already too high — that's a strong
# signal cooling isn't adequate.
set -euo pipefail

THRESH_IDLE_C=55
echo "[cooling] reading idle temperature..."
TEMP_RAW=$(vcgencmd measure_temp | grep -oE '[0-9]+\.[0-9]+')
TEMP_INT=${TEMP_RAW%.*}

echo "[cooling] idle = ${TEMP_RAW}°C (threshold ${THRESH_IDLE_C}°C)"

if (( TEMP_INT >= THRESH_IDLE_C )); then
    echo "[cooling] ABORT: idle temperature too high. Either the Pi is not idle"
    echo "          right now, or your cooling isn't adequate. Install an"
    echo "          active cooler (fan + heatsink, ideally a metal block) and"
    echo "          rerun. Without proper cooling, the overclock will throttle"
    echo "          or damage the SoC."
    exit 1
fi

echo "[cooling] OK."
