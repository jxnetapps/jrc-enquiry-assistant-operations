@echo off
REM Main startup script for Windows - uses virtual environment

echo ========================================
echo Starting JRC Enquiry Assistant
echo ========================================
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
    echo WARNING: Required packages not found in virtual environment!
    echo.
    echo Please install packages by running:
    echo   scripts\install-packages.bat
    echo.
    echo Or run the full setup:
    echo   setup-venv.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Starting application...
echo.

REM Start the application using venv Python directly (more reliable)
venv\Scripts\python.exe web_app.py

pause

