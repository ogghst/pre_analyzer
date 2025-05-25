@echo off
echo ========================================
echo   Analisi Profittabilita Comparator
echo ========================================
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

echo Working directory: %CD%
echo.

REM Try to detect Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Try to detect virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
) else (
    echo No virtual environment found at .venv
    echo Using system Python
    echo.
)

REM Check if Streamlit is available
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Streamlit is not installed
    echo Install with: pip install streamlit
    pause
    exit /b 1
)

echo Streamlit is available
echo.

REM Launch the application
echo Launching Analisi Profittabilita Comparator...
echo URL will be: http://localhost:8502
echo.
echo Press Ctrl+C to stop the application
echo ========================================
echo.

python run_profittabilita_comparator.py

echo.
echo Application has stopped
pause 