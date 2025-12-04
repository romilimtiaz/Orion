# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 14:19:37 2025

@author: romil
"""

# utils/credentials.py

import os
import json

CRED_FILE = "orion_credentials.json"

def load_credentials():
    if not os.path.exists(CRED_FILE):
        return {}

    with open(CRED_FILE, "r") as f:
        return json.load(f)

def save_credentials(data):
    with open(CRED_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_or_prompt_credentials():
    creds = load_credentials()

    if "email" not in creds:
        creds["email"] = input("📧 Enter your email address: ")

    if "password" not in creds:
        creds["password"] = input("🔐 Enter your app-specific email password: ")

    if "serpapi" not in creds:
        creds["serpapi"] = input("🔎 Enter your SerpAPI key (or leave blank): ")

    save_credentials(creds)
    return creds
