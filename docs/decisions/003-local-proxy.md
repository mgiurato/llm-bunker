# 3. Replace socat with a custom HTTP-aware proxy

## Status

Accepted (supersedes the original `alpine/socat` proxy)

## Context

`proxy` was originally `alpine/socat` doing a plain TCP forward
(`tcp-listen:8080 → tcp-connect:bunker:8080`). This satisfied the
network-isolation goal from [002](002-network-isolation.md), but the
model has no awareness of the current date/time and no way to look it
up (no internet, see [002](002-network-isolation.md)). Left alone, it
would either hallucinate a date or — worse, once an agentic client
offers it a tool — attempt to call a `get_datetime`-style tool, which is
a client-side action outside our isolation boundary entirely (see
[security.md](../security.md#what-this-does-not-protect-against)).

`socat` operates at the TCP level; it has no visibility into HTTP
requests or JSON bodies, so it cannot inject or modify anything.

## Decision

Replace `socat` with a small custom Python reverse proxy
(`proxy/app.py`, stdlib only — `http.server` + `http.client`) that:

- Forwards all requests to `bunker:8080` unchanged by default.
- For `POST /v1/chat/completions` (and `/chat/completions`), parses the
  JSON body and inserts (or merges into an existing) `system` message
  containing the live UTC date/time, plus a note that the model has no
  internet access or tools.
- Streams responses back chunk-by-chunk, preserving SSE streaming
  behavior for `stream: true` requests.

## Rationale

- This is the one thing `socat` structurally cannot do — it requires
  parsing and rewriting HTTP request bodies, not just forwarding bytes.
- Keeping it stdlib-only avoids adding a dependency surface (no pip
  packages, small Alpine-based image) while still being expressive
  enough for this one transformation.
- The proxy remains stateless — nothing is logged or persisted, so it
  doesn't become a new place to leak conversation content.
- Preserves everything from [002](002-network-isolation.md): still the
  only published port, still non-root, still `cap_drop: ALL` /
  `read_only` (see [004](004-non-root.md)).

## Consequences

- We now maintain a small piece of custom code instead of relying
  entirely on off-the-shelf images. It's simple enough (~90 lines) that
  this tradeoff is worth it for the behavior gained.
- The proxy assumes a single upstream (`bunker`) and a narrow set of
  paths to rewrite; extending it (e.g. to also inject stored
  "memory"/notes) is straightforward but not yet done.
- If llama.cpp's request/response shape changes significantly, the
  proxy's JSON parsing logic may need updating.
