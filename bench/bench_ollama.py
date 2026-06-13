"""Bench Ollama on the Pi 5 (from any LAN client) — qwen3:1.7b + qwen3:4b.

Usage:
    python bench_ollama.py

Env: OLLAMA_HOST (default http://raspberrypi.local:11434)
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

HOST = os.environ.get("OLLAMA_HOST", "http://raspberrypi.local:11434").rstrip("/")


def bench(model: str, prompt: str, n_predict: int, n_warmup: int = 1) -> tuple:
    body = {"model": model, "prompt": prompt, "stream": False, "think": False,
            "options": {"num_predict": n_predict}}
    for _ in range(n_warmup):
        req = urllib.request.Request(HOST + "/api/generate", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        json.load(urllib.request.urlopen(req, timeout=600))
    t0 = time.time()
    req = urllib.request.Request(HOST + "/api/generate", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    elapsed = time.time() - t0
    pf = d["prompt_eval_count"] / d["prompt_eval_duration"] * 1e9
    dc = d["eval_count"] / d["eval_duration"] * 1e9
    return elapsed, pf, dc, d["prompt_eval_count"], d["eval_count"]


SHORT = "Say hello."
LONG = "Here is a text: " + ("The cat sleeps on the couch. " * 80) + "Summarise in 5 words."

for model in ["qwen3:1.7b", "qwen3:4b"]:
    print(f"\n=== {model} ===")
    e, pf, dc, n_in, n_out = bench(model, SHORT, 60)
    print(f"  short ({n_in:4d}->{n_out:3d} tok, {e:.1f}s): prefill {pf:5.1f} tok/s, decode {dc:5.1f} tok/s")
    e, pf, dc, n_in, n_out = bench(model, LONG, 30)
    print(f"  long  ({n_in:4d}->{n_out:3d} tok, {e:.1f}s): prefill {pf:5.1f} tok/s, decode {dc:5.1f} tok/s")
