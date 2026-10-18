"""Local-only Azure Blob Storage exercise with seeded fictional procedures.

The official public Azurite development credential below is not a production secret.
The endpoint is fixed to localhost; no cloud credentials or model-selected URLs are accepted.
"""

import argparse
import hashlib
import json

from azure.core.exceptions import AzureError, ResourceExistsError
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import BlobServiceClient, ContentSettings
from pydantic import Field, ValidationError

from pharmaops.config import ROOT
from pharmaops.schemas import StrictModel

SEED_DIRECTORY = ROOT / "data/procedures"
CONTAINER = "pharmaops-procedures"
ACCOUNT_URL = "http://127.0.0.1:10000/devstoreaccount1"
# Published by Microsoft for Azurite only; never use this key for a real storage account.
DEVELOPMENT_KEY = (
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
)
MAX_BYTES = 256_000


class StorageError(Exception):
    pass


class ProcedureMetadata(StrictModel):
    document_id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=150)
    version: str = Field(min_length=1, max_length=20)
    country: str = Field(pattern=r"^(GLOBAL|BG|DE|RO)$")
    effective_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    status: str = Field(pattern=r"^(current|superseded)$")
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class StoredProcedure(StrictModel):
    name: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*\.md$")
    size: int = Field(ge=1, le=MAX_BYTES)
    etag: str
    metadata: ProcedureMetadata


def seed_files():
    return {path.name: path for path in sorted(SEED_DIRECTORY.glob("*.md"))}


def metadata_for(data: bytes) -> ProcedureMetadata:
    try:
        header = json.loads(data.decode("utf-8").split("---", 2)[1])
        return ProcedureMetadata(**header, sha256=hashlib.sha256(data).hexdigest())
    except (ValueError, IndexError, TypeError) as exc:
        raise StorageError(
            "Procedure header is invalid. Inspect it and republish the seed."
        ) from exc


class LocalProcedureStore:
    """A small SDK wrapper. Its methods are UI actions, never autonomous agent tools."""

    def __init__(self):
        self.service = BlobServiceClient(
            account_url=ACCOUNT_URL,
            credential={"account_name": "devstoreaccount1", "account_key": DEVELOPMENT_KEY},
            api_version="2023-11-03",
            retry_total=0,
            connection_timeout=3,
            read_timeout=5,
            transport=RequestsTransport(use_env_settings=False),
        )
        self.container = self.service.get_container_client(CONTAINER)

    def close(self):
        self.service.close()

    def publish(self):
        try:
            try:
                self.container.create_container()
            except ResourceExistsError:
                pass
            files = seed_files()
            if not files:
                raise StorageError("No seeded fictional procedures found.")
            for name, path in files.items():
                data = path.read_bytes()
                if len(data) > MAX_BYTES:
                    raise StorageError("A seeded procedure exceeds the 256 KB demo limit.")
                meta = metadata_for(data)
                self.container.upload_blob(
                    name=name,
                    data=data,
                    overwrite=True,
                    metadata=meta.model_dump(),
                    content_settings=ContentSettings(content_type="text/markdown; charset=utf-8"),
                )
            return len(files)
        except (AzureError, OSError, ValueError, ValidationError) as exc:
            raise StorageError(
                "Publishing failed. Start local Azurite on port 10000 and retry. "
                "Some files may already be stored; publishing again safely replaces the same names."
            ) from exc

    def list_procedures(self):
        try:
            allowed = seed_files()
            records = []
            for index, blob in enumerate(self.container.list_blobs(include=["metadata"])):
                if index >= 100:
                    raise StorageError("Storage listing exceeds the demo limit of 100 objects.")
                if blob.name in allowed:
                    records.append(
                        StoredProcedure(
                            name=blob.name, size=blob.size, etag=blob.etag, metadata=blob.metadata
                        )
                    )
            return sorted(records, key=lambda item: item.name)
        except (AzureError, ValueError, ValidationError) as exc:
            raise StorageError(
                "Procedure storage unavailable or invalid. "
                "Start Azurite and publish the demo procedures."
            ) from exc

    def download(self, name: str) -> bytes:
        if name not in seed_files():
            raise StorageError(
                "Choose one of the seeded procedure filenames; arbitrary paths are not allowed."
            )
        try:
            blob = self.container.get_blob_client(name)
            properties = blob.get_blob_properties()
            metadata = ProcedureMetadata.model_validate(properties.metadata)
            if not 0 < properties.size <= MAX_BYTES:
                raise StorageError("Stored procedure exceeds the demo size limit.")
            data = blob.download_blob(offset=0, length=MAX_BYTES + 1).readall()
            if (
                len(data) > MAX_BYTES
                or hashlib.sha256(data).hexdigest() != metadata.sha256
                or metadata_for(data) != metadata
            ):
                raise StorageError(
                    "Stored procedure integrity check failed. Inspect it and republish the seed."
                )
            return data
        except (AzureError, ValueError, ValidationError) as exc:
            raise StorageError(
                "Download failed. Check Azurite and republish the fictional procedure."
            ) from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["publish", "list", "download", "check"])
    parser.add_argument("--name", help="Seeded filename for download")
    args = parser.parse_args()
    storage = LocalProcedureStore()
    try:
        if args.command == "publish":
            print(f"Published {storage.publish()} fictional procedures to local Azurite.")
        elif args.command == "list":
            print(json.dumps([r.model_dump() for r in storage.list_procedures()], indent=2))
        elif args.command == "download":
            if not args.name:
                parser.error("download requires --name")
            data = storage.download(args.name)
            directory = ROOT / "data/runtime/blob-downloads"
            directory.mkdir(parents=True, exist_ok=True)
            target = directory / args.name
            if not target.resolve().is_relative_to(ROOT.resolve()):
                raise StorageError("Download target must stay inside the project.")
            target.write_bytes(data)
            print(f"Verified original procedure saved to {target}")
        else:
            count = storage.publish()
            records = storage.list_procedures()
            assert len(records) == count
            for record in records:
                assert storage.download(record.name) == seed_files()[record.name].read_bytes()
                assert record.metadata == metadata_for(seed_files()[record.name].read_bytes())
            storage.publish()
            assert len(storage.list_procedures()) == count
            print(
                json.dumps(
                    {
                        "storage": "Azurite Blob emulator, localhost only",
                        "uploaded": count,
                        "download_bytes_and_metadata_verified": count,
                        "repeated_publish_object_count": count,
                        "cloud_storage_validation": "not performed",
                    },
                    indent=2,
                )
            )
    except StorageError as exc:
        parser.exit(1, str(exc) + "\n")
    finally:
        storage.close()


if __name__ == "__main__":
    main()
