from django.urls import path

from . import views

app_name = "eventos_marketplace"

urlpatterns = [
    path("", views.eventos_publicos, name="eventos_publicos"),
    path("meus-bilhetes/", views.meus_bilhetes, name="meus_bilhetes"),
    path("pedido/", views.criar_pedido_bilhete, name="criar_pedido_bilhete"),
    path("<slug:slug>/", views.evento_publico_detalhe, name="evento_publico_detalhe"),
]
path("validar-bilhete/", views.validar_bilhete, name="validar_bilhete"),
