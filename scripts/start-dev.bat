@echo off
REM Development environment startup script for Windows

echo Starting Web ChatBot in Development Mode...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please create the virtual environment first by running:
    echo   setup-venv.bat
    echo.
    pause
    exit /b 1
)

REM Check if packages are installed
echo Checking virtual environment...
venv\Scripts\python.exe -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Required packages not found!
    echo Please run setup-venv.bat first to install dependencies
    pause
    exit /b 1
)

REM Set environment
set ENVIRONMENT=development

echo.
echo Starting application...
REM Start the application using venv Python directly (more reliable)
venv\Scripts\python.exe web_app.py

pause
