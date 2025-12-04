# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 08:58:19 2025

@author: romil
"""

# agents/translate_agent.py



from deep_translator import GoogleTranslator

def translate_text(text, target_lang="en"):
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return f"🌐 Translated to {target_lang}: {translated}"
    except Exception as e:
        return f"❌ Translation failed: {e}"
