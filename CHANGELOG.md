# Changelog

All notable changes to this project are documented here.

## [Unreleased] - 2026-09-25

### Added

- Initial `compose.yaml` stack: `bunker` (llama.cpp server) + `proxy` (ingress).
- Network isolation: `bunker` runs on an `internal: true` docker network with
  no published ports; only `proxy` is reachable from the host, on
  `127.0.0.1:8080`.
- Container hardening on both services: non-root user, `cap_drop: ALL`,
  `no-new-privileges`, `read_only` root filesystem.
- Custom Python reverse proxy (`proxy/`) replacing the original `socat`
  TCP forwarder, so requests to `/v1/chat/completions` can be rewritten
  in flight.
- Live UTC date/time injected as a system message on every chat request,
  since the model has no clock and no internet access to check one.
- `--reasoning off` on the model, so token budget isn't silently consumed
  by invisible chain-of-thought (`reasoning_content`) that never reaches
  `content`.
- Continue (`~/.continue/config.yaml`) wired up to the local model via the
  `openai` provider pointed at the proxy's `apiBase`.

### Removed

- `mmproj-model-f16.gguf` — multimodal projector, unused since vision
  support isn't needed right now. See [docs/models.md](docs/models.md)
  for the mmproj/model mismatch story.

### Fixed

- Model/mmproj mismatch (`n_embd` 1024 vs 2560) that prevented the server
  from starting at all — resolved by dropping `--mmproj` entirely.
