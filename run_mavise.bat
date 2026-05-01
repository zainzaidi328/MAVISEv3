@echo off
echo Starting MAVISE Project...

IF EXIST ".venv\Scripts\activate.bat" (
    echo Virtual environment found. Activating...
    call .venv\Scripts\activate.bat
) ELSE (
    echo No virtual environment found. Using global Python...
)

echo.
echo Starting Backend API...
start cmd /k "IF EXIST .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) & uvicorn api.main:app --reload"

echo Starting Streamlit Frontend...
start cmd /k "IF EXIST .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) & streamlit run frontend/app.py"

echo.
echo Both servers have been started in new windows!
echo If they immediately crash in those black windows, please tell me what the red/white error text says!
pause
