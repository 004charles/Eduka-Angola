from django.urls import path, include
from usuarios import views


urlpatterns = [
    path('conta_aluno/', views.conta_aluno, name = 'conta_aluno'),
    path('aluno/', views.aluno, name = 'aluno'),
    #------------------login---------------------------------
    path('Login_aluno/', views.Login_aluno, name = 'Login_aluno'), 
    path('Login_empresa/', views.Login_empresa, name = 'Login_empresa'), 
    path('Login_instrutor/', views.Login_instrutor, name = 'Login_instrutor'), 
    path('Login_biblioteca/', views.Login_biblioteca, name = 'Login_biblioteca'),
    path('Login_escola/', views.Login_escola, name = 'Login_escola'), 
    path('logout/', views.Logout, name='Logout'),
    path('tipo_user/', views.tipo_user, name = 'tipo_user'),

    
    
    #------------------Registro-------------------------
    path('registro_aluno/', views.Registro_aluno, name='Registro_aluno'),
    path('registro_empresa/', views.Registro_empresa, name='registro_empresa'),
    path('registro_instrutor/', views.Registro_instrutor, name='registro_instrutor'),
    path('registro_biblioteca/', views.registro_biblioteca, name = 'registro_biblioteca'),
    
    
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
