# Start the optional Azure Functions host locally; never logs into or deploys to Azure.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Python environment missing. Run: uv sync --frozen --python 3.12'
}
if (-not (Get-Command func -ErrorAction SilentlyContinue)) {
    throw 'Install Azure Functions Core Tools v4 from the official Microsoft source, then retry.'
}
$localSettings = Join-Path $projectRoot 'local.settings.json'
if (-not (Test-Path -LiteralPath $localSettings)) {
    Copy-Item -LiteralPath (Join-Path $projectRoot 'local.settings.example.json') -Destination $localSettings
}
$previousPath = $env:PATH
$previousVirtualEnv = $env:VIRTUAL_ENV
try {
    $env:VIRTUAL_ENV = Join-Path $projectRoot '.venv'
    $env:PATH = (Join-Path $projectRoot '.venv\Scripts') + [IO.Path]::PathSeparator + $previousPath
    & func start --address 127.0.0.1 --port 7071
    if ($LASTEXITCODE -ne 0) { throw 'Azure Functions local host did not start successfully.' }
}
finally {
    $env:PATH = $previousPath
    $env:VIRTUAL_ENV = $previousVirtualEnv
}
