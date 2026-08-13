from rest_framework import authentication, exceptions
from django.utils import timezone
from .models import ClienteAPIKey

class ClienteAPIKeyAuthentication(authentication.BaseAuthentication):
    """
    Classe de autenticação para chaves de API de clientes externos.
    Valida a chave passada no cabeçalho 'Authorization: Api-Key <chave>'.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
            
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'api-key':
            return None
            
        key_value = parts[1]
        try:
            api_key = ClienteAPIKey.objects.get(chave=key_value, ativo=True)
        except ClienteAPIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Chave de API inválida ou inativa.')
            
        # Atualizar a data do último uso
        api_key.ultimo_uso = timezone.now()
        api_key.save(update_fields=['ultimo_uso'])
        
        # Retorna None para o usuário (pois é uma chamada M2M de máquina) e a chave como auth
        return (None, api_key)
