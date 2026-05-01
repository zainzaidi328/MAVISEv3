import subprocess
import sys
import time
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
log_file_path = os.path.join(script_dir, "debug_log.txt")

with open(log_file_path, "w", encoding="utf-8") as f:
    f.write("--- Starting MAVISE Run Script ---\n")
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Script Directory: {script_dir}\n")

def log(msg):
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")
    print(msg)

try:
    log("Checking dependencies...")
    try:
        import uvicorn
        import streamlit
        log("Dependencies found!")
    except ImportError:
        log("Dependencies missing! Installing from requirements.txt...")
        req_path = os.path.join(script_dir, 'requirements.txt')
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path], capture_output=True, text=True)
        log("Pip Install Output:")
        log(result.stdout)
        if result.returncode != 0:
            log("Pip Install Error:")
            log(result.stderr)
            raise Exception("Pip install failed.")
        log("Dependencies installed successfully!")

    log("Starting FastAPI Backend...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=script_dir
    )
    time.sleep(2)
    
    log("Starting Streamlit Frontend...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "127.0.0.1"],
        cwd=script_dir
    )
    
    log("\nBoth servers started in the background.")
    log("Check http://127.0.0.1:8501")

    # Let them run for a few seconds to capture any immediate crash logs
    time.sleep(4)
    
    # Check if either process died immediately
    if backend.poll() is not None:
        log(f"Backend crashed with exit code {backend.poll()}! See terminal for output.")
    
    if frontend.poll() is not None:
        log(f"Frontend crashed with exit code {frontend.poll()}! See terminal for output.")

    log("--- Script finished initialization ---")
    
    backend.wait()
    frontend.wait()

except Exception as e:
    log(f"An unexpected error occurred: {e}")
