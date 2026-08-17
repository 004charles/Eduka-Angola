from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import EventoNotificacaoOutbox
from core.notification_events import NotificationEventPublishError, publish_notification_event


class Command(BaseCommand):
    help = 'Publica eventos pendentes no serviço separado de notificações.'

    def add_arguments(self, parser):
        parser.add_argument('--limite', type=int, default=50)

    def handle(self, *args, **options):
        limite = max(1, min(options['limite'], 200))
        eventos = EventoNotificacaoOutbox.objects.filter(publicado_em__isnull=True).order_by('criado_em')[:limite]
        publicados = 0
        falhados = 0
        for evento in eventos:
            try:
                resultado = publish_notification_event(
                    evento.event_type,
                    evento.event_id,
                    evento.payload,
                    occurred_at=evento.occurred_at,
                )
                if resultado.get('disabled'):
                    self.stderr.write(self.style.WARNING('Serviço de notificações não configurado; eventos permanecem pendentes.'))
                    break
            except NotificationEventPublishError as exc:
                evento.tentativas += 1
                evento.ultimo_erro = str(exc)[:4000]
                evento.save(update_fields=['tentativas', 'ultimo_erro'])
                falhados += 1
                self.stderr.write(self.style.WARNING(f'Falha em {evento.event_id}: {exc}'))
                continue
            evento.publicado_em = timezone.now()
            evento.tentativas += 1
            evento.ultimo_erro = ''
            evento.save(update_fields=['publicado_em', 'tentativas', 'ultimo_erro'])
            publicados += 1
        self.stdout.write(f'Eventos publicados: {publicados}; falhas: {falhados}.')
