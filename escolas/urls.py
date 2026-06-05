from django.urls import path
from . import views

app_name = 'escolas'

urlpatterns = [
    # Public views
    path('', views.lista_escolas, name='lista_escolas'),
    path('perfil/<int:pk>/', views.perfil_escola, name='perfil_escola'),
    path('orientacao/', views.onboarding_escolar, name='onboarding_escolar'),
    path('orientacao/resultado/', views.resultado_orientacao, name='resultado_orientacao'),
    
    # Admin staff views
    path('admin/', views.admin_escolas, name='admin_escolas'),
    path('admin/criar/', views.admin_criar_escola, name='admin_criar_escola'),
    path('admin/<int:pk>/editar/', views.admin_editar_escola, name='admin_editar_escola'),
    
    # Representante views
    path('representante/dashboard/', views.dashboard_representante, name='dashboard_representante'),
    path('representante/<int:escola_id>/dashboard/', views.dashboard_representante, name='dashboard_representante_escola'),
    path('representante/<int:escola_id>/info/', views.editar_info_escola, name='editar_info_escola'),
    path('representante/<int:escola_id>/perfil/', views.editar_perfil_escola, name='editar_perfil_escola'),
    
    # Cursos
    path('representante/<int:escola_id>/cursos/', views.gerenciar_cursos, name='gerenciar_cursos'),
    path('representante/<int:escola_id>/cursos/adicionar/', views.adicionar_curso, name='adicionar_curso'),
    path('representante/<int:escola_id>/cursos/<int:curso_id>/editar/', views.editar_curso, name='editar_curso'),
    path('representante/<int:escola_id>/cursos/<int:curso_id>/deletar/', views.deletar_curso, name='deletar_curso'),
    
    # Galeria
    path('representante/<int:escola_id>/galeria/', views.galeria_escola, name='galeria_escola'),
    path('representante/<int:escola_id>/galeria/<int:imagem_id>/deletar/', views.deletar_imagem, name='deletar_imagem'),
    
    # Parcerias
    path('representante/<int:escola_id>/parcerias/', views.parcerias_escola, name='parcerias_escola'),
    path('representante/<int:escola_id>/parcerias/<int:parceria_id>/editar/', views.editar_parceria, name='editar_parceria'),
    path('representante/<int:escola_id>/parcerias/<int:parceria_id>/deletar/', views.deletar_parceria, name='deletar_parceria'),
]
