"""Explicit index building and separately labelled retrieval / optional LLM evaluation."""

import argparse
import json
import time
from datetime import date

from pharmaops.client import BusinessClient
from pharmaops.config import ROOT, Settings
from pharmaops.knowledge import KnowledgeError, Retriever, build_index
from pharmaops.providers import ModelError, Provider
from pharmaops.workflow import run_workflow


def evaluate(settings, llm=False, limit=None, reference_date=date(2026, 10, 18), delay=12):
    cases = json.loads((ROOT / "eval/questions.json").read_text(encoding="utf-8"))
    if limit:
        cases = cases[:limit]
    if llm and settings.provider == "mock":
        raise ModelError(
            "Real-LLM evaluation requires groq or local mode. Mock is not LLM quality."
        )
    retriever = Retriever(settings)
    results = []
    hits = []
    ranks = []
    provider = Provider(settings) if llm else None
    client = BusinessClient(settings.api_url)
    try:
        for case in cases:
            row = {**case}
            if case["country"]:
                docs = retriever.search(case["question"], case["country"], reference_date, k=3)
                found = list(dict.fromkeys(d.metadata["document_id"] for d in docs))
                row["retrieved_documents"] = found
                if case["supported"]:
                    positions = [
                        i + 1
                        for i, d in enumerate(docs)
                        if d.metadata["document_id"] in case["sources"]
                    ]
                    hit = bool(positions)
                    reciprocal = 1 / min(positions) if positions else 0
                    hits.append(hit)
                    ranks.append(reciprocal)
                    row.update(hit_at_3=hit, reciprocal_rank_at_3=reciprocal)
            if llm:
                state = run_workflow(
                    provider,
                    retriever,
                    client,
                    question=case["question"],
                    country=case["country"],
                    mode="procedure",
                    reference_date=reference_date,
                )
                answer = state.get("answer")
                row["response"] = answer.model_dump() if answer else None
                row["message"] = state.get("message")
                row["trace"] = state.get("trace")
                row["model_error"] = state.get("error", False)
                # Human review is needed; no automatic quality score is invented.
            results.append(row)
            if llm:
                print(
                    f"Evaluated {case['id']}: "
                    + ("model error" if row["model_error"] else "response recorded"),
                    flush=True,
                )
                if delay and case is not cases[-1]:
                    time.sleep(delay)
    finally:
        client.close()
    report = {
        "evaluation": "real_llm_examples" if llm else "real_embedding_retrieval",
        "provider": settings.provider if llm else None,
        "model": settings.model if llm else None,
        "embedding_model": settings.embedding_model,
        "reference_date": str(reference_date),
        "k": 3,
        "supported_query_count": len(hits),
        "source_hit_rate_at_3": sum(hits) / len(hits) if hits else None,
        "mrr_at_3": sum(ranks) / len(ranks) if ranks else None,
        "answer_quality": "Not scored. Review relevance, completeness, and abstention.",
        "model_error_count": sum(r.get("model_error", False) for r in results) if llm else None,
        "verified_answer_count": sum(
            bool(r.get("response", {}).get("supported")) for r in results if r.get("response")
        )
        if llm
        else None,
        "results": results,
    }
    output = ROOT / "artifacts" / ("llm-examples.json" if llm else "retrieval.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    print(f"Reviewable report: {output}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["index", "evaluate", "model-check"])
    parser.add_argument("--llm", action="store_true", help="Make real configured model requests")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--delay",
        type=float,
        default=12,
        help="Seconds between real-LLM cases (default 12 for Free-plan quotas)",
    )
    parser.add_argument("--reference-date", type=date.fromisoformat, default=date(2026, 10, 18))
    args = parser.parse_args()
    settings = Settings.load()
    try:
        if args.command == "index":
            print("Building semantic index. First run downloads the small local embedding model.")
            print(json.dumps(build_index(settings), indent=2))
        elif args.command == "model-check":
            if settings.provider == "mock":
                raise ModelError("Mock mode is configured; no real-model validation was performed.")
            from langchain_core.documents import Document

            doc = Document(
                page_content="Record visible packaging damage before further handling.",
                metadata={"chunk_id": "MODEL-CHECK"},
            )
            answer = Provider(settings).answer("How do I record packaging damage?", [doc])
            from pharmaops.workflow import verify

            if not verify(answer, [doc]):
                raise ModelError("Model responded, but the structured evidence check failed.")
            print(
                "Real model structured response and citation check passed. "
                "This is a connectivity smoke test, not an answer-quality evaluation."
            )
        else:
            evaluate(settings, args.llm, args.limit, args.reference_date, max(0, args.delay))
    except (KnowledgeError, ModelError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
