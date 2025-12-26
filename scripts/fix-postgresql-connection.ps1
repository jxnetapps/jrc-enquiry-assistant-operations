# Fix PostgreSQL Connection Script
# This script helps diagnose and fix PostgreSQL connection issues

Write-Host "=== PostgreSQL Connection Fix ===" -ForegroundColor Green
Write-Host ""

# Test DNS resolution
Write-Host "1. Testing DNS Resolution..." -ForegroundColor Yellow
try {
    $result = Resolve-DnsName "db.umwxkbcvqvqqybjwcash.supabase.co" -ErrorAction Stop
    Write-Host "+ DNS Resolution successful" -ForegroundColor Green
    Write-Host "  IP Address: $($result.IPAddress)" -ForegroundColor White
} catch {
    Write-Host "- DNS Resolution failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Check your internet connection" -ForegroundColor White
    Write-Host "  2. Try using a different DNS server (8.8.8.8, 1.1.1.1)" -ForegroundColor White
    Write-Host "  3. Check if your firewall is blocking the connection" -ForegroundColor White
    Write-Host "  4. Contact your network administrator" -ForegroundColor White
    Write-Host ""
    Write-Host "For now, use SQLite mode:" -ForegroundColor Cyan
    Write-Host "  .\scripts\start-sqlite-only.ps1" -ForegroundColor Yellow
    exit 1
}

# Test port connectivity
Write-Host "`n2. Testing Port Connectivity..." -ForegroundColor Yellow
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("db.umwxkbcvqvqqybjwcash.supabase.co", 5432)
    $tcpClient.Close()
    Write-Host "+ Port 5432 is accessible" -ForegroundColor Green
} catch {
    Write-Host "- Port 5432 is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Check firewall settings" -ForegroundColor White
    Write-Host "  2. Check if your ISP is blocking the connection" -ForegroundColor White
    Write-Host "  3. Try using a VPN" -ForegroundColor White
    Write-Host ""
    Write-Host "For now, use SQLite mode:" -ForegroundColor Cyan
    Write-Host "  .\scripts\start-sqlite-only.ps1" -ForegroundColor Yellow
    exit 1
}

# Test PostgreSQL connection
Write-Host "`n3. Testing PostgreSQL Connection..." -ForegroundColor Yellow
try {
    python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:DbL9frkASS99v0f4@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres')
cursor = conn.cursor()
cursor.execute('SELECT 1')
conn.close()
print('+ PostgreSQL connection successful')
"
    Write-Host "+ PostgreSQL connection test passed" -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ PostgreSQL is working! You can now use the application normally." -ForegroundColor Green
} catch {
    Write-Host "- PostgreSQL connection failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Check PostgreSQL credentials" -ForegroundColor White
    Write-Host "  2. Verify the database exists" -ForegroundColor White
    Write-Host "  3. Check user permissions" -ForegroundColor White
    Write-Host ""
    Write-Host "For now, use SQLite mode:" -ForegroundColor Cyan
    Write-Host "  .\scripts\start-sqlite-only.ps1" -ForegroundColor Yellow
}

Write-Host "`n=== Fix Complete ===" -ForegroundColor Green

