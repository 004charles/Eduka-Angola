from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PagamentoViewSet, WebhookProntuView

router = DefaultRouter()
router.register(r'', PagamentoViewSet, basename='pagamento')
router.register(r'webhook', WebhookProntuView, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
]
