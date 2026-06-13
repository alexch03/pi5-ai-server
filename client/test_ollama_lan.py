"""Smoke-test the Pi's Ollama API from another machine on the LAN.

Usage:
    python test_ollama_lan.py [model]

Env: OLLAMA_HOST (default http://raspberrypi.local:11434)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

URL = os.environ.get("OLLAMA_HOST", "http://raspberrypi.local:11434").rstrip("/") + "/api/generate"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen3:1.7b"

body = {
    "model": MODEL,
    "prompt": "Say hello from the Pi 5 in one sentence.",
    "stream": False,
    "think": False,
    "options": {"num_predict": 40},
}

t0 = time.time()
req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"})
d = json.load(urllib.request.urlopen(req, timeout=120))
print(f"latency: {time.time()-t0:.1f}s")
print("response:", d["response"][:200].strip())
print(f"prefill: {d['prompt_eval_count']/d['prompt_eval_duration']*1e9:.1f} tok/s")
print(f"decode : {d['eval_count']/d['eval_duration']*1e9:.1f} tok/s")
