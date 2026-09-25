#!/usr/bin/env python3
"""Rough tokens/sec benchmark for the bunker model.

Sends a fixed prompt through the proxy N times and reports prompt
processing and generation speed, as reported by llama.cpp's own `timings`
field in each response. Useful as a before/after check when changing
--ctx-size, mem_limit, quantization, or the model itself.
"""

import argparse
import json
import statistics
import urllib.error
import urllib.request

PROMPT = "Explain, in a few paragraphs, how a hash table resolves collisions."


def run_once(max_tokens: int) -> dict:
    body = json.dumps(
        {
            "model": "MiniCPM-V-4_6-Q4_K_M.gguf",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": max_tokens,
        }
    ).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=200)
    args = parser.parse_args()

    prompt_speeds: list[float] = []
    gen_speeds: list[float] = []

    for i in range(1, args.runs + 1):
        print(f"Run {i}/{args.runs}...")
        try:
            payload = run_once(args.max_tokens)
        except (urllib.error.URLError, OSError) as exc:
            print(f"  Request failed: {exc}")
            continue

        timings = payload.get("timings")
        if not timings:
            print("  No 'timings' field in response, skipping.")
            continue

        prompt_speeds.append(timings["prompt_per_second"])
        gen_speeds.append(timings["predicted_per_second"])
        print(
            f"  prompt: {timings['prompt_per_second']:.1f} tok/s "
            f"({timings['prompt_n']} tokens) | "
            f"generation: {timings['predicted_per_second']:.1f} tok/s "
            f"({timings['predicted_n']} tokens)"
        )

    if not prompt_speeds:
        print("\nNo usable results.")
        raise SystemExit(1)

    print(f"\n== Averages over {len(prompt_speeds)} run(s) ==")
    print(f"Prompt processing: {statistics.mean(prompt_speeds):.1f} tok/s")
    print(f"Generation:        {statistics.mean(gen_speeds):.1f} tok/s")


if __name__ == "__main__":
    main()
