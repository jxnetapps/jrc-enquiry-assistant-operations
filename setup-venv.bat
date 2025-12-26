@echo off
echo ========================================
echo Creating Python Virtual Environment
echo ========================================
echo.

REM Try to find Python in different ways
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto found_python
)

REM If none found, show error and troubleshooting
echo ERROR: Python is not found in PATH
echo.
echo Troubleshooting:
echo 1. Check if Python is installed:
echo    - Open Command Prompt and try: python --version
echo    - Or try: python3 --version
echo    - Or try: py --version
echo.
echo 2. If Python is installed but not in PATH:
echo    - Add Python to PATH during installation
echo    - Or use the full path to Python executable
echo    - Example: C:\Python39\python.exe -m venv venv
echo.
echo 3. Install Python from: https://www.python.org/downloads/
echo    - Make sure to check "Add Python to PATH" during installation
echo.
echo 4. If using Python from Microsoft Store:
echo    - Try: py --version
echo    - Or: python3 --version
echo.
pause
exit /b 1

:found_python
echo Found Python command: %PYTHON_CMD%
echo Python version:
%PYTHON_CMD% --version
echo.

REM Check if virtual environment already exists
if exist "venv\" (
    echo Virtual environment already exists at: venv\
    echo.
    set /p recreate="Do you want to recreate it? (y/n): "
    if /i "%recreate%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo Using existing virtual environment.
        goto activate
    )
)

echo Creating virtual environment...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure you have Python 3.8 or higher installed
    echo.
    echo Trying alternative method...
    %PYTHON_CMD% -m virtualenv venv
    if errorlevel 1 (
        echo ERROR: Both venv and virtualenv failed
        echo Please ensure Python 3.8+ is properly installed
        pause
        exit /b 1
    )
)

echo.
echo Virtual environment created successfully!
echo.

:activate
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo Installing Dependencies
echo ========================================
echo.

echo Step 1: Upgrading pip, setuptools, and wheel...
%PYTHON_CMD% -m pip install --upgrade pip setuptools wheel

if errorlevel 1 (
    echo WARNING: Failed to upgrade pip/setuptools/wheel, continuing anyway...
)

echo.
echo Step 2: Installing core build tools...
python -m pip install --no-cache-dir build packaging

echo.
echo Step 3: Installing pydantic with pre-built wheels (Python 3.14 fix)...
python -m pip install --only-binary :all: --no-cache-dir "pydantic>=2.10.6,<3.0.0"

if errorlevel 1 (
    echo WARNING: Failed to install pydantic with pre-built wheels. Trying without --only-binary.
    python -m pip install --no-cache-dir "pydantic>=2.10.6,<3.0.0"
    if errorlevel 1 (
        echo ERROR: Failed to install pydantic. Please check your Python installation and compiler tools.
        pause
        exit /b 1
    )
)

echo.
echo Step 4: Installing essential packages (fastapi, uvicorn)...
python -m pip install --no-cache-dir --ignore-installed fastapi==0.104.1 uvicorn==0.24.0

echo.
echo Step 5: Creating temporary requirements file without pydantic and fastapi...
findstr /v /i "pydantic fastapi" requirements.txt > requirements_temp.txt 2>nul

if not exist requirements_temp.txt (
    echo WARNING: Could not create temp file, installing all remaining packages...
    python -m pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements.txt
    set INSTALL_SUCCESS=0
    if errorlevel 1 set INSTALL_SUCCESS=1
) else (
    echo Installing remaining requirements (pydantic and fastapi already installed)...
    python -m pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements_temp.txt
    set INSTALL_SUCCESS=0
    if errorlevel 1 set INSTALL_SUCCESS=1
    REM Clean up temp file
    if exist requirements_temp.txt del requirements_temp.txt 2>nul
)

if %INSTALL_SUCCESS%==1 (
    echo.
    echo ========================================
    echo Installation encountered errors
    echo ========================================
    echo.
    echo Trying alternative installation method (no build isolation)...
    echo.
    
    if exist requirements_temp.txt (
        python -m pip install --no-build-isolation --no-cache-dir -r requirements_temp.txt
    ) else (
        findstr /v /i "pydantic fastapi" requirements.txt > requirements_temp.txt 2>nul
        if exist requirements_temp.txt (
            python -m pip install --no-build-isolation --no-cache-dir -r requirements_temp.txt
        ) else (
            python -m pip install --no-build-isolation --no-cache-dir -r requirements.txt
        )
    )
    
    if errorlevel 1 (
        echo.
        echo ========================================
        echo Installation Completed with Warnings
        echo ========================================
        echo.
        echo Some packages failed to install.
        echo Essential packages (fastapi, uvicorn, pydantic) should be installed.
        echo.
        echo For packages requiring Rust (like asyncpg):
        echo - Install Rust: https://rustup.rs/
        echo - Or use Python 3.11/3.12 for better compatibility
        echo.
    ) else (
        echo.
        echo Installation completed with alternative method!
    )
    
    REM Clean up temp file
    if exist requirements_temp.txt del requirements_temp.txt 2>nul
) else (
    echo.
    echo All packages installed successfully!
    REM Clean up temp file
    if exist requirements_temp.txt del requirements_temp.txt 2>nul
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Virtual environment is now active.
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo Or use PowerShell:
echo   venv\Scripts\Activate.ps1
echo.
echo To deactivate, simply run:
echo   deactivate
echo.
echo To test your installation, run:
echo   python test_database_config.py
echo.
echo To start the application, run:
echo   python web_app.py
echo.
pause
