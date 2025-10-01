# PowerShell script to check PostgreSQL connection
# This script helps diagnose PostgreSQL connection issues

Write-Host "Checking PostgreSQL connection..." -ForegroundColor Yellow

# Check if PostgreSQL is running
$postgresProcesses = Get-Process -Name "postgres" -ErrorAction SilentlyContinue
if ($postgresProcesses) {
    Write-Host "PostgreSQL processes found:" -ForegroundColor Green
    $postgresProcesses | Format-Table ProcessName, Id, CPU -AutoSize
} else {
    Write-Host "No PostgreSQL processes found" -ForegroundColor Red
    Write-Host "Make sure PostgreSQL is installed and running" -ForegroundColor Yellow
}

# Check if port 5432 is listening
$port5432 = netstat -an | findstr :5432
if ($port5432) {
    Write-Host "Port 5432 is listening:" -ForegroundColor Green
    $port5432 | ForEach-Object { Write-Host $_ -ForegroundColor Green }
} else {
    Write-Host "Port 5432 is not listening" -ForegroundColor Red
    Write-Host "PostgreSQL may not be running or configured to listen on port 5432" -ForegroundColor Yellow
}

# Check environment variables
Write-Host "`nChecking PostgreSQL environment variables..." -ForegroundColor Yellow
$envVars = @("POSTGRESQL_CONNECTION_URI", "POSTGRESQL_DATABASE_NAME")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "$var is set" -ForegroundColor Green
    } else {
        Write-Host "$var is not set" -ForegroundColor Red
    }
}

Write-Host "`nPostgreSQL check completed!" -ForegroundColor Green
