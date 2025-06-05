@echo off
REM CI/CD Test Runner for Pre-Analyzer Unified Parser (Windows)
REM This script runs the complete test suite with proper error handling

echo 🧪 Starting Pre-Analyzer Test Suite
echo ======================================

REM Check Python version
echo 🐍 Python version:
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found!
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install main dependencies!
    exit /b 1
)

pip install -r requirements-test.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install test dependencies!
    exit /b 1
)

REM Run linting (optional, non-blocking)
echo 🔍 Running code linting...
flake8 parsers/unified_parser.py --max-line-length=127 --ignore=E501,W503 2>nul || echo ⚠️ Linting warnings found
flake8 tests/test_unified_parser.py --max-line-length=127 --ignore=E501,W503 2>nul || echo ⚠️ Test linting warnings found

REM Run tests with coverage
echo 🧪 Running tests with coverage...
pytest tests/test_unified_parser.py -v --tb=short --cov=parsers.unified_parser --cov-report=term --cov-report=xml --cov-report=html --junitxml=pytest-results.xml

if %ERRORLEVEL% equ 0 (
    echo ✅ All tests passed!
    echo 📊 Coverage report generated in htmlcov/
    echo 📄 JUnit XML report: pytest-results.xml
    echo 🎉 Ready for deployment!
    exit /b 0
) else (
    echo ❌ Tests failed!
    exit /b 1
) 