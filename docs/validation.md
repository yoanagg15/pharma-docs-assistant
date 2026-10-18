# Local validation record — 2026-10-18

[English](validation.md) | [Български](bg/validation.md)

Environment: Windows, Python 3.12.12, uv 0.11.29. Exact package versions are in `uv.lock`.
This record describes the initial local validation, before any user-authorized GitHub upload.
No hosted deployment or repository visibility change was performed.
The Groq key is stored only in ignored `.env` and was not printed in validation output.

## Checks actually executed

| Check | Observed result |
| --- | --- |
| Ruff lint | Passed |
| Ruff formatting check | Passed |
| Offline pytest | 24 passed |
| Real FastEmbed index build | Seven procedures, ten section chunks, persisted in Chroma |
| Real-embedding retrieval evaluation | 10 supported questions; source hit rate@3 = 1.0; MRR@3 = 1.0 |
| Groq model connectivity | Structured response and exact citation check passed for `qwen/qwen3.8-27b` |
| Full 14-case English workflow sample | 10 verified extractive answers, one insufficient-evidence response, two country clarifications, one out-of-scope response; zero model errors in the paced run |
| Bulgarian question and answer | Real Groq response with Bulgarian translations and validated original English quotes; visibly checked in the browser |
| Language switch | English/Bulgarian labels checked in the browser; input preservation tested offline |
| Live API / UI | Both localhost services started; a real-model complaint workflow prepared a draft through HTTP; explicit UI confirmation produced a fictional complaint reference |
| Repeated live UI submission | The same reference was returned with a visible already-submitted notice |

The retrieval metrics apply only to the ten supported questions in `eval/questions.json`.
They measure first relevant chunk rank against expected document IDs, not response accuracy.
The corpus and questions are small, authored examples; no held-out reliability claim is made.

An initial fast model-evaluation run returned several model errors after five responses.
The evaluation now spaces cases and counts errors explicitly. The paced 14-case run used a
15-second delay and completed without model errors. No provider switching or paid fallback
was used. The original Llama model name returned `model_not_found`; the current model was
selected from the account's actual available-model list. Qwen is currently a preview model;
its future availability is not guaranteed.

The full English sample preceded the final Bulgarian UI addition. The updated provider was
then exercised with a real Bulgarian question, and the final code passed the offline suite.
Real outputs were inspected, but there is no independently graded answer-quality score.

## Manually reviewable examples from the real English run

**Damaged outer packaging, BG** — the model selected:

> For a delivery with damaged outer packaging, separate the affected packages from routine receiving stock and record the visible damage before further handling.

Source: `SOP-DAMAGE-v2.0-ea286b1ecb27`. This addresses the receiving step; other selected
excerpts covered recording the delivery/count/description, photographs, quality review, and
complaint preparation. Country-specific completeness still needs human review.

**Which desk reviews damaged packaging in Bulgaria?** — the model selected:

> Notify the fictional Sofia quality desk before moving the separated packages to the review area.

Source: `SOP-DAMAGE-BG-v1.1-e125f3d446f6`.

**Can I promise replacement stock for missing items?** — the model selected:

> Do not promise replacement stock before the investigation is reviewed.

Source: `SOP-MISSING-v1.0-f8e8b7d4811e`.

**Refrigerated delivery temperature range** — the model/workflow returned insufficient
evidence; there is no temperature-range SOP in the corpus. No temperature was invented.

The complete local reports are in ignored `artifacts/retrieval.json` and
`artifacts/llm-examples.json`. Reproduce with the README commands. Bulgarian translations
are machine-generated and labelled; deterministic verification covers original excerpts,
not translation fidelity.

## What remains unverified

- GitHub-hosted CI execution: its workflow was configured; it had not run during initial local validation.
- Local OpenAI-compatible chat server: adapter exists; no local chat-model runtime was installed
  or tested. Ollama is not used by this project.
- Linux execution, broader adversarial prompt-injection resistance, independent human quality
  grading, large corpora, real organizational SOPs, and production behavior.
