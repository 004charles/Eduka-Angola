from django.urls import path, include
from usuarios import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('conta_aluno/', views.conta_aluno, name = 'conta_aluno'),
    path('aluno/', views.aluno, name = 'aluno'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('seguir-centro/<int:centro_id>/', views.seguir_centro, name='seguir_centro'),
    path('atualizar_localizacao/', views.atualizar_localizacao, name='atualizar_localizacao'),


    #------------------login---------------------------------
    path('Login_aluno/', views.Login_aluno, name = 'Login_aluno'), 
    path('Login_empresa/', views.Login_empresa, name = 'Login_empresa'), 
    path('user_profile/', views.user_profile, name='user_profile'),
    path('Login_instrutor/', views.Login_instrutor, name = 'Login_instrutor'), 
    path('Login_biblioteca/', views.Login_biblioteca, name = 'Login_biblioteca'),
    path('Login_escola/', views.Login_escola, name = 'Login_escola'), 
    path('logout/', views.Logout, name='Logout'),
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
    path('registro_aluno/', views.Registro_aluno, name='Registro_aluno'),
    path('registro_empresa/', views.Registro_empresa, name='registro_empresa'),
    path('registro_instrutor/', views.Registro_instrutor, name='registro_instrutor'),
    path('registro_biblioteca/', views.registro_biblioteca, name = 'registro_biblioteca'),
    
    #----------------perfil de usuarios--------------------
    path('configuracao_user/', views.configuracao_user, name = 'configuracao_user'),

    
    #----------------redefinir senha--------------------
    path('redefinir_senha/', views.Redefinir_senha, name='redefinir_senha'),
    path('redefinir_senha/solicitacao_enviada/', views.Solicitacao_enviada, name='redefinir_senha/solicitacao_enviada'),
    
    #-----------------------------aluno validacoes-----------------------
    path('valida_cadastro_aluno/', views.valida_cadastro_aluno, name = 'valida_cadastro_aluno'),
    path('valida_login_aluno/', views.valida_login_aluno, name = 'valida_login_aluno'),
    #----------------------------fim validacoes aluno------------------------------
    
    #---------------------------empresa validacoes--------------------------------
    path('valida_cadastro_empresa/', views.valida_cadastro_empresa, name = 'valida_cadastro_empresa'),
    path('valida_login_empresa/', views.valida_login_empresa, name = 'valida_login_empresa'),
    path('valida_cadastro_biblioteca/', views.valida_cadastro_biblioteca, name = 'valida_cadastro_biblioteca'),
    path('valida_login_biblioteca/', views.valida_login_biblioteca, name = 'valida_login_biblioteca'),
]
