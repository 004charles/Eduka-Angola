from django.urls import path
from . import views



urlpatterns = [
    path('', views.biblioteca, name='biblioteca'),
    path('livro/<int:livro_id>/', views.livro_detalhes, name='livro_detalhes'),
    path('categoria/<int:categoria_id>/', views.livros_por_categoria, name='livros_categoria'),
    path('pesquisar/', views.pesquisar_livros, name='pesquisar_livros'),
    
    # Autenticação e Registro de Bibliotecas
    path('login/', views.login_biblioteca, name='login_biblioteca'),
    path('registro/', views.registro_biblioteca, name='registro_biblioteca'),
    path('valida_cadastro/', views.valida_cadastro_biblioteca, name='valida_cadastro_biblioteca'),
    path('valida_login/', views.valida_login_biblioteca, name='valida_login_biblioteca'),
]