import os
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

def get_gemini_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY")


def get_model(name: Optional[str] = None):
    """
    Returns a configured Gemini model client or None if unavailable.
    """
    if not genai:
        print("⚠️ google-generativeai not installed. Install with `pip install google-generativeai`.")
        return None

    api_key = get_gemini_api_key()
    if not api_key:
        print("⚠️ GEMINI_API_KEY not set.")
        return None

    genai.configure(api_key=api_key)
    model_name = name or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    return genai.GenerativeModel(model_name)


def generate(model_name: Optional[str], prompt: str, system: Optional[str] = None) -> str:
    model = get_model(model_name)
    if not model:
        return ""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        res = model.generate_content(messages)
        return res.text or ""
    except Exception as e:
        print(f"⚠️ Gemini call failed: {e}")
        return ""
