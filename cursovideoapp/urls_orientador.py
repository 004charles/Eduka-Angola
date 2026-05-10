from django.urls import path
from . import views

urlpatterns = [
    path('', views.orientador_ia_view, name='orientador_ia_root'),
]
