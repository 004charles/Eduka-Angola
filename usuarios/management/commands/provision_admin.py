import os

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Cria uma conta administrativa a partir de ADMIN_BOOTSTRAP_* sem guardar credenciais no código.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default=os.getenv('ADMIN_BOOTSTRAP_EMAIL', ''))
        parser.add_argument('--name', default=os.getenv('ADMIN_BOOTSTRAP_NAME', 'Administrador Edukangola'))
        parser.add_argument('--password', default=os.getenv('ADMIN_BOOTSTRAP_PASSWORD', ''))

    def handle(self, *args, **options):
        email = str(options['email']).strip().lower()
        name = str(options['name']).strip() or 'Administrador Edukangola'
        password = str(options['password'])

        if not email or not password:
            raise CommandError('Defina ADMIN_BOOTSTRAP_EMAIL e ADMIN_BOOTSTRAP_PASSWORD antes de executar este comando.')
        try:
            validate_email(email)
        except ValidationError as error:
            raise CommandError('ADMIN_BOOTSTRAP_EMAIL não é um e-mail válido.') from error
        if len(password) < 12:
            raise CommandError('ADMIN_BOOTSTRAP_PASSWORD deve ter pelo menos 12 caracteres.')

        existing = Usuario.objects.filter(email=email).first()
        if existing:
            updated = []
            if existing.nome != name:
                existing.nome = name
                updated.append('nome')
            if existing.tipo_usuario != 'ADMIN':
                existing.tipo_usuario = 'ADMIN'
                updated.append('tipo_usuario')
            if not existing.is_active:
                existing.is_active = True
                updated.append('is_active')
            if not existing.is_staff:
                existing.is_staff = True
                updated.append('is_staff')
            if not existing.is_superuser:
                existing.is_superuser = True
                updated.append('is_superuser')
            if updated:
                existing.save(update_fields=updated)
                self.stdout.write(self.style.SUCCESS(f'Conta administrativa existente actualizada: {email}'))
            else:
                self.stdout.write(f'Conta administrativa já existe: {email}')
            return

        admin = Usuario.objects.create_superuser(email=email, nome=name, password=password)
        if admin.tipo_usuario != 'ADMIN':
            admin.tipo_usuario = 'ADMIN'
            admin.save(update_fields=['tipo_usuario'])
        self.stdout.write(self.style.SUCCESS(f'Conta administrativa criada: {email}'))
