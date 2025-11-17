#!/bin/bash
# Test runner script for SQLLineage API

set -e

echo "=== SQLLineage API Test Suite ==="
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

# Run tests
echo ""
echo "=== Running Tests ==="
echo ""

# Run unit tests
echo "Running unit tests..."
pytest tests/test_api.py -v

# Run integration tests
echo ""
echo "Running integration tests..."
pytest tests/test_integration.py -v

# Generate coverage report
echo ""
echo "Generating coverage report..."
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "=== Tests Complete ==="
echo "Coverage report: htmlcov/index.html"
