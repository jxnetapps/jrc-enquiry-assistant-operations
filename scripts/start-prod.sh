#!/bin/bash
# Production environment startup script for Linux/Mac

echo "Starting Web ChatBot in Production Mode..."

# Set environment
export ENVIRONMENT=production

# Start the application
python web_app.py
