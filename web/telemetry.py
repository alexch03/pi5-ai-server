"""Hardware telemetry — reads Pi state via vcgencmd / sysfs / lsmod.

Falls back to mock values when not running on a Pi (for local dev).
"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass
class Telemetry:
    pi_model: str
    arm_freq_mhz: int
    arm_freq_target_mhz: int
    cpu_temp_c: float
    core_volt: float
    throttled_hex: str
    throttled_label: str
    overclock_active: bool
    hailo_present: bool
    hailo_model: str | None
    ollama_active: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _run(cmd: list[str], timeout: int = 3) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def _read(path: str) -> str:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        return ""


def _throttle_label(hex_str: str) -> str:
    try:
        v = int(hex_str, 16)
    except (ValueError, TypeError):
        return "unknown"
    if v == 0:
        return "healthy"
    parts = []
    if v & 0x1: parts.append("under-volt now")
    if v & 0x2: parts.append("freq capped now")
    if v & 0x4: parts.append("throttle now")
    if v & 0x10000 and not (v & 0x1): parts.append("under-volt past")
    if v & 0x40000 and not (v & 0x4): parts.append("throttle past")
    return ", ".join(parts) if parts else "healthy"


def read_telemetry() -> Telemetry:
    if not shutil.which("vcgencmd"):
        demo = os.environ.get("DEMO_TELEMETRY") == "1"
        return Telemetry(
            pi_model="Raspberry Pi 5 Model B Rev 1.1" if demo else "dev-host (mock)",
            arm_freq_mhz=3000, arm_freq_target_mhz=3000,
            cpu_temp_c=42.3, core_volt=1.00,
            throttled_hex="0x0", throttled_label="healthy",
            overclock_active=True,
            hailo_present=demo, hailo_model="Hailo-10H" if demo else None,
            ollama_active=True,
        )

    model = _read("/sys/firmware/devicetree/base/model").replace("\x00", "").strip() or "unknown"

    freq_raw = _run(["vcgencmd", "measure_clock", "arm"])
    m = re.search(r"=(\d+)", freq_raw)
    freq_mhz = int(int(m.group(1)) / 1_000_000) if m else 0

    target_raw = _run(["vcgencmd", "get_config", "arm_freq"])
    m = re.search(r"=(\d+)", target_raw)
    target_mhz = int(m.group(1)) if m else 0

    temp_raw = _run(["vcgencmd", "measure_temp"])
    m = re.search(r"=([\d.]+)", temp_raw)
    temp = float(m.group(1)) if m else 0.0

    volt_raw = _run(["vcgencmd", "measure_volts", "core"])
    m = re.search(r"=([\d.]+)", volt_raw)
    volt = float(m.group(1)) if m else 0.0

    thr_raw = _run(["vcgencmd", "get_throttled"])
    m = re.search(r"=(0x[\da-fA-F]+)", thr_raw)
    thr_hex = m.group(1) if m else "0x0"

    oc_active = target_mhz > 2400

    hailo_dev = pathlib.Path("/dev/hailo0").exists()
    hailo_model: str | None = None
    if hailo_dev:
        lspci = _run(["lspci"])
        if "Hailo-10H" in lspci: hailo_model = "Hailo-10H"
        elif "Hailo-8" in lspci: hailo_model = "Hailo-8L"
        else: hailo_model = "Hailo (unknown rev)"

    ollama_active = _run(["systemctl", "is-active", "ollama"]) == "active"

    return Telemetry(
        pi_model=model,
        arm_freq_mhz=freq_mhz, arm_freq_target_mhz=target_mhz,
        cpu_temp_c=temp, core_volt=volt,
        throttled_hex=thr_hex, throttled_label=_throttle_label(thr_hex),
        overclock_active=oc_active,
        hailo_present=hailo_dev, hailo_model=hailo_model,
        ollama_active=ollama_active,
    )
