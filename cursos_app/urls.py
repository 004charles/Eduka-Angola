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
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
