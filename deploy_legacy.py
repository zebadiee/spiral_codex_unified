#!/usr/bin/env python3
"""
Cross-platform Python deployment script
Replacement for deploy.sh that works on Windows, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except FileNotFoundError as e:
        return False, "", str(e)

def main():
    print("🌀 Starting Spiral Codex deployment...")
    
    # Detect platform
    current_platform = platform.system()
    print(f"🖥️ Detected platform: {current_platform}")
    
    # Step 1: Clean environment
    print("🧹 Cleaning environment...")
    if Path(".venv").exists():
        shutil.rmtree(".venv")
        print("✅ Removed existing .venv")
    
    if Path("codex_root").exists():
        shutil.rmtree("codex_root")
        print("✅ Removed existing codex_root")
    
    # Step 2: Create isolated environment
    print("🐍 Creating Python virtual environment...")
    success, stdout, stderr = run_command([sys.executable, "-m", "venv", ".venv"])
    if not success:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return 1
    print("✅ Virtual environment created")
    
    # Step 3: Determine activation script path
    if current_platform == "Windows":
        activate_script = Path(".venv") / "Scripts" / "activate"
        python_exe = Path(".venv") / "Scripts" / "python.exe"
        pip_exe = Path(".venv") / "Scripts" / "pip.exe"
    else:
        activate_script = Path(".venv") / "bin" / "activate"
        python_exe = Path(".venv") / "bin" / "python"
        pip_exe = Path(".venv") / "bin" / "pip"
    
    # Step 4: Upgrade pip and install dependencies
    print("📦 Upgrading pip and installing dependencies...")
    
    # Upgrade pip
    success, stdout, stderr = run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    if not success:
        print(f"⚠️ Warning: Failed to upgrade pip: {stderr}")
    else:
        print("✅ Pip upgraded successfully")
    
    # Install requirements
    if Path("requirements.txt").exists():
        success, stdout, stderr = run_command([str(pip_exe), "install", "--prefer-binary", "-r", "requirements.txt"])
        if not success:
            print(f"❌ Failed to install requirements: {stderr}")
            return 1
        print("✅ Requirements installed successfully")
    else:
        print("⚠️ Warning: requirements.txt not found")
    
    # Step 5: Create structure
    print("📁 Creating directory structure...")
    codex_root = Path("codex_root")
    (codex_root / "kernel").mkdir(parents=True, exist_ok=True)
    (codex_root / "agents").mkdir(parents=True, exist_ok=True)
    (codex_root / "config").mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure created")
    
    # Step 6: Copy files
    print("📋 Copying files...")
    
    # Copy kernel files
    if Path("kernel").exists():
        for item in Path("kernel").iterdir():
            if item.is_file():
                shutil.copy2(item, codex_root / "kernel" / item.name)
            elif item.is_dir():
                shutil.copytree(item, codex_root / "kernel" / item.name, dirs_exist_ok=True)
        print("✅ Kernel files copied")
    
    # Copy agent files
    if Path("agents").exists():
        for item in Path("agents").iterdir():
            if item.is_file():
                shutil.copy2(item, codex_root / "agents" / item.name)
        print("✅ Agent files copied")
    
    # Copy config files
    if Path("config").exists():
        for item in Path("config").iterdir():
            if item.is_file():
                shutil.copy2(item, codex_root / "config" / item.name)
        print("✅ Config files copied")
    
    # Step 7: Create entropy bindings config if it doesn't exist
    entropy_config_path = codex_root / "config" / "entropy_bindings.yml"
    if not entropy_config_path.exists():
        print("⚙️ Creating entropy bindings config...")
        entropy_config = """default_entropy: 0.5
thresholds:
  low: 0.3
  high: 0.9
"""
        entropy_config_path.write_text(entropy_config, encoding='utf-8')
        print("✅ Entropy bindings config created")
    
    # Step 8: Start API
    print("🎛️ Launching FastAPI app on http://localhost:8000 ...")
    print("Use Ctrl+C to stop the server")
    
    # Determine the correct FastAPI entrypoint
    if Path("api/fastapi_app.py").exists():
        app_module = "api.fastapi_app:app"
    else:
        app_module = "fastapi_app:app"
    
    # Start uvicorn
    try:
        subprocess.run([
            str(python_exe), "-m", "uvicorn", 
            app_module, 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Make sure FastAPI and uvicorn are installed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
