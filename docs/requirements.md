# Requirements and scope

## User stories and acceptance criteria

| Priority | User story | Acceptance criteria |
| --- | --- | --- |
| P0 | As a receiving employee, I need the applicable packaging procedure. | Country is selected; only current effective global/local passages are retrieved; each displayed excerpt has a valid citation and expandable metadata. |
| P0 | As an employee, I need an honest answer when evidence is missing. | Unsupported model answers are withheld; unrelated questions are routed out; missing/ambiguous country requests clarification. |
| P0 | As an employee, I need to record a delivery complaint. | The application looks up the delivery via HTTP; validates required fields; retrieves procedure evidence; saves and previews a structured draft. |
| P0 | As an employee, I must control submission. | No graph submission tool exists; explicit UI confirmation is required; changed fields disable confirmation; stale server revisions are rejected. |
| P0 | As an employee, I need safe retries. | Repeated/concurrent submissions of the same confirmed draft return one reference and create one record. |
| P0 | As a demonstrator, I need offline checks. | Lint and tests run with mocks and test embeddings, without credentials or model downloads. |
| P1 | As a reviewer, I need to inspect model behavior honestly. | Real embedding retrieval and optional real-LLM examples are separate from offline tests; unverified capabilities are identified. |
| P1 | As a user, I need useful errors. | Unknown deliveries, API/model outage, missing index and invalid fields receive actionable messages; no raw credential-bearing exception is shown. |
| P1 | As a bilingual demonstrator, I need English and Bulgarian. | Language selector translates UI/messages; Bulgarian questions work with a real model; original English source quotes remain inspectable; form input survives language changes. |

## Mapping to role requirements

| Requirement | Demonstrated implementation | Remaining gap |
| --- | --- | --- |
| Python and APIs | Pydantic schemas, FastAPI, HTTPX, SQLite transactions | No real enterprise system access |
| LLMs and prompt engineering | Groq / local-compatible adapters, JSON structured responses, evidence-only prompts | Model quality depends on provider; broader evaluations needed |
| RAG and vector search | Section chunking, local embeddings, Chroma, metadata filters, citations | Small English corpus; no hybrid search or reranker |
| AI agents and tool execution | Model selects allowlisted tools inside a bounded LangGraph workflow | Constrained task agents, no general autonomous planning |
| Testing and CI/CD | pytest, Ruff, locked dependencies, GitHub Actions CI definition | Hosted CI must run after user-authorized push; no CD |
| Security | Ignored secrets, fixed destinations, schemas, confirmation gate, parameterized SQL | Local demo without production authentication or regulatory certification |
| Business communication | Requirements, activity trace, demo script, architecture and limitations | No real stakeholder interviews or acceptance study |
| Azure / cloud | No cloud infrastructure needed | No Azure deployment or Azure experience claimed |
| Deep learning | Uses pretrained embedding and language models | No model training or fine-tuning |

## Prioritized next steps

1. Expand human-labelled evidence questions and manually grade completeness, relevance, and abstention.
2. Validate an optional local-compatible chat model and document its exact runtime/settings.
3. Add draft-history viewing and session recovery without sharing conversations globally.
4. Evaluate country supplement precedence, contradictory procedures, and historical validity windows.
5. Add authentication and authorization only if moving beyond the localhost demo.

Uploads, additional agents, email, Azure infrastructure, and JavaScript frontends are outside the
first version. No claims of production readiness, affiliation, deployment, or clinical suitability.
