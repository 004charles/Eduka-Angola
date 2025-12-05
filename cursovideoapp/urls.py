# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cursos, name="lista_cursos"),
    path('<slug:slug>/', views.detalhe_curso, name="detalhe_curso"),
    path('<slug:slug>/inscrever/', views.toggle_inscricao, name="toggle_inscricao"),
    path('<slug:curso_slug>/aula/<int:pk>/', views.ver_aula, name="ver_aula"),
    path('aula/<int:aula_id>/progresso/', views.atualizar_progresso, name="atualizar_progresso"),
]