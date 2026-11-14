$pidFile = Join-Path $PSScriptRoot '.runtime\server.pid'
if (Test-Path -LiteralPath $pidFile) {
    $appPid = [int](Get-Content -LiteralPath $pidFile)
    $processInfo = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $appPid) -ErrorAction SilentlyContinue
    $expectedDirectory = $PSScriptRoot
    if ($processInfo -and $processInfo.CommandLine.Contains($expectedDirectory) -and ($processInfo.CommandLine.Contains('http.server') -or $processInfo.CommandLine.Contains('server.py'))) {
        Stop-Process -Id $appPid
        Write-Output 'AquaTwin server stopped.'
    } else {
        Write-Output 'No matching AquaTwin server; no process stopped.'
    }
}
