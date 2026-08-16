import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from cursos_app.models import Curso
from gestoreduka.forms import CursoForm
from gestoreduka.models import CentroDeFormacao

centro = CentroDeFormacao.objects.get(pk=1)

curso = Curso(
    centro=centro,
    titulo='Teste de cobrança',
    descricao='Teste',
    preco=Decimal('90000.000'),
    preco_inscricao=Decimal('20000.000'),
    mensalidade=Decimal('35000.000'),
    is_gratuito=False,
)

curso.tipo_cobranca_inscricao = 'SEM_PAGAMENTO'
assert curso.valor_a_cobrar_online() == 0
assert 'pagamento posterior' in curso.descricao_cobranca_online()

curso.tipo_cobranca_inscricao = 'APENAS_TAXA'
assert curso.valor_a_cobrar_online() == Decimal('20000.000')

curso.tipo_cobranca_inscricao = 'TAXA_E_MENSALIDADE'
assert curso.valor_a_cobrar_online() == Decimal('55000.000')
assert '1ª mensalidade' in curso.descricao_cobranca_online()

curso.tipo_cobranca_inscricao = 'CURSO_COMPLETO'
assert curso.valor_a_cobrar_online() == curso.preco_atual

curso.is_gratuito = True
assert curso.valor_a_cobrar_online() == 0
assert curso.descricao_cobranca_online() == 'Inscrição gratuita'

form = CursoForm()
for field_name in ('is_gratuito', 'tipo_cobranca_inscricao', 'preco_inscricao', 'mensalidade', 'permite_parcelamento', 'max_parcelas'):
    assert field_name in form.fields, field_name

print('PASS: inscrição direta sem pagamento inicial')
print('PASS: cobrança apenas da taxa de inscrição')
print('PASS: cobrança da taxa + primeira mensalidade')
print('PASS: cobrança do preço total do curso')
print('PASS: curso gratuito força inscrição sem pagamento')
print('PASS: GestorEduka expõe todas as opções comerciais no formulário')
