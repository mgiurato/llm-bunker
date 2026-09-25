# 1. Use llama.cpp's server for inference

## Status

Accepted

## Context

We need to serve a local GGUF model over an HTTP API on a Windows
machine with no GPU, without depending on any external/cloud inference
service.

## Decision

Use `ghcr.io/ggml-org/llama.cpp:server` as the inference engine, rather
than e.g. Ollama, vLLM, or a custom Python inference stack.

## Rationale

- Runs GGUF models directly, which is the most common quantized format
  for CPU-friendly local inference.
- Serves an OpenAI-compatible `/v1/chat/completions` API out of the box,
  so any OpenAI-compatible client (Continue, curl, custom scripts) can
  talk to it without a bespoke integration.
- CPU-only inference is a first-class, actively maintained path (unlike
  some alternatives that assume GPU availability).
- Ships its own minimal web UI, useful for direct debugging without
  standing up a separate client.
- Actively maintained upstream project (`ggml-org/llama.cpp`), with
  frequent releases and a wide flag surface for tuning behavior (context
  size, reasoning mode, multimodal projector, etc. — see
  [002](002-network-isolation.md) onward for how those get used here).

## Consequences

- We're tied to whatever the llama.cpp server's CLI flags and API shape
  expose — e.g. the `--reasoning` flag was needed to work around
  chain-of-thought output silently consuming the token budget (see
  [troubleshooting.md](../troubleshooting.md)).
- Performance on CPU-only hardware is modest (single-digit to low-teens
  tokens/sec for generation on this machine) — acceptable for the
  current use case, but a real constraint if usage grows.
