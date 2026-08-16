import os
from datetime import date, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from django.db import transaction
from cursos_app.models import Curso, Turma

course = Curso.objects.get(pk=1)
local_default = course.centro.nome
specs = [
    {
        'codigo': 'DEMO-TARDE-2026',
        'nome': 'Turma Demo — Tarde',
        'data_inicio': date(2026, 8, 24),
        'data_fim': date(2026, 9, 25),
        'turno': 'TARDE',
        'horario_inicio': time(14, 0),
        'horario_fim': time(16, 0),
        'dias_semana': 'SEG,QUA,SEX',
        'vagas_totais': 20,
        'local': local_default,
        'sala': 'Sala 2',
    },
    {
        'codigo': 'DEMO-NOITE-2026',
        'nome': 'Turma Demo — Noite',
        'data_inicio': date(2026, 9, 7),
        'data_fim': date(2026, 10, 9),
        'turno': 'NOITE',
        'horario_inicio': time(18, 0),
        'horario_fim': time(20, 0),
        'dias_semana': 'TER,QUI',
        'vagas_totais': 20,
        'local': local_default,
        'sala': 'Sala 3',
    },
    {
        'codigo': 'DEMO-SABADO-2026',
        'nome': 'Turma Demo — Sábado',
        'data_inicio': date(2026, 9, 5),
        'data_fim': date(2026, 10, 24),
        'turno': 'SABADO',
        'horario_inicio': time(9, 0),
        'horario_fim': time(13, 0),
        'dias_semana': 'SAB',
        'vagas_totais': 18,
        'local': local_default,
        'sala': 'Sala 4',
    },
]

with transaction.atomic():
    for spec in specs:
        turma, created = Turma.objects.get_or_create(
            curso=course,
            codigo=spec['codigo'],
            defaults={**spec, 'status': 'ABERTA', 'vagas_ocupadas': 0},
        )
        if not created:
            changed = False
            for field, value in spec.items():
                if getattr(turma, field) != value:
                    setattr(turma, field, value)
                    changed = True
            if turma.status != 'ABERTA':
                turma.status = 'ABERTA'
                changed = True
            if turma.vagas_ocupadas != 0:
                turma.vagas_ocupadas = 0
                changed = True
            if changed:
                turma.save()
        print(f'{"CRIADA" if created else "ATUALIZADA"}|id={turma.id}|codigo={turma.codigo}|nome={turma.nome}|status={turma.status}|inicio={turma.data_inicio}|fim={turma.data_fim}|turno={turma.get_turno_display()}|dias={turma.dias_semana}|horario={turma.horario_formatado}|vagas={turma.vagas_disponiveis}|local={turma.local}|sala={turma.sala}')
