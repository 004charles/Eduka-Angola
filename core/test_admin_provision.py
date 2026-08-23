import os
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from usuarios.models import Usuario


class ProvisionAdminCommandTests(TestCase):
    def test_cria_superadministrador_a_partir_de_variaveis_de_ambiente(self):
        with patch.dict(os.environ, {
            'ADMIN_BOOTSTRAP_EMAIL': 'novo.admin@test.com',
            'ADMIN_BOOTSTRAP_NAME': 'Nova Administração',
            'ADMIN_BOOTSTRAP_PASSWORD': 'SenhaTemporariaForte123',
        }, clear=False):
            call_command('provision_admin', stdout=StringIO())

        admin = Usuario.objects.get(email='novo.admin@test.com')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
        self.assertEqual(admin.tipo_usuario, 'ADMIN')
        self.assertTrue(admin.check_password('SenhaTemporariaForte123'))

    def test_reexecucao_nao_substitui_palavra_passe_existente(self):
        admin = Usuario.objects.create_superuser(
            email='existente.admin@test.com',
            nome='Administrador Existente',
            password='SenhaInicialForte123',
        )
        with patch.dict(os.environ, {
            'ADMIN_BOOTSTRAP_EMAIL': admin.email,
            'ADMIN_BOOTSTRAP_NAME': admin.nome,
            'ADMIN_BOOTSTRAP_PASSWORD': 'OutraSenhaForte123',
        }, clear=False):
            call_command('provision_admin', stdout=StringIO())

        admin.refresh_from_db()
        self.assertTrue(admin.check_password('SenhaInicialForte123'))
        self.assertFalse(admin.check_password('OutraSenhaForte123'))
