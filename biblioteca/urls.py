from django.urls import path
from . import views


urlpatterns = [
    path('biblioteca/', views.biblioteca, name = 'biblioteca'),
    path('livro/<int:livro_id>/', views.livro_detalhes, name='livro_detalhes'),
    path('categoria/<int:categoria_id>/', views.livros_por_categoria, name='livros_categoria'),
    path('pesquisar/', views.pesquisar_livros, name='pesquisar_livros'),
]