from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand

from cursos_app.models import Categoria
from cursovideoapp.models import Aula, Curso_video, ProgressoAula
from usuarios.models import Aluno, Usuario


class Command(BaseCommand):
    help = 'Cria uma conta de aluno com dois cursos em vídeo concluídos para testar a candidatura de formador.'

    email = 'aluno.elegivel@edukangola.local'
    password = 'EdukaAluno2026'

    def handle(self, *args, **options):
        user, _ = Usuario.objects.get_or_create(
            email=self.email,
            defaults={'nome': 'Mário de Carvalho', 'tipo_usuario': 'ALUNO', 'is_active': True},
        )
        user.nome = 'Mário de Carvalho'
        user.tipo_usuario = 'ALUNO'
        user.is_active = True
        user.set_password(self.password)
        user.save()
        aluno, _ = Aluno.objects.get_or_create(usuario=user, defaults={'nome': user.nome, 'ativo': True})
        aluno.nome = user.nome
        aluno.ativo = True
        aluno.save()
        categoria, _ = Categoria.objects.get_or_create(
            slug='competencias-digitais', defaults={'nome': 'Competências Digitais', 'descricao': 'Formação prática em ferramentas digitais.'}
        )
        for numero, titulo in enumerate(('Fundamentos de Excel', 'Comunicação Digital Profissional'), start=1):
            curso, _ = Curso_video.objects.update_or_create(
                slug=f'{titulo.lower().replace(" ", "-")}-elegivel-formador',
                defaults={'titulo': titulo, 'descricao': 'Curso concluído para demonstrar a elegibilidade de candidatura de formador.', 'categoria': categoria, 'is_pago': False},
            )
            curso.inscritos.add(aluno)
            aula, _ = Aula.objects.update_or_create(
                curso=curso, ordem=1,
                defaults={'titulo': f'Aula final {numero}', 'descricao': 'Aula concluída pela conta de demonstração.', 'duracao_segundos': 300},
            )
            ProgressoAula.objects.update_or_create(aluno=aluno, aula=aula, defaults={'concluida': True, 'tempo_assistido': 300})
        if not authenticate(username=self.email, password=self.password):
            self.stderr.write(self.style.ERROR('Não foi possível validar a conta de aluno de demonstração.'))
            return
        self.stdout.write(self.style.SUCCESS('Aluno elegível criado com sucesso.'))
        self.stdout.write(f'E-mail: {self.email}')
        self.stdout.write(f'Palavra-passe: {self.password}')
