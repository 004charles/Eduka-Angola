from django.urls import path

from . import views

app_name = "eventos_marketplace"

urlpatterns = [
    path("", views.eventos_publicos, name="eventos_publicos"),
    path("meus-bilhetes/", views.meus_bilhetes, name="meus_bilhetes"),
    path("pedido/", views.criar_pedido_bilhete, name="criar_pedido_bilhete"),
    path("validar-bilhete/", views.validar_bilhete, name="validar_bilhete"),
    path("<slug:slug>/", views.evento_publico_detalhe, name="evento_publico_detalhe"),
    # Management APIs
    path("gestao/", views.gestao_eventos_lista, name="gestao_eventos_lista"),
    path("gestao/criar/", views.gestao_evento_criar, name="gestao_evento_criar"),
    path("gestao/<int:evento_id>/", views.gestao_evento_dashboard, name="gestao_evento_dashboard"),
    path("gestao/<int:evento_id>/atualizar/", views.gestao_evento_update, name="gestao_evento_update"),
    path("gestao/<int:evento_id>/capa/", views.gestao_evento_upload_capa, name="gestao_evento_upload_capa"),
    path("gestao/<int:evento_id>/lotes/", views.gestao_evento_lotes, name="gestao_evento_lotes"),
    path("gestao/<int:evento_id>/lotes/<int:lote_id>/", views.gestao_evento_lote_detail, name="gestao_evento_lote_detail"),
    path("gestao/<int:evento_id>/vendas/", views.gestao_evento_vendas, name="gestao_evento_vendas"),
    path("gestao/<int:evento_id>/participantes/", views.gestao_evento_participantes, name="gestao_evento_participantes"),
]
