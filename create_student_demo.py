import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from django.db import transaction
from django.contrib.auth import authenticate
from usuarios.models import Usuario, Aluno, PerfilAluno

email = 'aluno.demo@eduka-angola.test'
password = 'EdukaAluno#2026'
nome = 'Aluno Demo Eduka-Angola'

with transaction.atomic():
    user, created = Usuario.objects.get_or_create(
        email=email,
        defaults={'nome': nome, 'tipo_usuario': 'ALUNO', 'is_active': True},
    )
    user.nome = nome
    user.tipo_usuario = 'ALUNO'
    user.is_active = True
    user.set_password(password)
    user.save()

    aluno, _ = Aluno.objects.get_or_create(usuario=user, defaults={'nome': nome})
    aluno.nome = nome
    aluno.ativo = True
    aluno.save(update_fields=['nome', 'ativo'])
    perfil, _ = PerfilAluno.objects.get_or_create(aluno=aluno)
    perfil.onboarding_completo = True
    perfil.save(update_fields=['onboarding_completo'])

check = authenticate(email=email, password=password)
print(f'{"CRIADA" if created else "ATUALIZADA"}|usuario_id={user.id}|aluno_id={aluno.id}|email={email}|autenticacao={bool(check)}')
