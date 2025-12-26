# Start JRC Enquiry Assistant in SQLite Mode
Write-Host "Starting JRC Enquiry Assistant in SQLite Mode..." -ForegroundColor Green
Write-Host ""

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

# Start the application
Write-Host "Starting application..." -ForegroundColor Cyan
python web_app.py
