import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("DATABASE_URL", None)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django
django.setup()
from django.contrib.auth import get_user_model
from cursovideoapp.models import Curso_video

User = get_user_model()
user = User.objects.get(email="muquissizangui@gmail.com", is_active=True)
aluno = user.aluno_profile
curso = Curso_video.objects.get(slug="excel-para-o-dia-a-dia")
curso.inscritos.add(aluno)
print("EMAIL", user.email)
print("ALUNO_ID", aluno.id)
print("COURSE_SLUG", curso.slug)
print("COURSE_TITLE", curso.titulo)
print("HAS_ACCESS", curso.inscritos.filter(pk=aluno.pk).exists())
print("LEARNING_URL", f"/aprender/video/{curso.slug}")
