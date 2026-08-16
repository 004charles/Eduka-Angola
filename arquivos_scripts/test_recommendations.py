import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("DATABASE_URL", None)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from cursovideoapp.models import Curso_video
from cursos_app.models import Inscricao

User = get_user_model()
user = User.objects.get(email="muquissizangui@gmail.com")
client = Client()
response = client.get("/api/react/recomendacoes/?limit=4")
print("VISITOR_STATUS", response.status_code)
print("VISITOR_COUNT", len(response.json().get("items", [])))
client.force_login(user)
response = client.get("/api/react/recomendacoes/?limit=4")
payload = response.json()
print("STUDENT_STATUS", response.status_code)
print("PERSONALIZED", payload.get("personalized"))
print("STUDENT_COUNT", len(payload.get("items", [])))
owned_ids = set(Inscricao.objects.filter(aluno=user.aluno_profile, status__in=["A", "P"]).values_list("curso_id", flat=True))
print("EXCLUDED_OWNED", all(item["id"] not in owned_ids for item in payload.get("items", [])))
for item in payload.get("items", []):
    print("ITEM", item["id"], item["titulo"], item["motivo"])
