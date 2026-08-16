import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from planos.models import Plano, AssinaturaMembro, VoucherPlano
from pagamentos.models import Pagamento
from gestoreduka.models import ConfiguracaoPlataforma, CentroDeFormacao

print('PLANOS')
for p in Plano.objects.all().order_by('id'):
    print({
        'id': p.id,
        'nome': p.nome,
        'preco': str(p.preco),
        'limite_cursos': p.limite_cursos,
        'alcance_km': p.alcance_km,
        'selo_verificacao': p.selo_verificacao,
        'prioridade_busca': p.prioridade_busca,
        'destaque_home': p.destaque_home,
        'acesso_relatorios': p.acesso_relatorios,
        'permite_inscricao_manual': p.permite_inscricao_manual,
        'permite_gerar_certificado': p.permite_gerar_certificado,
        'permite_cursos_video': p.permite_cursos_video,
        'limite_cursos_video': p.limite_cursos_video,
        'ativo': p.ativo,
    })

print('ASSINATURAS')
for a in AssinaturaMembro.objects.select_related('centro', 'plano').all().order_by('id'):
    print({
        'id': a.id,
        'centro_id': a.centro_id,
        'centro': a.centro.nome,
        'plano': a.plano.nome if a.plano else None,
        'status': a.status,
        'data_inicio': str(a.data_inicio),
        'data_fim': str(a.data_fim),
        'renovacao_automatica': a.renovacao_automatica,
        'esta_ativa': a.esta_ativa,
    })

print('VOUCHERS')
for v in VoucherPlano.objects.select_related('plano', 'centro').all().order_by('id'):
    print({'id': v.id, 'codigo': v.codigo, 'plano': v.plano.nome, 'centro': v.centro.nome, 'usado': v.usado})

print('PAGAMENTOS_ASSINATURA')
for p in Pagamento.objects.filter(tipo_pagamento='ASSINATURA_PLANO').select_related('plano', 'usuario').order_by('-data_criacao'):
    print({'referencia': p.referencia_pagamento, 'status': p.status, 'valor': str(p.valor_final), 'plano': p.plano.nome if p.plano else None, 'usuario_id': p.usuario_id, 'usuario_email': p.usuario.email, 'criado': str(p.data_criacao)})

print('CONFIGURACAO')
c = ConfiguracaoPlataforma.load()
print({'taxa_comissao': str(c.taxa_comissao), 'taxa_comissao_ead': str(c.taxa_comissao_ead), 'taxa_gestao_bolsas': str(c.taxa_gestao_bolsas), 'taxa_markup': str(c.taxa_markup)})

print('CENTROS')
for c in CentroDeFormacao.objects.all().order_by('id'):
    print({'id': c.id, 'nome': c.nome, 'metodo_precificacao': c.metodo_precificacao, 'usuario_id': c.usuario_id, 'ativo': c.ativo})
