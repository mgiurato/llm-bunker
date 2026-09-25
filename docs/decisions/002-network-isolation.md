# 2. Isolate the model container on an internal-only network

## Status

Accepted

## Context

The `bunker` service runs a third-party inference engine (llama.cpp)
loading a third-party model file (GGUF weights from a community
conversion). Neither the engine nor the weights are things we can fully
vet, and inference workloads on untrusted binary weights are a
reasonable place to apply defense in depth, even on a personal
workstation.

## Decision

Put `bunker` on a docker network (`bunker`) marked `internal: true`, and
publish no ports for it in `compose.yaml`. All access to it goes through
a separate `proxy` service, which is the only thing with a published
port.

## Rationale

- `internal: true` means docker gives that network no route to the
  internet — even if something inside `bunker` wanted to phone home, it
  has no path to do so.
- Not publishing any port on `bunker` means the only way to reach it is
  from another container on the same docker network — i.e. `proxy`.
- This costs nothing in normal operation (proxy adds negligible latency)
  and meaningfully shrinks what a compromised or buggy inference process
  could do.

## Consequences

- Every request has to go through `proxy`; debugging `bunker` directly
  from the host isn't possible without `docker compose exec` into the
  network.
- This isolation only covers the container/network layer. It does not
  protect against tool calls initiated by a client application on the
  model's behalf (see [security.md](../security.md#what-this-does-not-protect-against)) —
  that's a client-side concern, not something network policy can fix.
