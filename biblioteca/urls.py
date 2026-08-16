from django.urls import path
from . import views


urlpatterns = [
    path("", views.public_library, name="biblioteca_publica"),
    path("minha/", views.my_library, name="biblioteca_minha"),
    path("<slug:slug>/guardar/", views.toggle_library_book, name="biblioteca_guardar"),
    path("<slug:slug>/ler/", views.read_book, name="biblioteca_ler"),
    path("<slug:slug>/progresso/", views.update_reading_progress, name="biblioteca_progresso"),
    path("<slug:slug>/", views.public_book_detail, name="biblioteca_livro_publico"),
]
