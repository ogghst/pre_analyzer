@echo off
REM Unified Excel Analysis & Comparison Tool - Windows Launcher
REM This script launches the integrated analysis and comparison application

title Unified Excel Analysis ^& Comparison Tool

echo.
echo ============================================================
echo    Unified Excel Analysis ^& Comparison Tool
echo ============================================================
echo.
echo Starting the integrated analysis and comparison application...
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

REM Try to find an available port
echo.
echo Checking for available port...

REM Test if port 8501 is available
python -c "import socket; sock = socket.socket(); sock.bind(('localhost', 8501)); sock.close(); print('✅ Port 8501 is available')" 2>nul
if not errorlevel 1 (
    set PORT=8501
    goto :start_app
)

REM Try port 8502
python -c "import socket; sock = socket.socket(); sock.bind(('localhost', 8502)); sock.close(); print('✅ Port 8502 is available')" 2>nul
if not errorlevel 1 (
    set PORT=8502
    echo ⚠️  Port 8501 is in use, using port 8502 instead
    goto :start_app
)

REM Try port 8503
python -c "import socket; sock = socket.socket(); sock.bind(('localhost', 8503)); sock.close(); print('✅ Port 8503 is available')" 2>nul
if not errorlevel 1 (
    set PORT=8503
    echo ⚠️  Ports 8501-8502 are in use, using port 8503 instead
    goto :start_app
)

REM Try port 8504
python -c "import socket; sock = socket.socket(); sock.bind(('localhost', 8504)); sock.close(); print('✅ Port 8504 is available')" 2>nul
if not errorlevel 1 (
    set PORT=8504
    echo ⚠️  Ports 8501-8503 are in use, using port 8504 instead
    goto :start_app
)

REM Try port 8505
python -c "import socket; sock = socket.socket(); sock.bind(('localhost', 8505)); sock.close(); print('✅ Port 8505 is available')" 2>nul
if not errorlevel 1 (
    set PORT=8505
    echo ⚠️  Ports 8501-8504 are in use, using port 8505 instead
    goto :start_app
)

echo ERROR: No available ports found (tried 8501-8505)
echo Please close other Streamlit applications or restart your computer
echo.
pause
exit /b 1

:start_app
echo.
echo Launching application on http://localhost:%PORT%
echo.
echo NOTE: The application will open in your default web browser
echo       Press Ctrl+C in this window to stop the application
echo.
echo ============================================================

REM Launch the streamlit application
python -m streamlit run scope_of_supply_analyzer.py --server.port %PORT% --server.headless false --browser.gatherUsageStats false

echo.
echo Application stopped.
pause 