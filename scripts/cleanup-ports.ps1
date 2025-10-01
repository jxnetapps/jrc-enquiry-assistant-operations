# PowerShell script to clean up processes using port 8000
# Run this script if you get "address already in use" error

Write-Host "Checking for processes using port 8000..." -ForegroundColor Yellow

# Find processes using port 8000
$processes = netstat -ano | findstr :8000

if ($processes) {
    Write-Host "Found processes using port 8000:" -ForegroundColor Red
    $processes | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    
    # Extract PIDs and kill them
    $pids = $processes | ForEach-Object { 
        $parts = $_ -split '\s+'
        if ($parts.Length -gt 4) { $parts[4] }
    } | Where-Object { $_ -match '^\d+$' } | Sort-Object -Unique
    
    if ($pids) {
        Write-Host "Killing processes with PIDs: $($pids -join ', ')" -ForegroundColor Yellow
        $pids | ForEach-Object {
            try {
                Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
                Write-Host "Killed process with PID: $_" -ForegroundColor Green
            } catch {
                Write-Host "Could not kill process with PID: $_" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "No processes found using port 8000" -ForegroundColor Green
}

Write-Host "Port cleanup completed!" -ForegroundColor Green
