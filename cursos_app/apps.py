from django.apps import AppConfig

class CursosAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cursos_app'

    def ready(self):
        import cursos_app.signals  
        from . import signals  