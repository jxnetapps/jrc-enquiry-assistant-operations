#!/bin/bash

# Azure App Service Startup Script
# This script is used to start the application on Azure App Service

set -e  # Exit on any error

echo "Starting Web ChatBot Enhanced API on Azure App Service..."
echo "Timestamp: $(date)"

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
export WEBSITES_PORT=8000
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export ENVIRONMENT=production
export DEBUG=false

# Change to the application directory
cd /home/site/wwwroot

echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment: $ENVIRONMENT"
echo "Debug mode: $DEBUG"
echo "Python path: $PYTHONPATH"

# Create necessary directories
mkdir -p /home/site/wwwroot/chroma_db
mkdir -p /home/site/wwwroot/logs
mkdir -p /home/site/wwwroot/database

# Wait a moment to ensure all files are available
sleep 3

# List directory contents for debugging
echo "Directory contents:"
ls -la

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install --no-cache-dir --upgrade pip
    pip install --no-cache-dir -r requirements.txt
else
    echo "requirements.txt not found, skipping dependency installation"
fi

# Install Azure-specific dependencies if requirements-azure.txt exists
if [ -f "requirements-azure.txt" ]; then
    echo "Installing Azure-specific dependencies..."
    pip install --no-cache-dir -r requirements-azure.txt
else
    echo "requirements-azure.txt not found, skipping Azure-specific dependencies"
fi

# Set proper permissions
chmod +x /home/site/wwwroot/web_app.py

# Verify the application file exists
if [ ! -f "web_app.py" ]; then
    echo "Error: web_app.py not found!"
    echo "Contents of current directory:"
    ls -la
    echo "Looking for Python files:"
    find . -name "*.py" -type f
    exit 1
fi

# Check if the application can be imported
echo "Testing application import..."
python -c "import web_app; print('Application import successful')" || {
    echo "Error: Application import failed"
    exit 1
}

# Start the application
echo "Starting FastAPI application..."
echo "Using command: python web_app.py"
exec python web_app.py
