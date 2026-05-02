from django.db import models
from cursos_app.models import Instrutor

class InstrutorProxy(Instrutor):
    class Meta:
        proxy = True
        verbose_name = 'Candidatura de Instrutor'
        verbose_name_plural = 'Candidaturas de Instrutores'
        app_label = 'instrutores_app'
