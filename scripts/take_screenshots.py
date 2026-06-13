"""Capture README screenshots of the web UI using Playwright.

Run while the FastAPI dev server is up (DEMO_TELEMETRY=1) at
http://127.0.0.1:8765.

Outputs under docs/images/.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)
URL = "http://127.0.0.1:8765/"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 880},
            device_scale_factor=2,
            color_scheme="dark",
        )
        page = ctx.new_page()
        page.goto(URL)
        page.wait_for_selector("#pi-model")
        # Let telemetry populate
        page.wait_for_function("document.getElementById('pi-model').textContent.length > 5", timeout=8000)

        # Seed a conversation that shows off the value prop
        prompts = [
            "What does running a local LLM on a Raspberry Pi 5 give me that a cloud API doesn't? Answer in 3 short bullet points.",
        ]
        for prompt in prompts:
            page.locator("#input").fill(prompt)
            page.locator("#send").click()
            # Wait for stream to finish (decode tok/s populates)
            page.wait_for_function(
                "document.getElementById('decode-tps').textContent.includes('tok/s') && !document.getElementById('decode-tps').textContent.startsWith('—')",
                timeout=180_000,
            )
            time.sleep(0.5)  # let cursor stabilize

        # --- Hero shot: full UI ---
        hero = OUT / "hero.png"
        page.screenshot(path=str(hero), full_page=False)
        print(f"saved {hero.relative_to(HERE)}")

        # --- Sidebar zoom: just the right pane ---
        sidebar = OUT / "sidebar.png"
        page.locator("aside.sidebar").screenshot(path=str(sidebar))
        print(f"saved {sidebar.relative_to(HERE)}")

        # --- Chat zoom: just the chat pane ---
        chat = OUT / "chat.png"
        page.locator("section.chat").screenshot(path=str(chat))
        print(f"saved {chat.relative_to(HERE)}")

        # --- Agent mode shot (click the visible slider, not the hidden input) ---
        prev_decode = page.locator("#decode-tps").inner_text()
        page.locator("label.switch").click()
        time.sleep(0.3)
        page.locator("#input").fill("Plan: I want to back up /boot/firmware/config.txt before tweaking. Give me 3 short steps.")
        page.locator("#send").click()
        page.wait_for_function(
            f"document.getElementById('decode-tps').textContent !== {json.dumps(prev_decode)}",
            timeout=180_000,
        )
        time.sleep(1.0)
        agent = OUT / "agent-mode.png"
        page.screenshot(path=str(agent), full_page=False)
        print(f"saved {agent.relative_to(HERE)}")

        browser.close()


if __name__ == "__main__":
    main()
