#!/bin/bash

echo "========================================"
echo "Creating Python Virtual Environment"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists at: venv/"
    echo ""
    read -p "Do you want to recreate it? (y/n): " recreate
    if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
        source venv/bin/activate
        echo ""
        echo "Virtual environment activated!"
        echo ""
        echo "To activate in the future, run:"
        echo "  source venv/bin/activate"
        echo ""
        exit 0
    fi
fi

echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    echo "Make sure you have Python 3.8 or higher installed"
    exit 1
fi

echo ""
echo "Virtual environment created successfully!"
echo ""

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "========================================"
echo "Installing Dependencies"
echo "========================================"
echo ""

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "Installing base requirements..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Some packages failed to install"
    echo "You may need to install them manually"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Virtual environment is now active."
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate, simply run:"
echo "  deactivate"
echo ""
echo "To test your installation, run:"
echo "  python test_database_config.py"
echo ""
echo "To start the application, run:"
echo "  python web_app.py"
echo ""

