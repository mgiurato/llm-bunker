# 4. Run both containers as non-root, capabilities dropped, read-only filesystem

## Status

Accepted

## Context

Both `bunker` (running third-party inference code) and `proxy` (parsing
untrusted-shaped JSON bodies) are processes that don't need root
privileges, filesystem write access, or Linux capabilities to do their
job. Running them with root/default privileges would be strictly more
exposure than needed for no operational benefit.

## Decision

For both services in `compose.yaml`:

- `user: "1000:1000"` (`bunker`) / `USER 1000:1000` in
  `proxy/Dockerfile` — run as a non-root, unprivileged UID.
- `cap_drop: [ALL]` — drop every Linux capability.
- `security_opt: [no-new-privileges:true]` — prevent privilege
  escalation via setuid binaries or similar.
- `read_only: true` — root filesystem is read-only.
  - `bunker` gets a `tmpfs` mount at `/tmp` for whatever scratch space
    llama.cpp needs at runtime.
  - `proxy` needs no writable path at all — it holds no state.
- `./models:/models:ro` — model weights are mounted read-only into
  `bunker`, so the inference process can't modify or delete them.

## Rationale

This is standard container-hardening practice with essentially no
downside here: neither service needs to write files, escalate
privileges, or run as root for anything in its actual job (serving
inference requests, proxying HTTP). Applying least privilege costs
nothing at runtime and meaningfully limits blast radius if either
process is compromised or misbehaves.

## Consequences

- If a future change to either service needs to write files (e.g. a
  proxy that persists "memory" notes to disk, as discussed but not yet
  built), that will need an explicit writable volume or tmpfs mount
  added deliberately — the default posture is "no writes," which is the
  point.
- UID 1000 must have read access to whatever's bind-mounted
  (`./models`), which is already satisfied by default file permissions
  on this setup but is worth checking if models are copied in with
  different ownership.
