import subprocess
import os
import sys

# Start Uvicorn Backend
try:
    subprocess.Popen(
        ["cmd.exe", "/c", "start", "cmd.exe", "/k", "uvicorn api.main:app --reload"],
        cwd=r"c:\Users\Hp\OneDrive\Desktop\MAVISE_FYP\MAVISE_FYP"
    )
    print("Backend API launched in a new window.")
except Exception as e:
    print(f"Failed to launch Backend: {e}")

# Start Streamlit Frontend
try:
    subprocess.Popen(
        ["cmd.exe", "/c", "start", "cmd.exe", "/k", "streamlit run frontend/app.py"],
        cwd=r"c:\Users\Hp\OneDrive\Desktop\MAVISE_FYP\MAVISE_FYP"
    )
    print("Streamlit Frontend launched in a new window.")
except Exception as e:
    print(f"Failed to launch Frontend: {e}")
