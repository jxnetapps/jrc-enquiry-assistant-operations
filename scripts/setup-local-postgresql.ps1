# Setup Local PostgreSQL Script
# This script helps you set up a local PostgreSQL instance

Write-Host "=== Local PostgreSQL Setup ===" -ForegroundColor Green
Write-Host ""

Write-Host "This script will help you set up a local PostgreSQL instance." -ForegroundColor Yellow
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "1. Checking if PostgreSQL is installed..." -ForegroundColor Yellow
$postgresService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue

if ($postgresService) {
    Write-Host "+ PostgreSQL service found: $($postgresService.Name)" -ForegroundColor Green
    
    # Check if service is running
    if ($postgresService.Status -eq "Running") {
        Write-Host "+ PostgreSQL service is running" -ForegroundColor Green
    } else {
        Write-Host "- PostgreSQL service is not running. Starting..." -ForegroundColor Yellow
        Start-Service -Name $postgresService.Name
        Write-Host "+ PostgreSQL service started" -ForegroundColor Green
    }
} else {
    Write-Host "- PostgreSQL is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install PostgreSQL:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "  2. Run the installer" -ForegroundColor White
    Write-Host "  3. Set password for 'postgres' user" -ForegroundColor White
    Write-Host "  4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "For now, use SQLite mode:" -ForegroundColor Cyan
    Write-Host "  .\scripts\start-sqlite-only.ps1" -ForegroundColor Yellow
    exit 1
}

# Test local connection
Write-Host "`n2. Testing local PostgreSQL connection..." -ForegroundColor Yellow
try {
    python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:password@localhost:5432/postgres')
cursor = conn.cursor()
cursor.execute('SELECT 1')
conn.close()
print('+ Local PostgreSQL connection successful')
"
    Write-Host "+ Local PostgreSQL is working" -ForegroundColor Green
} catch {
    Write-Host "- Local PostgreSQL connection failed" -ForegroundColor Red
    Write-Host "  You may need to set the correct password" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For now, use SQLite mode:" -ForegroundColor Cyan
    Write-Host "  .\scripts\start-sqlite-only.ps1" -ForegroundColor Yellow
    exit 1
}

# Create application database
Write-Host "`n3. Creating application database..." -ForegroundColor Yellow
try {
    python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:password@localhost:5432/postgres')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE DATABASE jrc_chatbot_assistant_dev')
conn.close()
print('+ Database created successfully')
"
    Write-Host "+ Application database created" -ForegroundColor Green
} catch {
    Write-Host "- Database creation failed (may already exist)" -ForegroundColor Yellow
}

# Update configuration
Write-Host "`n4. Updating configuration..." -ForegroundColor Yellow
$envContent = @"
# Local PostgreSQL Configuration
ANSWER_STORAGE_TYPE=auto
POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@localhost:5432/jrc_chatbot_assistant_dev
POSTGRESQL_DATABASE_NAME=jrc_chatbot_assistant_dev

# Required settings
JWT_SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Environment
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
"@

$envContent | Out-File -FilePath ".env.local" -Encoding UTF8
Write-Host "+ Configuration saved to .env.local" -ForegroundColor Green

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "To use local PostgreSQL:" -ForegroundColor Cyan
Write-Host "  Copy .env.local to .env" -ForegroundColor White
Write-Host "  python web_app.py" -ForegroundColor White
Write-Host ""
Write-Host "Or continue using SQLite mode:" -ForegroundColor Cyan
Write-Host "  .\scripts\start-sqlite-only.ps1" -ForegroundColor White

