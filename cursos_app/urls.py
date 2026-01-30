from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cursos_app import views


urlpatterns = [
    path('home_cursos/', views.home_cursos, name = 'home_cursos'),
    path('curso_detalhe/<int:id>/', views.curso_detalhe, name='curso_detalhe'),
    path('centro/<int:centro_id>/cursos/', views.cursos_por_centro, name='cursos_por_centro'),
    path('categoria/<slug:slug>/', views.cursos_por_categoria, name='cursos_por_categoria'),
    path('pagina_categoria/', views.pagina_categoria, name = 'pagina_categoria'),
    path('todo_curso/', views.todo_curso, name = 'todo_curso'),
    path('buscar/', views.buscar_cursos, name='buscar_cursos'),
    path('curso/<int:curso_id>/inscrever/', views.inscrever_curso, name='inscrever_curso'),
    path('inscricao/<int:inscricao_id>/status/<str:status>/', views.alterar_status_inscricao, name='alterar_status_inscricao'),
    path('ficha_inscricao/<int:curso_id>/', views.ficha_inscricao, name='ficha_inscricao'),
    path('favorito/<int:curso_id>/', views.adicionar_favorito, name='adicionar_favorito'),
    path('centro/<int:centro_id>/instrutores/', views.instrutores_do_centro, name='instrutores_centro'),
    path('curso/<int:id>/', views.curso_detalhe, name='curso_detalhe'),
    path('curso/<int:curso_id>/avaliar/', views.adicionar_comentario, name='adicionar_comentario'),
    path('comentarios/<int:comentario_id>/excluir/', views.excluir_comentario, name='excluir_comentario'),
    path('comentarios/<int:comentario_id>/denunciar/', views.denunciar_comentario, name='denunciar_comentario'),
    path('', views.catalogo_cursos, name='catalogo_cursos'),

    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
