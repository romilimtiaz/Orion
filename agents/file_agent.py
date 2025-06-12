# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:29:15 2025

@author: romil
"""

# agents/file_agent.py

import os
import subprocess
import platform

def global_find_file(start_drive, target_filename):
    print(f"🌎 Searching for {target_filename} in {start_drive} ...")
    
    for root, dirs, files in os.walk(start_drive):
        for file in files:
            if file.lower() == target_filename.lower():
                file_path = os.path.join(root, file)
                print(f"✅ Found: {file_path}")
                return file_path
    
    print("❌ File not found.")
    return None

def open_file(file_path):
    if not file_path or not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📂 Opening file: {file_path}")
    
    system_platform = platform.system()
    
    if system_platform == "Windows":
        os.startfile(file_path)
    elif system_platform == "Darwin":  # MacOS
        subprocess.run(["open", file_path])
    else:  # Linux
        subprocess.run(["xdg-open", file_path])
