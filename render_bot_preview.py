"""
Render a static preview of the PyQt bot face to a PNG for README/GitHub.

Usage (from repo root):
    python render_bot_preview.py
Optionally set a state:
    BOT_STATE=angry python render_bot_preview.py
"""

from pathlib import Path
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from interactive_bot_gui import BotWidget


def render_bot(path: str = "assets/bot_preview.png", state: str = "thinking", size=(520, 340)):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    widget = BotWidget()
    # Stop timers so we render a stable frame
    widget.timer.stop()
    widget.auto_timer.stop()
    widget.resize(*size)
    widget.set_state(state)
    widget.mouth_level = 0.25  # slight mouth open for nicer expression

    image = QtGui.QImage(widget.size(), QtGui.QImage.Format.Format_ARGB32)
    image.fill(QtCore.Qt.GlobalColor.transparent)

    painter = QtGui.QPainter(image)
    widget.render(painter)
    painter.end()

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(out_path))
    print(f"✅ Saved bot preview to {out_path.resolve()}")

    app.quit()


if __name__ == "__main__":
    desired_state = os.environ.get("BOT_STATE", "thinking")
    render_bot(state=desired_state)
