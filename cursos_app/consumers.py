import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from .models import Curso, Inscricao, ComentarioCurso
from usuarios.models import Aluno

logger = logging.getLogger(__name__)

class CursoUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'curso_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info("Cliente conectado às atualizações de cursos")

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
        # Enviar atualização de curso para o cliente
        await self.send(text_data=json.dumps({
            'type': 'curso_update',
            'curso_id': event['curso_id'],
            'action': event['action'],
            'data': event['data']
        }))

    async def subscribe_curso(self, curso_id):
        # Adicionar ao grupo específico do curso
        await self.channel_layer.group_add(
            f'curso_{curso_id}',
            self.channel_name
        )

class CursoNotificacoesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Verificar se é um centro logado
        centro_id = await self.get_centro_id_from_session()
        if centro_id:
            self.room_group_name = f'notificacoes_centro_{centro_id}'
        else:
            # Se não for centro, verificar se é aluno
            aluno_id = await self.get_aluno_id_from_session()
            if aluno_id:
                self.room_group_name = f'notificacoes_aluno_{aluno_id}'
            else:
                await self.close()
                return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"Cliente conectado às notificações: {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notificacao_curso(self, event):
        # Enviar notificação para o cliente
        await self.send(text_data=json.dumps({
            'type': 'notificacao_curso',
            'titulo': event['titulo'],
            'mensagem': event['mensagem'],
            'curso_id': event.get('curso_id'),
            'categoria': event.get('categoria', 'info')
        }))

    @database_sync_to_async
    def get_centro_id_from_session(self):
        try:
            session_key = self.scope.get('query_string', b'').decode('utf-8')
            if 'session_key=' in session_key:
                session_key = session_key.split('session_key=')[1].split('&')[0]
                session = Session.objects.get(session_key=session_key)
                session_data = session.get_decoded()
                return session_data.get('centro_id')
        except Exception:
            return None

    @database_sync_to_async
    def get_aluno_id_from_session(self):
        try:
            session_key = self.scope.get('query_string', b'').decode('utf-8')
            if 'session_key=' in session_key:
                session_key = session_key.split('session_key=')[1].split('&')[0]
                session = Session.objects.get(session_key=session_key)
                session_data = session.get_decoded()
                return session_data.get('aluno')
        except Exception:
            return None

class SuporteCursoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.curso_id = self.scope['url_route']['kwargs']['curso_id']
        self.room_group_name = f'suporte_curso_{self.curso_id}'
        
        # Verificar se o usuário tem acesso ao curso
        if await self.tem_acesso_curso():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"Cliente conectado ao suporte do curso {self.curso_id}")
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        mensagem = text_data_json['mensagem']
        usuario_nome = text_data_json.get('usuario_nome', 'Anônimo')
        
        # Salvar mensagem de suporte
        mensagem_id = await self.salvar_mensagem_suporte(mensagem)
        
        # Enviar para o grupo
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
            curso = Curso.objects.get(id=self.curso_id, publicado=True)
            
            # Verificar se é centro dono do curso
            centro_id = self.get_centro_id_from_session()
            if centro_id and curso.centro.id == centro_id:
                return True
            
            # Verificar se é aluno inscrito
            aluno_id = self.get_aluno_id_from_session()
            if aluno_id and Inscricao.objects.filter(curso=curso, aluno_id=aluno_id, ativa=True).exists():
                return True
                
            return False
        except Exception:
            return False

    @database_sync_to_async
    def salvar_mensagem_suporte(self, mensagem):
        # Implementar lógica para salvar mensagens de suporte
        # Por enquanto, retorna um ID simulado
        return 1

class ProgressoCursoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.curso_id = self.scope['url_route']['kwargs']['curso_id']
        self.room_group_name = f'progresso_curso_{self.curso_id}'
        
        if await self.tem_acesso_curso():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

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

class ComentariosCursoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.curso_id = self.scope['url_route']['kwargs']['curso_id']
        self.room_group_name = f'comentarios_curso_{self.curso_id}'
        
        if await self.tem_acesso_curso():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comentario = text_data_json['comentario']
        usuario_id = text_data_json['usuario_id']
        
        comentario_obj = await self.salvar_comentario(comentario, usuario_id)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'novo_comentario',
                'comentario': comentario_obj.texto,
                'usuario_nome': comentario_obj.usuario.nome,
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
            return True
        except Curso.DoesNotExist:
            return False

    @database_sync_to_async
    def salvar_comentario(self, texto, usuario_id):
        # Implementar lógica para salvar comentários
        # Por enquanto, retorna um objeto simulado
        class ComentarioSimulado:
            def __init__(self):
                self.id = 1
                self.texto = texto
                self.data_criacao = timezone.now()
                self.usuario = type('Usuario', (), {'nome': 'Usuário'})()
        
        return ComentarioSimulado()