from django.urls import path, include
from gestoreduka import views


urlpatterns = [
    path('dashboard/centro/', views.centro_dashboard, name='centro_dashboard'),
    path("cadastro/confirmar/<uuid:token>/", views.confirmar_cadastro, name="confirmar_cadastro"),
    path('login_gestor/', views.login_gestor, name='login_gestor'),
    path('logout_gestor/', views.logout_gestor, name = 'logout_gestor'),
    path('configuracoes/', views.configuracao_gestor, name='configuracao_gestor'),
    path('configuracoes/dados/', views.atualizar_dados_pessoais, name='atualizar_dados_pessoais'),
    path('configuracoes/senha/', views.atualizar_senha, name='atualizar_senha'),
    path('configuracoes/redes-sociais/', views.atualizar_redes_sociais, name='atualizar_redes_sociais'),
    path('configuracoes/upload-imagem/', views.upload_imagem_perfil, name='upload_imagem_perfil'),
    path('configuracoes/upload-banner/', views.upload_banner, name='upload_banner'),
    path('cursos/', views.listar_cursos, name='listar_cursos'),
    path('cursos/criar/', views.criar_curso, name='criar_curso'),
    path('cursos/editar/<int:curso_id>/', views.editar_curso, name='editar_curso'),
    path('cursos/publicar/<int:curso_id>/', views.publicar_curso, name='publicar_curso'),
    path('cursos/despublicar/<int:curso_id>/', views.despublicar_curso, name='despublicar_curso'),
    path('cursos/excluir/<int:curso_id>/', views.excluir_curso, name='excluir_curso'),

]