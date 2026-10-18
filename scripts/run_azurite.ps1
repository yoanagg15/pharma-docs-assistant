# Run only local Blob Storage; do not provision or connect to an Azure account.
param([string]$NodeExecutable = 'node')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$nodeVersion = & $NodeExecutable --version
if ($LASTEXITCODE -ne 0 -or [int]($nodeVersion.TrimStart('v').Split('.')[0]) -lt 22) {
    throw 'Azurite needs Node.js 22+. Pass -NodeExecutable with the path to an existing supported Node.'
}
$azuriteScript = Join-Path $projectRoot 'tools\azurite\node_modules\azurite\dist\src\blob\main.js'
if (-not (Test-Path -LiteralPath $azuriteScript)) {
    throw 'Install the locked emulator first: pnpm --dir tools/azurite install --frozen-lockfile --ignore-scripts --store-dir ../../.pnpm-store'
}
$storageDirectory = Join-Path $projectRoot 'data\runtime\azurite'
New-Item -ItemType Directory -Force -Path $storageDirectory | Out-Null
& $NodeExecutable $azuriteScript --blobHost 127.0.0.1 --blobPort 10000 --silent --disableTelemetry --location $storageDirectory
if ($LASTEXITCODE -ne 0) { throw 'Local Azurite Blob Storage did not start successfully.' }
