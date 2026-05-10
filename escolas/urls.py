from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_escolas, name='lista_escolas'),
    path('orientacao/', views.onboarding_escolar, name='onboarding_escolar'),
    path('orientacao/resultado/', views.resultado_orientacao, name='resultado_orientacao'),
    path('perfil/<int:pk>/', views.perfil_escola, name='perfil_escola'),
]
