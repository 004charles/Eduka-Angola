#!/usr/bin/env python
"""
Script para criar usuários de teste no sistema EdukAngola
Execute: python manage.py shell < create_test_users.py
"""

from usuarios.models import Usuario, Aluno
from gestoreduka.models import CentroDeFormacao

# Criar superusuário admin
print("Criando superusuário admin...")
admin, created = Usuario.objects.get_or_create(
    email='admin@eduka.com',
    defaults={
        'nome': 'Administrador',
        'tipo_usuario': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print(f"✓ Superusuário criado: {admin.email}")
else:
    print(f"✓ Superusuário já existe: {admin.email}")

# Criar aluno de teste
print("\nCriando aluno de teste...")
aluno_user, created = Usuario.objects.get_or_create(
    email='aluno@teste.com',
    defaults={
        'nome': 'João Silva',
        'tipo_usuario': 'ALUNO',
        'is_active': True
    }
)
if created:
    aluno_user.set_password('senha123')
    aluno_user.save()
    
    # Criar perfil de aluno
    aluno_perfil = Aluno.objects.create(
        usuario=aluno_user,
        nome='João Silva',
        ativo=True
    )
    print(f"✓ Aluno criado: {aluno_user.email}")
else:
    print(f"✓ Aluno já existe: {aluno_user.email}")

# Criar gestor de centro de teste
print("\nCriando gestor de centro de teste...")
gestor_user, created = Usuario.objects.get_or_create(
    email='gestor@teste.com',
    defaults={
        'nome': 'Maria Santos',
        'tipo_usuario': 'GESTOR',
        'is_active': True
    }
)
if created:
    gestor_user.set_password('senha123')
    gestor_user.save()
    
    # Criar centro de formação
    centro = CentroDeFormacao.objects.create(
        usuario=gestor_user,
        nome='Centro de Formação Teste',
        email='gestor@teste.com',
        cidade='Luanda',
        provincia='Luanda',
        ativo=True
    )
    print(f"✓ Gestor criado: {gestor_user.email}")
    print(f"✓ Centro criado: {centro.nome}")
else:
    print(f"✓ Gestor já existe: {gestor_user.email}")

print("\n" + "="*50)
print("RESUMO DOS USUÁRIOS DE TESTE:")
print("="*50)
print(f"Admin:  admin@eduka.com")
print(f"Aluno:  aluno@teste.com")
print(f"Gestor: gestor@teste.com")
print("Senhas definidas nos scripts (verificar código-fonte)")
print("="*50)
