from django.urls import path
from . import views

app_name = 'instrutores_app'

urlpatterns = [
    path('cadastro/', views.instrutor_signup, name='signup'),
    path('login/', views.instrutor_login, name='login'),
    path('dashboard/', views.instrutor_dashboard, name='dashboard'),
    path('questoes/', views.listar_questoes, name='listar_questoes'),
    path('questoes/responder/<int:questao_id>/', views.responder_questao, name='responder_questao'),
    path('alunos/', views.listar_alunos, name='listar_alunos'),
    path('alunos/enviar-aviso/', views.enviar_aviso, name='enviar_aviso'),
    path('cursos/', views.listar_cursos, name='listar_cursos'),
    path('cursos/novo/', views.criar_curso, name='criar_curso'),
    path('cursos/editar/<int:curso_id>/', views.editar_curso, name='editar_curso'),
    path('cursos/<int:curso_id>/', views.detalhe_curso, name='detalhe_curso'),
    path('cursos/<int:curso_id>/aula/nova/', views.adicionar_aula, name='adicionar_aula'),
    path('aula/editar/<int:aula_id>/', views.editar_aula, name='editar_aula'),
    path('aula/remover/<int:aula_id>/', views.remover_aula, name='remover_aula'),
    path('aula/<int:aula_id>/material/novo/', views.adicionar_material, name='adicionar_material'),
    path('material/remover/<int:material_id>/', views.remover_material, name='remover_material'),
    path('cursos/<int:curso_id>/material-global/novo/', views.adicionar_material_curso, name='adicionar_material_curso'),
    path('material-global/remover/<int:material_id>/', views.remover_material_curso, name='remover_material_curso'),
    path('aula/<int:aula_id>/gerar-exercicio/', views.gerar_exercicio_aula, name='gerar_exercicio_aula'),
    path('curso/<int:curso_id>/gerar-todos-exercicios/', views.gerar_exercicios_curso, name='gerar_exercicios_curso'),
    path('aula/<int:aula_id>/exercicio/', views.gerenciar_exercicio, name='gerenciar_exercicio'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]
