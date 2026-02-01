from django.urls import path, include
from centro_formacao import views



urlpatterns = [
    path('home_centro/', views.home_centro, name = 'home_centro')
    
]


