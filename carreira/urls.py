from django.urls import path
from . import views

app_name = 'carreira'

urlpatterns = [
    path('vagas/', views.job_board, name='job_board'),
    path('vagas/<slug:slug>/', views.job_detail, name='job_detail'),
    path('vagas/<slug:slug>/candidatar/', views.candidatar_vaga, name='candidatar_vaga'),
]
