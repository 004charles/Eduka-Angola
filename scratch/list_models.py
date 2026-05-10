import os
import django
import sys
import google.generativeai as genai

# Configurar Django
sys.path.append('/home/carlos/Eduka-Angola')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from django.conf import settings

def list_models():
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    genai.configure(api_key=api_key)
    print("Modelos disponíveis:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

if __name__ == "__main__":
    list_models()
