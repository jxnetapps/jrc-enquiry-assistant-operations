@echo off
echo Starting JRC Enquiry Assistant in SQLite Mode...
echo.

REM Set environment variables for SQLite mode
set ANSWER_STORAGE_TYPE=sqlite
set POSTGRESQL_CONNECTION_URI=postgresql://invalid:invalid@localhost:5432/invalid
set POSTGRESQL_DATABASE_NAME=invalid

REM Set required environment variables
if not defined JWT_SECRET_KEY set JWT_SECRET_KEY=your-secret-key-here-change-in-production
if not defined ADMIN_USERNAME set ADMIN_USERNAME=admin
if not defined ADMIN_PASSWORD set ADMIN_PASSWORD=admin123

echo Environment configured for SQLite mode
echo.

REM Start the application
python web_app.py

pause
