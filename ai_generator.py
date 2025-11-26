import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ✔️ ENV değişkenini doğru oku
API_KEY = os.getenv("AIzaSyD5l9vOHprZnXjZSM7YOp7daYyAGwJX22w")
if not API_KEY:
    raise Exception("❌ GEMINI_API_KEY .env dosyasında bulunamadı!")

# ✔️ Gemini API yapılandırması
genai.configure(api_key=API_KEY)


def generate_ai_templates(topic):
    prompt = f"""
    Kullanıcı '{topic}' hakkında bir web sitesi oluşturmak istiyor.
    3 farklı HTML ve CSS şablonu üret.
    Her şablon:
    - modern
    - responsive (mobil uyumlu)
    - navbar, hero, içerik alanı ve footer içersin.

    Sonucu YALNIZCA JSON formatında döndür:
    [
      {{
        "id": 1,
        "name": "Tema Adı",
        "description": "Kısa açıklama",
        "html": "<!DOCTYPE html>...</html>",
        "css": "body{{...}}"
      }},
      ...
    ]
    """

    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}  # ✔️ direkt JSON döndürür
        )

        # ✔️ Tek API isteği — rate limit aşılmaz!
        response = model.generate_content(prompt)

        # ✔️ API zaten JSON döndürüyor
        return json.loads(response.text)

    except Exception as e:
        print("❌ Gemini hata:", e)
        return fallback_templates(topic, error=str(e))


def fallback_templates(topic, error="AI cevabı işlenemedi"):
    return [{
        "id": 0,
        "name": "Hata",
        "description": error,
        "html": f"<h1>{topic}</h1><p>{error}</p>",
        "css": "body{{font-family:sans-serif; text-align:center; padding:40px;}}"
    }]
