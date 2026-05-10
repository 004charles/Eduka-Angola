from django.apps import AppConfig


class CarreiraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carreira'

    def ready(self):
        import carreira.signals
