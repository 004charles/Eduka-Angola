from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/centro/(?P<conversa_id>\w+)/$', consumers.ChatCentroConsumer.as_asgi()),
    re_path(r'ws/chat/aluno/(?P<conversa_id>\w+)/$', consumers.ChatAlunoConsumer.as_asgi()),
]