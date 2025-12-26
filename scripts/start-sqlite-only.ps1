# Start Application in SQLite-Only Mode
# This completely bypasses PostgreSQL and uses only SQLite

Write-Host "=== Starting JRC Enquiry Assistant in SQLite-Only Mode ===" -ForegroundColor Green
Write-Host ""

# Set environment variables to force SQLite and disable PostgreSQL
$env:ANSWER_STORAGE_TYPE = "sqlite"
$env:POSTGRESQL_CONNECTION_URI = "postgresql://disabled:disabled@localhost:5432/disabled"
$env:POSTGRESQL_DATABASE_NAME = "disabled"

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

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - Database: SQLite only" -ForegroundColor White
Write-Host "  - PostgreSQL: Disabled" -ForegroundColor White
Write-Host "  - Mode: Development" -ForegroundColor White
Write-Host ""

Write-Host "Starting application..." -ForegroundColor Cyan
python web_app.py

