class PermissionsPolicyMiddleware:
    """Explicita que a aplicação pode pedir geolocalização ao próprio navegador."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault("Permissions-Policy", "geolocation=(self)")
        return response
