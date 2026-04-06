import google.generativeai as genai
from app.core.config import settings
import os

try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    print("Listing available models:")
    for m in genai.list_models():
        print(f"- {m.name} | Supported methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
