#!/bin/bash
# CI/CD Test Runner for Pre-Analyzer Unified Parser
# This script runs the complete test suite with proper error handling

set -e  # Exit on any error

echo "🧪 Starting Pre-Analyzer Test Suite"
echo "======================================"

# Check Python version
echo "🐍 Python version:"
python --version

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run linting (optional, non-blocking)
echo "🔍 Running code linting..."
if command -v flake8 &> /dev/null; then
    flake8 parsers/unified_parser.py --max-line-length=127 --ignore=E501,W503 || echo "⚠️ Linting warnings found"
    flake8 tests/test_unified_parser.py --max-line-length=127 --ignore=E501,W503 || echo "⚠️ Test linting warnings found"
else
    echo "⚠️ flake8 not available, skipping linting"
fi

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest tests/test_unified_parser.py \
    -v \
    --tb=short \
    --cov=parsers.unified_parser \
    --cov-report=term \
    --cov-report=xml \
    --cov-report=html \
    --junitxml=pytest-results.xml

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/"
    echo "📄 JUnit XML report: pytest-results.xml"
    echo "🎉 Ready for deployment!"
    exit 0
else
    echo "❌ Tests failed!"
    exit 1
fi 