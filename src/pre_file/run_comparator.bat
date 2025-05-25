@echo off
REM PRE File Comparator Launcher for Windows
REM This batch file launches the PRE File Comparator Streamlit application

echo 🚀 PRE File Comparator Launcher
echo ================================

REM Check if we're in the right directory
if not exist "pre_comparator_app.py" (
    echo ❌ Error: pre_comparator_app.py not found
    echo Make sure you're running this from the src/pre_file directory
    pause
    exit /b 1
)

REM Try to run with python runner script first
echo 🔍 Trying Python runner script...
python run_comparator.py
if %ERRORLEVEL% == 0 goto :end

REM If that failed, try direct streamlit command
echo 🔍 Trying direct streamlit command...
streamlit run pre_comparator_app.py
if %ERRORLEVEL% == 0 goto :end

REM If that failed, try python -m streamlit
echo 🔍 Trying python -m streamlit...
python -m streamlit run pre_comparator_app.py
if %ERRORLEVEL% == 0 goto :end

REM If all methods failed
echo ❌ Could not launch the application
echo.
echo 💡 Try these solutions:
echo 1. Install streamlit: pip install streamlit
echo 2. Activate your virtual environment if using one
echo 3. Run manually: python -m streamlit run pre_comparator_app.py
echo.
pause

:end
echo.
echo 👋 PRE File Comparator session ended
pause 