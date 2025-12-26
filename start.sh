#!/bin/bash
# Main startup script for Linux/Mac - uses virtual environment

echo "========================================"
echo "Starting JRC Enquiry Assistant"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo ""
    echo "Please create the virtual environment first by running:"
    echo "  ./setup-venv.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Starting application..."
echo ""

# Start the application using venv Python
python web_app.py

