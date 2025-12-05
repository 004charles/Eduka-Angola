import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Configure Django settings primeiro
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

# Importe o routing após o Django estar configurado
from gestoreduka import routing as gestoreduka_routing
from cursos_app import routing as cursos_routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                gestoreduka_routing.websocket_urlpatterns + 
                cursos_routing.websocket_urlpatterns
            )
        )
    ),
})