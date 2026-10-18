# Learning notes

**Embeddings** turn text into numerical vectors using a pretrained model. Similar meanings
often produce nearby vectors. Here FastEmbed runs a quantized ONNX model locally on CPU;
the application does not train the model or send embeddings to a paid service.

**Vector search** ranks stored vectors by a distance measure. Chroma persists them alongside
metadata. A small cosine distance means proximity in that embedding space, not a calibrated
probability that a passage answers the question. Metadata filters handle applicability separately.

**RAG** retrieves evidence before generating an answer. This project loads documents, chunks
within sections, embeds chunks, applies country/status/date filters, retrieves passages, and
asks a model to select relevant evidence. Every displayed claim must match a cited passage.
This reduces unsupported text but cannot ensure completeness, relevance, or real-world accuracy.

**Agents and tools**: a model-driven agent chooses an action within a bounded set. A tool is
an ordinary validated function exposed to that choice. The model can select retrieval, delivery
lookup, or draft preparation where allowed. The program enforces preconditions; it does not
trust model instructions as authorization. Submission belongs only to the explicit UI action.
The coordinator and verification nodes are deterministic, not autonomous agents.

**LangChain** supplies Documents, embeddings/vector-store interfaces, typed tools and model
integrations. **LangGraph** supplies a typed state graph, visible transitions and a recursion
limit. These libraries reduce integration work while keeping the small workflow readable.

**Structured output** means validating a model's JSON against a schema. It catches invalid
fields and shapes. It does not prove the content is true. The separate verifier checks exact
provenance. Request timeouts, output limits and finite tool budgets prevent unbounded execution.

**NLP / LLM application development** here means integrating pretrained models, crafting task
prompts, preparing evidence, handling tool/API contracts, checking outputs and measuring retrieval.
It does not mean deep-learning training, fine-tuning, or developing a foundation model.

**Evaluation** must separate deterministic software correctness from probabilistic model quality.
Fake vectors test filtering and persistence only. Real embeddings support ranking measurements.
Real chat-model outputs need human review for relevance, completeness and correct abstention.
A small successful demo is not a production reliability guarantee.

**Bilingual use**: interface language and delivery country are separate choices. Bulgarian
questions are translated into English search queries by the model; English procedures remain
the evidence. Bulgarian answer translations are useful for readability, but exact citation
verification applies to the original source and does not validate translation fidelity.

**Realistic next steps** are better labelled evaluation data, explicit document precedence,
draft recovery, stronger relevance checks, and production access controls if deployment is ever
needed. More agents or services do not automatically improve this focused application.
