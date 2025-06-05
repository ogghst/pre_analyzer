.PHONY: test install-deps lint coverage clean help test-fast test-ci

# Default target
help:
	@echo "Available commands:"
	@echo "  install-deps    Install all dependencies"
	@echo "  test           Run all tests"
	@echo "  test-fast      Run tests without coverage"
	@echo "  test-ci        Run tests like in CI/CD pipeline"
	@echo "  lint           Run code linting"
	@echo "  coverage       Run tests with coverage report"
	@echo "  clean          Clean up test artifacts"

# Install dependencies
install-deps:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

# Run all tests
test: install-deps
	pytest tests/ -v --tb=short

# Run tests quickly without coverage
test-fast:
	pytest tests/test_unified_parser.py -v

# Run tests like CI/CD pipeline
test-ci: install-deps lint coverage
	@echo "✅ All CI/CD pipeline tests completed"

# Run linting
lint:
	flake8 parsers/unified_parser.py --max-line-length=127 --ignore=E501,W503
	flake8 tests/test_unified_parser.py --max-line-length=127 --ignore=E501,W503

# Run tests with coverage
coverage: install-deps
	pytest tests/test_unified_parser.py --cov=parsers.unified_parser --cov-report=term --cov-report=html --cov-report=xml

# Clean up test artifacts
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf pytest-results.xml
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run specific test class
test-class:
	pytest tests/test_unified_parser.py::TestUnifiedQuotationParser -v

# Run specific test function  
test-function:
	pytest tests/test_unified_parser.py::TestUnifiedQuotationParser::test_file_type_detection_pre_files -v 