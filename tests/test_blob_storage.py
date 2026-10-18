import hashlib
from types import SimpleNamespace

import pytest
from azure.core.exceptions import AzureError, ResourceExistsError

from pharmaops.blob_storage import LocalProcedureStore, StorageError, metadata_for, seed_files


@pytest.fixture
def storage(monkeypatch):
    class Container:
        exists = False

        def __init__(self):
            self.blobs = {}

        def create_container(self):
            if self.exists:
                raise ResourceExistsError("already exists")
            self.exists = True

        def upload_blob(self, name, data, metadata, **_kwargs):
            self.blobs[name] = {"data": data, "metadata": metadata}

        def list_blobs(self, **_kwargs):
            return [
                SimpleNamespace(
                    name=name, size=len(value["data"]), etag="test-etag", metadata=value["metadata"]
                )
                for name, value in self.blobs.items()
            ]

        def get_blob_client(self, name):
            value = self.blobs[name]
            return SimpleNamespace(
                get_blob_properties=lambda: SimpleNamespace(
                    size=len(value["data"]), metadata=value["metadata"]
                ),
                download_blob=lambda **_kwargs: SimpleNamespace(readall=lambda: value["data"]),
            )

    container = Container()
    service = SimpleNamespace(get_container_client=lambda _: container, close=lambda: None)
    monkeypatch.setattr("pharmaops.blob_storage.BlobServiceClient", lambda **_: service)
    store = LocalProcedureStore()
    yield store, container
    store.close()


def test_seed_publish_preserves_metadata_and_repeated_names(storage):
    store, _ = storage
    assert store.publish() == 7
    records = store.list_procedures()
    assert len(records) == 7
    for record in records:
        original = seed_files()[record.name].read_bytes()
        assert store.download(record.name) == original
        assert record.metadata == metadata_for(original)
    assert sum(r.metadata.status == "superseded" for r in records) == 1
    store.publish()
    assert len(store.list_procedures()) == 7


@pytest.mark.parametrize("name", ["../.env", "C:/private.txt", "https://example.com/file.md"])
def test_arbitrary_blob_paths_rejected(storage, name):
    with pytest.raises(StorageError, match="arbitrary paths"):
        storage[0].download(name)


def test_changed_download_with_old_metadata_is_rejected(storage):
    store, container = storage
    store.publish()
    name = next(iter(seed_files()))
    container.blobs[name]["data"] += b"\nModified stored content."
    with pytest.raises(StorageError, match="integrity check failed"):
        store.download(name)


def test_malformed_stored_header_returns_safe_error(storage):
    store, container = storage
    store.publish()
    name = next(iter(seed_files()))
    invalid = b"A stored object without a Markdown metadata header."
    container.blobs[name]["data"] = invalid
    container.blobs[name]["metadata"]["sha256"] = hashlib.sha256(invalid).hexdigest()
    with pytest.raises(StorageError, match="header is invalid"):
        store.download(name)


def test_storage_failure_has_safe_actionable_message(storage, monkeypatch):
    store, container = storage

    def unavailable(**_):
        raise AzureError("raw sensitive diagnostic")

    monkeypatch.setattr(container, "list_blobs", unavailable)
    with pytest.raises(StorageError, match="Start Azurite") as error:
        store.list_procedures()
    assert "sensitive" not in str(error.value)
