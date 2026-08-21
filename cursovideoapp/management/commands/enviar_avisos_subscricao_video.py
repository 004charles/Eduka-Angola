from django.core.management.base import BaseCommand

from cursovideoapp.subscription_notifications import processar_avisos_expiracao_subscricao_video


class Command(BaseCommand):
    help = 'Envia os avisos de 7 dias, 3 dias e 24 horas antes do fim de subscrições de vídeo.'

    def handle(self, *args, **options):
        resultado = processar_avisos_expiracao_subscricao_video()
        self.stdout.write(self.style.SUCCESS(
            'Avisos de subscrição processados: '
            f"{resultado['avisos_criados']} novos, {resultado['notificacoes_plataforma']} na plataforma, "
            f"{resultado['emails_enviados']} e-mails enviados, {resultado['emails_falhados']} falhados."
        ))
