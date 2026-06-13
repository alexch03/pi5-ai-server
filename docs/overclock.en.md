# Pi 5 overclock — stable 3.0 GHz

The Pi 5 ships at 2.4 GHz. With **real active cooling** (fan + heatsink,
ideally a metal block), you can push it to **3.0 GHz** with no throttle and
~25% faster decode on small LLMs running on CPU.

## TL;DR

```bash
bash install/02_active_cooling_check.sh   # idle temp sanity check
bash install/01_overclock.sh              # patches config.txt with a backup
sudo reboot
bash bench/stress_test.sh                 # 60s stress + telemetry
```

If anything goes sideways: `bash install/rollback_overclock.sh && sudo reboot`.

## What the patch does

In `/boot/firmware/config.txt`, the script appends a delimited block:

```ini
# --- OC block pi5-ai-server ---
arm_freq=3000
gpu_freq=1000
over_voltage_delta=60000
# --- /OC block pi5-ai-server ---
```

- `arm_freq=3000` — target CPU frequency (MHz)
- `gpu_freq=1000` — VideoCore VII at 1.0 GHz
- `over_voltage_delta=60000` — +60 mV on the SoC rail for 3 GHz stability

The original file is backed up to `config.txt.bak.preoc` on first run. The
block is idempotent — re-running the script doesn't duplicate it.

## Observed results (Pi 5 16GB + active alu block)

| Load                                 | Frequency | Load voltage | Max temp | Throttle |
|--------------------------------------|-----------|--------------|----------|----------|
| Idle                                 | 1500 MHz  | ~0.76 V      | 38°C     | 0x0      |
| 60s stress-ng matrixprod (4 cores)   | 3000 MHz  | ~1.00 V      | 62°C     | 0x0      |

Pi 5 thermal throttle kicks in at 80°C → 18°C of headroom. If your silicon
is good you can try `arm_freq=3100` + `over_voltage_delta=70000`, but test
each step with `bench/stress_test.sh`.

## Why the cooling check is mandatory

Without active cooling, the SoC will:
1. Hit 80°C within seconds at 3 GHz
2. Throttle down → worse performance than stock
3. Long-term: shortens silicon lifetime

The `02_active_cooling_check.sh` script reads the idle temp. If it's above
55°C, it bails — strong signal cooling is inadequate (or the Pi isn't
actually idle when you ran it).

## Recommended cooling

- **Official Raspberry Pi 5 active cooler** (~$10) — what I use
- Decent alternatives: Argon ONE V5, Pironman 5
- Avoid for OC: passive heatsinks alone (even big ones)

## Rollback

```bash
bash install/rollback_overclock.sh
sudo reboot
```

If the backup exists it restores the original; otherwise it strips the added
block. You're back to stock 2.4 GHz.

## Live diagnostics

```bash
vcgencmd measure_clock arm     # current freq in Hz
vcgencmd measure_temp          # SoC temperature
vcgencmd measure_volts core    # voltage
vcgencmd get_throttled         # 0x0 = perfect
```

`get_throttled` bits worth knowing:

| Bit       | Meaning                            |
|-----------|------------------------------------|
| 0x1       | currently under-volted             |
| 0x2       | freq currently capped              |
| 0x4       | throttle currently active          |
| 0x10000   | under-volt **has happened**        |
| 0x40000   | throttle **has happened**          |

`0x50000` means "throttled in the past but fine now" — typically a brief
spike during a stress test. Reboot then re-run the stress test.
