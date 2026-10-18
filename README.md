# PharmaOps AI — Distribution Support Assistant

[English](README.md) | [Български](README.bg.md)

An independent portfolio project for a junior Python / AI developer. Employees can inspect
fictional distribution procedures and prepare delivery complaints, then explicitly confirm
submission to a **simulated** business API. No real pharmaceutical company is involved.
Procedures are illustrative operational examples, not medical or regulatory guidance.

## What it does

- Country-aware semantic retrieval with expandable document metadata and source passages.
- Groq API integration (Free plan available, subject to provider quotas), optional local
  OpenAI-compatible server, and a clearly labelled deterministic mock mode. No Ollama required.
- A bounded LangGraph workflow with model-driven tool selection and deterministic controls.
- Structured extractive answers: each original claim must be an exact quote from a cited passage.
  Bulgarian translations are labelled separately.
- Ten fictional deliveries in BG, DE, and RO; versioned drafts and idempotent confirmed submissions.
- Per-session Streamlit state, safe failure messages, and an activity trace without hidden reasoning.
- English / Bulgarian language selector for the UI and model answers. Original source excerpts
  remain in English; Bulgarian translations are labelled and do not replace citation verification.
- Offline pytest coverage and GitHub Actions CI. No cloud deployment is implemented or claimed.

## Architecture

Streamlit → bounded LangGraph → LangChain tools → local Chroma / simulated FastAPI → SQLite.
Groq supplies model inference; FastEmbed supplies local ONNX embeddings. A configured local
OpenAI-compatible server such as LM Studio can replace Groq. The UI never opens the business DB.
See [architecture](docs/architecture.md), [requirements](docs/requirements.md),
[demo script](docs/demo-script.md), and [learning notes](docs/learning-notes.md).

## Windows PowerShell setup

Prerequisites: Windows, Python 3.12, and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Python 3.13 is also permitted by the project; validation uses 3.12. Internet is needed to install
packages and obtain the embedding model initially. An API account is needed only for Groq mode.

```powershell
Set-Location D:\_AI\pharma-docs-assistant\pharma-docs-assistant
uv python install 3.12  # Skip if already installed
uv sync --frozen --python 3.12
Copy-Item .env.example .env  # Only if .env does not already exist; never overwrite your key
notepad .env
```

`uv.lock` pins direct and transitive dependencies. `uv sync --frozen` reproduces the resolution;
`pyproject.toml` records supported dependency ranges. Do not commit `.env`, model caches,
databases, indexes, or local evaluation artifacts. `.gitignore` excludes them.

## Configure model access

