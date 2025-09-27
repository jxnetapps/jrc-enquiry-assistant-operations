#!/bin/bash
# Staging environment startup script for Linux/Mac

echo "Starting Web ChatBot in Staging Mode..."

# Set environment
export ENVIRONMENT=staging

# Start the application
python web_app.py
