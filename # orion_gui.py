# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 14:24:21 2025

@author: romil
"""

# orion_gui.py

import tkinter as tk
from tkinter import scrolledtext
import threading
from main import main_logic  # You’ll wrap your main.py logic into a function


class OrionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Orion AI Assistant")
        self.root.geometry("600x500")
        self.root.config(bg="#1e1e1e")

        # User input box
        self.input_label = tk.Label(root, text="Enter your command:", bg="#1e1e1e", fg="white")
        self.input_label.pack(pady=(20, 5))

        self.user_input = tk.Entry(root, width=60, font=("Arial", 14))
        self.user_input.pack(pady=5)

        self.submit_button = tk.Button(root, text="Ask Orion", command=self.handle_input)
        self.submit_button.pack(pady=10)

        # Output display
        self.output_box = scrolledtext.ScrolledText(root, width=70, height=20, bg="#252526", fg="#d4d4d4", font=("Consolas", 11))
        self.output_box.pack(pady=10)

    def handle_input(self):
        user_command = self.user_input.get().strip()
        self.output_box.insert(tk.END, f"\n👤 You: {user_command}\n")
        self.output_box.insert(tk.END, "🧠 Orion: Thinking...\n")
        self.output_box.see(tk.END)

        # Run backend in a thread
        thread = threading.Thread(target=self.run_orion_logic, args=(user_command,))
        thread.start()

    def run_orion_logic(self, user_command):
        result = main_logic(user_command)
        self.output_box.insert(tk.END, result + "\n")
        self.output_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = OrionGUI(root)
    root.mainloop()
