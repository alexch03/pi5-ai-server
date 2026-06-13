"""pi5-ai-server web UI — FastAPI + HTMX, SSE streaming chat + live Pi telemetry.

Env:
    OLLAMA_URL  default http://127.0.0.1:11434
    WEB_HOST    default 0.0.0.0
    WEB_PORT    default 8080
"""
from __future__ import annotations

import json
import os
import pathlib

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from telemetry import read_telemetry

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
HERE = pathlib.Path(__file__).parent

app = FastAPI(title="pi5-ai-server", version="0.2.0")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")


async def _ollama_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    models = await _ollama_models()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": models or ["qwen3:1.7b", "qwen3:4b"],
        "default_model": "qwen3:1.7b" if "qwen3:1.7b" in models else (models[0] if models else "qwen3:1.7b"),
    })


@app.get("/api/health")
async def health():
    t = read_telemetry()
    return JSONResponse(t.to_dict())


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "qwen3:1.7b")
    agent_mode = bool(body.get("agent_mode", False))

    if agent_mode and messages and messages[0].get("role") != "system":
        messages = [{"role": "system", "content": (
            "You are an autonomous agent running on a Raspberry Pi 5. "
            "Reply concisely. If a tool would help, mention what you'd do — "
            "but for now stay text-only; real tool calls go through ~/mini_agent.py."
        )}] + messages

    async def gen():
        payload = {"model": model, "messages": messages, "stream": True, "think": False}
        try:
            async with httpx.AsyncClient(timeout=None) as c:
                async with c.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as r:
                    r.raise_for_status()
                    async for line in r.aiter_lines():
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        chunk = obj.get("message", {}).get("content", "")
                        if chunk:
                            yield f"data: {json.dumps({'delta': chunk})}\n\n"
                        if obj.get("done"):
                            stats = {
                                "decode_tok_s": (
                                    obj.get("eval_count", 0) / obj.get("eval_duration", 1) * 1e9
                                    if obj.get("eval_duration") else 0
                                ),
                                "prefill_tok_s": (
                                    obj.get("prompt_eval_count", 0) / obj.get("prompt_eval_duration", 1) * 1e9
                                    if obj.get("prompt_eval_duration") else 0
                                ),
                                "total_tokens": obj.get("eval_count", 0),
                            }
                            yield f"data: {json.dumps({'done': True, 'stats': stats})}\n\n"
                            return
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


def main():
    import uvicorn
    host = os.environ.get("WEB_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT") or os.environ.get("WEB_PORT") or "8080")
    uvicorn.run("app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
