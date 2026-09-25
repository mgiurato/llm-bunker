# llm-bunker

A self-hosted, network-isolated MiniCPM-V chat model, served over an
OpenAI-compatible API and reachable only through a local proxy.

## Quick start

```sh
docker compose up -d --build
curl http://127.0.0.1:8080/v1/models
```

Open the built-in chat UI at [http://127.0.0.1:8080](http://127.0.0.1:8080),
or point any OpenAI-compatible client (e.g. [Continue](https://continue.dev))
at `http://127.0.0.1:8080/v1`.

## Documentation

- [docs/architecture.md](docs/architecture.md) — how the pieces fit together
- [docs/setup.md](docs/setup.md) — getting the stack running from scratch
- [docs/security.md](docs/security.md) — the isolation/hardening model
- [docs/models.md](docs/models.md) — which model, why, where to get it
- [docs/continue.md](docs/continue.md) — wiring this up to Continue
- [docs/troubleshooting.md](docs/troubleshooting.md) — problems we've hit and their fixes
- [docs/decisions/](docs/decisions/) — architecture decision records

## Layout

```text
compose.yaml   # the two-service stack (bunker + proxy)
proxy/         # custom reverse proxy (date/time injection)
models/        # GGUF model weights (gitignored)
```