Recommended for this setup: create a key in [Groq Console](https://console.groq.com/keys),
stay on the Free plan, and set these values in `.env`:

```dotenv
MODEL_PROVIDER=groq
GROQ_API_KEY=your_key_here
MODEL_NAME=qwen/qwen3.8-27b
```

Never paste the key into chat, source code, screenshots, or Git. Free quotas and supported
model names can change: check [Groq limits](https://console.groq.com/docs/rate-limits) and
[models](https://console.groq.com/docs/models). A free account is not an unlimited service.
No payment fallback or automatic provider switch is implemented. Only fictional prompts and
procedure excerpts should be sent. LangSmith tracing is disabled by the application.

To work without an API key:

```dotenv
MODEL_PROVIDER=mock
```

Mock mode is a deterministic development simulation, **not a real LLM demonstration**. It
still uses the real semantic index in the UI; only automated offline tests inject test vectors.

For an existing local OpenAI-compatible model server (not installed by this project):

```dotenv
MODEL_PROVIDER=local
LOCAL_LLM_URL=http://127.0.0.1:1234/v1
MODEL_NAME=your_loaded_model_id
```

The server/model must support JSON mode and enough context for evidence. Local-provider
compatibility must be validated on the chosen model; support in code is not proof of a tested
runtime. No local LLM weights or runtimes are installed automatically.

## Build or rebuild the index

```powershell
uv run --frozen python -m pharmaops.cli index
```

First build downloads `BAAI/bge-small-en-v1.5` through FastEmbed (a quantized ONNX model,
roughly tens of MB; the full cache is larger). This is a local embedding model, not a chat LLM.
It runs on CPU and needs no paid API. The command prints a helpful failure if unavailable;
there is no keyword-search fallback. Downloads and Chroma data stay in `data/runtime/`.
Subsequent runs can use the cached embedding model.

Rebuild after editing documents or changing the embedding model. The collection identity
includes the corpus and model, and a manifest selects the completed build. This avoids reusing
an old corpus accidentally. Previous collections remain locally; they are not queried.

## Start the services

In PowerShell terminal 1, from the project directory:

```powershell
uv run --frozen uvicorn pharmaops.business:app --host 127.0.0.1 --port 8000
```

In terminal 2:

```powershell
uv run --frozen streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open [the UI](http://127.0.0.1:8501), [API docs](http://127.0.0.1:8000/docs), or
[API health](http://127.0.0.1:8000/health). Both services bind to localhost. Stop each with Ctrl+C.
On first API startup, SQLite tables and ten fictional deliveries are seeded automatically.

Select BG, ask the default packaging question, then prepare a complaint for DEL-1002 with
`Outer carton torn at the corner.` and one affected package. Review the sources and draft;
check the confirmation box and click **Confirm and submit complaint**. Repeating this call
returns the original complaint reference. Editing fields disables confirmation until the
updated draft is saved and reviewed. Use **Start a new complaint** after submission.

## Checks and evaluations

```powershell
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen python scripts/check_docs.py
uv run --frozen pytest -q
uv run --frozen python -m pharmaops.cli model-check
uv run --frozen python -m pharmaops.cli evaluate
uv run --frozen python -m pharmaops.cli evaluate --llm --limit 3
```

1. Offline tests use deterministic fake embeddings and mock models, no model downloads or
   external APIs. They cover contracts, filters, citations, API errors, injection controls,
   bounded graph execution, stale confirmation, and duplicate/concurrent submission.
2. Retrieval evaluation uses **real local embeddings** over 14 cases at a fixed reference date.
   Source hit rate@3 is the fraction of supported questions with any expected source in the
   first three chunks. MRR@3 averages `1 / first relevant chunk rank`, or zero when absent.
   Global and country-specific chunks count separately. Multiple chunks from one document can
   occupy ranks. Unsupported/ambiguous cases are not counted in those retrieval metrics.
3. Optional `--llm` makes real provider calls and saves actual answers for human review.
   Citation/excerpt validation is separate from relevance and completeness; no automatic answer
   quality score is claimed. The three-case run is a smoke sample, not a comprehensive evaluation.

Reports are written to ignored `artifacts/retrieval.json` and `artifacts/llm-examples.json`.
Real-model cases are spaced 12 seconds apart by default to reduce Free-plan throttling;
use `--delay 15` to increase the interval. Model errors are counted separately in the report.
Use `--reference-date 2026-10-18` for reproducible filtering. The UI defaults to today's date.
See [validation record](docs/validation.md) for what actually ran. GitHub Actions runs lint,
formatting, and offline tests without secrets. This is CI; no CD is configured.

## Limitations and troubleshooting

- No production authentication, tenant isolation, durable server conversation store, medical
  decision making, temperature SOPs, email, or real enterprise integration. Do not expose the
  local services to a public network.
- Exact excerpt verification checks provenance, not truth, relevance, or completeness. Extractive
  answers sacrifice fluent synthesis to keep claims inspectable. Human review remains necessary.
- Injection detection is a small heuristic, not a complete defense. The main boundaries are
  fixed tool allowlists, typed inputs, API-owned data, and keeping submission outside the graph.
- Scope and country routing use transparent rules and the UI workflow selection, not a general
  natural-language intent classifier. BG/DE/RO are the supported demo countries.
- Cosine distances are uncalibrated. Top-three retrieval with a heuristic distance cutoff of 0.65
  can miss relevant evidence or return irrelevant passages; low distance does not prove support.
- Index missing: run the index command. Embedding download failure: check connectivity and retry.
  Never substitute fake vectors in the production retrieval path.
- API unavailable: start terminal 1. The UI does not write directly to SQLite as a fallback.
- Model unavailable / HTTP 429: check the key, model name and account quota; wait and retry.
  Requests have timeouts and no automatic paid fallback. Raw provider errors and keys are hidden.
- Local port busy: stop the existing service or change both the command and relevant `.env` URL.
- Streamlit sessions reset when the process restarts. Business drafts and complaints remain in
  SQLite, but this small UI does not implement a draft-history browser.

## Documentation languages

Project documentation is maintained in English and Bulgarian. Each document links to its
counterpart; behavioral changes should update both versions together. The fictional RAG
source corpus remains in English. See [repository instructions](AGENTS.md).
CI checks for missing language counterparts, broken local documentation links, and mismatched
executable command/configuration blocks with `scripts/check_docs.py`. Translation accuracy
and semantic agreement still require human review.

## Official references used

[LangChain Groq](https://docs.langchain.com/oss/python/integrations/chat/groq),
[Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma),
[LangGraph](https://docs.langchain.com/oss/python/langgraph/graph-api),
[FastEmbed](https://qdrant.github.io/fastembed/),
[FastAPI](https://fastapi.tiangolo.com/tutorial/body/),
[Streamlit state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state),
[uv locking](https://docs.astral.sh/uv/concepts/projects/sync/).
