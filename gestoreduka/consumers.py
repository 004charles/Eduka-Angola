import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from .models import Conversa, Mensagem, CentroDeFormacao
from usuarios.models import Aluno

logger = logging.getLogger(__name__)

class ChatCentroConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversa_id = self.scope['url_route']['kwargs']['conversa_id']
        self.room_group_name = f'chat_centro_{self.conversa_id}'
        
        # Obter session key da query string ou do scope
        session_key = self.scope.get('query_string', b'').decode('utf-8')
        if 'session_key=' in session_key:
            session_key = session_key.split('session_key=')[1].split('&')[0]
        
        try:
            # Verificar se o centro tem permissão para acessar esta conversa
            centro_id = await self.get_centro_id_from_session(session_key)
            if not centro_id:
                await self.close()
                return
                
            centro = await self.get_centro(centro_id)
            conversa = await self.get_conversa_centro(self.conversa_id, centro)
            
            # Entrar no grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"Centro {centro.nome} conectado ao chat {self.conversa_id}")
            
        except Exception as e:
            logger.error(f"Erro na conexão WebSocket do centro: {e}")
            await self.close()

    async def disconnect(self, close_code):
        # Sair do grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Conexão WebSocket fechada: {close_code}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            mensagem = text_data_json['mensagem']
            tipo = text_data_json.get('tipo', 'TEXTO')
            
            # Obter session key
            session_key = self.scope.get('query_string', b'').decode('utf-8')
            if 'session_key=' in session_key:
                session_key = session_key.split('session_key=')[1].split('&')[0]
            
            # Salvar mensagem no banco
            centro_id = await self.get_centro_id_from_session(session_key)
            if centro_id:
                mensagem_obj = await self.save_mensagem_centro(mensagem, tipo, centro_id)
                
                # Enviar mensagem para o grupo
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'mensagem': mensagem,
                        'remetente_nome': mensagem_obj.remetente_centro.nome,
                        'is_centro': True,
                        'data_envio': mensagem_obj.data_envio.strftime('%H:%M'),
                        'mensagem_id': mensagem_obj.id
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao receber mensagem: {e}")

    async def chat_message(self, event):
        # Enviar mensagem para WebSocket
        await self.send(text_data=json.dumps({
            'mensagem': event['mensagem'],
            'remetente_nome': event['remetente_nome'],
            'is_centro': event['is_centro'],
            'data_envio': event['data_envio'],
            'mensagem_id': event['mensagem_id']
        }))

    @database_sync_to_async
    def get_centro_id_from_session(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            return session_data.get('centro_id')
        except Session.DoesNotExist:
            return None

    @database_sync_to_async
    def get_centro(self, centro_id):
        return CentroDeFormacao.objects.get(id=centro_id, ativo=True)

    @database_sync_to_async
    def get_conversa_centro(self, conversa_id, centro):
        return Conversa.objects.get(id=conversa_id, centro=centro)

    @database_sync_to_async
    def save_mensagem_centro(self, mensagem_texto, tipo, centro_id):
        centro = CentroDeFormacao.objects.get(id=centro_id)
        conversa = Conversa.objects.get(id=self.conversa_id)
        
        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente_centro=centro,
            mensagem=mensagem_texto,
            tipo=tipo
        )
        
        # Atualizar última mensagem
        conversa.ultima_mensagem = mensagem.data_envio
        conversa.save()
        
        return mensagem

class ChatAlunoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversa_id = self.scope['url_route']['kwargs']['conversa_id']
        self.room_group_name = f'chat_aluno_{self.conversa_id}'
        
        # Obter session key da query string
        session_key = self.scope.get('query_string', b'').decode('utf-8')
        if 'session_key=' in session_key:
            session_key = session_key.split('session_key=')[1].split('&')[0]
        
        try:
            # Verificar se o aluno tem permissão
            aluno_id = await self.get_aluno_id_from_session(session_key)
            if not aluno_id:
                await self.close()
                return
                
            aluno = await self.get_aluno(aluno_id)
            conversa = await self.get_conversa_aluno(self.conversa_id, aluno)
            
            # Entrar no grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"Aluno {aluno.nome} conectado ao chat {self.conversa_id}")
            
        except Exception as e:
            logger.error(f"Erro na conexão WebSocket do aluno: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            mensagem = text_data_json['mensagem']
            tipo = text_data_json.get('tipo', 'TEXTO')
            
            # Obter session key
            session_key = self.scope.get('query_string', b'').decode('utf-8')
            if 'session_key=' in session_key:
                session_key = session_key.split('session_key=')[1].split('&')[0]
            
            # Salvar mensagem no banco
            aluno_id = await self.get_aluno_id_from_session(session_key)
            if aluno_id:
                mensagem_obj = await self.save_mensagem_aluno(mensagem, tipo, aluno_id)
                
                # Enviar mensagem para o grupo
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'mensagem': mensagem,
                        'remetente_nome': mensagem_obj.remetente_aluno.nome,
                        'is_centro': False,
                        'data_envio': mensagem_obj.data_envio.strftime('%H:%M'),
                        'mensagem_id': mensagem_obj.id
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao receber mensagem do aluno: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'mensagem': event['mensagem'],
            'remetente_nome': event['remetente_nome'],
            'is_centro': event['is_centro'],
            'data_envio': event['data_envio'],
            'mensagem_id': event['mensagem_id']
        }))

    @database_sync_to_async
    def get_aluno_id_from_session(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            return session_data.get('aluno')
        except Session.DoesNotExist:
            return None

    @database_sync_to_async
    def get_aluno(self, aluno_id):
        return Aluno.objects.get(id=aluno_id, ativo=True)

    @database_sync_to_async
    def get_conversa_aluno(self, conversa_id, aluno):
        return Conversa.objects.get(id=conversa_id, aluno=aluno)

    @database_sync_to_async
    def save_mensagem_aluno(self, mensagem_texto, tipo, aluno_id):
        aluno = Aluno.objects.get(id=aluno_id)
        conversa = Conversa.objects.get(id=self.conversa_id)
        
        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente_aluno=aluno,
            mensagem=mensagem_texto,
            tipo=tipo
        )
        
        # Atualizar última mensagem
        conversa.ultima_mensagem = mensagem.data_envio
        conversa.save()
        
        return mensagem