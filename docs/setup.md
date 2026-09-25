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

## 6. Verify health

```sh
docker compose ps
```

Both `bunker` and `proxy` should show `Up`/`healthy`. Then:

```sh
docker compose logs bunker
```

Look for `llama_server: model loaded` and
`listening on http://0.0.0.0:8080`. If you see a
`mismatch between text model and mmproj` error instead, see
[troubleshooting.md](troubleshooting.md).

## 7. Verify inference

```sh
curl -sN -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniCPM-V-4_6-Q4_K_M.gguf","messages":[{"role":"user","content":"ciao"}],"stream":true,"max_tokens":30}'
```

Expect `data: {...}` SSE chunks with non-null `content` fields, ending in
`data: [DONE]`. Or open [http://127.0.0.1:8080](http://127.0.0.1:8080)
for llama.cpp's built-in chat UI.

## 8. Verify network isolation

Confirm `bunker` has no route out:

```sh
docker compose exec bunker sh -c "curl -m 3 -sI https://example.com" || echo "no egress (expected)"
```

This should fail — `bunker` sits on the `internal: true` network with no
published ports (see [architecture.md](architecture.md) and
[security.md](security.md)).

## 9. Verify non-root execution

```sh
docker compose exec bunker id
docker compose exec proxy id
```

Both should report `uid=1000`, not `uid=0(root)`.

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
