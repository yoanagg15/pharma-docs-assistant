"""A small bounded graph: model agents choose tools; deterministic nodes enforce policy."""

import re
from datetime import date
from typing import Literal, TypedDict
from uuid import uuid4

from langchain.tools import tool
from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from pharmaops.client import BusinessError
from pharmaops.knowledge import KnowledgeError
from pharmaops.providers import ModelError
from pharmaops.schemas import ComplaintInput, Delivery, Draft, GroundedAnswer

INSUFFICIENT = "The available procedures do not support an answer to this question."
UNSAFE = re.compile(
    r"ignore (?:all |any )?(?:previous|prior|system) instructions|system prompt|"
    r"disregard.*instructions|reveal.*secret|execute.*shell|bypass.*confirmation",
    re.I,
)
TOPIC = re.compile(
    r"packag|damag|missing|deliver|discrepan|return|complaint|escalat|"
    r"опаков|повред|липс|достав|несъответ|връщ|оплак|жалб|ескалац",
    re.I,
)


class State(TypedDict, total=False):
    question: str
    mode: Literal["procedure", "complaint"]
    country: str | None
    reference_date: date
    language: Literal["en", "bg"]
    fields: dict
    previous_draft: Draft | None
    delivery: Delivery
    evidence: list[Document]
    draft: Draft
    answer: GroundedAnswer
    message: str
    trace: list[str]
    calls: int
    decision: str
    query: str
    done: bool
    error: bool


def verify(answer: GroundedAnswer, evidence: list[Document]) -> bool:
    by_id = {d.metadata["chunk_id"]: d.page_content for d in evidence}
    return (
        answer.supported
        and bool(answer.claims)
        and all(
            c.citation_id in by_id
            and c.quote in by_id[c.citation_id]
            and not UNSAFE.search(c.quote)
            for c in answer.claims
        )
    )


