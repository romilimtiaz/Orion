# agents/file_agent.py

import os
import subprocess
import platform
from pathlib import Path

def global_find_file(start_path, target_filename):
    start_path = Path(start_path).expanduser().resolve()
    print(f"🌎 Searching for {target_filename} in {start_path} ...")

    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.lower() == target_filename.lower():
                file_path = Path(root) / file
                print(f"✅ Found: {file_path}")
                return str(file_path)

    print("❌ File not found.")
    return None

def open_file(file_path):
    if not file_path:
        print("❌ No file path provided.")
        return

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    # Safety: only open files under the user's home directory
    home = Path.home().resolve()
    try:
        path.relative_to(home)
    except ValueError:
        print(f"❌ Refusing to open file outside home directory: {path}")
        return

    print(f"📂 Opening file: {path}")

    system_platform = platform.system()

    if system_platform == "Windows":
        os.startfile(path)
    elif system_platform == "Darwin":  # MacOS
        subprocess.run(["open", str(path)])
    else:  # Linux
        subprocess.run(["xdg-open", str(path)])
