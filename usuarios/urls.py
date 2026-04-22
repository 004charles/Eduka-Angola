from django.urls import path, include
from usuarios import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('conta_aluno/', views.conta_aluno, name = 'conta_aluno'),
    path('aluno/', views.aluno_dashboard, name='aluno'),
    path('aluno/dashboard/', views.aluno_dashboard, name='aluno_dashboard'),
    path('aluno/cursos/', views.aluno_cursos, name='aluno_cursos'),
    path('aluno/favoritos/', views.aluno_favoritos, name='aluno_favoritos'),
    path('aluno/depoimento/', views.aluno_depoimento, name='aluno_depoimento'),
    path('aluno/perfil/', views.aluno_perfil, name='aluno_perfil'),
    path('aluno/configuracoes/', views.aluno_configuracoes, name='aluno_configuracoes'),
    path('enviar_depoimento/', views.enviar_depoimento, name='enviar_depoimento'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('atualizar_localizacao/', views.atualizar_localizacao, name='atualizar_localizacao'),
    path('aluno_chat/', views.aluno_chat, name='aluno_chat'),
    path('aluno_chat/mensagens/<int:conversa_id>/ajax/', views.get_mensagens_aluno_ajax, name='get_mensagens_aluno_ajax'),


    #------------------login---------------------------------
    path('login_aluno/', views.login_aluno, name = 'login_aluno'), 
    path('user_profile/', views.user_profile, name='user_profile'),
    path('login_instrutor/', views.login_instrutor, name = 'login_instrutor'), 
    path('logout/', views.logout_usuario, name='logout'),
    path('tipo_user/', views.tipo_user, name = 'tipo_user'),
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url='/admin/password_reset/done/',
        ),
        name='password_reset'
    ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/admin/reset/done/'
        ),
        name='password_reset_confirm'
    ),
    path(
        'admin/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),


    
    
    #------------------Registro-------------------------
    path('registro_aluno/', views.registro_aluno, name='registro_aluno'),
    path('registro_instrutor/', views.registro_instrutor, name='registro_instrutor'),
    
    #----------------perfil de usuarios--------------------
    path('configuracao_user/', views.configuracao_user, name = 'configuracao_user'),

    
    #----------------redefinir senha e verificacao--------------------
    path('esqueci_senha/', views.esqueci_senha, name='esqueci_senha'),
    path('redefinir_senha/', views.redefinir_senha, name='redefinir_senha'),
    path('verificar_email/', views.verificar_email, name='verificar_email'),

    #-----------------------------aluno validacoes-----------------------
    path('valida_cadastro_aluno/', views.valida_cadastro_aluno, name = 'valida_cadastro_aluno'),
    path('valida_login_aluno/', views.valida_login, name = 'valida_login_aluno'),
    #----------------------------fim validacoes aluno------------------------------

    # Link de Compatibilidade para Registro de Centros (caso links antigos tenham sido enviados)
    path('cadastro/confirmar/<uuid:token>/', include('gestoreduka.urls')),
]
