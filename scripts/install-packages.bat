@echo off
REM Quick package installation script for virtual environment

echo ========================================
echo Installing Required Packages
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run setup-venv.bat first
    pause
    exit /b 1
)

echo Using virtual environment Python...
echo.

REM Upgrade pip, setuptools, wheel
echo Step 1: Upgrading pip, setuptools, wheel...
venv\Scripts\python.exe -m pip install --upgrade --no-cache-dir pip setuptools wheel build packaging

echo.
echo Step 2: Installing pydantic with pre-built wheels (Python 3.14 fix)...
venv\Scripts\python.exe -m pip install --only-binary :all: --no-cache-dir "pydantic>=2.10.6,<3.0.0"

if errorlevel 1 (
    echo WARNING: Failed to install pydantic with pre-built wheels
    echo Trying without --only-binary...
    venv\Scripts\python.exe -m pip install --no-cache-dir "pydantic>=2.10.6,<3.0.0"
)

echo.
echo Step 3: Installing essential packages first...
venv\Scripts\python.exe -m pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0

echo.
echo Step 4: Creating temporary requirements without pydantic and fastapi...
findstr /v /i "pydantic fastapi" requirements.txt > requirements_temp.txt 2>nul

if not exist requirements_temp.txt (
    echo WARNING: Could not create temp file, installing remaining packages...
    set USE_TEMP=0
) else (
    set USE_TEMP=1
)

echo.
echo Step 5: Installing remaining packages from requirements.txt...
echo This may take several minutes...
echo Note: Some packages may fail on Python 3.14 (like asyncpg, psycopg2-binary)
echo.

if "%USE_TEMP%"=="1" (
    venv\Scripts\python.exe -m pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements_temp.txt
) else (
    venv\Scripts\python.exe -m pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements.txt
)

set INSTALL_RESULT=%errorlevel%

if %INSTALL_RESULT% neq 0 (
    echo.
    echo Some packages failed. Trying alternative method (no build isolation)...
    if "%USE_TEMP%"=="1" (
        venv\Scripts\python.exe -m pip install --no-build-isolation --no-cache-dir -r requirements_temp.txt
    ) else (
        venv\Scripts\python.exe -m pip install --no-build-isolation --no-cache-dir -r requirements.txt
    )
)

REM Clean up
if exist requirements_temp.txt del requirements_temp.txt 2>nul

echo.
echo ========================================
echo Installation Summary
echo ========================================
echo.
echo Checking installed packages...
venv\Scripts\python.exe -m pip list | findstr /i "fastapi uvicorn pinecone pydantic"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo If some packages failed to install, you may need to:
echo 1. Install Rust for packages that require compilation
echo 2. Use Python 3.11 or 3.12 for better compatibility
echo 3. Install problematic packages individually
echo.
pause

