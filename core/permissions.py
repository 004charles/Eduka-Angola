from rest_framework import permissions
from .models import ClienteAPIKey

class HasClienteAPIKey(permissions.BasePermission):
    """
    Permissão que valida se a chamada foi autenticada via Chave de API válida.
    """
    def has_permission(self, request, view):
        return isinstance(request.auth, ClienteAPIKey)

class HasAPIKeyOrAuthenticated(permissions.BasePermission):
    """
    Permissão que permite acesso se o usuário estiver autenticado (JWT)
    OU se a requisição possuir uma Chave de API de cliente válida.
    """
    def has_permission(self, request, view):
        # 1. Verificar se é um usuário autenticado normal (JWT)
        if request.user and request.user.is_authenticated:
            return True
            
        # 2. Verificar se foi autenticado via chave de API de máquina
        return isinstance(request.auth, ClienteAPIKey)
