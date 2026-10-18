# Local Azure Blob Storage exercise

[English](blob-storage.md) | [Български](bg/blob-storage.md)

This optional exercise publishes the seven fictional Markdown procedures into **Azurite**,
Microsoft's local Azure Storage emulator. Python uses the official `azure-storage-blob` SDK
to upload, list metadata, and download the originals. No Azure account, subscription, login,
payment card, or cloud resource is needed. Emulator testing is not cloud Storage validation.

## Start the emulator

Prerequisites: the project's Python environment, Node.js 22+, and pnpm 11.25.0. These are
development tools, not a JavaScript frontend. `tools/azurite/package.json` pins Azurite 3.37.0;
`pnpm-lock.yaml` locks its transitive packages. `uv.lock` locks Python SDK 12.31.0 and its
dependencies. See [pnpm installation](https://pnpm.io/installation) if pnpm is not available.
Initial package installation needs internet; subsequent emulator use is local.

From the repository root in PowerShell:

```powershell
uv sync --frozen --python 3.12
node --version
pnpm --version
pnpm --dir tools/azurite install --frozen-lockfile --ignore-scripts --store-dir ../../.pnpm-store
.\scripts\run_azurite.ps1
```

Keep this terminal running. The helper starts only Blob Storage on `127.0.0.1:10000`, disables
Azurite telemetry and access logging, and persists emulator data under ignored
`data/runtime/azurite/`. It does not start Queue/Table Storage or create a real Azure account.
Stop it with Ctrl+C.

If the system Node is older than 22, pass an existing supported binary explicitly. The
following is the already available Node 24 used for validation on this Codex workstation;
the script does not install or replace system Node:

```powershell
.\scripts\run_azurite.ps1 -NodeExecutable "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
```

That Codex-specific path is optional and environment-dependent. On another machine, use
Node 22+ on PATH or provide its actual executable path. Installation of this exercise did
not update the existing system Node 14.

## Use the interface

Open the Streamlit app and select **Document storage** / **Хранилище за документи**.

1. Click **Publish demo procedures**. The SDK creates the private emulator container
   `pharmaops-procedures` if absent and uploads only files seeded in `data/procedures/`.
2. Refresh the list and select a filename. Inspect document ID, title, version, country,
   effective date, current/superseded status, byte size, ETag, and SHA-256 metadata.
3. Click **Prepare verified download**, then **Download original procedure**. The original
   English Markdown is returned after size, checksum, and header/metadata checks.

The tab is bilingual. Opening the app does not connect to Azurite; storage operations run
only after the corresponding button is clicked. An unavailable emulator produces a helpful
message. Existing procedure and complaint workflows do not require this emulator.

## Command-line demonstration

With Azurite running, use another terminal:

```powershell
uv run --frozen python -m pharmaops.blob_storage publish
uv run --frozen python -m pharmaops.blob_storage list
uv run --frozen python -m pharmaops.blob_storage download --name 01-damage.md
uv run --frozen python -m pharmaops.blob_storage check
```

Downloads go to ignored `data/runtime/blob-downloads/`. The `check` command makes actual
Azure SDK HTTP requests to Azurite: it uploads all seven documents, compares downloaded
bytes and metadata with the original files, republishes, and verifies that the object count
remains seven. This is distinct from offline tests that substitute a fake storage client.

Repeated publication deliberately replaces the same filenames. It does not create a document
history or delete unrelated blobs. Listing is limited to known seeded filenames and at most
100 enumerated objects; each procedure is limited to 256,000 bytes. Raw Markdown is preserved,
including the superseded procedure and its status. Storage does not decide procedure applicability.

## Boundary with RAG and business data

The new library is a storage integration exercise. It does not automatically reindex blobs,
replace the authoritative local seed corpus, change vector retrieval, or upload complaints,
conversation history, `.env`, databases, or personal files. The existing RAG index still comes
from `data/procedures/` and enforces its own country/status/date filters. An explicit governed
Blob-to-index ingestion path would be a separate future change.

No storage method is exposed as an agent tool. The SDK destination is fixed to the local
emulator; models and UI input cannot select a remote account or arbitrary filesystem paths.
Downloaded content remains untrusted data and does not authorize tools or submissions.

## Authentication, compatibility, and limitations

The implementation uses Microsoft's publicly documented Azurite development account and key.
That public emulator credential is not a production secret. No real cloud connection string
or credential is read by this storage module. The client disables environment proxy use,
has three-second connection / five-second read timeouts, and no automatic retries.

The client explicitly requests Storage API version `2023-11-03`, which supports the basic
operations exercised here and is accepted by the pinned emulator. API-version checking remains
enabled; there is no `--skipApiVersionCheck` or loose mode. This avoids relying on whichever
newer service version becomes the SDK default.

SHA-256 and header checks detect inconsistent downloaded content/metadata; they do not prove
authenticity if someone can replace both content and metadata. Cloud RBAC, managed identity,
SAS, Key Vault, encryption configuration, durability, service scale, and deployment are not
validated. The shared emulator key is appropriate only for this localhost development setup.

Troubleshooting: start Azurite before publishing, check Node 22+ and port 10000 if startup
fails, and publish again if the container is missing. A partially failed publish can leave
some files stored; retrying safely replaces the same seeded names. A failed integrity check
requires inspection and republishing, not silently accepting the altered file.

See [Microsoft Azurite guidance](https://learn.microsoft.com/en-us/azure/storage/common/storage-install-azurite?tabs=npm),
[the official Python Blob quickstart](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python),
and [Azurite's public development credentials](https://github.com/Azure/Azurite#default-storage-account).
