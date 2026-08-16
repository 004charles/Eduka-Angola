import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("DATABASE_URL", None)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from cursos_app.models import Curso, Favorito

User = get_user_model()
user = User.objects.get(email="muquissizangui@gmail.com")
course = Curso.objects.filter(publicado=True, ativo=True).order_by("id").first()
Favorito.objects.filter(aluno=user.aluno_profile, curso=course).delete()
client = Client(enforce_csrf_checks=True)
print("VISITOR_STATUS", client.get("/auth/api/react/aluno/favoritos/").status_code)
client.force_login(user)
client.get("/auth/api/react/aluno/favoritos/")
csrf = client.cookies.get("csrftoken").value
body = json.dumps({"curso_id": course.id})
first = client.post("/auth/api/react/aluno/favoritos/alternar/", data=body, content_type="application/json", HTTP_X_CSRFTOKEN=csrf)
print("SAVE_STATUS", first.status_code, "SAVED", first.json().get("favorito"))
listing = client.get("/auth/api/react/aluno/favoritos/").json()
print("LISTED", course.id in listing.get("favorito_ids", []))
second = client.post("/auth/api/react/aluno/favoritos/alternar/", data=body, content_type="application/json", HTTP_X_CSRFTOKEN=csrf)
print("REMOVE_STATUS", second.status_code, "REMOVED", second.json().get("favorito") is False)
print("FINAL_COUNT", Favorito.objects.filter(aluno=user.aluno_profile, curso=course).count())
