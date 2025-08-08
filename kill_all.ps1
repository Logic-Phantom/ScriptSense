# ScriptSense Server Shutdown Script
# Terminate all Python and Node.js processes

Write-Host "[SHUTDOWN] ScriptSense server shutdown in progress..." -ForegroundColor Yellow

# Terminate Python processes
Write-Host "[PYTHON] Terminating Python processes..." -ForegroundColor Cyan
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    foreach ($process in $pythonProcesses) {
        Write-Host "  - Terminating Python process: PID $($process.Id)" -ForegroundColor Gray
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Write-Host "    SUCCESS: Process $($process.Id) terminated" -ForegroundColor Green
        } catch {
            Write-Host "    WARNING: Could not terminate process $($process.Id)" -ForegroundColor Yellow
        }
    }
    Write-Host "[SUCCESS] Python process termination completed" -ForegroundColor Green
} else {
    Write-Host "[INFO] No running Python processes found" -ForegroundColor Blue
}

# Terminate Node.js processes
Write-Host "[NODEJS] Terminating Node.js processes..." -ForegroundColor Cyan
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    foreach ($process in $nodeProcesses) {
        Write-Host "  - Terminating Node.js process: PID $($process.Id)" -ForegroundColor Gray
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Write-Host "    SUCCESS: Process $($process.Id) terminated" -ForegroundColor Green
        } catch {
            Write-Host "    WARNING: Could not terminate process $($process.Id) - may already be closed" -ForegroundColor Yellow
        }
    }
    Write-Host "[SUCCESS] Node.js process termination completed" -ForegroundColor Green
} else {
    Write-Host "[INFO] No running Node.js processes found" -ForegroundColor Blue
}

# Check for uvicorn processes
Write-Host "[UVICORN] Checking for uvicorn processes..." -ForegroundColor Cyan
$uvicornProcesses = Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue
if ($uvicornProcesses) {
    foreach ($process in $uvicornProcesses) {
        Write-Host "  - Terminating uvicorn process: PID $($process.Id)" -ForegroundColor Gray
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Write-Host "    SUCCESS: Process $($process.Id) terminated" -ForegroundColor Green
        } catch {
            Write-Host "    WARNING: Could not terminate process $($process.Id)" -ForegroundColor Yellow
        }
    }
    Write-Host "[SUCCESS] uvicorn process termination completed" -ForegroundColor Green
} else {
    Write-Host "[INFO] No running uvicorn processes found" -ForegroundColor Blue
}

# Check for FastAPI processes
Write-Host "[FASTAPI] Checking for FastAPI processes..." -ForegroundColor Cyan
try {
    $fastApiProcesses = Get-WmiObject Win32_Process | Where-Object { 
        $_.CommandLine -like "*fastapi*" -or $_.CommandLine -like "*uvicorn*" 
    }
    if ($fastApiProcesses) {
        foreach ($process in $fastApiProcesses) {
            Write-Host "  - Terminating FastAPI process: PID $($process.ProcessId)" -ForegroundColor Gray
            try {
                Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
                Write-Host "    SUCCESS: Process $($process.ProcessId) terminated" -ForegroundColor Green
            } catch {
                Write-Host "    WARNING: Could not terminate process $($process.ProcessId)" -ForegroundColor Yellow
            }
        }
        Write-Host "[SUCCESS] FastAPI process termination completed" -ForegroundColor Green
    } else {
        Write-Host "[INFO] No FastAPI processes found" -ForegroundColor Blue
    }
} catch {
    Write-Host "[WARNING] Could not check for FastAPI processes: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check for specific port usage (8000, 3000)
Write-Host "[PORTS] Checking for processes using ports 8000 and 3000..." -ForegroundColor Cyan
try {
    $portsChecked = 0
    
    # Check port 8000
    $port8000Output = netstat -ano | Select-String ":8000"
    if ($port8000Output) {
        foreach ($line in $port8000Output) {
            $lineString = $line.ToString()
            $parts = $lineString -split '\s+'
            $pid = $parts[-1]
            if ($pid -and $pid -match '^\d+$') {
                Write-Host "  - Found process on port 8000: PID $pid" -ForegroundColor Gray
                try {
                    Stop-Process -Id $pid -Force -ErrorAction Stop
                    Write-Host "    SUCCESS: Process $pid terminated" -ForegroundColor Green
                    $portsChecked++
                } catch {
                    Write-Host "    WARNING: Could not terminate process $pid" -ForegroundColor Yellow
                }
            }
        }
    }
    
    # Check port 3000
    $port3000Output = netstat -ano | Select-String ":3000"
    if ($port3000Output) {
        foreach ($line in $port3000Output) {
            $lineString = $line.ToString()
            $parts = $lineString -split '\s+'
            $pid = $parts[-1]
            if ($pid -and $pid -match '^\d+$') {
                Write-Host "  - Found process on port 3000: PID $pid" -ForegroundColor Gray
                try {
                    Stop-Process -Id $pid -Force -ErrorAction Stop
                    Write-Host "    SUCCESS: Process $pid terminated" -ForegroundColor Green
                    $portsChecked++
                } catch {
                    Write-Host "    WARNING: Could not terminate process $pid" -ForegroundColor Yellow
                }
            }
        }
    }
    
    if ($portsChecked -eq 0) {
        Write-Host "[INFO] No processes found on ports 8000 or 3000" -ForegroundColor Blue
    } else {
        Write-Host "[SUCCESS] Port cleanup completed ($portsChecked processes)" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not check port usage: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[COMPLETE] All ScriptSense servers have been terminated!" -ForegroundColor Green
Write-Host "[INFO] To restart servers, run 'run_all.ps1'" -ForegroundColor Yellow

# Wait briefly for user to see results
Start-Sleep -Seconds 1

# Optional: Clear any remaining cache or temp files
Write-Host ""
Write-Host "[CLEANUP] Cleaning up temporary files..." -ForegroundColor Cyan
$cleanupCount = 0

try {
    # Remove Python cache files
    if (Test-Path "__pycache__") {
        Remove-Item -Recurse -Force "__pycache__" -ErrorAction SilentlyContinue
        Write-Host "  - Removed Python cache files" -ForegroundColor Gray
        $cleanupCount++
    }
    
    # Remove Node.js cache files  
    if (Test-Path "node_modules\.cache") {
        Remove-Item -Recurse -Force "node_modules\.cache" -ErrorAction SilentlyContinue
        Write-Host "  - Removed Node.js cache files" -ForegroundColor Gray
        $cleanupCount++
    }
    
    # Remove temporary log files
    $logFiles = Get-ChildItem -Path "." -Filter "*.log" -ErrorAction SilentlyContinue
    if ($logFiles) {
        $logFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  - Removed $($logFiles.Count) log files" -ForegroundColor Gray
        $cleanupCount++
    }
    
    if ($cleanupCount -gt 0) {
        Write-Host "[SUCCESS] Cleanup completed ($cleanupCount operations)" -ForegroundColor Green
    } else {
        Write-Host "[INFO] No temporary files to clean" -ForegroundColor Blue
    }
} catch {
    Write-Host "[WARNING] Some cleanup operations failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[DONE] Script execution completed successfully!" -ForegroundColor Magenta
Write-Host "======================================================" -ForegroundColor White