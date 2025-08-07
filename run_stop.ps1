# Auto stop script (Windows PowerShell)
# Reads .server_pids file and stops server processes

if (Test-Path .server_pids) {
    $pids = Get-Content .server_pids
    foreach ($procid in $pids) {
        try {
            Stop-Process -Id $procid -Force
            Write-Host "Process $procid stopped successfully."
        } catch {
            Write-Host "Process $procid could not be stopped or was already stopped."
        }
    }
    Remove-Item .server_pids
    Write-Host "---"
    Write-Host "All server processes have been stopped."
    Write-Host "---"
} else {
    Write-Host ".server_pids file not found. Servers may not be running."
}