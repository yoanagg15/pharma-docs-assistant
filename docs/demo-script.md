# Interview demo — approximately four minutes

[English](demo-script.md) | [Български](bg/demo-script.md)

Use the real configured provider only after `model-check` passes. If using mock mode, state
up front that model decisions are simulated. Do not present mock responses as LLM validation.
Start the API/UI and build the index before the demonstration.

## 0:00–0:35 — business purpose

“This is my independent portfolio project. It helps fictional receiving employees find
applicable operational procedures and record delivery complaints. All deliveries and SOPs
are invented. It is not medical advice or a production pharmaceutical system.”

Show the local-demo, provider, and fictional-data labels. Explain that Groq inference can use
its Free plan, while embeddings and business storage stay local. There is no Azure deployment.

## 0:35–1:35 — grounded procedure answer

Choose BG. Ask: “What should I do if a delivery arrives with damaged outer packaging?”
Inspect the answer and expand the source passages. Show title, section, version, country,
effective date, and stable citation ID. Explain that the application displays selected exact
excerpts and deterministically verifies their presence, rather than guaranteeing that an LLM's
unrestricted answer is correct. Point to the concise activity trace.

## 1:35–2:55 — complaint and confirmation

Open Delivery complaints. Use DEL-1002, damaged_packaging, one affected package, investigation,
and “Outer carton torn at the corner during receiving.” Prepare the draft. Show the delivery
lookup trace, applicable country, source IDs, structured fields, and revision.

Explain that the graph cannot submit. Check the review checkbox and explicitly click the
confirmation button. Read the returned complaint reference. Click again to demonstrate the
same reference. Before submission, you can alternatively edit a field to show confirmation
being disabled until an updated draft is reviewed.

## 2:55–3:40 — evidence limits and reliability

Ask: “What exact temperature range is required for a refrigerated delivery?” The corpus has
no temperature SOP; expect insufficient evidence. If a real model instead selects an irrelevant
excerpt, acknowledge it as a relevance failure and record it for evaluation, not as success.
Try an unknown delivery (DEL-9999) if time permits. Show the useful error.

## 3:40–4:00 — tests and scope

Show actual local test results and the retrieval report. Distinguish deterministic checks,
real embedding ranking metrics, and human review of real-model answers. Explain that the
workflow is bounded, CI is configured, and deployment/authentication remain future work.

## Interview questions tied to the code

Optional Azure follow-up: use the [local Functions guide](azure-local.md) to start Core Tools,
look up DEL-1002 on port 7071, and explain how the same FastAPI API is adapted to a Python
HTTP-triggered function. Describe this as local development and testing, not Azure deployment.

Optional Blob follow-up: open Document storage, publish the seven fictional procedures to
Azurite, inspect metadata, and prepare a verified download. Explain the distinction between
object storage and the Chroma vector index, and label the emulator as local rather than cloud.
See [the Blob guide](blob-storage.md).

- **Why LangGraph?** `workflow.py` makes routing, tool execution, verification, and termination
  explicit. There are at most four tool choices and a recursion limit; this is inspectable.
- **Which parts are agents?** The model selects an allowed tool/query and evidence excerpts.
  Coordinator, tool dispatcher, and verification are deterministic nodes. Mock choices are simulations.
- **Why separate FastAPI?** It demonstrates an actual HTTP integration boundary; the UI cannot
  bypass the simulated business system by writing its SQLite tables directly.
- **What stops double submissions?** A fingerprint bound to the saved draft, immutable submitted
  drafts, a transaction, and unique constraints. A changed revision rejects stale confirmation.
- **How do you address hallucination?** Filter applicable documents, prompt for exact excerpts,
  verify citation IDs and text, and abstain on verification failure. Relevance still needs review.
- **How do you address prompt injection?** Documents cannot grant tools. No submission tool exists;
  allowed calls and preconditions are enforced independently of the model. Pattern checks are secondary.
- **What did you train?** Nothing. The project integrates pretrained models and evaluates an application.
- **What would production need?** Authentication, permissions, operational review, broader evaluation,
  secure deployment, monitoring, document governance, and integration with a real system.
