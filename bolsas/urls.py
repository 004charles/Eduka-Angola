from django.urls import path
from . import views

app_name = 'bolsas'

urlpatterns = [
    path('candidatar/', views.candidatar_bolsa, name='candidatar'),
]
