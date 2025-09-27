@echo off
REM Production environment startup script for Windows

echo Starting Web ChatBot in Production Mode...

REM Set environment
set ENVIRONMENT=production

REM Start the application
python web_app.py

pause
