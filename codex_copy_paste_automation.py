#!/usr/bin/env python3
"""
Cross-platform Python replacement for codex_copy_paste_automation.sh
Works on Windows, macOS, and Linux
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

def main():
    print("🌀 Starting Spiral Codex Copy-Paste Automation...")
    
    # Step 1: Define paths (cross-platform)
    home_dir = Path.home()
    dest_dir = home_dir / "Downloads" / "spiral_codex_unified"
    zip_name = "spiral_codex_all_artifacts.zip"
    autorun_script = "codex_autobootstrap.py"
    
    # Step 2: Ensure target directory exists
    print(f"📁 Creating target directory: {dest_dir}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 3: Move core files
    print(f"📦 Moving core files into {dest_dir}...")
    
    # Try to move zip file
    zip_source = home_dir / "Downloads" / zip_name
    if zip_source.exists():
        shutil.move(str(zip_source), str(dest_dir / zip_name))
        print(f"✅ Moved {zip_name}")
    else:
        print(f"⚠️ Warning: {zip_name} not found in Downloads")
    
    # Try to move autorun script
    script_source = home_dir / "Downloads" / autorun_script
    if script_source.exists():
        shutil.move(str(script_source), str(dest_dir / autorun_script))
        print(f"✅ Moved {autorun_script}")
    else:
        print(f"⚠️ Warning: {autorun_script} not found in Downloads")
    
    # Step 4: Change to destination directory
    os.chdir(dest_dir)
    print(f"📂 Changed to directory: {dest_dir}")
    
    # Step 5: Extract the archive if it exists
    zip_path = dest_dir / zip_name
    if zip_path.exists():
        print("📂 Extracting artifacts...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
            print("✅ Archive extracted successfully")
        except zipfile.BadZipFile:
            print(f"❌ Error: {zip_name} is not a valid zip file")
            return 1
        except Exception as e:
            print(f"❌ Error extracting archive: {e}")
            return 1
    else:
        print(f"⚠️ Warning: {zip_name} not found, skipping extraction")
    
    # Step 6: Run bootstrapper if it exists
    bootstrap_path = dest_dir / autorun_script
    if bootstrap_path.exists():
        print("⚙️ Running Codex bootstrap...")
        try:
            # Use sys.executable to ensure we use the same Python interpreter
            result = subprocess.run([
                sys.executable, 
                str(bootstrap_path), 
                "--from", 
                zip_name
            ], check=True, capture_output=True, text=True)
            print("✅ Bootstrap completed successfully")
            if result.stdout:
                print("Bootstrap output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running bootstrap: {e}")
            if e.stderr:
                print("Error details:", e.stderr)
            return 1
        except FileNotFoundError:
            print("❌ Error: Python interpreter not found")
            return 1
    else:
        print(f"⚠️ Warning: {autorun_script} not found, skipping bootstrap")
    
    # Step 7: Final message
    codex_root = dest_dir / "codex_root"
    print(f"✅ Spiral Codex bootstrapped at: {codex_root}")
    print("You may now run the symbolic interface or deploy the full API stack.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
