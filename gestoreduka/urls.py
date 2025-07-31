from django.urls import path, include
from gestoreduka import views


urlpatterns = [
    path('dashboard/centro/', views.centro_dashboard, name='centro_dashboard')

]