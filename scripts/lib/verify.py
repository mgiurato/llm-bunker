#!/usr/bin/env python3
"""Full setup verification for llm-bunker.

Mirrors docs/setup.md steps 6-9: container health, model loaded, inference,
network isolation, non-root execution. Each check prints PASS/FAIL; exits
non-zero if anything fails.
"""

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

failures = 0


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)


def step(name: str):
    def decorator(fn):
        def wrapper():
            global failures
            print(f"\n== {name} ==")
            try:
                fn()
                print(f"PASS: {name}")
            except Exception as exc:  # noqa: BLE001 - report and keep going
                print(f"FAIL: {name}\n  {exc}")
                failures += 1

        return wrapper

    return decorator


@step("Container health")
def check_containers() -> None:
    result = run(["docker", "compose", "ps", "--format", "json"])
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("No containers found. Run 'docker compose up -d --build' first.")
    containers = {json.loads(line)["Service"]: json.loads(line) for line in lines}
    for svc in ("bunker", "proxy"):
        c = containers.get(svc)
        if not c:
            raise RuntimeError(f"{svc} service not found.")
        if c["State"] != "running":
            raise RuntimeError(f"{svc} is not running (state: {c['State']}).")


@step("Model loaded")
def check_model_loaded() -> None:
    result = run(["docker", "compose", "logs", "bunker"])
    if "model loaded" not in result.stdout:
        raise RuntimeError(
            "'model loaded' not found in bunker logs. "
            "Check for a startup error (e.g. mmproj mismatch)."
        )


@step("Inference")
def check_inference() -> None:
    body = json.dumps(
        {
            "model": "MiniCPM-V-4_6-Q4_K_M.gguf",
            "messages": [{"role": "user", "content": "ciao"}],
            "max_tokens": 20,
        }
    ).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read())
    except (urllib.error.URLError, OSError) as exc:
        raise RuntimeError(f"Request to the proxy failed: {exc}") from exc

    content = payload["choices"][0]["message"].get("content") or ""
    if not content.strip():
        raise RuntimeError(
            "Model returned empty content. If --reasoning isn't off, check for "
            "reasoning_content eating the token budget instead."
        )
    print(f"  Model replied: {content}")


@step("Network isolation (bunker has no egress)")
def check_network_isolation() -> None:
    result = run(
        ["docker", "compose", "exec", "bunker", "sh", "-c", "curl -m 3 -sI https://example.com"]
    )
    if result.returncode == 0:
        raise RuntimeError(
            "bunker reached the internet, but it should be on an internal-only network. "
            "Check compose.yaml's 'bunker' network has internal: true and no ports are "
            "published for the bunker service."
        )


@step("Non-root execution")
def check_non_root() -> None:
    for svc in ("bunker", "proxy"):
        result = run(["docker", "compose", "exec", svc, "id"])
        if "uid=1000" not in result.stdout:
            raise RuntimeError(f"{svc} is not running as uid 1000: {result.stdout.strip()}")


def main() -> None:
    check_containers()
    check_model_loaded()
    check_inference()
    check_network_isolation()
    check_non_root()

    if failures:
        print(f"\n{failures} check(s) failed.")
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
