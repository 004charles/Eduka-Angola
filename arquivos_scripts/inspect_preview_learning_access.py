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
print("STUDENTS")
for user in User.objects.filter(tipo_usuario="ALUNO").order_by("id")[:10]:
    print(user.id, user.email, user.nome, user.is_active)
print("VIDEO_COURSES")
for course in Curso_video.objects.all().order_by("id")[:10]:
    print(course.id, course.slug, course.titulo, course.is_gratuito, course.aulas.count())
