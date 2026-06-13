# Architecture

```
┌─ Pi 5 (192.168.x.x:11434) ──────────────────────────────┐
│                                                          │
│  systemd service: ollama.service                         │
│   └─ /usr/local/bin/ollama serve                         │
│       └─ bind 0.0.0.0:11434, CORS *                      │
│                                                          │
│  ~/mini_agent.py                                         │
│   ├─ POST /api/chat (model + tools + messages)           │
│   ├─ executes tool calls locally in ~/agent-workdir/     │
│   └─ loops until model returns no tool_calls             │
│                                                          │
│  Models on disk (~/.ollama/models):                      │
│   ├─ qwen3:1.7b (1.4 GB) — fast, agentic                 │
│   └─ qwen3:4b   (2.5 GB) — better quality, slower        │
└──────────────────────────────────────────────────────────┘
                    ▲                ▲
                    │ LAN HTTP       │ SSH
                    │                │
┌─ Any client on LAN (Windows / Mac / Linux) ─────────────┐
│  client/test_ollama_lan.py  ─────► /api/generate        │
│  client/pi_run.py           ─────► SSH command          │
│  client/pi_put.py           ─────► SFTP file            │
│  bench/bench_ollama.py      ─────► throughput numbers   │
└──────────────────────────────────────────────────────────┘
```

## Why this shape

- **Ollama exposed on the LAN, not the WAN.** No reverse proxy, no Cloudflare
  tunnel, no auth layer — the API is in your house and only your devices reach
  it. If you want it on the internet, put it behind a tunnel/VPN; **do not**
  forward port 11434 on your router.
- **Mini-agent runs on the Pi, not on the client.** That keeps tool calls
  local (file I/O, shell) and the only network hop is the model call. Latency
  is dominated by token generation (~11 tok/s on the Pi for qwen3:1.7b), not
  HTTP.
- **No GPU layer.** The Pi 5 has VideoCore VII — not usable for LLM inference
  in practice (no real backend support). Everything runs on the 4 ARM cores
  at 3 GHz.

## Performance envelope

Measured on a Pi 5 16GB at 3.0 GHz (active cooling):

| Model      | Prefill (short) | Decode    | RAM   | Verdict                  |
|------------|-----------------|-----------|-------|--------------------------|
| qwen3:1.7b | 65 tok/s        | 11 tok/s  | ~2 GB | Use this for agents      |
| qwen3:4b   | 22 tok/s        | 4 tok/s   | ~4 GB | OK for chat, slow tools  |
| qwen3:8b   | n/a             | n/a       | n/a   | RAM-OK but painfully slow |

Rule of thumb: anything bigger than 2B params on a Pi 5 CPU is too slow for
interactive use.

## What's intentionally NOT here

- **Hailo AI HAT.** The HAT is great for vision (YOLO) but doesn't help with
  LLM inference (no llama.cpp backend). This setup is purely CPU + Ollama.
- **Claude Code on the Pi.** It installs fine but its system prompt is too
  large for the Pi's prefill speed — every turn takes minutes. Use it on a
  desktop and have it talk to the Pi's Ollama API instead.
- **Docker.** Adds memory pressure with no upside on a single-purpose box.
  Native systemd service is simpler.

## File layout

```
pi5-ai-server/
├── install/
│   ├── bootstrap.sh              # curl | bash — clones repo + runs installer
│   ├── install_all.sh            # orchestrator
│   ├── 01_overclock.sh           # 3 GHz OC, idempotent, with rollback
│   ├── 02_active_cooling_check.sh
│   ├── 03_install_ollama.sh      # binary + systemd + LAN bind
│   ├── 04_pull_models.sh         # qwen3:1.7b + qwen3:4b
│   ├── 05_install_mini_agent.sh
│   └── rollback_overclock.sh
├── agent/
│   └── mini_agent.py             # the agentic loop
├── bench/
│   ├── bench_ollama.py           # tok/s measurements
│   └── stress_test.sh            # 60s stress + telemetry
├── client/
│   ├── pi_run.py                 # SSH command runner
│   ├── pi_put.py                 # SFTP upload
│   ├── test_ollama_lan.py        # 1-shot LAN smoke
│   └── requirements.txt
├── docs/
│   ├── overclock.md / .en.md
│   ├── cooling.md / .en.md
│   └── architecture.md
├── .env.example
├── .gitignore
├── LICENSE
└── README.md / README.en.md
```
