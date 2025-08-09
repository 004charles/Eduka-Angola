from django.urls import path
from . import views

app_name = 'blog'  

urlpatterns = [
    path('lista_posts/', views.lista_posts, name='lista_posts'),
    path('<slug:slug>/', views.detalhe_post, name='detalhe_post'),
    path('categoria/<slug:slug>/', views.posts_por_categoria, name='posts_por_categoria'),
    path('tag/<slug:slug>/', views.posts_por_tag, name='posts_por_tag'),
    path('buscar/', views.buscar_posts, name='buscar_posts'),
]
