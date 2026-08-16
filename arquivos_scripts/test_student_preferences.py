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
from cursos_app.models import Categoria

User = get_user_model()
user = User.objects.get(email="muquissizangui@gmail.com")
client = Client()
print("VISITOR_STATUS", client.get("/auth/api/react/aluno/preferencias/").status_code)
client.force_login(user)
response = client.get("/auth/api/react/aluno/preferencias/")
payload = response.json()
print("GET_STATUS", response.status_code)
print("CATEGORY_COUNT", len(payload.get("categorias", [])))
category = Categoria.objects.order_by("id").first()
body = {**payload["preferencias"], "categoria_ids": [category.id], "modalidades": ["ONLINE"], "objectivos": ["Emprego e carreira"], "disponibilidades": ["Noite"], "provincias": [], "faixa_preco": "QUALQUER", "quer_certificado": True}
response = client.post("/auth/api/react/aluno/preferencias/actualizar/", data=json.dumps(body), content_type="application/json")
print("POST_STATUS", response.status_code)
print("POST_OK", response.json().get("ok"))
response = client.get("/auth/api/react/aluno/preferencias/")
updated = response.json().get("preferencias", {})
print("PERSISTED", updated.get("categoria_ids") == [category.id] and updated.get("modalidades") == ["ONLINE"] and updated.get("quer_certificado") is True)
