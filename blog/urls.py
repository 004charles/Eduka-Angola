from django.urls import path
from . import views

app_name = 'blog'  

urlpatterns = [
    path('lista_posts/', views.lista_posts, name='lista_posts'),
    path('privacidade/', views.privacidade, name='privacidade'),
    path('categoria/<slug:slug>/', views.posts_por_categoria, name='posts_por_categoria'),
    path('post/<slug:slug>/', views.detalhe_post, name='detalhe_post'), 
    path('post/<slug:slug>/comentar/', views.comentar_post, name='comentar_post'),
    path('comentario/<int:comentario_id>/<str:tipo>/', views.reagir_comentario, name='reagir_comentario'),
    path('tag/<slug:slug>/', views.posts_por_tag, name='posts_por_tag'),
    path('buscar/', views.buscar_posts, name='buscar_posts'),
]
