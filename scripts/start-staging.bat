@echo off
REM Staging environment startup script for Windows

echo Starting Web ChatBot in Staging Mode...

REM Set environment
set ENVIRONMENT=staging

REM Start the application
python web_app.py

pause
