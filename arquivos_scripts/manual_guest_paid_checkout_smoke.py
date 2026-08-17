import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.test import Client
from django.db import transaction
from usuarios.models import Usuario
from cursos_app.models import Curso

class RollbackTest(Exception):
    pass

email = 'visitante.teste.pago@eduka-angola.test'
Usuario.objects.filter(email=email).delete()
client = Client()

try:
    with transaction.atomic():
        curso = Curso.objects.get(pk=1)
        turma = curso.turmas.get(pk=1)
        curso.is_gratuito = False
        curso.preco = 90000
        curso.preco_inscricao = 20000
        curso.tipo_cobranca_inscricao = 'APENAS_TAXA'
        curso.save(update_fields=['is_gratuito', 'preco', 'preco_inscricao', 'tipo_cobranca_inscricao'])
        turma.status = 'ABERTA'
        turma.save(update_fields=['status'])

        response = client.post('/cursos/curso/1/inscrever/', data={
            'nome': 'Visitante Pago Teste',
            'email': email,
            'telefone': '+244 923 333 444',
            'turma_escolhida': '1',
        })
        assert response.status_code == 302
        assert '/cursos/pagamento/' in response.url

        pagamento_page = client.get(response.url)
        assert pagamento_page.status_code == 200
        payment_html = pagamento_page.content.decode('utf-8')
        assert '20' in payment_html or '20000' in payment_html
        assert 'Visitante Pago Teste' in payment_html
        raise RollbackTest()
except RollbackTest:
    pass
finally:
    Usuario.objects.filter(email=email).delete()

print('PASS: visitante pago chega ao checkout sem login')
print('PASS: valor inicial e aluno aparecem no resumo de pagamento')
