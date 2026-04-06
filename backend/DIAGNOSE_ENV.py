import sys
import os
import subprocess

def check_env():
    print("="*50)
    print("KPGU AI - SYSTEM DIAGNOSTICS")
    print("="*50)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Directory: {os.getcwd()}")
    print("\nEnvironment Variables:")
    print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'None')}")
    
    print("\nSearch Paths (sys.path):")
    for path in sys.path:
        print(f" - {path}")

    print("\nChecking for critical modules:")
    modules = ['fastapi', 'uvicorn', 'pydantic', 'typing_extensions', 'langchain']
    for mod in modules:
        try:
            m = __import__(mod)
            print(f" [OK] {mod} is installed at: {os.path.dirname(m.__file__)}")
        except ImportError:
            print(f" [!!] {mod} is MISSING")

    print("\nRunning 'pip list' check...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Could not run pip list: {e}")

if __name__ == "__main__":
    check_env()
