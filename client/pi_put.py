"""Upload a local file to the Pi via SFTP.

Usage:
    python pi_put.py <local_path> <remote_path>

Credentials from .env / env vars: PI_HOST, PI_USER, PI_PASSWORD.
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

HOST = os.environ.get("PI_HOST")
USER = os.environ.get("PI_USER", "pi")
PASSWORD = os.environ.get("PI_PASSWORD")

if not HOST:
    sys.exit("PI_HOST not set. Copy .env.example to .env and fill it in.")

if len(sys.argv) != 3:
    sys.exit(__doc__)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASSWORD, timeout=15)
sftp = client.open_sftp()
sftp.put(sys.argv[1], sys.argv[2])
print("uploaded", sys.argv[1], "->", sys.argv[2])
sftp.close()
client.close()
