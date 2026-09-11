#!/usr/bin/env python
"""
Script para criar usuários GESTOR para centros existentes que não têm usuários associados.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from gestoreduka.models import CentroDeFormacao
from usuarios.models import Usuario

def criar_usuarios_para_centros():
    """Cria usuários GESTOR para centros que não têm usuários associados."""
    centros_sem_usuario = CentroDeFormacao.objects.filter(usuario__isnull=True)
    
    print(f"Encontrados {centros_sem_usuario.count()} centros sem usuário associado.\n")
    
    for centro in centros_sem_usuario:
        print(f"Processando centro: {centro.nome} ({centro.email})")
        
        # Verificar se já existe um usuário com este email
        try:
            usuario = Usuario.objects.get(email=centro.email)
            print(f"  ✓ Usuário já existe: {usuario.email}")
        except Usuario.DoesNotExist:
            # Criar novo usuário
            # IMPORTANTE: Você precisará redefinir a senha através do link de confirmação
            usuario = Usuario.objects.create(
                email=centro.email,
                nome=centro.nome or f"Gestor {centro.email}",
                tipo_usuario='GESTOR',
                is_active=True,
            )
            # Definir uma senha temporária (o usuário deverá alterá-la)
            usuario.set_password('TemporaryPass123!')
            usuario.save()
            print(f"  ✓ Usuário criado: {usuario.email}")
            print(f"    Senha temporária definida (ocultada por segurança)")
        
        # Associar o usuário ao centro
        centro.usuario = usuario
        centro.save()
        print(f"  ✓ Usuário associado ao centro\n")
    
    print("Processo concluído!")
    print("\n" + "="*60)
    print("IMPORTANTE: Os usuários foram criados com senha temporária.")
    print("Recomenda-se que os gestores alterem suas senhas após o primeiro login.")
    print("="*60)

if __name__ == '__main__':
    criar_usuarios_para_centros()