- Authentication, authorization, regulated deployment, and continuous deployment are not implemented.

## Azure Functions local follow-up — 2026-10-18

The optional adapter was run with Core Tools 4.14.0, Functions runtime 4.1052.200.26352,
Python 3.12.12, and `azure-functions` 1.25.0. The host indexed `pharmaops_business_api` and
listened on `127.0.0.1:7071`, confirmed using the operating system's listening socket table.
No Azure login, subscription, cloud resource, Storage emulator, or cloud deployment was used.

`python -m scripts.check_functions` made real HTTP calls through that local host. Health and
DEL-1002 lookup passed; an unknown delivery returned 404; a changed draft rejected the old
confirmation with 409; repeated submission returned the same fictional complaint reference.
This validates the local Functions transport and shared business API, not Azure-hosted AI,
cloud identities, distributed storage, production behavior, or an additional real-LLM run.
See [the local guide](azure-local.md) for reproducible commands.
After adding the adapter, the offline suite still passed all 24 tests. Ruff lint/format and
the bilingual documentation checker passed (seven document pairs). Hosted CI for this
follow-up has not been verified.

## Local Blob Storage follow-up — 2026-10-18

Azurite 3.37.0 ran on `127.0.0.1:10000` with the existing Node 24.19.0 binary; system Node
14 was not replaced. The developer tool dependency setup used pnpm 11.25.0 with install
scripts disabled and a saved lockfile. Python used `azure-storage-blob` 12.31.0 with
Storage API `2023-11-03`; no cloud account or user credential was used for storage.

The real SDK integration check uploaded seven seeded Markdown procedures, listed their
metadata, verified byte-for-byte downloads and header metadata, and confirmed that repeated
publication still listed seven objects. A verified CLI download was saved under ignored
runtime data. The Streamlit publication and verified-download preparation were checked in
the browser. Offline tests use a fake storage service and additionally cover arbitrary path
rejection, altered bytes, malformed headers, and safe failure messages.

All 31 offline tests passed after this change. Ruff and the documentation checker passed
(eight document pairs). The library remains separate from RAG ingestion. Azure cloud Blob
Storage, production authentication, durability, and hosted CI for this change are unverified.
See [the storage guide](blob-storage.md).

## Repository review — 2026-10-18

Reviewed 62 Git-visible working files, three available historical commits, and all locally
available Git objects (114 blobs, 32 trees, three commits). Pattern checks covered provider
tokens, private keys, JWTs, credential assignments, authenticated URLs, and SAS signatures.
The actual local Groq key was compared in memory without printing it. No secret candidates
or copies of that key were found. Historical trees contained no real `.env`,
`local.settings.json`, private-key files, or runtime databases. GitHub advertised only
`master` at `78f419b`, matching the reviewed repository head.

An actual `.env` exists locally and is ignored; `.env.example` has an empty key field.
The hardcoded Azurite key is a public emulator credential, confirmed against the installed
package README, not a user or production Azure secret. `local-demo` is a dummy credential.
No history rewrite or credential deletion was needed.

The seven procedures, generator for ten fictional deliveries, evaluation questions, and test
fixtures were reviewed; no real customer/company records or sensitive business data were
identified. Pattern scans for emails, international phones, IBANs, and labelled personal
identifiers found no candidates in project file contents or historical versions. Git author
metadata is outside this dataset review. These checks cannot guarantee the absence of every
unknown secret, sensitive detail, or remote-only object.

README explains architecture, technologies, configuration, indexing, startup, and verification.
Both README versions and the bilingual UI now explicitly display **Proof of Concept (PoC)**
and **synthetic pharmaceutical distribution data**. The RAG source corpus was not changed.
Ruff lint and formatting (47 files), documentation checks (eight pairs), and offline tests
passed again: **31 passed**. This is not a fresh real-model/cloud evaluation or a production
security audit. The one-off report remains in ignored `artifacts/repository-audit.json`;
it contains locations and categories, never matched secret values.
