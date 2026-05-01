@echo off
color 0B
title MAVISE AI - PRIMARY SPA LAUNCHER
echo =========================================================
echo    MAVISE AI - PRIMARY SPA ENGINE
echo =========================================================
echo.

cd /d "%~dp0"

echo [1/2] Opening browser at http://127.0.0.1:8000
start http://127.0.0.1:8000

echo [2/2] Initializing Backend Server...
echo.

:: Try running with the most likely python that has uvicorn
:: We'll check if uvicorn is available first
python -m uvicorn --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Dependencies found in system Python.
    python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    echo [!] uvicorn not found in system Python. Checking virtual environment...
    if exist ".venv\Scripts\python.exe" (
        ".venv\Scripts\python.exe" -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
    ) else (
        echo [ERROR] Could not find uvicorn or python environment!
        echo Please run: pip install fastapi uvicorn torchaudio whisper-openai
        pause
    )
)

pause
