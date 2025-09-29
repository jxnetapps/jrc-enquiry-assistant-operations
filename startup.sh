#!/bin/bash

# Azure App Service Startup Script
# This script is used to start the application on Azure App Service

set -e  # Exit on any error

echo "Starting Web ChatBot Enhanced API on Azure App Service..."

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

# Create necessary directories
mkdir -p /home/site/wwwroot/chroma_db
mkdir -p /home/site/wwwroot/logs

# Wait a moment to ensure all files are available
sleep 2

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install --no-cache-dir --upgrade pip
    pip install --no-cache-dir -r requirements.txt
fi

# Install Azure-specific dependencies if requirements-azure.txt exists
if [ -f "requirements-azure.txt" ]; then
    echo "Installing Azure-specific dependencies..."
    pip install --no-cache-dir -r requirements-azure.txt
fi

# Set proper permissions
chmod +x /home/site/wwwroot/web_app.py

# Verify the application file exists
if [ ! -f "web_app.py" ]; then
    echo "Error: web_app.py not found!"
    echo "Contents of current directory:"
    ls -la
    exit 1
fi

# Start the application
echo "Starting FastAPI application..."
exec python web_app.py
