from django.urls import path

from . import views


urlpatterns = [
    path("", views.catalogo_publico, name="mercado_catalogo_publico"),
    path("produtos/<slug:slug>/", views.produto_publico, name="mercado_produto_publico"),
    path("pedidos/", views.criar_pedido, name="mercado_criar_pedido"),
    path("pedidos/meus/", views.meus_pedidos, name="mercado_meus_pedidos"),
    path("pedidos/<str:referencia>/pagar/", views.iniciar_pagamento, name="mercado_iniciar_pagamento"),
]
