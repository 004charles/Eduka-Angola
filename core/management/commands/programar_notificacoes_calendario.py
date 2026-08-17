from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import FeriadoNacional
from core.notification_events import queue_notification_event


class Command(BaseCommand):
    help = 'Agenda avisos de feriados e datas relevantes próximos.'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=14)

    def handle(self, *args, **options):
        hoje = timezone.localdate()
        limite = hoje + timedelta(days=max(1, min(options['dias'], 90)))
        datas = FeriadoNacional.objects.filter(activo=True, data__range=(hoje, limite))
        total = 0
        for data in datas:
            event_id = f'calendar.notice:{data.data.isoformat()}'
            queue_notification_event(
                'calendar.notice',
                event_id,
                {'title': data.titulo, 'message': data.descricao or f'{data.titulo} acontece em {data.data:%d/%m/%Y}.', 'link': '/calendario'},
                occurred_at=timezone.now(),
            )
            total += 1
        self.stdout.write(f'Avisos de calendário agendados: {total}')
