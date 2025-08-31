from django.contrib import admin
from .models import Curso_video, Aula, Categoria
from django.contrib.auth.models import Group


admin.site.register(Curso_video)
admin.site.register(Aula)
admin.site.site_header = "Edukangola"
admin.site.site_title = "Edukangola Administração"
admin.site.index_title = "Administração do Site"
admin.site.unregister(Group)
admin.site.register(Categoria)