# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_videos, name="home_videos"), # Replacing empty path
    path('lista/', views.lista_cursos, name="lista_cursos"),
    path('api/toggle_favorito/', views.toggle_favorito_video, name='api_toggle_favorito_video'),
    path('api/load_more_videos/', views.api_load_more_videos, name='api_load_more_videos'),
    path('<slug:slug>/', views.detalhe_curso, name="detalhe_curso"),
    path('<slug:slug>/inscrever/', views.toggle_inscricao, name="toggle_inscricao"),
    path('<slug:slug>/comentar/', views.salvar_comentario_video, name="salvar_comentario_video"),
    path('<slug:curso_slug>/aula/<int:pk>/', views.ver_aula, name="ver_aula"),
    path('aula/<int:aula_id>/progresso/', views.atualizar_progresso, name="atualizar_progresso"),
]