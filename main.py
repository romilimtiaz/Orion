# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:20:22 2025

@author: romil
"""


# main.py

from agents.llm_planner_agent import plan_command
from agents.file_agent import open_file, global_find_file
from agents.browser_agent import open_website, open_website_and_search
import os
import re

if __name__ == "__main__":
    print("Welcome to Orion 🦾")
    user_command = input("Enter your command: ")
    
    print("\nPlanning steps...\n")
    steps = plan_command(user_command)
    
    print("📝 Steps:")
    print(steps)
    
    # --- BrowserAgent: full URL + optional search ---
    search_match = re.search(r'(?:go to|open)\s+(https?://[^\s]+|[^\s]+\.com)(?:.*search\s+(.*))?', user_command, re.IGNORECASE)

    if search_match:
        url_part = search_match.group(1)
        search_text = search_match.group(2) if search_match.group(2) else None
        
        # Prepare URL
        if not url_part.startswith("http"):
            url = "https://" + url_part
        else:
            url = url_part
        
        if search_text:
            open_website_and_search(url, search_text)
        else:
            open_website(url)
    
    # --- BrowserAgent: known websites ---
    elif "linkedin" in user_command.lower():
        open_website("https://www.linkedin.com")
    elif "google" in user_command.lower():
        open_website("https://www.google.com")
    elif "youtube" in user_command.lower():
        open_website("https://www.youtube.com")
    
    # --- FileAgent: open files ---
    else:
        match = re.search(r'open\s+(.*\.(pdf|docx|doc|txt|mp4|png|jpg|wav|xlsx|csv))', user_command, re.IGNORECASE)
        if match:
            target_filename = match.group(1).strip()
            print(f"🎯 Target filename detected: {target_filename}")
            
            start_drive = "C:\\"  # You can make this dynamic later
            
            file_path = global_find_file(start_drive, target_filename)
            open_file(file_path)
        else:
            print("⚠️ Could not detect filename or website in command.")

