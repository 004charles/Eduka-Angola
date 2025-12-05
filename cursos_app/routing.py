from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket para atualizações em tempo real de cursos
    re_path(r'ws/cursos/atualizacoes/$', consumers.CursoUpdatesConsumer.as_asgi()),
    
    # WebSocket para notificações de novos cursos
    re_path(r'ws/cursos/notificacoes/$', consumers.CursoNotificacoesConsumer.as_asgi()),
    
    # WebSocket para chat de suporte técnico dos cursos
    re_path(r'ws/cursos/suporte/(?P<curso_id>\w+)/$', consumers.SuporteCursoConsumer.as_asgi()),
    
    # WebSocket para atualizações de progresso do aluno
    re_path(r'ws/cursos/progresso/(?P<curso_id>\w+)/$', consumers.ProgressoCursoConsumer.as_asgi()),
    
    # WebSocket para comentários e discussões do curso
    re_path(r'ws/cursos/comentarios/(?P<curso_id>\w+)/$', consumers.ComentariosCursoConsumer.as_asgi()),
]