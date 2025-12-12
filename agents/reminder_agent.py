# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 08:57:52 2025

@author: romil
"""

# agents/reminder_agent.py

import threading
import time
from datetime import datetime

def schedule_reminder(task, delay_seconds):
    def alert():
        print(f"\n🔔 Reminder: {task}")

    threading.Timer(delay_seconds, alert).start()
    return f"⏰ Reminder set for {delay_seconds // 60:.0f} minutes from now: '{task}'"


def calculate_delay(target_time_str):
    try:
        target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M")
        now = datetime.now()
        delay = (target_time - now).total_seconds()
        return max(0, delay)
    except:
        return -1
