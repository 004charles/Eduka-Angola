from django.urls import path
from . import views

app_name = 'estagio'

urlpatterns = [
    path('estagios/', views.lista_estagios, name='lista_estagios'),
    path('estagio/<slug:slug>/', views.estagio_detalhe, name='estagio_detalhe'),
]