#!/bin/bash
# Development environment startup script for Linux/Mac

echo "Starting Web ChatBot in Development Mode..."
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

# Set environment
export ENVIRONMENT=development

echo ""
echo "Starting application..."
# Start the application using venv Python
python web_app.py
