"""Take a screenshot of the web UI as served by the actual Pi (not localhost).

The hero.png you ship to GitHub should ideally come from this — it's the
truthful end-state.

Usage: python scripts/screenshot_from_pi.py [pi_url]
"""
from __future__ import annotations

import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.1.121:8080"
HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "docs" / "images" / "hero-from-pi.png"

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1400, "height": 880}, device_scale_factor=2, color_scheme="dark")
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_selector("#pi-model")
    page.wait_for_function("document.getElementById('pi-model').textContent.length > 5", timeout=8000)
    page.locator("#input").fill("What does running a local LLM on a Raspberry Pi 5 give me that a cloud API doesn't? Answer in 3 short bullet points.")
    page.locator("#send").click()
    page.wait_for_function(
        "document.getElementById('decode-tps').textContent.includes('tok/s') && !document.getElementById('decode-tps').textContent.startsWith('—')",
        timeout=180_000,
    )
    time.sleep(0.5)
    page.screenshot(path=str(OUT), full_page=False)
    print(f"saved {OUT.relative_to(HERE)}")
    browser.close()
