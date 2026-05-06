#!/bin/bash
# Run tests with coverage

set -e

echo "🧪 Running AI Job Bot Test Suite..."

cd backend

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements-dev.txt -q

# Run pytest with coverage
echo "🔍 Running tests..."
pytest tests/ -v --cov=app --cov-report=term --cov-report=html

echo "
✅ Tests complete!

Coverage report: backend/htmlcov/index.html
"

# Open coverage report in browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open htmlcov/index.html
fi
