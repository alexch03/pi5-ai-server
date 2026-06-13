# pi5-ai-server

> [🇫🇷 Version française](README.md)

Turn a Raspberry Pi 5 into a local agentic AI server with one-command install,
a stable 3 GHz overclock, and a Python mini-agent that calls tools via Ollama.

**No Hailo, no GPU, no cloud.** Just the Pi 5 CPU + Ollama + qwen3, exposed on
the LAN so your other machines can hit it.

---

## What it does

- ✅ Installs Ollama and exposes it on the LAN (port `11434`)
- ✅ Pulls the models that actually run well on a Pi 5 (qwen3:1.7b, qwen3:4b)
- ✅ Applies a **stable, reversible** 3.0 GHz overclock (automatic backup of
  `config.txt`, validated with 60s stress-ng matrixprod under 62°C)
- ✅ Refuses to overclock if your cooling isn't adequate
- ✅ Installs a mini-agent (`mini_agent.py`) that loops on `/api/chat` with
  tools (`write_file`, `read_file`, whitelisted `run_command`)
- ✅ LAN clients to test from Windows/Mac/Linux (SSH, SFTP, bench)

## Requirements

- Raspberry Pi 5 (8 or 16 GB)
- **Active cooling** (alu block + official fan or equivalent) — non-negotiable
  for the OC, see [docs/cooling.en.md](docs/cooling.en.md)
- Debian 12 Bookworm or 13 Trixie, kernel 6.6+
- Internet (to pull Ollama + the models)
- ~5 GB free disk

## One-command install

On a fresh Pi:

```bash
curl -fsSL https://raw.githubusercontent.com/alexch03/pi5-ai-server/main/install/bootstrap.sh | bash
```

What it does:
1. Clones this repo to `~/pi5-ai-server`
2. Checks your cooling (idle temp < 55°C)
3. Applies the 3.0 GHz overclock with a `config.txt` backup
4. Installs Ollama and wires it as a LAN-bound systemd service
5. Pulls `qwen3:1.7b` and `qwen3:4b`
6. Installs `~/mini_agent.py`

Then:

```bash
sudo reboot                    # apply the OC
bash bench/stress_test.sh      # verify it holds (60s stress, throttled must stay 0x0)
```

## Step-by-step install (alternative)

```bash
git clone https://github.com/alexch03/pi5-ai-server.git
cd pi5-ai-server
chmod +x install/*.sh bench/*.sh
bash install/install_all.sh
```

Each step is its own script (`install/01_*.sh` to `install/05_*.sh`), runnable
independently.

## Try the agent

From the Pi (SSH):

```bash
python3 ~/mini_agent.py "write hello.txt with 'hi pi' then read it back"
```

Expected output (qwen3:1.7b, ~15s end-to-end):

```
[  3.4s] step 1: write_file({"path":"hello.txt","content":"hi pi"}) -> "OK, wrote: hello.txt"
[  8.1s] step 2: read_file({"path":"hello.txt"}) -> "hi pi"
[ 12.9s] AGENT: DONE: hello.txt written and read, content is "hi pi".
--- total: 12.9s, model: qwen3:1.7b
```

## Try from another LAN machine

```bash
git clone https://github.com/alexch03/pi5-ai-server.git
cd pi5-ai-server
pip install -r client/requirements.txt
cp .env.example .env       # set your Pi's IP
python client/test_ollama_lan.py
```

## Measured performance (Pi 5 16GB @ 3.0 GHz, active cooling)

| Model      | Prefill (short) | Decode    | Verdict                          |
|------------|-----------------|-----------|----------------------------------|
| qwen3:1.7b | 65 tok/s        | 11 tok/s  | Best for agents on a Pi 5        |
| qwen3:4b   | 22 tok/s        | 4 tok/s   | Writes better, slow tool-calls   |

Mini-agent qwen3:1.7b on a multi-tool task: ~17s end-to-end.

## Why no Hailo AI HAT?

The Hailo is excellent for **vision** (YOLOv8 at 30fps comfortably) but has
no LLM backend (no llama.cpp support). For text/agentic AI it does nothing
on this setup. CPU + Ollama, full stop.

## Security

- Ollama is exposed on the LAN only (`0.0.0.0:11434`). **Do not** forward port
  11434 on your router. To reach it off-LAN, put it behind a VPN (Tailscale,
  WireGuard).
- SSH credentials for the `client/` scripts come from `.env` (gitignored), not
  hardcoded.
- The mini-agent restricts `run_command` to a whitelist (`ls`, `cat`, `echo`,
  ...). File writes are confined to `~/agent-workdir` via path-escape checks.

## Optional module — Hailo AI HAT

If you have a Hailo-8L (AI HAT / HAT+), a **separate** module enables PCIe
and installs the driver/runtime. It does **not** touch the LLM stack
(Ollama stays on CPU, Hailo dedicated to vision).

```bash
cd ~/pi5-ai-server/install/hailo_optional
bash 06_install_hailo.sh && sudo reboot
bash test_hailo_yolo.sh
```

Details: [install/hailo_optional/README.md](install/hailo_optional/README.md).

## Documentation

- [docs/overclock.en.md](docs/overclock.en.md) — OC details, measurements, rollback
- [docs/cooling.en.md](docs/cooling.en.md) — why active cooling is mandatory
- [docs/architecture.md](docs/architecture.md) — diagram + design rationale
- [docs/enable_ssh.md](docs/enable_ssh.md) — enable SSH on a freshly flashed Pi

## Uninstall / rollback

```bash
# Back to stock 2.4 GHz
bash install/rollback_overclock.sh && sudo reboot

# Stop Ollama
sudo systemctl disable --now ollama.service

# Remove models (frees ~4 GB)
ollama rm qwen3:1.7b qwen3:4b
```

## License

MIT — see [LICENSE](LICENSE).
