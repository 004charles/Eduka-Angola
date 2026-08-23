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
        
        if path.startswith('/admin-interno/'):
            settings.SESSION_COOKIE_NAME = 'eduka_admin_session'
        else:
            settings.SESSION_COOKIE_NAME = 'eduka_session'
            
        response = self.get_response(request)
        
        # Restaurar o valor original (importante para ambientes multi-thread)
        settings.SESSION_COOKIE_NAME = original_session_cookie
        
        return response
