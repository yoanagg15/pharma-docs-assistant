from datetime import date

from pharmaops.knowledge import Retriever, build_index, load_documents
from tests.conftest import OfflineEmbeddings


def test_ingestion_metadata_and_stability():
    docs = load_documents()
    assert len({d.metadata["document_id"] for d in docs}) == 7
    assert [d.id for d in docs] == [d.id for d in load_documents()]
    assert all(
        {
            "title",
            "section",
            "version",
            "effective_date",
            "country",
            "status",
            "document_id",
            "chunk_id",
        }
        <= d.metadata.keys()
        for d in docs
    )


def test_country_date_and_superseded_filter(offline_settings):
    embeddings = OfflineEmbeddings()
    build_index(offline_settings, embeddings)
    retriever = Retriever(offline_settings, embeddings)
    for country in ("BG", "DE", "RO"):
        docs = retriever.search("damaged packaging return", country, date(2026, 10, 18), k=30)
        assert docs
        assert all(d.metadata["country"] in {country, "GLOBAL"} for d in docs)
        assert all(d.metadata["status"] == "current" for d in docs)
        expected_countries = {"GLOBAL", country} if country != "RO" else {"GLOBAL"}
        assert {d.metadata["country"] for d in docs} == expected_countries
        assert "SOP-DAMAGE-OLD" not in {d.metadata["document_id"] for d in docs}
    early = retriever.search("damage Bulgaria", "BG", date(2026, 2, 1), k=30)
    assert all(d.metadata["document_id"] != "SOP-DAMAGE-BG" for d in early)
    assert retriever.search("damage", "BG", date(2024, 1, 1), k=30) == []
