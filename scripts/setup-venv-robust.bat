@echo off
echo ========================================
echo Creating Python Virtual Environment (Robust)
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

echo ERROR: Python is not found in PATH
pause
exit /b 1

:found_python
echo Found Python command: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check if virtual environment already exists
if exist "venv\" (
    echo Virtual environment already exists at: venv\
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
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

:activate
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo Installing Dependencies (Robust Method)
echo ========================================
echo.

echo Step 1: Upgrading pip, setuptools, and wheel...
call venv\Scripts\python.exe -m pip install --upgrade --no-cache-dir pip setuptools wheel

echo.
echo Step 2: Installing core build tools...
call venv\Scripts\python.exe -m pip install --no-cache-dir build packaging

echo.
echo Step 3: Installing requirements with error handling...
call venv\Scripts\python.exe -m pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo Primary installation method failed
    echo Trying alternative methods...
    echo ========================================
    echo.
    
    echo Method 2: Installing without build isolation...
    call venv\Scripts\python.exe -m pip install --no-build-isolation --no-cache-dir -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo Method 3: Installing packages individually...
        echo This will take longer but helps identify problematic packages...
        echo.
        
        REM Install packages one by one
        for /f "tokens=*" %%i in (requirements.txt) do (
            echo Installing: %%i
            call venv\Scripts\python.exe -m pip install --no-cache-dir --upgrade-strategy only-if-needed "%%i"
            if errorlevel 1 (
                echo WARNING: Failed to install: %%i
                echo Trying with --no-build-isolation...
                call venv\Scripts\python.exe -m pip install --no-build-isolation --no-cache-dir "%%i"
                if errorlevel 1 (
                    echo ERROR: Could not install: %%i
                )
            )
        )
    )
)

echo.
echo ========================================
echo Installation Summary
echo ========================================
echo.
echo Checking installed packages...
call venv\Scripts\python.exe -m pip list

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Virtual environment is now active.
echo.
echo To activate in the future:
echo   venv\Scripts\activate.bat
echo.
pause

