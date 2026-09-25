# Troubleshooting

## Server won't start: `mismatch between text model and mmproj`

```text
error: mismatch between text model (n_embd = 1024) and mmproj (n_embd = 2560)
hint: you may be using wrong mmproj
```

The `--mmproj` file doesn't belong to the same model/version as
`--model`. Either drop `--mmproj` entirely (if you don't need vision
support — see [models.md](models.md)), or re-download both files from
the exact same GGUF repo/commit.

## Responses hang on "Generating..." forever

The model may be emitting `reasoning_content` (chain-of-thought) instead
of `content`. If `max_tokens` is capped and the model spends the whole
budget "thinking," `content` never gets populated — clients that only
render `delta.content` (like Continue) show nothing and appear stuck,
even though the server is actively streaming tokens.

Check `docker compose logs bunker` — if you see steadily increasing
`n_gen` counts but the client shows nothing, this is almost certainly
it. Confirm by hitting the API directly with `curl -N` and inspecting
the raw SSE stream for `reasoning_content` vs `content` fields.

Fix: `compose.yaml` passes `--reasoning off` on `bunker`, so this
shouldn't recur. If it does (e.g. after a model change), re-verify that
flag is still present.

## The model keeps asking to call a tool

Symptom: a chat client shows something like:

```text
Let's check the current time to respond appropriately.
Allow use of get_datetime from Browser Tools?
[Allow once] [Deny]
```

even though `bunker` has no internet access. A tool-use-trained model
will still attempt an available tool even if the system prompt says "you
have no tools" — the presence of a tool schema in the request overrides
text instructions, since the model wasn't trained to reconcile those two
contradictory signals.

Two independent sources of tools to check:

1. **llama.cpp's own built-in web UI** (`http://127.0.0.1:8080`) ships a
   "Browser" tool group (including "Current time") enabled by default
   for new conversations, stored in the browser's `localStorage`. Open
   the settings panel, disable those tools, **Save settings**.
2. **Continue's own agent tools**, configured client-side in Continue,
   independent of anything in this repo.

Click **Deny** in the moment; disable the offending tool group for the
long-term fix. The [proxy](architecture.md)'s date/time injection means
the model has the correct date without needing a tool at all — the tool
prompt is a client-side offer, not something the model requires to
function correctly.

## Continue: model doesn't appear in the chat model selector

Check the `provider` field in `~/.continue/config.yaml`. It must be a
provider Continue actually recognizes — `openai` for an
OpenAI-compatible server like llama.cpp. `provider: local` (or any other
made-up value) silently fails to register the model. See
[continue.md](continue.md).

## Requests take a long time / prompt is much larger than expected

Agentic clients (Continue's Agent mode, llama.cpp's own tool-enabled
chat) send substantial system-prompt and tool-schema overhead on every
request — often 1000+ tokens even for a one-word message. On CPU-only
inference this dominates latency far more than the visible reply length.
See [continue.md](continue.md#performance-expectations) for mitigations.
