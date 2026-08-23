from django.conf import settings

class AdminSessionMiddleware:
    """
    Middleware para separar os cookies de sessão entre o Django Admin e o site principal.
    Isso permite que um usuário esteja logado como Aluno no frontend e Admin no backend
    ao mesmo tempo no mesmo navegador.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # Guardar o nome do cookie original para restaurar depois
        original_session_cookie = settings.SESSION_COOKIE_NAME
        
        is_admin_contingency = path.startswith('/admin-interno/')
        is_react_admin_auth = path.startswith((
            '/auth/api/react/admin/',
            '/backend/auth/api/react/admin/',
        ))
        is_react_admin_api = path.startswith((
            '/api/react/administracao/',
            '/backend/api/react/administracao/',
        ))

        # O painel React em /admin usa a sessão já criada no antigo acesso
        # administrativo quando ela existe. Desta forma, a migração não obriga
        # a equipa a iniciar uma segunda sessão para consultar o novo painel.
        if is_admin_contingency or is_react_admin_auth or (is_react_admin_api and request.COOKIES.get('eduka_admin_session')):
            settings.SESSION_COOKIE_NAME = 'eduka_admin_session'
        else:
            settings.SESSION_COOKIE_NAME = 'eduka_session'
            
        response = self.get_response(request)
        
        # Restaurar o valor original (importante para ambientes multi-thread)
        settings.SESSION_COOKIE_NAME = original_session_cookie
        
        return response
