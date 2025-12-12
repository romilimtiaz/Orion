import platform
import shutil
import subprocess


def _run(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode(errors="ignore")
    except Exception as e:
        return False, str(e)


def lock_screen():
    system = platform.system().lower()
    if system == "linux":
        ok, err = _run(["loginctl", "lock-session"])
        return "🔒 Screen locked." if ok else f"❌ Failed to lock screen: {err}"
    elif system == "darwin":
        ok, err = _run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        return "🔒 Screen locked." if ok else f"❌ Failed to lock screen: {err}"
    elif system == "windows":
        ok, err = _run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "🔒 Screen locked." if ok else f"❌ Failed to lock screen: {err}"
    return "❌ Unsupported OS for lock."


def volume(action: str):
    system = platform.system().lower()
    if system != "linux":
        return "❌ Volume control implemented for Linux pulse audio only."
    if not shutil.which("pactl"):
        return "❌ pactl not found. Install PulseAudio utilities."
    if action == "up":
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
        return "🔊 Volume up."
    if action == "down":
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
        return "🔉 Volume down."
    if action == "mute":
        _run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        return "🤫 Toggled mute."
    return "❌ Unknown volume action."


def brightness(action: str):
    system = platform.system().lower()
    if system != "linux":
        return "❌ Brightness control implemented for Linux only."
    if shutil.which("brightnessctl"):
        if action == "up":
            _run(["brightnessctl", "set", "+10%"])
            return "💡 Brightness up."
        if action == "down":
            _run(["brightnessctl", "set", "10%-"])
            return "💡 Brightness down."
    elif shutil.which("xbacklight"):
        if action == "up":
            _run(["xbacklight", "-inc", "10"])
            return "💡 Brightness up."
        if action == "down":
            _run(["xbacklight", "-dec", "10"])
            return "💡 Brightness down."
    return "❌ Brightness tool not found (install brightnessctl or xbacklight)."
