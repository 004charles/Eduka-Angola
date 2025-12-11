from django.conf import settings

def languages(request):
    return {
        'LANGUAGES': settings.LANGUAGES,
        'CURRENT_LANGUAGE': request.LANGUAGE_CODE,
    }