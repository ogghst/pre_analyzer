# Test Suite for Pre-Analyzer Unified Parser

This directory contains comprehensive tests for the unified parser functionality, designed to run in both local development and CI/CD pipeline environments.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Package initialization
├── conftest.py                 # Shared pytest fixtures and configuration
├── test_unified_parser.py      # Main test suite for unified parser
└── README.md                   # This file
```

## 🧪 Test Coverage

The test suite covers:

### File Type Detection Tests
- ✅ PRE file pattern recognition
- ✅ Analisi Profittabilita file pattern recognition  
- ✅ Unknown file type handling (defaults to AP)

### Parser Functionality Tests
- ✅ Successful PRE file parsing
- ✅ Successful Analisi Profittabilita file parsing
- ✅ Fallback mechanism when primary parser fails
- ✅ Error handling when both parsers fail
- ✅ JSON output generation

### Parser Recommendation Tests
- ✅ Confidence scoring for file types
- ✅ Recommendation logic validation
- ✅ Edge case handling

### Module-Level Function Tests
- ✅ Forced parser selection
- ✅ Automatic file type detection
- ✅ File analysis functionality
- ✅ Error handling for invalid inputs

### Integration Tests
- ✅ End-to-end workflow testing
- ✅ Error resilience validation
- ✅ Component interaction verification

## 🚀 Running Tests

### Local Development

#### Quick Test Run
```bash
# Run all unified parser tests
pytest tests/test_unified_parser.py -v

# Run specific test class
pytest tests/test_unified_parser.py::TestUnifiedQuotationParser -v

# Run specific test function
pytest tests/test_unified_parser.py::TestUnifiedQuotationParser::test_file_type_detection_pre_files -v
```

#### With Coverage
```bash
# Run tests with coverage report
pytest tests/test_unified_parser.py --cov=parsers.unified_parser --cov-report=html --cov-report=term
```

#### Using Make (if available)
```bash
make test-fast          # Quick test run
make test-ci            # Full CI/CD-like test run
make coverage           # Tests with coverage
make lint               # Code linting only
```

#### Using Python Script
```bash
# Cross-platform test runner
python run_tests.py
```

### CI/CD Pipeline

#### GitHub Actions
The repository includes a `.github/workflows/test.yml` file that:
- Tests on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Runs on both Ubuntu and Windows
- Includes dependency caching
- Generates coverage reports
- Uploads test artifacts

#### Manual CI/CD Simulation

**Linux/macOS:**
```bash
chmod +x test_runner.sh
./test_runner.sh
```

**Windows:**
```cmd
test_runner.bat
```

## 🔧 Test Configuration

### pytest.ini
The project includes a `pytest.ini` file with optimized settings:
- Verbose output with short tracebacks
- Colored output for better readability
- Test discovery configuration
- Warning filters
- Performance monitoring

### Dependencies
Test dependencies are managed in `requirements-test.txt`:
- `pytest>=7.0.0` - Test framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-mock>=3.10.0` - Mocking utilities
- `pytest-html>=3.1.0` - HTML test reports
- `pytest-xdist>=3.0.0` - Parallel test execution
- `coverage>=7.0.0` - Coverage analysis
- `flake8>=6.0.0` - Code linting

## 🎯 Test Design Principles

### Mocking Strategy
- **External Dependencies**: All file I/O and parser dependencies are mocked
- **No Real Files**: Tests don't require actual Excel files
- **Isolated Testing**: Each test is independent and doesn't affect others
- **Fast Execution**: Mocking ensures tests run quickly

### CI/CD Compatibility
- **No External Resources**: Tests don't depend on external files or services
- **Cross-Platform**: Tests work on Windows, Linux, and macOS
- **Deterministic**: Tests produce consistent results across environments
- **Parallel Safe**: Tests can run in parallel without conflicts

### Error Handling
- **Comprehensive Coverage**: Tests cover both success and failure scenarios
- **Edge Cases**: Unusual inputs and boundary conditions are tested
- **Graceful Degradation**: Fallback mechanisms are thoroughly tested

## 📊 Test Reports

### Coverage Reports
After running tests with coverage, reports are generated in:
- `htmlcov/index.html` - Interactive HTML coverage report
- `coverage.xml` - XML format for CI/CD integration
- Terminal output - Summary coverage statistics

### JUnit XML
For CI/CD integration, JUnit XML reports are generated:
- `pytest-results.xml` - Test results in JUnit format

## 🐛 Debugging Tests

### Running Individual Tests
```bash
# Run with maximum verbosity
pytest tests/test_unified_parser.py::test_function_name -vvv

# Run with debugger on failure
pytest tests/test_unified_parser.py --pdb

# Run with print statements visible
pytest tests/test_unified_parser.py -s
```

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Path Issues**: Tests should be run from project root
3. **Mock Failures**: Check that mocked objects match expected interfaces

## 🔄 Continuous Integration

### GitHub Actions Workflow
The test suite integrates with GitHub Actions to:
- Run tests on every push and pull request
- Test multiple Python versions
- Generate and upload coverage reports
- Cache dependencies for faster builds
- Fail builds on test failures

### Local CI Simulation
Use the provided scripts to simulate CI/CD locally:
- Installs fresh dependencies
- Runs linting checks
- Executes full test suite
- Generates coverage reports
- Provides clear pass/fail status

## 📈 Extending Tests

### Adding New Tests
1. Follow the existing naming convention: `test_*`
2. Use descriptive docstrings
3. Mock external dependencies
4. Include both positive and negative test cases
5. Update this README if adding new test categories

### Test Categories
Use pytest markers to categorize tests:
```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration  
def test_integration_workflow():
    pass
```

## 🎉 Success Criteria

A successful test run should show:
- ✅ All tests passing
- 📊 High code coverage (>90%)
- 🔍 No linting errors
- ⚡ Fast execution time (<2 minutes)
- 📄 Generated reports and artifacts 