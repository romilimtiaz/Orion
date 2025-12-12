# This is a PyQt6-based GUI mockup styled like a JARVIS interface
# It includes: voice activation, voice-to-text, and chat-like feedback loop

from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import speech_recognition as sr
import sys

class VoiceRecognitionThread(QThread):
    text_captured = pyqtSignal(str)

    def run(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            try:
                self.text_captured.emit("🎧 Listening for your command...")
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                self.text_captured.emit(f"🗣️ You said: {text}")
                self.text_captured.emit(f"🧠 Orion is processing: {text}")
            except sr.UnknownValueError:
                self.text_captured.emit("❌ Could not understand audio.")
            except sr.RequestError:
                self.text_captured.emit("❌ Speech recognition failed (check internet).")

class JarvisGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orion Jarvis Interface")
        self.setGeometry(200, 100, 800, 500)
        self.setStyleSheet("background-color: #101820; color: #00FFFF; font-family: Consolas;")

        self.layout = QVBoxLayout()

        self.title = QLabel("🧠 Orion Assistant Interface")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.title)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1A1A1A; color: #7FFFD4; font-size: 14px;")
        self.layout.addWidget(self.chat_display)

        self.listen_button = QPushButton("🎤 Activate Voice")
        self.listen_button.setStyleSheet("background-color: #004466; color: white; padding: 10px; font-size: 14px;")
        self.listen_button.clicked.connect(self.activate_voice)
        self.layout.addWidget(self.listen_button)

        self.setLayout(self.layout)

    def activate_voice(self):
        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.text_captured.connect(self.update_chat)
        self.voice_thread.start()

    def update_chat(self, message):
        self.chat_display.append(message)

# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = JarvisGUI()
    gui.show()
    sys.exit(app.exec())

