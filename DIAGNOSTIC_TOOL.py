import sys
import os
import socket
import subprocess

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

print("==========================================")
print("🔍 KPGU BOT - EMERGENCY DIAGNOSTIC TOOL")
print("==========================================")

# 1. Check Python
print(f"\n[1] Python Version: {sys.version}")

# 2. Check File Paths
root = os.getcwd()
print(f"[2] Project Root: {root}")
backend_path = os.path.join(root, "backend")
venv_python = os.path.join(backend_path, "venv", "Scripts", "python.exe")

if os.path.exists(venv_python):
    print(f"✅ Venv Python found: {venv_python}")
else:
    print(f"❌ ERROR: Venv Python NOT FOUND at {venv_python}")

# 3. Check Port 8080
if check_port(8080):
    print("❌ ERROR: Port 8080 is ALREADY IN USE by another program.")
    print("   Please restart your computer or close other apps.")
else:
    print("✅ Port 8080 is free.")

# 4. Try starting server and capture error
print("\n[3] Attempting to start server for test (Wait 5s)...")
try:
    process = subprocess.Popen(
        [venv_python, "-m", "uvicorn", "main:app", "--port", "8080", "--host", "127.0.0.1"],
        cwd=backend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
    
    if "Error" in stderr or "traceback" in stderr.lower():
        print("\n❌ SERVER FAILED TO START. ERROR LOG:")
        print("------------------------------------------")
        print(stderr)
        print("------------------------------------------")
    else:
        print("\n✅ SERVER STARTED SUCCESSFULLY IN TEST.")
        print("   If you still see 'Connection Refused', check your firewall.")

except Exception as e:
    print(f"\n❌ FATAL SYSTEM ERROR: {str(e)}")

print("\n==========================================")
print("📌 PLEASE COPY THE ERROR LOG ABOVE AND SHOW IT.")
print("==========================================")
input("Press Enter to close...")
