import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser
from .models import Curso, Inscricao, ComentarioCurso
from usuarios.models import Aluno

logger = logging.getLogger(__name__)


async def _get_user_from_scope(scope):
    """Extrai o usuário do scope usando cookie-based session (não query string)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    cookies = scope.get('cookies', {})
    
    # Tentar session cookie do admin
    session_key = cookies.get('eduka_admin_session') or cookies.get('eduka_session')
    
    if not session_key:
        # Fallback: tentar do query string (DEPRECATED — manter para retrocompatibilidade)
        qs = scope.get('query_string', b'').decode('utf-8', errors='ignore')
        if 'session_key=' in qs:
            session_key = qs.split('session_key=')[1].split('&')[0]
            logger.warning("WebSocket: session_key via query string (deprecated)")
    
    if not session_key:
        return AnonymousUser(), None, None
    
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            user = await database_sync_to_async(User.objects.get)(id=user_id)
            centro_id = session_data.get('centro_id')
            aluno_id = session_data.get('aluno')
            return user, centro_id, aluno_id
    except Exception:
        pass
    
    return AnonymousUser(), None, None


class CursoUpdatesConsumer(AsyncWebsocketConsumer):
    """Consumer para atualizações de cursos — requer autenticação."""
    
    async def connect(self):
        self.user, _, _ = await _get_user_from_scope(self.scope)
        
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        self.room_group_name = 'curso_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket curso_updates: user={self.user.id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'subscribe_curso':
            curso_id = text_data_json.get('curso_id')
            await self.subscribe_curso(curso_id)

    async def curso_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'curso_update',
            'curso_id': event['curso_id'],
            'action': event['action'],
            'data': event['data']
        }))

    async def subscribe_curso(self, curso_id):
        await self.channel_layer.group_add(
            f'curso_{curso_id}',
            self.channel_name
        )


class CursoNotificacoesConsumer(AsyncWebsocketConsumer):
    """Consumer para notificações — requer autenticação via session cookie."""
    
    async def connect(self):
        self.user, self.centro_id, self.aluno_id = await _get_user_from_scope(self.scope)
        
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        if self.centro_id:
            self.room_group_name = f'notificacoes_centro_{self.centro_id}'
        elif self.aluno_id:
            self.room_group_name = f'notificacoes_aluno_{self.aluno_id}'
        else:
            await self.close(code=4001)
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket notificações: {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notificacao_curso(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notificacao_curso',
            'titulo': event['titulo'],
            'mensagem': event['mensagem'],
            'curso_id': event.get('curso_id'),
            'categoria': event.get('categoria', 'info')
        }))


class SuporteCursoConsumer(AsyncWebsocketConsumer):
    """Consumer de suporte — requer autenticação + inscrito no curso ou dono."""
    
    async def connect(self):
        self.curso_id = self.scope['url_route']['kwargs']['curso_id']
        self.room_group_name = f'suporte_curso_{self.curso_id}'
        
        self.user, self.centro_id, self.aluno_id = await _get_user_from_scope(self.scope)
        
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        if await self.tem_acesso_curso():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"WebSocket suporte curso {self.curso_id}: user={self.user.id}")
        else:
            await self.close(code=4003)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        mensagem = text_data_json['mensagem']
        usuario_nome = self.user.nome or 'Anônimo'
        
        mensagem_id = await self.salvar_mensagem_suporte(mensagem)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'mensagem_suporte',
                'mensagem': mensagem,
                'usuario_nome': usuario_nome,
                'mensagem_id': mensagem_id,
                'timestamp': text_data_json.get('timestamp')
            }
        )

    async def mensagem_suporte(self, event):
        await self.send(text_data=json.dumps({
            'type': 'mensagem_suporte',
            'mensagem': event['mensagem'],
            'usuario_nome': event['usuario_nome'],
            'mensagem_id': event['mensagem_id'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def tem_acesso_curso(self):
        try:
            curso = Curso.objects.get(id=self.centro_id or 0) or Curso.objects.get(id=self.curso_id)
            curso = Curso.objects.get(id=self.curso_id)
            
            # Centro dono do curso
            if self.centro_id and curso.centro_id == self.centro_id:
                return True
            
            # Aluno inscrito
            if self.aluno_id and Inscricao.objects.filter(
                curso=curso, aluno_id=self.aluno_id, status='A'
            ).exists():
                return True
            
            return False
        except Exception:
            return False

    @database_sync_to_async
    def salvar_mensagem_suporte(self, mensagem):
        return 1


class ProgressoCursoConsumer(AsyncWebsocketConsumer):
    """Consumer de progresso — requer autenticação + inscrito no curso."""
    
    async def connect(self):
        self.curso_id = self.scope['url_route']['kwargs']['curso_id']
        self.room_group_name = f'progresso_curso_{self.curso_id}'
        
        self.user, self.centro_id, self.aluno_id = await _get_user_from_scope(self.scope)
        
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        if await self.tem_acesso_curso():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close(code=4003)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def atualizacao_progresso(self, event):
        await self.send(text_data=json.dumps({
            'type': 'atualizacao_progresso',
            'aluno_id': event['aluno_id'],
            'progresso': event['progresso'],
            'modulo_completo': event.get('modulo_completo'),
            'curso_id': event['curso_id']
        }))

    @database_sync_to_async
    def tem_acesso_curso(self):
        try:
            curso = Curso.objects.get(id=self.curso_id)
            if self.aluno_id and Inscricao.objects.filter(
                curso=curso, aluno_id=self.aluno_id, status='A'
            ).exists():
                return True
            if self.centro_id and curso.centro_id == self.centro_id:
                return True
            return False
        except Exception:
            return False


class ComentariosCursoConsumer(AsyncWebsocketConsumer):
    """Consumer de comentários — requer autenticação + acesso ao curso."""
    
    async def connect(self):
        self.curso_id = self.scope['url_route']['kwargs']['curso_id']
        self.room_group_name = f'comentarios_curso_{self.curso_id}'
        
        self.user, self.centro_id, self.aluno_id = await _get_user_from_scope(self.scope)
        
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        if await self.tem_acesso_curso():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close(code=4003)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comentario = text_data_json['comentario']
        
        comentario_obj = await self.salvar_comentario(comentario)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'novo_comentario',
                'comentario': comentario_obj.texto,
                'usuario_nome': self.user.nome or 'Anônimo',
                'timestamp': comentario_obj.data_criacao.isoformat(),
                'comentario_id': comentario_obj.id
            }
        )

    async def novo_comentario(self, event):
        await self.send(text_data=json.dumps({
            'type': 'novo_comentario',
            'comentario': event['comentario'],
            'usuario_nome': event['usuario_nome'],
            'timestamp': event['timestamp'],
            'comentario_id': event['comentario_id']
        }))

    @database_sync_to_async
    def tem_acesso_curso(self):
        try:
            curso = Curso.objects.get(id=self.curso_id, publicado=True)
            # Centro dono
            if self.centro_id and curso.centro_id == self.centro_id:
                return True
            # Aluno inscrito
            if self.aluno_id and Inscricao.objects.filter(
                curso=curso, aluno_id=self.aluno_id, status='A'
            ).exists():
                return True
            return False
        except Curso.DoesNotExist:
            return False

    @database_sync_to_async
    def salvar_comentario(self, texto):
        from django.utils import timezone as _tz
        
        class ComentarioSimulado:
            def __init__(self):
                self.id = 1
                self.texto = texto
                self.data_criacao = _tz.now()
                self.usuario = type('Usuario', (), {'nome': 'Usuário'})()
        
        return ComentarioSimulado()
