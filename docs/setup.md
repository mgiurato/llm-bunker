# Setup

## 1. Install Docker Desktop

Docker Desktop for Windows, with the compose plugin (`docker compose ...`
should work from a shell once installed).

## 2. Clone repository

```sh
git clone <this-repo-url>
cd llm-bunker
```

## 3. Download model manually

Get `MiniCPM-V-4_6-Q4_K_M.gguf` and place it at
`models/MiniCPM-V-4_6-Q4_K_M.gguf`. See [models.md](models.md) for the
source repo and filename details. Model weights are gitignored and not
part of this repository — only `models/.gitkeep` is tracked.

## 4. Verify model checksum

```sh
sha256sum models/MiniCPM-V-4_6-Q4_K_M.gguf
```

Compare against the SHA256 recorded in [models.md](models.md). If it
doesn't match, re-download rather than proceeding — a corrupted or
substituted GGUF can fail to load or, worse, load with different
behavior than expected.

## 5. Start stack

```sh
docker compose up -d --build
```

First run pulls `ghcr.io/ggml-org/llama.cpp:server` and builds the
`proxy` image from `proxy/Dockerfile`.

## 6-9. Verify health, inference, network isolation, non-root execution

`scripts/verify.{sh,ps1}` runs all four checks and exits non-zero if any
fail:

```sh
./scripts/verify.sh      # Linux/macOS
```

```powershell
.\scripts\verify.ps1      # Windows
```

It checks, in order: `bunker`/`proxy` are running, `bunker`'s logs
contain `model loaded`, a real chat completion returns non-empty
content, `bunker` cannot reach the internet, and both containers run as
uid 1000. See [scripts/lib/verify.py](../scripts/lib/verify.py) for
exactly what each step does — both entrypoints call the same Python
logic, there's no divergence between platforms to worry about.

If "Model loaded" fails, look for a `mismatch between text model and
mmproj` error in `docker compose logs bunker` — see
[troubleshooting.md](troubleshooting.md). Once the stack's up day to day,
`scripts/healthcheck.{sh,ps1}` is a faster containers+API-only check for
routine use; `scripts/benchmark.{sh,ps1}` measures tokens/sec.

You can also just open [http://127.0.0.1:8080](http://127.0.0.1:8080)
for llama.cpp's built-in chat UI.

## Stopping

```sh
docker compose down
```

## Changing the model

Edit `--model` in `compose.yaml`'s `bunker.command`, drop the new GGUF
into `models/`, update the checksum in [models.md](models.md), then:

```sh
docker compose up -d --force-recreate bunker
```
