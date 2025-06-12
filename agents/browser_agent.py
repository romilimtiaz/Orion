# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 17:13:56 2025

@author: romil
"""
# agents/browser_agent.py

from playwright.sync_api import sync_playwright
import time

def open_website(url):
    print(f"🌐 Opening website: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        
        print(f"✅ Website opened: {url}")
        
        input("Press Enter to close the browser...")
        browser.close()

def open_website_and_search(url, search_text):
    print(f"🌐 Opening website: {url} and searching for: {search_text}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Example: Google search box
        if "google.com" in url:
            print("🔍 Typing in Google search box...")
            page.wait_for_selector("input[name='q']")  # Wait for search box
            page.fill("input[name='q']", search_text)
            page.keyboard.press("Enter")
        
        # Example: YouTube search box
        elif "youtube.com" in url:
            print("🔍 Typing in YouTube search box...")
            page.wait_for_selector("input#search")
            page.fill("input#search", search_text)
            page.keyboard.press("Enter")
        
        else:
            print("⚠️ Search automation not defined for this site yet.")
        
        print("✅ Search executed.")
        
        input("Press Enter to close the browser...")
        browser.close()
