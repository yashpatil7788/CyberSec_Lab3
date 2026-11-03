"""NetProbe Lab: single mitigation (strict IPv4 address allow-list).

IIIT Allahabad Cyber Security (IT-30001). In-band OS command injection.

This assignment version applies exactly ONE fix: validate the input as an
IPv4 address before command construction/execution. The original shell=True
execution is deliberately retained for an isolated before/after comparison.
Lab-only example: bind to localhost. Not production-hardened software.
"""

from __future__ import annotations

import os
import ipaddress
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024  # The form only needs a few bytes.

IS_WINDOWS = os.name == "nt"
SYSTEM_LABEL = "Windows" if IS_WINDOWS else "Linux / macOS"
NORMAL_TARGET = "127.0.0.1"
# The default attack sample is for a local, owned lab machine only.
ATTACK_TARGET = "127.0.0.1 & whoami" if IS_WINDOWS else "127.0.0.1; whoami"


def validate_ipv4(target: str) -> str:
    """Allow-list: accept only a syntactically valid IPv4 address.

    IPv4Address rejects shell operators, spaces, hostnames, flags, and
    other non-IP syntax. Return the canonical address string.
    """
    return str(ipaddress.IPv4Address(target))


def make_command(target: str) -> str:
    """Original command construction, now called only with validated IPv4."""
    # Original concatenation retained to isolate the effect of one fix.
    ping_prefix = "ping -n 1 -w 1000" if IS_WINDOWS else "ping -c 1 -W 1"
    return f"{ping_prefix} {target}"


def execute_unsafe(command: str) -> dict:
    """Original shell execution retained for the single-mitigation experiment."""
    # shell=True deliberately unchanged; only validated IPv4 reaches here.
    try:
        completed = subprocess.run(
            command,
            shell=True,                 # UNCHANGED from vulnerable version.
            text=True,
            capture_output=True,       # In-band: server returns command output.
            timeout=6,
            errors="replace",
        )
        combined = (completed.stdout or "") + (completed.stderr or "")
        return {
            "output": combined[:16000] or "(The command produced no output.)",
            "return_code": completed.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "The command exceeded the 6-second lab timeout.",
            "return_code": None,
            "timed_out": True,
        }
    except OSError as exc:
        return {
            "output": f"The local OS could not start the command: {exc}",
            "return_code": None,
            "timed_out": False,
        }


@app.get("/")
def index():
    return render_template(
        "index.html",
        os_label=SYSTEM_LABEL,
        normal_target=NORMAL_TARGET,
        attack_target=ATTACK_TARGET,
        target=NORMAL_TARGET,
        response=None,
        timestamp=None,
    )


@app.post("/diagnose")
def diagnose():
    target = request.form.get("target", "")[:200].strip()

    # THE ONLY IMPLEMENTED MITIGATION: strict IPv4 allow-list before execution.
    try:
        validated_ip = validate_ipv4(target)
    except ValueError:
        response = {
            "output": "BLOCKED: Input is not a valid IPv4 address. No OS command was executed.",
            "command": "(not assembled — rejected by IPv4 allow-list)",
            "return_code": None,
            "timed_out": False,
            "blocked": True,
            "target": target,
        }
        status_code = 400
    else:
        command = make_command(validated_ip)
        response = execute_unsafe(command)
        response["command"] = command
        response["target"] = target
        response["blocked"] = False
        status_code = 200

    return render_template(
        "index.html",
        os_label=SYSTEM_LABEL,
        normal_target=NORMAL_TARGET,
        attack_target=ATTACK_TARGET,
        target=target,
        response=response,
        timestamp=datetime.now().strftime("%H:%M:%S"),
    ), status_code


if __name__ == "__main__":
    print("\nLOCAL LAB ONLY — strict IPv4 allow-list mitigation (ONE FIX)")
    print("Visit http://127.0.0.1:5000/  |  Press Ctrl+C to stop\n")
    # Hard-coded loopback binding. Never expose this lab to LAN or the Internet.
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
