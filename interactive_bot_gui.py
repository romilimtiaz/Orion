"""
PyQt6 animated bot face with simple voice input and mood colors.
- Idle/neutral: cyan/blue
- Thinking: green
- Angry: red
- Mouth animation follows a rough audio level or idle pulse
- Optional speech recognition (Google Web Speech) to capture a line and set state from keywords

Run: python interactive_bot_gui.py
Dependencies: PyQt6; optional speech_recognition + pyaudio for mic input
"""

import sys
import math
import random
threading = None
try:
    import speech_recognition as sr  # optional
except ImportError:
    sr = None

from PyQt6 import QtCore, QtGui, QtWidgets


class VoiceThread(QtCore.QThread):
    level = QtCore.pyqtSignal(float)
    transcript = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)

    def run(self):
        if not sr:
            self.error.emit("speech_recognition not installed.")
            return
        try:
            rec = sr.Recognizer()
            with sr.Microphone() as mic:
                rec.adjust_for_ambient_noise(mic, duration=0.5)
                audio = rec.listen(mic, timeout=5, phrase_time_limit=6)
            # crude RMS for mouth animation
            raw = audio.get_raw_data()
            if raw:
                import array
                arr = array.array('h', raw)
                rms = math.sqrt(sum(a * a for a in arr) / len(arr))
                norm = min(1.0, rms / 5000.0)
                self.level.emit(norm)
            try:
                text = rec.recognize_google(audio)
                self.transcript.emit(text)
            except Exception as e:
                self.error.emit(f"ASR failed: {e}")
        except Exception as e:
            self.error.emit(str(e))


class BotWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orion Bot Face")
        self.resize(520, 340)
        self.state = "neutral"
        self.mouth_level = 0.1
        self.blink_timer = 0.0
        self.listen_thread = None
        self.transcript_text = "Say something..."
        self.info_text = ""
        self.auto_timer = QtCore.QTimer(self)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        btn_listen = QtWidgets.QPushButton("🎤 Listen", self)
        btn_listen.clicked.connect(self.start_listen)
        btn_think = QtWidgets.QPushButton("💡 Thinking", self)
        btn_think.clicked.connect(lambda: self.set_state("thinking"))
        btn_angry = QtWidgets.QPushButton("🔥 Angry", self)
        btn_angry.clicked.connect(lambda: self.set_state("angry"))
        btn_neutral = QtWidgets.QPushButton("💤 Neutral", self)
        btn_neutral.clicked.connect(lambda: self.set_state("neutral"))

        self.status_label = QtWidgets.QLabel(self.transcript_text, self)
        self.status_label.setStyleSheet("color: #9fd1ff;")

        bar = QtWidgets.QHBoxLayout()
        for b in (btn_listen, btn_think, btn_angry, btn_neutral):
            bar.addWidget(b)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.status_label)
        layout.addStretch()

        # periodically shuffle mood so colors animate on their own
        self.auto_timer.timeout.connect(self.randomize_state)
        self.schedule_next_auto_state()

    def start_listen(self):
        if self.listen_thread and self.listen_thread.isRunning():
            return
        self.status_label.setText("Listening...")
        self.set_state("thinking")
        self.listen_thread = VoiceThread()
        self.listen_thread.level.connect(self.on_level)
        self.listen_thread.transcript.connect(self.on_transcript)
        self.listen_thread.error.connect(self.on_error)
        self.listen_thread.start()

    def on_level(self, lvl: float):
        self.mouth_level = max(self.mouth_level, min(1.0, lvl))

    def on_transcript(self, text: str):
        self.transcript_text = text
        self.status_label.setText(text)
        tl = text.lower()
        if "angry" in tl or "mad" in tl:
            self.set_state("angry")
        elif "think" in tl or "processing" in tl:
            self.set_state("thinking")
        else:
            self.set_state("neutral")

    def on_error(self, msg: str):
        self.status_label.setText(msg)
        self.set_state("neutral")

    def set_state(self, state: str):
        self.state = state
        # reset auto shuffle timer so manual interactions still get variety
        self.schedule_next_auto_state()

    def schedule_next_auto_state(self):
        delay_ms = random.randint(2, 6) * 1000  # between 2-6 seconds
        self.auto_timer.start(delay_ms)

    def randomize_state(self):
        states = ["neutral", "thinking", "angry"]
        choices = [s for s in states if s != self.state] or states
        self.set_state(random.choice(choices))

    def tick(self):
        # decay mouth level
        self.mouth_level *= 0.92
        # idle pulse to keep mouth from freezing
        self.mouth_level = max(0.05, self.mouth_level)
        self.blink_timer += 0.016
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QtGui.QColor(5, 10, 30))

        card = QtCore.QRectF(w/2 - 170, h/2 - 100, 340, 200)
        # colors by state
        if self.state == "angry":
            base = QtGui.QColor(90, 20, 30)
            border = QtGui.QColor(255, 60, 60)
            glow = QtGui.QColor(255, 80, 80)
        elif self.state == "thinking":
            base = QtGui.QColor(20, 50, 30)
            border = QtGui.QColor(80, 200, 120)
            glow = QtGui.QColor(120, 240, 160)
        else:
            base = QtGui.QColor(10, 20, 60)
            border = QtGui.QColor(0, 160, 255)
            glow = QtGui.QColor(0, 200, 255)

        # border
        pen = QtGui.QPen(border, 3)
        painter.setPen(pen)
        painter.setBrush(base)
        painter.drawRoundedRect(card, 24, 24)

        inner = card.adjusted(8, 8, -8, -8)
        painter.fillRect(inner, base.darker(110))

        # scan lines
        painter.setPen(QtGui.QPen(QtGui.QColor(8, 16, 40), 1))
        y = int(inner.top())
        left = int(inner.left())
        right = int(inner.right())
        while y < inner.bottom():
            painter.drawLine(left, y, right, y)
            y += 4

        # eyes
        t = self.blink_timer
        eye_y = inner.top() + 55
        eye_dx = 70
        for cx in (inner.center().x() - eye_dx, inner.center().x() + eye_dx):
            self.draw_eye(painter, cx, eye_y, t, glow)

        # mouth
        self.draw_mouth(painter, inner)

        # text
        painter.setPen(QtGui.QColor(150, 190, 255))
        painter.setFont(QtGui.QFont("Consolas", 16))
        painter.drawText(int(inner.left()) + 16, int(inner.bottom()) - 16, self.state.upper())

    def draw_eye(self, painter, cx, cy, t, glow_color):
        pulse = 1.0 + 0.12 * math.sin(t * 2.0 + cx)
        outer_w, outer_h = int(70 * pulse), 26
        inner_w, inner_h = int(46 * pulse), 14

        outer = QtCore.QRectF(0, 0, outer_w, outer_h)
        outer.moveCenter(QtCore.QPointF(cx, cy))
        inner = QtCore.QRectF(0, 0, inner_w, inner_h)
        inner.moveCenter(QtCore.QPointF(cx, cy))

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(glow_color)
        painter.drawRoundedRect(outer, 14, 14)
        painter.setBrush(QtGui.QColor(210, 230, 255))
        painter.drawRoundedRect(inner, 10, 10)

    def draw_mouth(self, painter, inner):
        base_h = 6
        h = base_h + 30 * self.mouth_level
        w = 120
        rect = QtCore.QRectF(0, 0, w, h)
        rect.moveCenter(QtCore.QPointF(inner.center().x(), inner.center().y() + 20))
        painter.setBrush(QtGui.QColor(80, 140, 200))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 4, 4)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = BotWidget()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
