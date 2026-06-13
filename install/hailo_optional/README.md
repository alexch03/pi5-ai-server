# Hailo AI HAT — optional module

> ⚠️ This is **optional and independent** from the LLM stack.
> Ollama runs on CPU. The Hailo HAT runs vision models. They don't talk to
> each other.

## What this is for

The Hailo-8L (AI HAT / AI HAT+) is a PCIe vision accelerator: YOLOv8/n,
pose estimation, depth, etc. It does **not** help with LLMs (no llama.cpp
backend). If you only want a local chat/agent, skip this directory.

Use this module if you want:
- A camera pipeline running detection at 30+ fps in parallel to Ollama
- A door/garden/cat watcher feeding events to the mini-agent
- Anything where Pi CPU YOLO would be too slow

## Hardware

- Raspberry Pi 5 (any RAM tier — Hailo doesn't care)
- Official Pi 5 AI HAT or AI HAT+ with the Hailo-8L module
- **PCIe FFC cable** plugged into the **J11 connector** on the Pi 5 (it's the
  small flat connector, NOT the GPIO header — getting this wrong is the #1
  reason "Hailo not detected")
- Active cooling for the Pi (the HAT adds heat; the Pi will throttle without
  it, especially if you OC the CPU)

## Install (after Ollama stack is in place)

```bash
cd ~/pi5-ai-server/install/hailo_optional
bash 06_install_hailo.sh   # enables PCIe + installs driver/runtime
sudo reboot                # mandatory — PCIe only comes up on cold boot
bash test_hailo_yolo.sh    # smoke test
```

## What `06_install_hailo.sh` does

1. Confirms you're on a Pi 5 (refuses on Pi 4 / Pi 3 / Zero — no PCIe)
2. Appends an idempotent block to `/boot/firmware/config.txt`:
   ```ini
   # --- Hailo PCIe block pi5-ai-server ---
   dtparam=pciex1
   #dtparam=pciex1_gen=3    # optional, faster but experimental
   # --- /Hailo PCIe block pi5-ai-server ---
   ```
3. Adds Hailo's official apt repo
4. Installs `hailo-all` (driver + runtime + post-processing)
5. Tells you to reboot

## Verify after reboot

```bash
hailortcli fw-control identify   # board info, serial, fw version
ls /dev/hailo0                   # device node should exist
lsmod | grep hailo               # hailo_pci module loaded
lspci | grep -i hailo            # PCIe device visible
```

If any of those fails, check:
- The FFC cable is fully seated on **both** ends (it's notoriously fragile)
- You actually rebooted (not just `systemctl restart`)
- You're on a Pi 5 (not a Pi 4)

## Coexistence with Ollama

There's no conflict — Ollama uses CPU + RAM, the Hailo uses PCIe + its own
on-chip memory. Active cooling is mandatory anyway (already required by the
3 GHz CPU OC).

## Why this is separate from the main installer

- 80% of users of `pi5-ai-server` won't have the Hailo HAT (it's a $70 add-on)
- Hailo's apt repo can change URLs; isolating it keeps the core installer
  resilient
- The Hailo install touches `config.txt` + PCIe — keeping it opt-in avoids
  surprising the Pi 4 user base
