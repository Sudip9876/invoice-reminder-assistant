@echo off
echo ========================================================
echo  Starting Invoice & Payment-Reminder Assistant...
echo ========================================================
cd /d "%~dp0"

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Launching Streamlit dashboard...
.venv\Scripts\streamlit.exe run app.py
pause
