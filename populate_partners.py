import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()
from gestoreduka.models import CentroDeFormacao, Parceria

centro = CentroDeFormacao.objects.first()
parcerias_data = [
    {'nome_empresa': 'ISCTE - Instituto Superior', 'tipo_parceria': 'Ensino Superior', 'descricao': 'Parceria para formacao profissional e estagios', 'localizacao': 'Luanda, Ingombota', 'contacto': '+244 923 456 789', 'parceiro_externo': True, 'aceita_candidaturas': True},
    {'nome_empresa': 'UNITEL Academy', 'tipo_parceria': 'Telecomunicacoes', 'descricao': 'Formacao em telecomunicacoes e tecnologia', 'localizacao': 'Luanda, Miramar', 'contacto': '+244 923 111 222', 'parceiro_externo': True, 'aceita_candidaturas': True},
    {'nome_empresa': 'Sonangol Training Center', 'tipo_parceria': 'Petroleo e Gas', 'descricao': 'Formacao tecnica para o sector petrolifero', 'localizacao': 'Luanda, Viana', 'contacto': '+244 923 333 444', 'parceiro_externo': True, 'aceita_candidaturas': False},
    {'nome_empresa': 'BFA Academy', 'tipo_parceria': 'Financas e Bancario', 'descricao': 'Formacao em banca, financas e gestao', 'localizacao': 'Luanda, Centro', 'contacto': '+244 923 555 666', 'parceiro_externo': True, 'aceita_candidaturas': True},
    {'nome_empresa': 'Angola Cables Academy', 'tipo_parceria': 'Tecnologia', 'descricao': 'Formacao em redes, fibra optica e data centers', 'localizacao': 'Benguela', 'contacto': '+244 923 777 888', 'parceiro_externo': True, 'aceita_candidaturas': True},
]

count = 0
for data in parcerias_data:
    nome = data['nome_empresa']
    obj, created = Parceria.objects.get_or_create(
        centro=centro,
        nome_empresa=nome,
        defaults=data
    )
    if created:
        count += 1
        print('  [create] ' + nome)
    else:
        print('  [skip] ' + nome)

print('')
print(str(count) + ' parceiros criados (total: ' + str(Parceria.objects.count()) + ')')
