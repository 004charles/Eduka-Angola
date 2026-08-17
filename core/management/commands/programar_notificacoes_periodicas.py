from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.notification_events import queue_notification_event
from cursovideoapp.models import ProgressoAula


class Command(BaseCommand):
    help = 'Agenda eventos periódicos de resumo e continuidade de aprendizagem.'

    def add_arguments(self, parser):
        parser.add_argument('--tipo', choices=('semanal', 'aprendizagem'), required=True)

    def handle(self, *args, **options):
        if options['tipo'] == 'semanal':
            self._weekly()
        else:
            self._learning()

    def _weekly(self):
        now = timezone.now()
        iso_year, iso_week, _ = now.isocalendar()
        event_id = f'weekly.digest:{iso_year}-W{iso_week:02d}'
        queue_notification_event(
            'weekly.digest.requested',
            event_id,
            {'title': 'Novidades da semana', 'message': 'Veja os cursos, turmas, livros e eventos que podem ajudar no seu próximo passo.', 'link': '/cursos'},
            occurred_at=now,
        )
        self.stdout.write(f'Resumo semanal agendado: {event_id}')

    def _learning(self):
        cutoff = timezone.now() - timedelta(days=7)
        alunos = ProgressoAula.objects.filter(concluida=False, data_ultimo_acesso__lte=cutoff).values_list('aluno_id', flat=True).distinct()
        total = 0
        for aluno_id in alunos:
            event_id = f'learning.reminder:{aluno_id}:{cutoff.date().isoformat()}'
            queue_notification_event(
                'learning.reminder',
                event_id,
                {'recipient_id': aluno_id, 'title': 'Retome a sua aprendizagem', 'message': 'Tem uma aula por concluir. Reserve alguns minutos para continuar de onde parou.', 'link': '/aluno'},
                occurred_at=timezone.now(),
            )
            total += 1
        self.stdout.write(f'Lembretes de aprendizagem agendados: {total}')
