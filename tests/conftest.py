import hashlib
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from langchain_core.embeddings import Embeddings

from pharmaops.business import create_app
from pharmaops.config import Settings
from pharmaops.schemas import Draft


class OfflineEmbeddings(Embeddings):
    """Deterministic test vectors only. Never used by the application or retrieval evaluation."""

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        digest = hashlib.sha256(text.encode()).digest()
        return [float(b) / 255 for b in digest]


@pytest.fixture
def offline_settings(tmp_path):
    return replace(Settings(), runtime=tmp_path, embedding_model="offline-test-vectors")


@pytest.fixture
def api(tmp_path):
    with TestClient(create_app(tmp_path / "business.sqlite3")) as client:
        yield client


@pytest.fixture
def draft():
    return Draft(
        delivery_id="DEL-1002",
        category="damaged_packaging",
        description="Outer carton torn at the corner.",
        affected_packages=1,
        requested_resolution="investigation",
        draft_id="test-draft",
        revision=1,
        country="BG",
        source_ids=["SOP-DAMAGE-v2.0-test"],
    )
