# Changelog

All notable changes to this project are documented here.

## [1.1.0] - 2026-09-25

### Added

- `scripts/{healthcheck,verify,benchmark}.{sh,ps1}` — cross-platform
  entrypoints sharing one Python implementation in `scripts/lib/`, so
  there's a single source of truth for what "healthy"/"verified" means
  instead of duplicated shell logic per OS.
- `--ctx-size` raised from 8192 to 32768 tokens; measured impact on idle
  and under-load memory was negligible for this model/quantization.
- `mem_limit: 16g` hard cap on `bunker`, as a safety ceiling.
- GGUF quantization naming glossary in `docs/models.md` (`Q`/`IQ`/`K`
  schemes, bit-depth, `_S`/`_M`/`_L`/`_XS` suffixes).
- `MODEL_FILE` environment variable parameterizes which GGUF `bunker`
  loads (`compose.yaml`, `.env.example`), instead of hand-editing
  `--model`. Downloaded and documented four additional candidate models
  (Hermes-3-Llama-3.1-8B, Qwen2.5-Coder-7B-Instruct, Llama-3.2-3B-Instruct,
  Phi-4-mini-instruct) alongside MiniCPM-V in `docs/models.md`, evaluating
  them against MiniCPM-V's weak agentic tool-selection (see
  `docs/troubleshooting.md`).
- `config/continue.config.yaml.example` — Continue config template
  listing an entry per available model (only one meant to be active at
  a time, matching `MODEL_FILE`).
- `.markdownlint.json` — scopes `MD024` to sibling headings only (so
  repeated `### Added`/`### Removed` across CHANGELOG version sections
  don't trip it) and excludes code blocks/tables from `MD013` line
  length.

### Fixed

- `config/continue.config.yaml.example` and `docs/continue.md`'s
  MiniCPM-V entry still had `contextLength: 8192`, left over from
  before `--ctx-size` was raised to 32768 — now matches the other
  model entries and `compose.yaml`.

## [1.0.0] - 2026-09-25

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
