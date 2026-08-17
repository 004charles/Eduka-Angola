import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.test import Client
from django.db import transaction
from usuarios.models import Usuario, Aluno
from cursos_app.models import Curso

class RollbackTest(Exception):
    pass

email = 'visitante.teste.home@eduka-angola.test'
Usuario.objects.filter(email=email).delete()
client = Client()

try:
    with transaction.atomic():
        curso = Curso.objects.get(pk=1)
        turma = curso.turmas.get(pk=1)
        turma.status = 'ABERTA'
        turma.save(update_fields=['status'])

        ficha = client.get('/cursos/ficha_inscricao/1/')
        assert ficha.status_code == 200, (ficha.status_code, ficha.url)
        ficha_html = ficha.content.decode('utf-8')
        assert 'Não precisa de criar uma conta agora' in ficha_html
        assert 'name="telefone"' in ficha_html

        response = client.post('/cursos/curso/1/inscrever/', data={
            'nome': 'Visitante Teste Homepage',
            'email': email,
            'telefone': '+244 923 111 222',
            'turma_escolhida': '1',
        })
        print('POST_STATUS', response.status_code, 'URL', response.url)
        assert response.status_code == 302, response.status_code
        assert '/cursos/curso/1/' in response.url

        user = Usuario.objects.get(email=email)
        aluno = Aluno.objects.get(usuario=user)
        assert aluno.inscricoes.filter(curso_id=1).exists()
        assert client.session.get('guest_inscricao_id')
        raise RollbackTest()
except RollbackTest:
    pass
finally:
    Usuario.objects.filter(email=email).delete()

print('PASS: visitante vê ficha sem login')
print('PASS: visitante cria inscrição gratuita com nome, email e telefone')
print('PASS: sessão de inscrição é guardada sem autenticar o visitante')
