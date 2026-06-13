"""Run a command on the Pi over SSH (password or key auth).

Usage:
    python pi_run.py "uptime"
    python pi_run.py --file local_script.sh   # uploads and runs

Credentials are read from .env or environment:
    PI_HOST, PI_USER, PI_PASSWORD (optional if your key is loaded)
"""
from __future__ import annotations

import os
import sys

import paramiko

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOST = os.environ.get("PI_HOST")
USER = os.environ.get("PI_USER", "pi")
PASSWORD = os.environ.get("PI_PASSWORD")

if not HOST:
    sys.exit("PI_HOST not set. Copy .env.example to .env and fill it in.")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    if sys.argv[1] == "--file":
        with open(sys.argv[2], encoding="utf-8") as f:
            cmd = f.read()
        timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    else:
        cmd = sys.argv[1]
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=15)
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    if out:
        print(out, end="")
    if err:
        print("[stderr]", err, end="", file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
