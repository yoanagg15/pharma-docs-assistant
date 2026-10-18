# Azure Functions locally — no subscription required

[English](azure-local.md) | [Български](bg/azure-local.md)

The optional adapter runs the existing simulated business API in the real Azure Functions
local runtime. It requires no Azure account, subscription, card, `az login`, or deployed
resource. It demonstrates local Azure Functions development, not cloud deployment.

For a separate Azure SDK exercise, see [local Blob Storage](blob-storage.md). That optional
library uses Azurite; this HTTP-only Functions host still runs independently without it.

## What runs

`function_app.py` uses the official `azure-functions` SDK and its Python v2 programming model.
`AsgiFunctionApp` adapts the existing FastAPI application to an HTTP-triggered function named
`pharmaops_business_api`. The ASGI startup lifecycle initializes the same SQLite schema and
fictional deliveries as the Uvicorn version. Routing, validation, versioned drafts, explicit
confirmation, and idempotency stay in the shared FastAPI code.

`host.json` removes the default `api` prefix, so endpoint paths stay unchanged. The helper
script starts Core Tools on `127.0.0.1:7071`. It selects this repository's Python environment
only for that process and restores the caller's environment when the host exits.
It creates ignored `local.settings.json` from the credential-free example only when absent.
The HTTP-only configuration uses local file-based host secret storage. The verified setup
does not need an Azure Storage account, Azurite, Docker, Node.js, or a new model download.

## Prerequisites and start

Use Python 3.12, uv, and Azure Functions Core Tools v4. The local validation used Core Tools
4.14.0 and `azure-functions` 1.25.0; `uv.lock` pins the SDK dependency. Core Tools is a separate
Microsoft installation, not installed by `uv sync`. If it is missing, use the
[official installation instructions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local).
No Azure CLI login is needed. Initial dependency installation may need internet.

From the repository root in Windows PowerShell:

```powershell
uv sync --frozen --python 3.12
func --version
.\scripts\run_functions.ps1
```

Keep that terminal running. In a second terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:7071/health
Invoke-RestMethod http://127.0.0.1:7071/deliveries/DEL-1002
uv run --frozen python -m scripts.check_functions
```

The last command makes real localhost HTTP calls with `BusinessClient`. It checks health,
delivery lookup, an unknown delivery, stale confirmation rejection, and repeated submission.
It creates one deliberately fictional complaint and prints the returned reference. This is
an intentional integration check, not a real business submission or an LLM evaluation.

The Uvicorn API on port 8000 and Functions on 7071 can coexist. Both use the same local SQLite
file, so their simulated records are shared. Use Ctrl+C in the Functions terminal to stop it.

## Connect the existing UI

The UI's API destination remains operator-controlled. In another PowerShell terminal:

```powershell
$env:BUSINESS_API_URL = "http://127.0.0.1:7071"
uv run --frozen streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

Open [the optional UI instance](http://127.0.0.1:8502). The separate port avoids interrupting
an existing UI on 8501. The model mode still comes from `.env`: Groq remains a separate
provider, and mock mode remains visibly simulated. Azure Functions hosts only the business
API in this version; it does not replace the LLM, embeddings, Chroma, or the agent graph.
Close that terminal when finished to discard its temporary API URL setting.

## What this demonstrates for an interview

- Python Azure Functions HTTP integration using the official local host and SDK.
- Adapting an ASGI API while preserving one implementation of business validation.
- Host/worker configuration, localhost HTTP testing, and diagnosing request failures.
- Separating local development from Azure provisioning, authentication, and deployment.

An accurate description is: “Local Azure Functions development and testing with Python,
Core Tools, and FastAPI integration; cloud deployment not performed.”

Be ready to explain an HTTP trigger, `AsgiFunctionApp`, the purpose of `host.json` and
`local.settings.json`, how the client changes endpoints, and why duplicate requests return
one complaint reference.

## Limits and troubleshooting

There is no cloud deployment, Azure OpenAI/Foundry inference, AI Search, Entra ID / managed
identity validation, Key Vault integration, or Application Insights cloud telemetry. Local
SQLite and anonymous HTTP access are demo choices, not production Functions architecture.
`.funcignore` excludes secrets and runtime data from potential packaging, but packaging and
deployment have not been validated and no deployment command is provided.

- Missing Python: run the sync command before the helper. It expects `.venv` in this repository.
- Missing `func`: install the official Core Tools v4. No paid Azure service is needed to run the host.
- Port 7071 busy: stop the prior local Functions process; do not change unrelated services.
- Host starts but HTTP fails: check the Functions terminal, confirm `pharmaops_business_api`
  was indexed, and use the root paths above without an extra `/api` prefix.
- A new trigger requiring Storage is outside this HTTP-only configuration. Such an extension
  may require an emulator such as Azurite or a separately configured Azure service.
- Keep `local.settings.json`, local host files, SQLite data, and `.env` out of Git. No cloud
  connection strings belong in the example settings.

See [Microsoft local development guidance](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
and the [official ASGI adapter API](https://learn.microsoft.com/en-us/python/api/azure-functions/azure.functions.asgifunctionapp?view=azure-python).