def create_workflow(provider, retriever, client):
    @tool
    def retrieve_procedures(query: str, country: str) -> list[Document]:
        """Find currently effective fictional procedures for one supported country."""
        return retriever.search(query, country, active_date[0])

    @tool
    def lookup_delivery(delivery_id: str) -> Delivery:
        """Look up a fictional delivery through the configured simulated business API."""
        if not re.fullmatch(r"DEL-\d{4}", delivery_id):
            raise BusinessError("Use a delivery identifier such as DEL-1002.")
        return client.delivery(delivery_id)

    @tool
    def prepare_draft(draft_json: str) -> Draft:
        """Validate and save a complaint draft, without submitting a complaint."""
        return client.save(Draft.model_validate_json(draft_json))

    # Closure is created per request/session, never shared globally between conversations.
    active_date = [date.today()]

    def coordinator(state):
        trace = ["Coordinator selected the " + state["mode"] + " workflow."]
        active_date[0] = state.get("reference_date", date.today())
        question = state["question"]
        if len(question) > 1500:
            return {"trace": trace, "done": True, "message": "Use at most 1,500 characters."}
        if not TOPIC.search(question) or re.search(
            r"\bdosage\b|\bdiagnos|\bprescri|дозиров|диагноз|предпис", question, re.I
        ):
            return {
                "trace": trace,
                "done": True,
                "message": "I cover fictional distribution procedures and complaints. "
                "I cannot provide medical advice or answer unrelated questions.",
            }
        if state["mode"] == "procedure" and not state.get("country"):
            return {
                "trace": trace,
                "done": True,
                "message": "Choose one country (BG, DE, or RO) to select applicable procedures.",
            }
        mentioned = set(re.findall(r"\b(BG|DE|RO)\b", question.upper()))
        names = {"BULGARIA": "BG", "GERMANY": "DE", "ROMANIA": "RO"}
        names.update({"БЪЛГАРИЯ": "BG", "ГЕРМАНИЯ": "DE", "РУМЪНИЯ": "RO"})
        mentioned.update(code for name, code in names.items() if name in question.upper())
        if len(mentioned) > 1 or (
            mentioned and state.get("country") and state["country"] not in mentioned
        ):
            return {
                "trace": trace,
                "done": True,
                "message": "Country is ambiguous. Select one country matching your question.",
            }
        if state["mode"] == "complaint":
            fields = state.get("fields", {})
            missing = [
                name for name in ComplaintInput.model_fields if fields.get(name) in (None, "")
            ]
            if missing:
                return {
                    "trace": trace + ["Missing information: " + ", ".join(missing)],
                    "done": True,
                    "message": "Complete required complaint fields: " + ", ".join(missing),
                }
            try:
                ComplaintInput.model_validate(fields)
            except ValidationError:
                return {
                    "trace": trace,
                    "done": True,
                    "message": "Review the delivery ID, "
                    "description (10–1,500 characters), category, and package count.",
                }
        return {"trace": trace, "calls": 0, "evidence": [], "done": False}

    def agent(state):
        if state.get("calls", 0) >= 4:
            return {"done": True, "message": "Tool limit reached. Refine your request and retry."}
        allowed = ["clarify"]
        if state["mode"] == "complaint" and not state.get("delivery"):
            allowed.append("lookup_delivery")
        if state.get("country") and not state.get("evidence"):
            allowed.append("retrieve_procedures")
        if state.get("delivery") and state.get("evidence"):
            allowed.append("prepare_draft")
        try:
            decision = provider.decide(state["question"], allowed, bool(state.get("evidence")))
        except ModelError as exc:
            return {"done": True, "error": True, "message": str(exc)}
        if decision.tool not in allowed:
            return {"done": True, "message": "Model requested a disallowed tool. No action taken."}
        if decision.tool == "clarify":
            return {
                "done": True,
                "message": "Please clarify the delivery issue and required fields.",
            }
        return {
            "decision": decision.tool,
            "query": decision.query or state["question"],
            "calls": state["calls"] + 1,
        }

    def execute(state):
        trace = list(state["trace"])
        try:
            if state["decision"] == "lookup_delivery":
                delivery = lookup_delivery.invoke({"delivery_id": state["fields"]["delivery_id"]})
                if state.get("country") and delivery.country != state["country"]:
                    return {
                        "done": True,
                        "message": "Selected country does not match delivery. "
                        f"Choose {delivery.country} and prepare the draft again.",
                    }
                trace.append(f"Found delivery {delivery.delivery_id}.")
                return {"delivery": delivery, "country": delivery.country, "trace": trace}
            if state["decision"] == "retrieve_procedures":
                docs = retrieve_procedures.invoke(
                    {"query": state["query"], "country": state["country"]}
                )
                safe_docs = [d for d in docs if not UNSAFE.search(d.page_content)]
                trace.append(f"Retrieved {len(safe_docs)} passages.")
                if len(safe_docs) != len(docs):
                    trace.append("Excluded suspicious document instructions.")
                if not safe_docs:
                    return {"evidence": [], "trace": trace, "done": True, "message": INSUFFICIENT}
                return {"evidence": safe_docs, "trace": trace}
            previous = state.get("previous_draft")
            draft = Draft(
                **state["fields"],
                country=state["delivery"].country,
                draft_id=previous.draft_id if previous else uuid4().hex,
                revision=previous.revision + 1 if previous else 1,
                source_ids=[d.metadata["chunk_id"] for d in state["evidence"]],
            )
            draft = prepare_draft.invoke({"draft_json": draft.model_dump_json()})
            trace.append("Draft ready for review.")
            return {
                "draft": draft,
                "trace": trace,
                "done": True,
                "message": "Review the draft. Submission requires your explicit confirmation.",
            }
        except (BusinessError, KnowledgeError, ValidationError) as exc:
            message = (
                str(exc) if not isinstance(exc, ValidationError) else "Draft validation failed."
            )
            return {"done": True, "message": message, "trace": trace}

    def knowledge_answer(state):
        try:
            answer = provider.answer(
                state["question"], state["evidence"], state.get("language", "en")
            )
            return {
                "answer": answer,
                "trace": state["trace"] + ["Knowledge agent selected evidence."],
            }
        except ModelError as exc:
            return {"done": True, "error": True, "message": str(exc)}

    def verification(state):
        if state.get("done"):
            return {}
        if not verify(state["answer"], state["evidence"]):
            return {
                "answer": GroundedAnswer(supported=False, claims=[]),
                "message": INSUFFICIENT,
                "trace": state["trace"] + ["Verification withheld an unsupported answer."],
            }
        return {
            "message": "Evidence-backed procedure excerpts:",
            "trace": state["trace"] + ["Verified citation IDs and exact supporting excerpts."],
        }

    graph = StateGraph(State)
    graph.add_node("coordinator", coordinator)
    graph.add_node("agent", agent)
    graph.add_node("tools", execute)
    graph.add_node("knowledge", knowledge_answer)
    graph.add_node("verification", verification)
    graph.add_edge(START, "coordinator")
    graph.add_conditional_edges("coordinator", lambda s: END if s.get("done") else "agent")
    graph.add_conditional_edges("agent", lambda s: END if s.get("done") else "tools")
    graph.add_conditional_edges(
        "tools",
        lambda s: (
            END
            if s.get("done")
            else ("knowledge" if s["mode"] == "procedure" and s.get("evidence") else "agent")
        ),
    )
    graph.add_edge("knowledge", "verification")
    graph.add_edge("verification", END)
    return graph.compile()


def run_workflow(provider, retriever, client, **request):
    return create_workflow(provider, retriever, client).invoke(request, {"recursion_limit": 16})
