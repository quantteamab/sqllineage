#!/bin/bash
# Development server starter for SQLLineage API

set -e

echo "=== Starting SQLLineage API in Development Mode ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install parent sqllineage package in development mode
echo "Installing sqllineage from parent directory..."
pip install -q -e ..

# Create logs directory
mkdir -p logs

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env file found, using defaults..."
    cp .env.example .env
    echo "Created .env from .env.example. Please configure it."
fi

# Start the service
echo ""
echo "Starting service on port ${SERVICE_PORT:-8000}..."
echo "Swagger UI: http://localhost:${SERVICE_PORT:-8000}/docs"
echo ""

cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port ${SERVICE_PORT:-8000}
