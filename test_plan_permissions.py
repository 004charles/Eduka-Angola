import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.db import transaction
from gestoreduka.models import CentroDeFormacao
from planos.models import Plano, AssinaturaMembro
from gestoreduka.plan_permissions import permite, limite, get_plano_ativo


class RollbackTest(Exception):
    pass


try:
    with transaction.atomic():
        centro = CentroDeFormacao.objects.get(pk=1)
        plano = Plano.objects.create(
            nome='__TESTE_PERMISSOES__',
            descricao='Plano temporário de teste',
            preco=Decimal('1000.00'),
            limite_cursos=8,
            permite_inscricao_manual=True,
            permite_gerar_certificado=True,
            permite_cursos_video=True,
            limite_cursos_video=3,
            ativo=True,
        )
        assinatura = AssinaturaMembro.objects.create(centro=centro, plano=plano, status='ATIVO')

        assert get_plano_ativo(centro).pk == plano.pk
        assert permite(centro, 'permite_inscricao_manual') is True
        assert permite(centro, 'permite_gerar_certificado') is True
        assert permite(centro, 'permite_cursos_video') is True
        assert limite(centro, 'limite_cursos', padrao=0) == 8
        assert limite(centro, 'limite_cursos_video', padrao=0) == 3

        assinatura.status = 'PENDENTE'
        assinatura.save(update_fields=['status'])
        centro.refresh_from_db()
        assert get_plano_ativo(centro) is None
        assert permite(centro, 'permite_inscricao_manual') is False

        print('PASS: plano ativo disponibiliza as permissões configuradas')
        print('PASS: limites numéricos são lidos diretamente do plano')
        print('PASS: assinatura pendente bloqueia permissões protegidas')
        raise RollbackTest()
except RollbackTest:
    pass
