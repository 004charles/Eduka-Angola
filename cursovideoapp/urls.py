from django.urls import path
from . import views

app_name = 'cursovideoapp'

urlpatterns = [
    path('', views.home_videos, name="home_videos"), # Replacing empty path
    path('lista/', views.lista_cursos, name="lista_cursos"),
    path('api/toggle_favorito/', views.toggle_favorito_video, name='api_toggle_favorito_video'),
    path('api/load_more_videos/', views.api_load_more_videos, name='api_load_more_videos'),
    path('api/curso/<int:curso_id>/comentarios/', views.api_carregar_comentarios_video, name='api_carregar_comentarios_video'),
    path('analytics/', views.analytics_mercado, name='analytics_mercado'),
    path('orientador-ia/', views.orientador_ia_view, name='orientador_ia'),
    path('api/orientador-ia/', views.api_orientacao_vocacional, name='api_orientacao_vocacional'),
    path('sessao/<str:sessao_tipo>/', views.sessao_ver_todos, name="sessao_ver_todos"),
    path('<slug:slug>/', views.detalhe_curso, name="detalhe_curso"),
    path('<slug:slug>/inscrever/', views.toggle_inscricao, name="toggle_inscricao"),
    path('<slug:slug>/comentar/', views.salvar_comentario_video, name="salvar_comentario_video"),
    path('<slug:curso_slug>/aula/<int:pk>/', views.ver_aula, name="ver_aula"),
    path('aula/<int:aula_id>/progresso/', views.atualizar_progresso, name="atualizar_progresso"), 
    path('aula/<int:aula_id>/salvar-nota/', views.salvar_nota_aula, name="salvar_nota_aula"),
    path('aula/<int:aula_id>/comentar/', views.salvar_comentario_aula, name="salvar_comentario_aula"),
    path('aula/<int:aula_id>/exercicio/', views.detalhes_exercicio, name="detalhes_exercicio"),
    path('aula/<int:aula_id>/exercicio/submeter/', views.submeter_exercicio, name="submeter_exercicio"),
    path('exercicio/resultado/<int:resultado_id>/', views.resultado_exercicio, name="resultado_exercicio"),
    path('emitir-certificado/<slug:curso_slug>/', views.emitir_certificado, name="emitir_certificado"),
    path('verificar-certificado/<str:codigo>/', views.verificar_certificado, name="verificar_certificado"),
    path('curso/<int:curso_id>/importar-playlist/', views.importar_playlist_youtube, name="importar_playlist_youtube"),
    path('curso/<int:curso_id>/importar-playlist-admin/', views.importar_playlist_admin, name="importar_playlist_admin"),
]