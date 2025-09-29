from django.urls import path, include
from gestoreduka import views


urlpatterns = [
    path('dashboard/centro/', views.centro_dashboard, name='centro_dashboard'),
    path("cadastro/confirmar/<uuid:token>/", views.confirmar_cadastro, name="confirmar_cadastro"),
    path('login_gestor/', views.login_gestor, name='login_gestor'),

]