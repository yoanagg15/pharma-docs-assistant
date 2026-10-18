# Local validation record — 2026-10-18

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
