# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 08:56:19 2025

@author: romil
"""

# agents/calendar_agent.py

from ics import Calendar, Event
from datetime import datetime
import os

CALENDAR_FILE = "orion_schedule.ics"

def schedule_event(event_name, event_time):
    c = Calendar()

    # Convert string to datetime (simple format)
    try:
        dt = datetime.strptime(event_time, "%Y-%m-%d %H:%M")  # Expecting "2025-06-24 14:00"
    except ValueError:
        return "❌ Invalid datetime format. Use 'YYYY-MM-DD HH:MM'."

    e = Event()
    e.name = event_name
    e.begin = dt

    # Load existing calendar if exists
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, "r") as f:
            c = Calendar(f.read())

    c.events.add(e)

    with open(CALENDAR_FILE, "w") as f:
        f.writelines(c.serialize_iter())

    return f"📅 Event '{event_name}' scheduled on {event_time}."
