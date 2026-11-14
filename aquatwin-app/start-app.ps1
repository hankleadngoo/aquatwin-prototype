$ErrorActionPreference = 'Stop'
$appRoot = $PSScriptRoot
$staticRoot = Join-Path $appRoot 'dist'
$runtimeRoot = Join-Path $appRoot '.runtime'
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$appUrl = 'http://127.0.0.1:8765/'
$alreadyRunning = $false
try {
    $page = Invoke-WebRequest -Uri $appUrl -UseBasicParsing -TimeoutSec 2
    $alreadyRunning = $page.Content -match 'AquaTwin'
    if ($alreadyRunning) {
        try {
            $health = Invoke-RestMethod -Uri ($appUrl + 'api/health') -TimeoutSec 2
            $alreadyRunning = $health.bridgeVersion -eq '1.1.0'
        } catch { $alreadyRunning = $false }
        if (-not $alreadyRunning) { throw 'Port 8765 is used by another application. Stop the previous AquaTwin server before restarting.' }
    }
    if (-not $alreadyRunning) { throw 'Port 8765 is used by another application.' }
} catch {
    if ($_.Exception.Message -match 'another application') { throw }
}
if (-not $alreadyRunning) {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
    $appProcess = Start-Process -FilePath $pythonExe -ArgumentList @(('"' + (Join-Path $appRoot 'server.py') + '"'),'--port','8765') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimeRoot 'server.log') -RedirectStandardError (Join-Path $runtimeRoot 'server-error.log')
    $appProcess.Id | Set-Content -LiteralPath (Join-Path $runtimeRoot 'server.pid')
    for ($attempt = 0; $attempt -lt 25; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $appUrl -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { break }
        } catch { Start-Sleep -Milliseconds 200 }
    }
}
Start-Process $appUrl
Write-Output ('AquaTwin: ' + $appUrl)
