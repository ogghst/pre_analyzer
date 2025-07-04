#!/usr/bin/env python3
"""
Lint and Format Script
Test script to check all linting and formatting tools
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode == 0:
            print(f"✅ {description} passed!")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed!")
            if result.stdout.strip():
                print(f"STDOUT: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"STDERR: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"💥 Error running {description}: {e}")
        return False


def main():
    """Run all linting and formatting checks."""
    print("🚀 Running complete code quality check...")
    
    # Define all the checks
    checks = [
        (["black", "--check", "scope_of_supply_analyzer.py"], "Black formatting check"),
        (["isort", "--check-only", "scope_of_supply_analyzer.py"], "Import sorting check"),
        (["flake8", "scope_of_supply_analyzer.py"], "Flake8 style check"),
        (["mypy", "scope_of_supply_analyzer.py"], "MyPy type checking"),
        (["bandit", "-r", ".", "-x", "tests,.*venv"], "Bandit security check"),
    ]
    
    # Run all checks
    results = []
    for command, description in checks:
        success = run_command(command, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    passed = 0
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
        if success:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("🎉 All quality checks passed!")
        return 0
    else:
        print("⚠️  Some quality checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 