@echo off
REM Simple Unified Excel Analysis & Comparison Tool - Windows Launcher

title Unified Excel Analysis ^& Comparison Tool

echo.
echo ============================================================
echo    Unified Excel Analysis ^& Comparison Tool
echo ============================================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if Python is available
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    echo.
    pause
    exit /b 1
)
echo ✅ Python found

REM Check if streamlit is available
echo Checking Streamlit installation...
python -c "import streamlit; print('✅ Streamlit', streamlit.__version__, 'found')" 2>nul
if errorlevel 1 (
    echo ERROR: Streamlit is not installed
    echo Please install streamlit: pip install streamlit
    echo.
    pause
    exit /b 1
)

REM Check if the main application file exists
if not exist "scope_of_supply_analyzer.py" (
    echo ERROR: scope_of_supply_analyzer.py not found
    echo Please make sure you're running this from the src directory
    echo.
    pause
    exit /b 1
)
echo ✅ Found scope_of_supply_analyzer.py

echo.
echo 📊 Launching application...
echo 🌐 The application will open in your default web browser
echo ⏹️  Press Ctrl+C in this window to stop the application
echo.
echo ============================================================

REM Launch the streamlit application (let streamlit choose the port)
python -m streamlit run scope_of_supply_analyzer.py

echo.
echo Application stopped.
pause 