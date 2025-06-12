# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:19:29 2025

@author: romil
"""

# agents/llm_planner_agent.py

import ollama

def plan_command(user_command):
    prompt = f"""
You are an intelligent assistant.
Given the following user command, split it into simple actionable steps.
Output in numbered list.

Command: "{user_command}"

Steps:
"""
    response = ollama.chat(model='llama3:8b', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']
