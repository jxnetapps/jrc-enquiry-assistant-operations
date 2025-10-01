#!/bin/bash

# Startup script for Azure App Service
echo "Starting JRC Enquiry Assistant Operations..."

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Check if we're in production mode
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
    # Run migrations if needed
    python -m scripts.migrate
else
    echo "Running in development mode"
fi

# Start the application
echo "Starting FastAPI application on port $WEBSITES_PORT"
uvicorn web_app:app --host 0.0.0.0 --port $WEBSITES_PORT --workers 1
