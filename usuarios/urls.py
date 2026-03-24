from django.urls import path, include
from usuarios import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('conta_aluno/', views.conta_aluno, name = 'conta_aluno'),
    path('aluno/', views.aluno, name = 'aluno'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('atualizar_localizacao/', views.atualizar_localizacao, name='atualizar_localizacao'),
    path('aluno_chat/', views.aluno_chat, name='aluno_chat'),


    #------------------login---------------------------------
    path('login_aluno/', views.login_aluno, name = 'login_aluno'), 
    path('user_profile/', views.user_profile, name='user_profile'),
    path('login_instrutor/', views.login_instrutor, name = 'login_instrutor'), 
    path('login_escola/', views.login_escola, name = 'login_escola'), 
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
]
