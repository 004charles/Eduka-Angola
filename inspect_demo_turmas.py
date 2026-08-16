import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from cursos_app.models import Curso

curso = Curso.objects.select_related('centro').get(pk=1)
print(f'CURSO={curso.id}|{curso.titulo}|CENTRO={curso.centro_id}:{curso.centro.nome}')
for turma in curso.turmas.all().order_by('data_inicio', 'turno'):
    print(
        f'TURMA={turma.id}|codigo={turma.codigo}|nome={turma.nome}|'
        f'status={turma.status}|inicio={turma.data_inicio}|fim={turma.data_fim}|'
        f'turno={turma.turno}|horario={turma.horario_inicio}-{turma.horario_fim}|'
        f'dias={turma.dias_semana}|vagas={turma.vagas_totais}/{turma.vagas_disponiveis}|'
        f'local={turma.local}|sala={turma.sala}|filial={turma.filial_id}'
    )
print('FILIAIS=')
for filial in curso.centro.filiais.all().order_by('id'):
    print(f'FILIAL={filial.id}|{filial.nome}|cidade={getattr(filial, "cidade", "")}|endereco={getattr(filial, "endereco", "")}')
