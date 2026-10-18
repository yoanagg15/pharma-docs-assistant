"""Section-aware ingestion, local semantic embeddings, persistent Chroma retrieval."""

import hashlib
import json
from datetime import date
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pharmaops.config import ROOT, Settings


class KnowledgeError(Exception):
    pass


def load_documents(directory: Path = ROOT / "data/procedures") -> list[Document]:
    chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
    for path in sorted(directory.glob("*.md")):
        _, header, body = path.read_text(encoding="utf-8").split("---", 2)
        meta = json.loads(header)
        required = {"document_id", "title", "version", "country", "effective_date", "status"}
        if not required <= meta.keys():
            raise KnowledgeError(f"Missing document metadata: {path.name}")
        meta["effective_int"] = int(date.fromisoformat(meta["effective_date"]).strftime("%Y%m%d"))
        if meta["country"] not in {"GLOBAL", "BG", "DE", "RO"}:
            raise KnowledgeError(f"Unsupported country: {path.name}")
        section = "Overview"
        for block in body.split("\n## "):
            if "\n" in block and block != body.split("\n## ")[0]:
                section, content = block.split("\n", 1)
            else:
                content = block
            if not content.strip():
                continue
            for i, text in enumerate(splitter.split_text(content.strip())):
                digest = hashlib.sha256(f"{section}|{i}|{text}".encode()).hexdigest()[:12]
                chunk_id = f"{meta['document_id']}-v{meta['version']}-{digest}"
                chunks.append(
                    Document(
                        page_content=text,
                        id=chunk_id,
                        metadata={**meta, "section": section, "chunk_id": chunk_id},
                    )
                )
    if not chunks:
        raise KnowledgeError("No procedure documents found.")
    if len({d.id for d in chunks}) != len(chunks):
        raise KnowledgeError("Duplicate document identifiers. Check document IDs and versions.")
    return chunks


class LocalEmbeddings(Embeddings):
    def __init__(self, settings: Settings):
        from fastembed import TextEmbedding

        try:
            self.model = TextEmbedding(
                model_name=settings.embedding_model,
                cache_dir=str(settings.runtime / "embedding-cache"),
                threads=2,
            )
        except Exception as exc:
            raise KnowledgeError(
                "Local embedding model unavailable. First index build needs "
                "internet for the small FastEmbed model download. Retry the "
                "index command when connected; no keyword fallback is used."
            ) from exc

    def embed_documents(self, texts):
        return [v.tolist() for v in self.model.passage_embed(texts)]

    def embed_query(self, text):
        return next(self.model.query_embed(text)).tolist()


def eligibility(country: str, reference_date: date):
    return {
        "$and": [
            {"country": {"$in": [country, "GLOBAL"]}},
            {"status": "current"},
            {"effective_int": {"$lte": int(reference_date.strftime("%Y%m%d"))}},
        ]
    }


def store(settings, collection, embeddings):
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=collection,
        embedding_function=embeddings,
        persist_directory=str(settings.runtime / "chroma"),
        collection_metadata={"hnsw:space": "cosine"},
    )


def build_index(settings: Settings, embeddings=None, documents=None):
    docs = documents if documents is not None else load_documents()
    payload = json.dumps([(d.id, d.metadata, d.page_content) for d in docs], sort_keys=True)
    digest = hashlib.sha256((settings.embedding_model + payload).encode()).hexdigest()[:20]
    name = "procedures-" + digest
    db = store(settings, name, embeddings or LocalEmbeddings(settings))
    db.add_documents(docs, ids=[d.id for d in docs])
    settings.runtime.mkdir(parents=True, exist_ok=True)
    manifest = {
        "collection": name,
        "embedding_model": settings.embedding_model,
        "chunk_count": len(docs),
        "corpus_digest": digest,
    }
    temporary = settings.runtime / "index.tmp"
    temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temporary.replace(settings.runtime / "index.json")
    return manifest


class Retriever:
    def __init__(self, settings, embeddings=None):
        try:
            manifest = json.loads((settings.runtime / "index.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise KnowledgeError(
                "Index missing. Run: uv run python -m pharmaops.cli index"
            ) from exc
        if manifest["embedding_model"] != settings.embedding_model:
            raise KnowledgeError("Embedding model changed. Rebuild the index first.")
        self.db = store(settings, manifest["collection"], embeddings or LocalEmbeddings(settings))

    def search(self, query: str, country: str, reference_date: date, k=3):
        if country not in {"BG", "DE", "RO"}:
            raise KnowledgeError("Choose one country: BG, DE, or RO.")
        try:
            matches = self.db.similarity_search_with_score(
                query[:1000], k=k, filter=eligibility(country, reference_date)
            )
            # Cosine distance cutoff is a heuristic, never a confidence percentage.
            return [doc for doc, distance in matches if distance <= 0.65]
        except Exception as exc:
            raise KnowledgeError(
                "Semantic retrieval failed. Rebuild the local index and retry."
            ) from exc
