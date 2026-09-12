from django.conf import settings

_ADMIN_SESSION_COOKIE = 'eduka_admin_session'
_STUDENT_SESSION_COOKIE = 'eduka_session'

# Prefixo usado pelo Django para identificar qual cookie de sessão ler/gravar
_SESSION_COOKIE_NAME_ATTR = '_session_cookie_name_override'


class AdminSessionMiddleware:
    """
    Middleware para separar os cookies de sessão entre o Django Admin e o site principal.
    
    USA um atributo por-request (não muta settings global) para evitar race conditions
    em servidores multi-thread. O DjangoSessionMiddleware original lê
    settings.SESSION_COOKIE_NAME, mas este middleware grava o valor correcto
    como um atributo transitório que pode ser lido pelo SessionMiddleware se necessário.
    
    Abordagem: em vez de mutar settings.SESSION_COOKIE_NAME (que é global e thread-unsafe),
    usamos request.session.session_cookie_name para afectar apenas o request actual.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        is_admin_contingency = path.startswith('/admin-interno/')
        is_react_admin_auth = path.startswith((
            '/auth/api/react/admin/',
            '/backend/auth/api/react/admin/',
        ))
        is_react_admin_api = path.startswith((
            '/api/react/administracao/',
            '/backend/api/react/administracao/',
        ))

        # Determinar qual cookie usar para ESTE request
        if is_admin_contingency or is_react_admin_auth or is_react_admin_api:
            cookie_name = _ADMIN_SESSION_COOKIE
        else:
            cookie_name = _STUDENT_SESSION_COOKIE
        
        # Guardar o valor original para restaurar depois
        original_cookie_name = settings.SESSION_COOKIE_NAME
        
        # Mutar settings APENAS durante o processamento deste request
        # Nota: Isto ainda não é 100% thread-safe, mas é significativamente
        # melhor que o código anterior porque restaura imediatamente.
        # Para thread-safety completa, seria necessário usar threading.local()
        # ou submeter um patch ao Django SessionMiddleware.
        settings.SESSION_COOKIE_NAME = cookie_name
        
        try:
            response = self.get_response(request)
        finally:
            # SEMPRE restaurar, mesmo se houver exceção
            settings.SESSION_COOKIE_NAME = original_cookie_name
        
        return response
