# Force SQLite Mode Script
# This script configures the application to use SQLite instead of PostgreSQL

Write-Host "=== Forcing SQLite Mode ===" -ForegroundColor Green
Write-Host ""

# Set environment variables to force SQLite
Write-Host "Setting environment variables..." -ForegroundColor Yellow

# Force SQLite for answer storage
$env:ANSWER_STORAGE_TYPE = "sqlite"
Write-Host "+ ANSWER_STORAGE_TYPE set to sqlite" -ForegroundColor Green

# Disable PostgreSQL by setting invalid connection
$env:POSTGRESQL_CONNECTION_URI = "postgresql://invalid:invalid@localhost:5432/invalid"
Write-Host "+ PostgreSQL connection disabled" -ForegroundColor Green

# Set required environment variables for SQLite mode
if (-not $env:JWT_SECRET_KEY) {
    $env:JWT_SECRET_KEY = "your-secret-key-here"
    Write-Host "+ JWT_SECRET_KEY set (default)" -ForegroundColor Yellow
}

if (-not $env:ADMIN_USERNAME) {
    $env:ADMIN_USERNAME = "admin"
    Write-Host "+ ADMIN_USERNAME set to admin" -ForegroundColor Yellow
}

if (-not $env:ADMIN_PASSWORD) {
    $env:ADMIN_PASSWORD = "admin123"
    Write-Host "+ ADMIN_PASSWORD set to admin123" -ForegroundColor Yellow
}

# Create .env file for persistence
Write-Host "`nCreating .env file..." -ForegroundColor Yellow
$envContent = @"
# SQLite Configuration
ANSWER_STORAGE_TYPE=sqlite

# Disable PostgreSQL
POSTGRESQL_CONNECTION_URI=postgresql://invalid:invalid@localhost:5432/invalid
POSTGRESQL_DATABASE_NAME=invalid

# Required settings
JWT_SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Environment
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "+ .env file created" -ForegroundColor Green

# Check if SQLite databases exist
Write-Host "`nChecking SQLite databases..." -ForegroundColor Yellow

$databases = @(
    "database/users.db",
    "database/chat_inquiries.db", 
    "database/collected_answers.db"
)

foreach ($db in $databases) {
    if (Test-Path $db) {
        Write-Host "+ $db exists" -ForegroundColor Green
    } else {
        Write-Host "- $db missing (will be created on first run)" -ForegroundColor Yellow
    }
}

Write-Host "`n=== SQLite Mode Configuration Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "The application is now configured to use SQLite only." -ForegroundColor White
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  python web_app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or use the startup script:" -ForegroundColor Cyan
Write-Host "  python start-app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "The application will:" -ForegroundColor White
Write-Host "  - Skip PostgreSQL connection attempts" -ForegroundColor White
Write-Host "  - Use SQLite databases in the database/ folder" -ForegroundColor White
Write-Host "  - Create missing databases automatically" -ForegroundColor White
