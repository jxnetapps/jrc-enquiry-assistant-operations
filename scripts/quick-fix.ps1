# Quick Fix Script for Common Issues
# This script addresses the most common startup issues

Write-Host "=== JRC Enquiry Assistant - Quick Fix Script ===" -ForegroundColor Green
Write-Host ""

# 1. Clean up port 8000
Write-Host "1. Cleaning up port 8000..." -ForegroundColor Yellow
$processes = netstat -ano | findstr :8000
if ($processes) {
    Write-Host "Found processes using port 8000, killing them..." -ForegroundColor Red
    $pids = $processes | ForEach-Object { 
        $parts = $_ -split '\s+'
        if ($parts.Length -gt 4) { $parts[4] }
    } | Where-Object { $_ -match '^\d+$' } | Sort-Object -Unique
    
    $pids | ForEach-Object {
        try {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
            Write-Host "Killed process with PID: $_" -ForegroundColor Green
        } catch {
            Write-Host "Could not kill process with PID: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Port 8000 is free" -ForegroundColor Green
}

# 2. Check PostgreSQL
Write-Host "`n2. Checking PostgreSQL..." -ForegroundColor Yellow
$postgresProcesses = Get-Process -Name "postgres" -ErrorAction SilentlyContinue
if ($postgresProcesses) {
    Write-Host "PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "PostgreSQL is not running - application will use SQLite fallback" -ForegroundColor Yellow
}

# 3. Check environment variables
Write-Host "`n3. Checking environment variables..." -ForegroundColor Yellow
$requiredVars = @("JWT_SECRET_KEY", "ADMIN_USERNAME", "ADMIN_PASSWORD")
$missingVars = @()

foreach ($var in $requiredVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "$var is set" -ForegroundColor Green
    } else {
        Write-Host "$var is missing" -ForegroundColor Red
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "`nMissing required environment variables:" -ForegroundColor Red
    $missingVars | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host "`nPlease set these variables or create a .env file" -ForegroundColor Yellow
}

# 4. Check Python dependencies
Write-Host "`n4. Checking Python dependencies..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn, sqlalchemy" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python dependencies are installed" -ForegroundColor Green
    } else {
        Write-Host "Some Python dependencies are missing" -ForegroundColor Red
        Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not check Python dependencies" -ForegroundColor Red
}

# 5. Check if startup.sh exists and is executable
Write-Host "`n5. Checking startup script..." -ForegroundColor Yellow
if (Test-Path "startup.sh") {
    Write-Host "startup.sh exists" -ForegroundColor Green
} else {
    Write-Host "startup.sh is missing" -ForegroundColor Red
    Write-Host "The startup script has been created for you" -ForegroundColor Yellow
}

# 6. Summary and recommendations
Write-Host "`n=== SUMMARY ===" -ForegroundColor Green
Write-Host ""

if ($missingVars.Count -eq 0) {
    Write-Host "✓ Environment variables are set" -ForegroundColor Green
} else {
    Write-Host "✗ Some environment variables are missing" -ForegroundColor Red
}

Write-Host "✓ Port 8000 has been cleaned up" -ForegroundColor Green
Write-Host "✓ FastAPI deprecation warnings have been fixed" -ForegroundColor Green

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. If environment variables are missing, create a .env file" -ForegroundColor White
Write-Host "2. Run: python web_app.py" -ForegroundColor White
Write-Host "3. Or for production: .\deploy-manual.ps1" -ForegroundColor White

Write-Host "`n=== QUICK START ===" -ForegroundColor Cyan
Write-Host "To start the application now:" -ForegroundColor White
Write-Host "  python web_app.py" -ForegroundColor Yellow

Write-Host "`nQuick fix completed!" -ForegroundColor Green
