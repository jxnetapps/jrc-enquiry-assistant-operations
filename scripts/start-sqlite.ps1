# Start JRC Enquiry Assistant in SQLite Mode
Write-Host "Starting JRC Enquiry Assistant in SQLite Mode..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create the virtual environment first by running:" -ForegroundColor Yellow
    Write-Host "  setup-venv.bat" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Set environment variables for SQLite mode
$env:ANSWER_STORAGE_TYPE = "sqlite"
$env:POSTGRESQL_CONNECTION_URI = "postgresql://invalid:invalid@localhost:5432/invalid"
$env:POSTGRESQL_DATABASE_NAME = "invalid"

# Set required environment variables
if (-not $env:JWT_SECRET_KEY) {
    $env:JWT_SECRET_KEY = "your-secret-key-here-change-in-production"
}
if (-not $env:ADMIN_USERNAME) {
    $env:ADMIN_USERNAME = "admin"
}
if (-not $env:ADMIN_PASSWORD) {
    $env:ADMIN_PASSWORD = "admin123"
}

Write-Host "Environment configured for SQLite mode" -ForegroundColor Yellow
Write-Host ""

# Start the application using venv Python
Write-Host "Starting application..." -ForegroundColor Cyan
python web_app.py
