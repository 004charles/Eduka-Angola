from django.urls import path

from . import views

app_name = "eventos_marketplace"

urlpatterns = [
    path("", views.eventos_publicos, name="eventos_publicos"),
    path("pedido/", views.criar_pedido_bilhete, name="criar_pedido_bilhete"),
    path("<slug:slug>/", views.evento_publico_detalhe, name="evento_publico_detalhe"),
]
