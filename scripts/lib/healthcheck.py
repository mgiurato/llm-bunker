#!/usr/bin/env python3
"""Fast health check for the llm-bunker stack: containers running, API responding."""

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def container_statuses() -> list[dict]:
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"'docker compose ps' failed:\n{result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        fail("No containers found. Run 'docker compose up -d' first.")
    return [json.loads(line) for line in lines]


def main() -> None:
    print("Checking container status...")
    containers = {c["Service"]: c for c in container_statuses()}
    for svc in ("bunker", "proxy"):
        c = containers.get(svc)
        if not c:
            fail(f"{svc} service not found.")
        if c["State"] != "running":
            fail(f"{svc} is not running (state: {c['State']}).")
    print("Containers: OK")

    print("Checking API responsiveness...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=10) as resp:
            resp.read()
    except (urllib.error.URLError, OSError) as exc:
        fail(f"API did not respond on http://127.0.0.1:8080/v1/models\n{exc}")
    print("API: OK")

    print("\nHealthcheck passed.")


if __name__ == "__main__":
    main()
