#!/usr/bin/env bash
# 60-second stress-ng run with telemetry snapshots every 10s.
# Run this AFTER applying the overclock + reboot to confirm the silicon holds.
# Healthy result: throttled stays 0x0, temp < 70°C, freq stays at target.
set -euo pipefail

if ! command -v stress-ng > /dev/null; then
    echo "[stress] installing stress-ng..."
    sudo apt-get update -qq && sudo apt-get install -y -qq stress-ng
fi

TARGET_FREQ=$(vcgencmd get_config arm_freq | cut -d= -f2)
echo "=== Stress 60s @ ${TARGET_FREQ} MHz (target) ==="

nohup stress-ng --cpu 4 --cpu-method matrixprod --timeout 60s > /tmp/stress.log 2>&1 &
PID=$!

for i in 1 2 3 4 5 6; do
    sleep 10
    freq=$(vcgencmd measure_clock arm | cut -d= -f2)
    temp=$(vcgencmd measure_temp | cut -d= -f2)
    thr=$(vcgencmd get_throttled | cut -d= -f2)
    volt=$(vcgencmd measure_volts core | cut -d= -f2)
    printf 't=%2ds  freq=%4d MHz  temp=%s  volt=%s  throttled=%s\n' \
           $((i * 10)) $((freq / 1000000)) "$temp" "$volt" "$thr"
done
wait $PID

echo
echo '=== After stress ==='
vcgencmd get_throttled
vcgencmd measure_temp
echo
echo '=== dmesg tail ==='
dmesg -t | tail -5
