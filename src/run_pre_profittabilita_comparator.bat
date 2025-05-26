@echo off
REM PRE vs Analisi Profittabilita Cross-Comparator Launcher (Windows)
REM This script launches the specialized cross-comparison application

echo.
echo ================================================================
echo    PRE vs Analisi Profittabilita Cross-Comparator
echo ================================================================
echo.
echo  Comprehensive Cross-File Analysis ^& WBE Impact Assessment
echo.
echo  This tool provides:
echo   ^> Data consistency validation between files
echo   ^> WBE impact analysis and margin assessment  
echo   ^> Financial impact evaluation
echo   ^> Project structure comparison
echo   ^> Missing items analysis
echo   ^> Detailed item-by-item comparison
echo.
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "APP_PATH=%SCRIPT_DIR%pre_profittabilita_comparator_app.py"

REM Check if the application file exists
if not exist "%APP_PATH%" (
    echo ❌ Application file not found: %APP_PATH%
    echo Please ensure the application files are in the correct location
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit is not installed
    echo Installing Streamlit...
    python -m pip install streamlit
    if errorlevel 1 (
        echo ❌ Failed to install Streamlit
        echo Please install manually: pip install streamlit
        pause
        exit /b 1
    )
)

REM Check for required dependencies
echo 🔍 Checking dependencies...
python -c "import pandas, plotly, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo ❌ Missing required dependencies
    echo Installing required packages...
    python -m pip install pandas plotly openpyxl
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo Please install manually: pip install pandas plotly openpyxl
        pause
        exit /b 1
    )
)

echo ✅ All dependencies are available
echo.
echo 🔄 Launching PRE vs Analisi Profittabilita Cross-Comparator...
echo 📁 App location: %APP_PATH%
echo 🌐 Opening in browser...
echo.
echo ================================================================
echo  Instructions:
echo   1. Upload one PRE quotation file
echo   2. Upload one Analisi Profittabilita file  
echo   3. Explore different analysis views
echo   4. Export reports and CSV files as needed
echo.
echo  Press Ctrl+C to stop the application
echo ================================================================
echo.

REM Launch the Streamlit application
python -m streamlit run "%APP_PATH%" ^
    --theme.base light ^
    --theme.primaryColor "#1f77b4" ^
    --theme.backgroundColor "#ffffff" ^
    --theme.secondaryBackgroundColor "#f0f2f6" ^
    --server.headless false ^
    --browser.gatherUsageStats false

REM Check exit status
if errorlevel 1 (
    echo.
    echo ❌ Application exited with an error
    pause
    exit /b 1
)

echo.
echo 👋 PRE vs Analisi Profittabilita Cross-Comparator closed
pause 