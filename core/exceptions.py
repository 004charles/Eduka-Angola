from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

def custom_exception_handler(exc, context):
    # Primeiro, chama o exception handler padrão do DRF para obter a resposta padrão
    response = exception_handler(exc, context)

    # Se a resposta do DRF existir
    if response is not None:
        custom_data = {
            'status': 'error',
            'message': 'Ocorreu um erro de validação ou de processamento da requisição.',
            'details': response.data
        }
        
        # Obter mensagens mais amigáveis se possível
        if isinstance(response.data, dict) and 'detail' in response.data:
            custom_data['message'] = response.data['detail']
            
        response.data = custom_data
    else:
        # Se for um erro do banco de dados (ex: chaves únicas duplicadas)
        if isinstance(exc, IntegrityError):
            custom_data = {
                'status': 'error',
                'message': 'Erro de integridade dos dados. Verifique se o registro já existe.',
                'details': str(exc)
            }
            return Response(custom_data, status=status.HTTP_400_BAD_REQUEST)
            
        # Caso geral de erro do servidor
        custom_data = {
            'status': 'error',
            'message': 'Ocorreu um erro interno no servidor. Tente novamente mais tarde.',
            'details': str(exc)
        }
        return Response(custom_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
