#!/usr/bin/env python3
"""Mini local agent — agentic loop on top of Ollama's /api/chat.

Usage:
    python3 mini_agent.py "task description" [model]

Env vars:
    OLLAMA_URL    default http://127.0.0.1:11434
    AGENT_MODEL   default qwen3:1.7b
    AGENT_WORKDIR default ~/agent-workdir
"""
from __future__ import annotations

import json
import os
import pathlib
import shlex
import subprocess
import sys
import time
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("AGENT_MODEL", "qwen3:1.7b")
WORKDIR = pathlib.Path(os.environ.get("AGENT_WORKDIR", str(pathlib.Path.home() / "agent-workdir"))).resolve()
MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "10"))

CMD_WHITELIST = {"ls", "cat", "echo", "wc", "date", "uname", "df", "free",
                 "head", "tail", "grep", "hostname", "uptime", "pwd", "stat"}

SYSTEM = (
    "You are an autonomous agent running on a small ARM box. Accomplish the task "
    "by calling the tools step by step. Workdir: " + str(WORKDIR) + ". "
    "When the task is done, reply with a short text starting with DONE: "
)

TOOLS = [
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write a text file (path relative to workdir).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file (path relative to workdir).",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run a safe shell command (whitelist enforced).",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}},
                       "required": ["command"]}}},
]


def _safe_path(rel: str) -> pathlib.Path:
    p = (WORKDIR / rel.lstrip("/")).resolve()
    if WORKDIR not in p.parents and p != WORKDIR:
        raise ValueError(f"path escapes workdir: {rel}")
    return p


def call_tool(name: str, args: dict) -> str:
    try:
        if name == "write_file":
            p = _safe_path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"OK, wrote: {args['path']}"
        if name == "read_file":
            p = _safe_path(args["path"])
            return p.read_text(encoding="utf-8")[:2000]
        if name == "run_command":
            parts = shlex.split(args["command"])
            if not parts or parts[0] not in CMD_WHITELIST:
                return f"ERROR: command not in whitelist {sorted(CMD_WHITELIST)}"
            r = subprocess.run(parts, capture_output=True, text=True, timeout=20, cwd=WORKDIR)
            return (r.stdout + r.stderr)[:2000] or "(no output)"
        return "ERROR: unknown tool"
    except Exception as e:
        return f"ERROR: {e}"


def chat(model: str, messages: list) -> dict:
    body = {"model": model, "messages": messages, "tools": TOOLS, "stream": False, "think": False}
    req = urllib.request.Request(
        OLLAMA_URL + "/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req, timeout=1500))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    task = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL
    WORKDIR.mkdir(parents=True, exist_ok=True)

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": task},
    ]
    t0 = time.time()
    for step in range(1, MAX_STEPS + 1):
        d = chat(model, messages)
        msg = d["message"]
        messages.append(msg)
        calls = msg.get("tool_calls") or []
        if not calls:
            print(f"[{time.time()-t0:6.1f}s] AGENT: {(msg.get('content') or '').strip()[:400]}")
            break
        for tc in calls:
            fn = tc["function"]
            raw = fn["arguments"]
            args = raw if isinstance(raw, dict) else json.loads(raw)
            result = call_tool(fn["name"], args)
            preview = json.dumps(args, ensure_ascii=False)[:120]
            print(f"[{time.time()-t0:6.1f}s] step {step}: {fn['name']}({preview}) -> {result[:120]!r}")
            messages.append({"role": "tool", "content": result, "tool_name": fn["name"]})
    print(f"--- total: {time.time()-t0:.1f}s, model: {model}")


if __name__ == "__main__":
    main()
