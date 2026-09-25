# Models

## MiniCPM-V 4.6 Q4_K_M

```text
Repository:
  https://huggingface.co/openbmb/MiniCPM-V-4.6      (model card / base)
  https://github.com/openbmb/minicpm                (source / docs)
  GGUF build: community conversion repo (Patricck1) offering
  F16, Q4_0/Q4_1, Q4_K_M, Q4_K_S, Q5_*, Q6_K, Q8_0 + matching mmproj

Filename:
  MiniCPM-V-4_6-Q4_K_M.gguf

Format:
  GGUF

Quantization:
  Q4_K_M

Size:
  ~529 MB

Expected location:
  models/MiniCPM-V-4_6-Q4_K_M.gguf

SHA256:
  6b0c74962c44bc6bf4b655b9b02c13eda9d5a0491543ae976d1ac18e4b7892e

Multimodal projector:
  Not currently installed.
```

## Why no multimodal projector

MiniCPM-V-4.6 is a vision-language model; `mmproj-model-f16.gguf` is the
projector needed for image input. Vision support isn't needed right now,
so `--mmproj` is omitted in `compose.yaml` and no mmproj file is kept in
`models/`.

**Pitfall hit during setup:** loading an `mmproj-model-f16.gguf` from a
different MiniCPM-V variant/commit than the text model produced

```text
mismatch between text model (n_embd = 1024) and mmproj (n_embd = 2560)
```

and the server refused to start — a hard failure, not a degradation. If
multimodal support is added back later, download **both** the model and
its mmproj file from the exact same GGUF repo/commit; don't mix mmproj
files across sources or model sizes. Record the new SHA256 here when you
do.

## Choosing a quantization

`Q4_K_M` is a reasonable default balance of size/quality/speed for
CPU-only inference — no GPU on this machine, see
[decisions/001-llama-cpp.md](decisions/001-llama-cpp.md). Larger
quantizations (`Q5_K_M`, `Q6_K`, `Q8_0`) trade more RAM and slower
inference for closer-to-F16 quality; smaller ones (`Q4_0`) trade quality
for a bit more speed/less RAM.

## Reasoning is disabled

`compose.yaml` passes `--reasoning off`. Without it, the model emits
chain-of-thought into a separate `reasoning_content` stream field before
any visible `content` — on CPU this can consume the entire `max_tokens`
budget before a single visible token is produced, which looks like the
server is hung. See
[troubleshooting.md](troubleshooting.md#responses-hang-on-generating-forever)
for the full story.
