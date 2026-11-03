"""Educational, INTENTIONALLY VULNERABLE Flask application.

IIIT Allahabad Cyber Security (IT-30001)
Variant: OS command injection — in-band.

WARNING: This demo executes untrusted text through an OS shell.
Run ONLY on your personal lab machine, bound to 127.0.0.1. Never deploy.
"""

from __future__ import annotations

import os
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


def make_command(target: str) -> str:
    """Build an intentionally vulnerable shell command from untrusted input."""
    # FLAW 1: untrusted input is concatenated straight into an OS command.
    ping_prefix = "ping -n 1 -w 1000" if IS_WINDOWS else "ping -c 1 -W 1"
    return f"{ping_prefix} {target}"


def execute_unsafe(command: str) -> dict:
    """Run a deliberately unsafe shell command and return the visible output."""
    # FLAW 2: shell=True allows shell metacharacters in `target` to execute.
    try:
        completed = subprocess.run(
            command,
            shell=True,                 # Deliberate vulnerability for the assignment.
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
    command = make_command(target)
    response = execute_unsafe(command)
    response["command"] = command
    response["target"] = target
    return render_template(
        "index.html",
        os_label=SYSTEM_LABEL,
        normal_target=NORMAL_TARGET,
        attack_target=ATTACK_TARGET,
        target=target,
        response=response,
        timestamp=datetime.now().strftime("%H:%M:%S"),
    )


if __name__ == "__main__":
    print("\nLOCAL LAB ONLY — intentionally vulnerable command injection demo")
    print("Visit http://127.0.0.1:5000/  |  Press Ctrl+C to stop\n")
    # Hard-coded loopback binding. Never expose this lab to LAN or the Internet.
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
