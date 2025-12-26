@echo off
echo ========================================
echo Python Installation Troubleshooter
echo ========================================
echo.

echo Checking for Python installations...
echo.

echo 1. Checking 'python' command:
python --version 2>nul
if errorlevel 1 (
    echo    [NOT FOUND] 'python' command not available
) else (
    echo    [FOUND] python command works
    python --version
)
echo.

echo 2. Checking 'python3' command:
python3 --version 2>nul
if errorlevel 1 (
    echo    [NOT FOUND] 'python3' command not available
) else (
    echo    [FOUND] python3 command works
    python3 --version
)
echo.

echo 3. Checking 'py' launcher:
py --version 2>nul
if errorlevel 1 (
    echo    [NOT FOUND] 'py' launcher not available
) else (
    echo    [FOUND] py launcher works
    py --version
)
echo.

echo 4. Checking common Python installation paths:
if exist "C:\Python39\python.exe" (
    echo    [FOUND] C:\Python39\python.exe
    C:\Python39\python.exe --version
)
if exist "C:\Python310\python.exe" (
    echo    [FOUND] C:\Python310\python.exe
    C:\Python310\python.exe --version
)
if exist "C:\Python311\python.exe" (
    echo    [FOUND] C:\Python311\python.exe
    C:\Python311\python.exe --version
)
if exist "C:\Python312\python.exe" (
    echo    [FOUND] C:\Python312\python.exe
    C:\Python312\python.exe --version
)
if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo    [FOUND] %LOCALAPPDATA%\Programs\Python\Python39\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" --version
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo    [FOUND] %LOCALAPPDATA%\Programs\Python\Python310\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" --version
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo    [FOUND] %LOCALAPPDATA%\Programs\Python\Python311\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" --version
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo    [FOUND] %LOCALAPPDATA%\Programs\Python\Python312\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" --version
)
echo.

echo 5. Checking PATH environment variable:
echo    Current PATH contains:
echo %PATH% | findstr /i "python" >nul
if errorlevel 1 (
    echo    [WARNING] No Python paths found in PATH
) else (
    echo    [OK] Python paths found in PATH
)
echo.

echo ========================================
echo Recommendations:
echo ========================================
echo.
echo If Python is installed but not found:
echo 1. Reinstall Python from https://www.python.org/downloads/
echo    - Make sure to check "Add Python to PATH" during installation
echo.
echo 2. Manually add Python to PATH:
echo    - Open System Properties ^> Environment Variables
echo    - Add Python installation directory to PATH
echo    - Add Python Scripts directory to PATH
echo.
echo 3. Use full path to Python:
echo    - Find your Python installation path
echo    - Use: "C:\Path\To\Python\python.exe" -m venv venv
echo.
echo 4. If using Microsoft Store Python:
echo    - Use: py -m venv venv
echo    - Or: python3 -m venv venv
echo.
pause

