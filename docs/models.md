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

## GGUF quantization naming glossary

GGUF filenames follow a pattern like `Q4_K_M` or `IQ3_XS` that looks
cryptic but decodes into a few independent axes. General shape:

```text
[I]Q<bits>[_<variant>][_<size>]
```

### The letters

- **`Q`** — "quantized": the classic llama.cpp quantization scheme.
- **`IQ`** — "importance quantization" (i-quants): a newer scheme that
  uses a calibration dataset (an "importance matrix", `imatrix`) to
  decide which weights matter most and preserve them better. Generally
  better quality per bit than plain `Q` at the same size, especially at
  very low bit-widths (2–3 bit), but slower to compute during inference.
- **`K`** — "k-quants": weights are quantized in blocks, and different
  tensor types (attention vs. feed-forward, etc.) get different
  effective bit-depths within the same nominal quantization — e.g. a
  `Q4_K` model doesn't use exactly 4 bits everywhere, some tensors get
  more, some less, tuned for the best quality/size tradeoff. This is
  why `Q4_K_M` beats `Q4_0` at a similar file size.
- **`F16` / `BF16` / `F32`** — not quantized at all: full 16-bit float,
  "brain float" 16-bit, or full 32-bit float. These are the
  highest-quality (and largest) files, usually the source a GGUF is
  converted from, or a baseline for perplexity comparisons.

### The numbers

The digit right after `Q`/`IQ` is **bits per weight** — `2`, `3`, `4`,
`5`, `6`, `8`. Lower = smaller file and less RAM, but more quality loss.
`Q4_K_M` (~4 bits/weight effective) is the common "good enough" default
for CPU inference; `Q8_0` is close to lossless but roughly double the
size; `Q2_K`/`IQ2_*` are usable mainly when RAM is the hard constraint.

### The size/variant suffix

For legacy (non-K) quants:

- **`_0`** — a single scale factor per block, no offset. Simplest,
  oldest scheme.
- **`_1`** — scale **and** a minimum/offset per block. Slightly better
  quality than `_0` at the same bit-width, slightly larger.

For K-quants and I-quants, the suffix instead indicates relative
size/quality **within** that bit-width family:

- **`_S`** — Small: smallest file, lowest quality in that family.
- **`_M`** — Medium: balanced default (what we use for MiniCPM-V).
- **`_L`** — Large: largest file, highest quality in that family.
- **`_XS`** / **`_XXS`** — Extra (Extra) Small: used mainly on i-quants,
  pushed even smaller than `_S`.

So `Q4_K_M` reads as: 4-bit, k-quant scheme, medium size/quality point
within the 4-bit k-quant family. `Q6_K` has no size suffix because at
6-bit the k-quant scheme only ships one variant. `IQ3_XS` reads as:
importance-quantized, 3-bit, extra-small variant.

### Other letters you'll see around GGUF files

- **`mmproj`** — multimodal projector file, paired with a vision-language
  model's text weights (see
  [above](#why-no-multimodal-projector)) — not a quantization scheme.
- **`imatrix`** — the importance-matrix calibration file itself,
  sometimes distributed alongside i-quants for reference; not something
  you load into llama.cpp directly.

## Reasoning is disabled

`compose.yaml` passes `--reasoning off`. Without it, the model emits
chain-of-thought into a separate `reasoning_content` stream field before
any visible `content` — on CPU this can consume the entire `max_tokens`
budget before a single visible token is produced, which looks like the
server is hung. See
[troubleshooting.md](troubleshooting.md#responses-hang-on-generating-forever)
for the full story.
