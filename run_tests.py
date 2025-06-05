#!/usr/bin/env python3
"""
Local test runner that mimics CI/CD pipeline behavior
Run this script to execute the same tests that run in CI/CD
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        return False
    else:
        print(f"✅ PASSED: {description}")
        return True

def main():
    """Main test runner"""
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Starting Pre-Analyzer Test Suite")
    print(f"📁 Working directory: {project_root}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("🐍 Virtual environment detected")
    else:
        print("⚠️  Warning: Not in a virtual environment")
    
    success_count = 0
    total_tests = 0
    
    # Install test dependencies
    total_tests += 1
    if run_command("pip install -r requirements-test.txt", "Installing test dependencies"):
        success_count += 1
    
    # Install main dependencies  
    total_tests += 1
    if run_command("pip install -r requirements.txt", "Installing main dependencies"):
        success_count += 1
    
    # Run linting (non-blocking)
    total_tests += 1
    lint_success = run_command("flake8 parsers/unified_parser.py --max-line-length=127 --ignore=E501", "Code linting")
    if lint_success:
        success_count += 1
    else:
        print("⚠️  Linting failed but continuing with tests")
    
    # Run main test suite
    total_tests += 1
    if run_command("pytest tests/test_unified_parser.py -v --tb=short", "Running unified parser tests"):
        success_count += 1
    
    # Run tests with coverage
    total_tests += 1
    if run_command("pytest tests/test_unified_parser.py --cov=parsers.unified_parser --cov-report=term --cov-report=html", "Running coverage tests"):
        success_count += 1
    
    # Run all tests in the tests directory
    if os.path.exists("tests") and len(os.listdir("tests")) > 3:  # More than just __init__.py, conftest.py, test_unified_parser.py
        total_tests += 1
        if run_command("pytest tests/ -v", "Running all tests"):
            success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print('='*60)
    print(f"✅ Passed: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Ready for CI/CD")
        return 0
    else:
        print("💥 Some tests failed. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 