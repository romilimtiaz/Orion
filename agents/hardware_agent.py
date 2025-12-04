import os
import subprocess
import platform

# Scaffold for hardware control; disabled unless explicitly allowed via ORION_ALLOW_HARDWARE=1.

ALLOWED_ACTIONS = {
    "lock_screen": {
        "linux": ["loginctl", "lock-session"],
        "darwin": ["osascript", "-e", 'tell application "System Events" to keystroke "q" using {control down, command down}'],
        "windows": ["rundll32.exe", "user32.dll,LockWorkStation"],
    },
    "shutdown": {
        "linux": ["shutdown", "-h", "now"],
        "darwin": ["shutdown", "-h", "now"],
        "windows": ["shutdown", "/s", "/t", "0"],
    },
}


def execute_hardware_action(action: str):
    if os.environ.get("ORION_ALLOW_HARDWARE") != "1":
        return "❌ Hardware control disabled (set ORION_ALLOW_HARDWARE=1 to enable)."
    system = platform.system().lower()
    commands = ALLOWED_ACTIONS.get(action, {})
    cmd = commands.get(system)
    if not cmd:
        return f"❌ Action '{action}' not allowed or unsupported on {system}."
    try:
        subprocess.Popen(cmd)
        return f"⚙️ Executed hardware action: {action}"
    except Exception as e:
        return f"❌ Hardware action failed: {e}"
