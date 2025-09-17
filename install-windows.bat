@echo off
echo Installing Web ChatBot Enhanced for Windows...
echo.

echo Installing base requirements...
pip install -r requirements.txt

echo.
echo Checking if you want to install ChromaDB for cloud mode...
echo This requires Microsoft Visual C++ Build Tools.
echo.
set /p install_chroma="Install ChromaDB for cloud mode? (y/n): "

if /i "%install_chroma%"=="y" (
    echo.
    echo Installing ChromaDB...
    echo If this fails, you can try: pip install chromadb --no-deps
    pip install -r requirements-cloud.txt
    if errorlevel 1 (
        echo.
        echo ChromaDB installation failed. You can still use local mode.
        echo To install ChromaDB later, run: pip install chromadb --no-deps
    )
) else (
    echo.
    echo Skipping ChromaDB installation. You can install it later with:
    echo pip install -r requirements-cloud.txt
)

echo.
echo Installation complete!
echo.
echo To test your installation, run:
echo python test_database_config.py
echo.
echo To start the application, run:
echo python web_app.py
echo.
pause
