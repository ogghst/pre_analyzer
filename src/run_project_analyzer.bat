@echo off
echo.
echo ========================================
echo   Project Structure Analyzer
echo ========================================
echo.
echo Launching comprehensive project analysis tool...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Streamlit is available
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit is not installed
    echo Installing Streamlit...
    pip install streamlit
    if errorlevel 1 (
        echo ❌ Failed to install Streamlit
        pause
        exit /b 1
    )
)

REM Launch the application
echo ✅ Starting Project Structure Analyzer...
echo.
echo 🌐 The application will open in your default browser
echo 🔄 Press Ctrl+C to stop the application
echo.

python run_project_analyzer.py

echo.
echo 👋 Project Structure Analyzer stopped
pause 