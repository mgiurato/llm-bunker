# Security model

This stack assumes a single-user workstation, not a multi-tenant server.
The threat it defends against is a compromised or misbehaving inference
process (buggy model weights, a malicious GGUF, a bug in llama.cpp
itself) reaching out to the network or the host filesystem — not a
remote attacker, since nothing here is exposed beyond `127.0.0.1`.

## Layers

1. **Internal-only network for `bunker`.** The `bunker` docker network is
   declared `internal: true`, and the `bunker` service publishes no
   ports. The model server has no route to the internet and no route to
   the host except through `proxy`.
2. **Single ingress point.** Only `proxy` has a published port
   (`127.0.0.1:8080:8080`), and it's bound to loopback — nothing on the
   LAN can reach it.
3. **Non-root containers.** Both services run as UID 1000 (`user:
   "1000:1000"` on `bunker`, `USER 1000:1000` in `proxy/Dockerfile`).
   Neither runs as root inside its container.
4. **Dropped capabilities + no privilege escalation.** Both services set
   `cap_drop: [ALL]` and `security_opt: [no-new-privileges:true]`.
5. **Read-only root filesystem.** Both services set `read_only: true`.
   `bunker` gets a `tmpfs` mount at `/tmp` for whatever scratch space
   llama.cpp needs at runtime; `proxy` needs no writable paths at all.
6. **Read-only model mount.** `./models` is mounted into `bunker` as
   `:ro` — the inference process can't modify or delete model weights.

## What this does *not* protect against

- **Tool calls initiated by a client, not the container.** If you use an
  agentic client (Continue, or llama.cpp's own web UI) with tools
  enabled, the model's text output can trigger a tool call that the
  *client* executes on the host — e.g. a browser automation tool. The
  container's network isolation is irrelevant here, since the tool runs
  outside the container entirely. See
  [troubleshooting.md](troubleshooting.md#the-model-keeps-asking-to-call-a-tool)
  for the concrete case we hit (llama.cpp's built-in "Browser" tools).
  Review tool-call prompts before approving them.
- **No authentication.** llama.cpp is started without `--api-key`, so
  anything that can reach `127.0.0.1:8080` can use the API. This is
  acceptable only because the port is loopback-only and the machine is
  single-user. Don't change the `ports:` binding to `0.0.0.0` without
  adding an API key.
- **Supply chain of the model weights themselves.** Nothing here
  verifies the GGUF file's provenance beyond wherever you downloaded it
  from (see [models.md](models.md)).
