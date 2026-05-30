from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [
    path('inscrever/<int:curso_id>/', views.inscrever_curso, name='inscrever-curso'),
    path('centros/buscar/', views.buscar_centros, name='buscar_centros'),
    path('teste-pagamento/', views.teste_pagamento, name='teste_pagamento'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
