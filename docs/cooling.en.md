# Active cooling — non-negotiable for this setup

Without active cooling, **don't overclock**. The Pi 5 at 3 GHz dissipates
~12W on a 1.5 cm² die — a passive heatsink saturates within seconds.

## What we want from cooling

- **Fan + heatsink**, not just a heatsink
- Idle < 50°C in a 22°C room
- 60s stress-ng matrixprod 4 cores: peak < 70°C, throttle 0x0
- Acceptable noise (the official Pi 5 fan is inaudible at 30% PWM)

## Validated setups

- **Official Raspberry Pi 5 active cooler** — $10, 30s to install, what I use
  (62°C max under 3 GHz stress)
- **Argon ONE V5** — massive alu case + fan, outperforms the official one
  long-term but pricier

## Setups to avoid

- Bare Pi 5, no cooling
- Passive heatsink alone, even a big one — convection over 5×5 cm isn't enough
- Closed plastic cases with no airflow

## Verify your setup holds

```bash
bash bench/stress_test.sh
```

Healthy output:

```
=== Stress 60s @ 3000 MHz (target) ===
t=10s  freq=3000 MHz  temp=56.4'C  volt=1.00V  throttled=0x0
t=20s  freq=3000 MHz  temp=59.8'C  volt=1.00V  throttled=0x0
t=30s  freq=3000 MHz  temp=61.2'C  volt=1.00V  throttled=0x0
t=40s  freq=3000 MHz  temp=61.8'C  volt=1.00V  throttled=0x0
t=50s  freq=3000 MHz  temp=62.0'C  volt=1.00V  throttled=0x0
t=60s  freq=3000 MHz  temp=62.0'C  volt=1.00V  throttled=0x0
```

If you see `throttled=0x4` (throttle active) or the freq dropping below 3000,
cooling isn't keeping up → either upgrade it, or back off the OC
(`arm_freq=2800`).
