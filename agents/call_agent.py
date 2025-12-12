import json
import os
from twilio.twiml.voice_response import VoiceResponse

STATE_FILE = "call_status.json"
DEFAULT_STATUS = "I'm busy right now. Please call later."


def get_status():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except Exception:
            pass
    return {"message": DEFAULT_STATUS}


def set_status(message: str):
    data = {"message": message or DEFAULT_STATUS}
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)
    return data


def build_twiml(caller: str | None = None):
    status = get_status()["message"]
    resp = VoiceResponse()
    caller_text = f"{caller}. " if caller else ""
    resp.say(f"This is Orion. {caller_text}{status}")
    return str(resp)
