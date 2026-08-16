import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("DATABASE_URL", None)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email="muquissizangui@gmail.com")
client = Client()
client.force_login(user)
response = client.get("/api/react/video-cursos/excel-para-o-dia-a-dia/sala/")
print("STATUS", response.status_code)
payload = response.json()
print("TOP_LEVEL", sorted(payload.keys()))
print("LESSONS", len(payload.get("aulas", [])))
print("AVISOS", len(payload.get("avisos", [])))
print("MATERIAIS", len(payload.get("materiais", [])))
for aula in payload.get("aulas", []):
    print("AULA", aula["id"], "NOTA", bool(aula.get("nota")), "DUVIDAS", len(aula.get("duvidas", [])), "EXERCICIO", bool(aula.get("exercicio")), "MATERIAIS", len(aula.get("materiais", [])))
certificate = client.get("/api/react/video-cursos/excel-para-o-dia-a-dia/certificado/")
print("CERTIFICATE_STATUS", certificate.status_code)
print("CERTIFICATE_KEYS", sorted(certificate.json().keys()))
