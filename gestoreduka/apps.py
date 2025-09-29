from django.apps import AppConfig


class GestoredukaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestoreduka'


    def ready(self):
        import gestoreduka.signals  # 🔥 garante que os signals são registrados


