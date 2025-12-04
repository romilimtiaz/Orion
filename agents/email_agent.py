# agents/email_agent.py

import imaplib
import email
from email.header import decode_header
import smtplib
from email.message import EmailMessage
# Ollama client is optional; handle absence gracefully so the app still starts.
try:
    import ollama
except ImportError:
    ollama = None
import re
import os
import json
from agents.llm_planner_agent import plan_command  # use planner for intent parsing

CONTACTS_FILE = "contacts.json"

# ========== CONTACT MEMORY ==========

def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return {}
    with open(CONTACTS_FILE, 'r') as f:
        return json.load(f)

def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)

def remember_contact(name, email_addr):
    contacts = load_contacts()
    contacts[name.lower()] = email_addr
    save_contacts(contacts)

def get_contact_email(name):
    contacts = load_contacts()
    return contacts.get(name.lower())

# ========== EMAIL READING ==========

def read_unread_emails(username, app_password, n=5):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, app_password)
    imap.select("inbox")

    result, data = imap.search(None, 'UNSEEN')
    email_ids = data[0].split()
    latest_emails = email_ids[-n:]
    messages = []

    for i in reversed(latest_emails):
        res, msg_data = imap.fetch(i, "(RFC822)")
        for response in msg_data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                from_ = msg.get("From")
                messages.append({
                    "from": from_,
                    "subject": subject,
                    "body": extract_body(msg)
                })

    imap.logout()
    return messages

def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

# ========== EMAIL SENDING ==========

def send_email(username, app_password, to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(username, app_password)
        smtp.send_message(msg)
        print("✅ Email sent successfully.")

# ========== EMAIL GENERATION ==========

def generate_email_from_prompt(prompt, context_email=None, model: str | None = None):
    system_prompt = f"""
You are a professional AI assistant. Write a clear and polite email based on this user intent:

Instruction: {prompt}
"""
    if context_email:
        system_prompt += f"\n\nReplying to this email:\n{context_email}"

    if not ollama:
        print("⚠️ Ollama Python client not installed. Please install `ollama` to enable AI email drafting.")
        return ""

    response = ollama.chat(model=model or "llama3", messages=[{"role": "user", "content": system_prompt}])
    return response["message"]["content"]

# ========== MASTER HANDLER ==========

def handle_email_instruction(natural_command, username, app_password, planner_model=None, email_model=None):
    if "reply to" in natural_command.lower():
        # === REPLY TO UNREAD EMAIL ===
        messages = read_unread_emails(username, app_password, 1)
        if not messages:
            print("📭 No unread emails.")
            return

        latest = messages[0]
        print(f"📥 From: {latest['from']}\nSubject: {latest['subject']}")
        print("-" * 40)
        print(latest["body"][:400])

        short_instruction = input("\n💬 What should I say in reply?\n> ")
        reply = generate_email_from_prompt(short_instruction, latest["body"], model=email_model)
        if not reply:
            print("❌ Could not generate reply without Ollama.")
            return
        print("\n📝 Generated reply:\n", reply)

        confirm = input("Send this reply? (yes/no): ").lower()
        if confirm == "yes":
            send_email(username, app_password, latest["from"], "Re: " + latest["subject"], reply)
        else:
            print("❌ Reply cancelled.")

    else:
        # === COMPOSE NEW EMAIL USING LLM PLANNER ===
        plan = plan_command(natural_command, model=planner_model)
        info = plan.get("info", {})

        to_email = info.get("recipient")
        subject = info.get("subject", "No Subject")
        message = info.get("message", subject)

        if not to_email or not message:
            print("⚠️ Could not extract email info from the command.")
            return

        # Save contact (auto-generate name)
        name = to_email.split("@")[0].split(".")[0].capitalize()
        remember_contact(name, to_email)

        print(f"\n🧠 Sending email to {to_email} with subject: {subject}")
        print("📄 Message:\n", message or "[empty]")

        confirm = input("Send this email? (yes/no): ").lower()
        if confirm == "yes":
            send_email(username, app_password, to_email, subject, message)
        else:
            print("❌ Email cancelled.")
