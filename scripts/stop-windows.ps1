$ErrorActionPreference = "Stop"

$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $connections) {
  Write-Host "No process found on port 8000."
  exit 0
}

$processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($processId in $processIds) {
  Stop-Process -Id $processId -Force
}

Write-Host "Stopped processes on port 8000."
