# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 14:18:42 2025

@author: romil
"""

# utils/memory.py

import json
import os

MEMORY_FILE = "orion_memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def get_contact(name):
    memory = load_memory()
    return memory.get("contacts", {}).get(name)


def remember_contact(name, email):
    memory = load_memory()
    if "contacts" not in memory:
        memory["contacts"] = {}
    memory["contacts"][name] = email
    save_memory(memory)
