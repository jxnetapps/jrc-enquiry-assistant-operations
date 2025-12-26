@echo off
echo Starting JRC Enquiry Assistant in SQLite Mode...
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
    echo Installing packages... This may take a few minutes.
    echo.
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install --only-binary :all: --no-cache-dir "pydantic>=2.10.6,<3.0.0"
    python -m pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install packages
        echo Please run setup-venv.bat to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Packages installed successfully!
    echo.
)

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

REM Start the application using venv Python directly (more reliable)
echo Starting application...
venv\Scripts\python.exe web_app.py

pause
