"""Operações protegidas da administração React.

Cada recurso tem uma lista explícita de campos permitidos. A camada nunca expõe
segredos de integração e nunca permite remoções destrutivas por esta interface.
"""

from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.utils import timezone

from cursos_app.models import Curso, Inscricao
from cursovideoapp.models import Curso_video, PlanoSubscricaoVideo, AssinaturaVideoAluno
from bolsas.models import Bolsa, CandidaturaBolsa
from estagio.models import Estagio, InscricaoEstagio
from escolas.models import Escola
from biblioteca.models import Livro
from blog.models import Post
from gestoreduka.models import CentroDeFormacao, Filial, ConfiguracaoPlataforma, ConviteEventos
from mercado.models import LojaParceira, PedidoMercado, ProdutoMercado
from pagamentos.models import ConfiguracaoPagamento, Pagamento
from usuarios.models import Usuario

from .models import AdminAuditLog, MensagemContato, PerguntaFrequente


SECTION_LABELS = {
    'centros': ('Centros e filiais', 'Gestão de parceiros, presença e disponibilidade'),
    'cursos': ('Cursos presenciais', 'Publicação, disponibilidade e destaque de cursos'),
    'video-cursos': ('Cursos em vídeo', 'Oferta editorial e cursos de vídeo'),
    'planos-video': ('Planos de vídeo', 'Preço, vigência e disponibilidade da subscrição mensal'),
    'subscricoes-video': ('Subscrições de vídeo', 'Acesso de alunos ao catálogo de cursos em vídeo'),
    'utilizadores': ('Utilizadores', 'Contas, funções e actividade de acesso'),
    'inscricoes': ('Inscrições', 'Decisões de inscrição em cursos presenciais'),
    'pagamentos': ('Pagamentos', 'Acompanhamento financeiro e reconciliação manual'),
    'lojas': ('Lojas parceiras', 'Validação e activação de lojas do Mercado'),
    'produtos': ('Produtos do Mercado', 'Stock, publicação e disponibilidade'),
    'pedidos': ('Pedidos do Mercado', 'Recolha, entrega e ocorrências'),
    'contactos': ('Contactos', 'Mensagens recebidas pelo suporte'),
    'perguntas': ('Perguntas frequentes', 'Conteúdo de apoio público'),
    'bolsas': ('Bolsas atribuídas', 'Bolsas de estudo e respectivos estados'),
    'candidaturas-bolsas': ('Candidaturas a bolsas', 'Análise de candidaturas de estudantes'),
    'estagios': ('Estágios', 'Oportunidades profissionais publicadas'),
    'candidaturas-estagios': ('Candidaturas a estágios', 'Decisão sobre candidaturas profissionais'),
    'escolas': ('Escolas', 'Catálogo público de escolas'),
    'biblioteca': ('Biblioteca', 'Obras digitais publicadas pela Edukangola'),
    'noticias': ('Notícias', 'Publicação editorial e vídeos de actualidade'),
    'configuracoes': ('Configurações', 'Pagamentos, moedas e taxas de plataforma'),
    'convites-eventos': ('Convites de Eventos', 'Código de acesso para gestores de eventos independentes'),
    'auditoria': ('Auditoria', 'Histórico de acções administrativas React'),
}


def _choice_label(instance, field_name):
    getter = getattr(instance, f'get_{field_name}_display', None)
    return getter() if callable(getter) else str(getattr(instance, field_name, ''))


def _choices(instance, field_name):
    field = instance._meta.get_field(field_name)
    return [{'value': value, 'label': label} for value, label in field.choices]


def _bool(value):
    if isinstance(value, bool):
        return value
    raise ValueError('O valor deve ser verdadeiro ou falso.')


def _audit(actor, resource, instance, action, before, after):
    AdminAuditLog.objects.create(
        ator=actor,
        recurso=resource,
        objeto_id=str(instance.pk),
        acao=action,
        antes={key: _audit_value(value) for key, value in before.items()},
        depois={key: _audit_value(value) for key, value in after.items()},
    )


def _audit_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return value


def _section_queryset(section, term):
    term = (term or '').strip()
    if section == 'centros':
        query = CentroDeFormacao.objects.select_related('usuario').order_by('-data_criacao')
        return query.filter(Q(nome__icontains=term) | Q(email__icontains=term) | Q(cidade__icontains=term)) if term else query
    if section == 'cursos':
        query = Curso.objects.select_related('centro').order_by('-data_atualizacao')
        return query.filter(Q(titulo__icontains=term) | Q(centro__nome__icontains=term)) if term else query
    if section == 'video-cursos':
        query = Curso_video.objects.select_related('instrutor', 'centro').order_by('-data_publicacao')
        return query.filter(Q(titulo__icontains=term) | Q(instrutor__nome__icontains=term)) if term else query
    if section == 'planos-video':
        query = PlanoSubscricaoVideo.objects.order_by('ordem', 'preco', 'id')
        return query.filter(Q(nome__icontains=term) | Q(descricao__icontains=term)) if term else query
    if section == 'subscricoes-video':
        query = AssinaturaVideoAluno.objects.select_related('aluno__usuario', 'plano').order_by('-data_fim')
        return query.filter(Q(aluno__usuario__nome__icontains=term) | Q(aluno__usuario__email__icontains=term) | Q(plano__nome__icontains=term)) if term else query
    if section == 'utilizadores':
        query = Usuario.objects.order_by('-data_criacao')
        return query.filter(Q(nome__icontains=term) | Q(email__icontains=term)) if term else query
    if section == 'inscricoes':
        query = Inscricao.objects.select_related('aluno__usuario', 'curso').order_by('-data_inscricao')
        return query.filter(Q(aluno__usuario__nome__icontains=term) | Q(curso__titulo__icontains=term) | Q(codigo_inscricao__icontains=term)) if term else query
    if section == 'pagamentos':
        query = Pagamento.objects.select_related('usuario').order_by('-data_criacao')
        return query.filter(Q(referencia_pagamento__icontains=term) | Q(usuario__email__icontains=term) | Q(usuario__nome__icontains=term)) if term else query
    if section == 'lojas':
        query = LojaParceira.objects.order_by('-atualizado_em')
        return query.filter(Q(nome__icontains=term) | Q(municipio__icontains=term)) if term else query
    if section == 'produtos':
        query = ProdutoMercado.objects.select_related('loja').order_by('-atualizado_em')
        return query.filter(Q(titulo__icontains=term) | Q(loja__nome__icontains=term)) if term else query
    if section == 'pedidos':
        query = PedidoMercado.objects.select_related('utilizador').order_by('-criado_em')
        return query.filter(Q(referencia__icontains=term) | Q(nome_comprador__icontains=term) | Q(email_comprador__icontains=term)) if term else query
    if section == 'contactos':
        query = MensagemContato.objects.order_by('-criado_em')
        return query.filter(Q(nome__icontains=term) | Q(email__icontains=term) | Q(assunto__icontains=term)) if term else query
    if section == 'perguntas':
        query = PerguntaFrequente.objects.order_by('categoria', 'ordem', 'id')
        return query.filter(Q(pergunta__icontains=term) | Q(categoria__icontains=term)) if term else query
    if section == 'bolsas':
        query = Bolsa.objects.select_related('patrocinador', 'aluno__usuario', 'curso').order_by('-data_inicio')
        return query.filter(Q(aluno__usuario__nome__icontains=term) | Q(patrocinador__nome__icontains=term)) if term else query
    if section == 'candidaturas-bolsas':
        query = CandidaturaBolsa.objects.select_related('aluno__usuario', 'curso_pretendido').order_by('-data_candidatura')
        return query.filter(Q(aluno__usuario__nome__icontains=term) | Q(curso_pretendido__titulo__icontains=term)) if term else query
    if section == 'estagios':
        query = Estagio.objects.order_by('-data_publicacao')
        return query.filter(Q(titulo__icontains=term) | Q(empresa__icontains=term)) if term else query
    if section == 'candidaturas-estagios':
        query = InscricaoEstagio.objects.select_related('aluno__usuario', 'estagio').order_by('-data_inscricao')
        return query.filter(Q(aluno__usuario__nome__icontains=term) | Q(estagio__titulo__icontains=term)) if term else query
    if section == 'escolas':
        query = Escola.objects.order_by('-data_criacao')
        return query.filter(Q(nome__icontains=term) | Q(provincia__icontains=term)) if term else query
    if section == 'biblioteca':
        query = Livro.objects.select_related('autor').order_by('-atualizado_em')
        return query.filter(Q(titulo__icontains=term) | Q(autor__nome__icontains=term)) if term else query
    if section == 'noticias':
        query = Post.objects.order_by('-publicado_em')
        return query.filter(Q(titulo__icontains=term) | Q(resumo__icontains=term)) if term else query
    if section == 'convites-eventos':
        query = ConviteEventos.objects.select_related('criado_por').order_by('-criado_em')
        return query.filter(Q(nome_organizacao__icontains=term) | Q(codigo__icontains=term) | Q(email_gestor__icontains=term)) if term else query
    if section == 'auditoria':
        query = AdminAuditLog.objects.select_related('ator').order_by('-criado_em')
        return query.filter(Q(recurso__icontains=term) | Q(acao__icontains=term) | Q(ator__email__icontains=term)) if term else query
    return None


def _row(section, item):
    if section == 'centros':
        return {'id': str(item.pk), 'title': item.nome or 'Centro sem nome', 'subtitle': ' · '.join(filter(None, [item.cidade, item.pais, item.email])), 'status': 'ACTIVO' if item.ativo else 'INACTIVO', 'status_label': 'Activo' if item.ativo else 'Inactivo', 'details': [item.telefone or 'Sem telefone'], 'switches': [{'field': 'ativo', 'label': 'Activo', 'value': item.ativo}]}
    if section == 'cursos':
        return {'id': str(item.pk), 'title': item.titulo, 'subtitle': item.centro.nome, 'status': 'PUBLICADO' if item.publicado and item.ativo else 'RASCUNHO', 'status_label': 'Publicado' if item.publicado and item.ativo else 'Não publicado', 'details': [f'{item.preco_inscricao} {item.moeda}', item.modalidade], 'switches': [{'field': 'publicado', 'label': 'Publicado', 'value': item.publicado}, {'field': 'ativo', 'label': 'Activo', 'value': item.ativo}, {'field': 'destaque', 'label': 'Destaque', 'value': item.destaque}]}
    if section == 'video-cursos':
        return {'id': str(item.pk), 'title': item.titulo, 'subtitle': item.instrutor.nome if item.instrutor_id else 'Edukangola', 'status': 'DESTAQUE' if item.destaque else 'NORMAL', 'status_label': 'Em destaque' if item.destaque else 'Publicado', 'details': ['Original Edukangola' if item.is_original_edukangola else 'Curso parceiro'], 'switches': [{'field': 'destaque', 'label': 'Destaque', 'value': item.destaque}]}
    if section == 'planos-video':
        return {'id': str(item.pk), 'title': item.nome, 'subtitle': item.descricao or 'Acesso ao catálogo de cursos em vídeo', 'status': 'ACTIVO' if item.ativo else 'INACTIVO', 'status_label': 'Disponível' if item.ativo else 'Indisponível', 'details': [f'{item.preco} {item.moeda}/mês', f'{item.periodo_dias} dias'], 'switches': [{'field': 'ativo', 'label': 'Disponível', 'value': item.ativo}, {'field': 'destaque', 'label': 'Destaque', 'value': item.destaque}]}
    if section == 'subscricoes-video':
        return {'id': str(item.pk), 'title': item.aluno.usuario.nome or item.aluno.usuario.email, 'subtitle': item.plano.nome, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [f'Até {item.data_fim.strftime("%d/%m/%Y")}', f'{item.valor_cobrado} {item.moeda}'], 'select': {'field': 'status', 'label': 'Estado', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'utilizadores':
        return {'id': str(item.pk), 'title': item.nome or item.email, 'subtitle': item.email, 'status': item.tipo_usuario, 'status_label': _choice_label(item, 'tipo_usuario'), 'details': ['Activo' if item.is_active else 'Suspenso'], 'switches': [{'field': 'is_active', 'label': 'Conta activa', 'value': item.is_active}]}
    if section == 'inscricoes':
        return {'id': str(item.pk), 'title': item.aluno.usuario.nome or item.aluno.usuario.email, 'subtitle': item.curso.titulo, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [item.codigo_inscricao or 'Sem código', item.tipo_inscricao], 'select': {'field': 'status', 'label': 'Decisão', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'pagamentos':
        return {'id': str(item.pk), 'title': item.referencia_pagamento, 'subtitle': item.usuario.nome or item.usuario.email, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [f'{item.valor_final} {item.moeda}', _choice_label(item, 'tipo_pagamento')], 'select': {'field': 'status', 'label': 'Estado', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'lojas':
        return {'id': str(item.pk), 'title': item.nome, 'subtitle': ' · '.join(filter(None, [item.municipio, item.provincia])), 'status': 'ACTIVA' if item.ativa and item.verificada else 'PENDENTE', 'status_label': 'Activa e verificada' if item.ativa and item.verificada else 'Pendente de validação', 'details': [item.email_operacional or 'Sem e-mail'], 'switches': [{'field': 'verificada', 'label': 'Verificada', 'value': item.verificada}, {'field': 'ativa', 'label': 'Activa', 'value': item.ativa}]}
    if section == 'produtos':
        return {'id': str(item.pk), 'title': item.titulo, 'subtitle': item.loja.nome, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [f'{item.preco} {item.moeda}', f'{item.quantidade_disponivel} em stock'], 'select': {'field': 'status', 'label': 'Estado', 'value': item.status, 'options': _choices(item, 'status')}, 'number': {'field': 'quantidade_disponivel', 'label': 'Stock', 'value': item.quantidade_disponivel}, 'switches': [{'field': 'destaque', 'label': 'Destaque', 'value': item.destaque}]}
    if section == 'pedidos':
        return {'id': str(item.pk), 'title': item.referencia, 'subtitle': item.nome_comprador, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [f'{item.total} {item.moeda}', item.municipio], 'select': {'field': 'status', 'label': 'Etapa', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'contactos':
        return {'id': str(item.pk), 'title': item.assunto, 'subtitle': f'{item.nome} · {item.email}', 'status': 'LIDO' if item.lido else 'NOVO', 'status_label': 'Lido' if item.lido else 'Novo', 'details': [item.mensagem[:120]], 'switches': [{'field': 'lido', 'label': 'Lido', 'value': item.lido}]}
    if section == 'perguntas':
        return {'id': str(item.pk), 'title': item.pergunta, 'subtitle': item.categoria, 'status': 'PUBLICADA' if item.publicada else 'RASCUNHO', 'status_label': 'Publicada' if item.publicada else 'Rascunho', 'details': [item.idioma.upper()], 'switches': [{'field': 'publicada', 'label': 'Publicada', 'value': item.publicada}]}
    if section == 'bolsas':
        return {'id': str(item.pk), 'title': item.aluno.usuario.nome or item.aluno.usuario.email, 'subtitle': f'{item.patrocinador.nome} · {item.curso.titulo if item.curso_id else "Curso não definido"}', 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [f'{item.porcentagem}% de bolsa'], 'select': {'field': 'status', 'label': 'Estado', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'candidaturas-bolsas':
        return {'id': str(item.pk), 'title': item.aluno.usuario.nome or item.aluno.usuario.email, 'subtitle': item.curso_pretendido.titulo, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [item.data_candidatura.strftime('%d/%m/%Y')], 'select': {'field': 'status', 'label': 'Decisão', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'estagios':
        return {'id': str(item.pk), 'title': item.titulo, 'subtitle': f'{item.empresa} · {item.cidade}', 'status': 'ACTIVO' if item.ativo else 'INACTIVO', 'status_label': 'Activo' if item.ativo else 'Inactivo', 'details': [f'{item.vagas_disponiveis} vaga(s)'], 'switches': [{'field': 'ativo', 'label': 'Activo', 'value': item.ativo}, {'field': 'destaque', 'label': 'Destaque', 'value': item.destaque}]}
    if section == 'candidaturas-estagios':
        return {'id': str(item.pk), 'title': item.aluno.usuario.nome or item.aluno.usuario.email, 'subtitle': item.estagio.titulo, 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [item.data_inscricao.strftime('%d/%m/%Y')], 'select': {'field': 'status', 'label': 'Decisão', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'escolas':
        return {'id': str(item.pk), 'title': item.nome, 'subtitle': f'{item.municipio} · {item.provincia}', 'status': 'ACTIVA' if item.ativa else 'INACTIVA', 'status_label': 'Activa' if item.ativa else 'Inactiva', 'details': [item.get_tipo_rede_display()], 'switches': [{'field': 'ativa', 'label': 'Activa', 'value': item.ativa}]}
    if section == 'biblioteca':
        return {'id': str(item.pk), 'title': item.titulo, 'subtitle': item.autor.nome, 'status': item.estado, 'status_label': _choice_label(item, 'estado'), 'details': [item.formato, 'Gratuito' if item.gratuito else 'Pago'], 'select': {'field': 'estado', 'label': 'Publicação', 'value': item.estado, 'options': _choices(item, 'estado')}, 'switches': [{'field': 'em_destaque', 'label': 'Destaque', 'value': item.em_destaque}]}
    if section == 'noticias':
        return {'id': str(item.pk), 'title': item.titulo, 'subtitle': _choice_label(item, 'tipo_conteudo'), 'status': item.status, 'status_label': _choice_label(item, 'status'), 'details': [item.publicado_em.strftime('%d/%m/%Y')], 'select': {'field': 'status', 'label': 'Publicação', 'value': item.status, 'options': _choices(item, 'status')}}
    if section == 'convites-eventos':
        status = 'ACTIVO' if item.esta_valido else 'EXPIRADO'
        status_label = 'Activo' if item.esta_valido else 'Expirado/Revogado'
        details = [item.codigo, item.email_gestor or 'Sem e-mail']
        if item.usado_em:
            details.append(f'Usado em {item.usado_em.strftime("%d/%m/%Y %H:%M")}')
        if item.expira_em:
            details.append(f'Expira em {item.expira_em.strftime("%d/%m/%Y")}')
        return {'id': str(item.pk), 'title': item.nome_organizacao, 'subtitle': f'Criado por {item.criado_por.nome or item.criado_por.email}', 'status': status, 'status_label': status_label, 'details': details, 'switches': [{'field': 'ativo', 'label': 'Activo', 'value': item.ativo}]}
    if section == 'auditoria':
        actor = item.ator.nome or item.ator.email if item.ator_id else 'Sistema'
        return {'id': str(item.pk), 'title': f'{item.recurso} · {item.acao}', 'subtitle': actor, 'status': 'REGISTADO', 'status_label': 'Registado', 'details': [item.criado_em.strftime('%d/%m/%Y %H:%M')], 'readonly': True}
    raise KeyError(section)


def list_operations(section, term='', page=1, page_size=25):
    if section == 'configuracoes':
        pagamento, _ = ConfiguracaoPagamento.objects.get_or_create(pk=1)
        plataforma, _ = ConfiguracaoPlataforma.objects.get_or_create(pk=1)
        return {'title': SECTION_LABELS[section][0], 'description': SECTION_LABELS[section][1], 'section': section, 'total': 2, 'page': 1, 'page_size': 2, 'items': [
            {'id': 'pagamento', 'title': 'Configuração de pagamentos', 'subtitle': f'{pagamento.get_gateway_padrao_display()} · {pagamento.get_moeda_padrao_display()}', 'status': 'ACTIVO' if pagamento.pagamentos_ativados else 'PAUSADO', 'status_label': 'Pagamentos activos' if pagamento.pagamentos_ativados else 'Pagamentos pausados', 'details': [f'Expiração: {pagamento.tempo_expiracao_link_minutos} min'], 'switches': [{'field': 'pagamentos_ativados', 'label': 'Pagamentos activos', 'value': pagamento.pagamentos_ativados}], 'select': {'field': 'gateway_padrao', 'label': 'Gateway', 'value': pagamento.gateway_padrao, 'options': _choices(pagamento, 'gateway_padrao')}},
            {'id': 'plataforma', 'title': 'Taxas da plataforma', 'subtitle': 'Comissões e markup', 'status': 'CONFIGURADO', 'status_label': 'Configurado', 'details': [f'Comissão: {plataforma.taxa_comissao}%', f'Markup: {plataforma.taxa_markup}%'], 'readonly': True},
        ]}
    query = _section_queryset(section, term)
    if query is None or section not in SECTION_LABELS:
        raise KeyError(section)
    page = max(1, int(page or 1))
    page_size = min(100, max(10, int(page_size or 25)))
    total = query.count()
    start = (page - 1) * page_size
    return {'title': SECTION_LABELS[section][0], 'description': SECTION_LABELS[section][1], 'section': section, 'total': total, 'page': page, 'page_size': page_size, 'items': [_row(section, item) for item in query[start:start + page_size]]}


def _get_instance(section, item_id):
    models = {
        'centros': CentroDeFormacao, 'cursos': Curso, 'video-cursos': Curso_video, 'planos-video': PlanoSubscricaoVideo, 'subscricoes-video': AssinaturaVideoAluno,
        'utilizadores': Usuario, 'inscricoes': Inscricao, 'pagamentos': Pagamento,
        'lojas': LojaParceira, 'produtos': ProdutoMercado, 'pedidos': PedidoMercado,
        'contactos': MensagemContato, 'perguntas': PerguntaFrequente,
        'bolsas': Bolsa, 'candidaturas-bolsas': CandidaturaBolsa, 'estagios': Estagio,
        'candidaturas-estagios': InscricaoEstagio, 'escolas': Escola, 'biblioteca': Livro, 'noticias': Post,
        'convites-eventos': ConviteEventos,
    }
    model = models.get(section)
    if not model:
        raise KeyError(section)
    return model.objects.get(pk=item_id)


ALLOWED_FIELDS = {
    'centros': {'nome', 'email', 'telefone', 'cidade', 'provincia', 'pais', 'endereco', 'site', 'ativo'},
    'cursos': {'titulo', 'descricao_curta', 'preco_inscricao', 'mensalidade', 'vagas_minimas', 'publicado', 'ativo', 'destaque'},
    'video-cursos': {'titulo', 'descricao', 'destaque'},
    'planos-video': {'nome', 'descricao', 'preco', 'moeda', 'periodo_dias', 'ordem', 'ativo', 'destaque'}, 'subscricoes-video': {'status'},
    'utilizadores': {'nome', 'email', 'is_active'}, 'inscricoes': {'status', 'observacoes'}, 'pagamentos': {'status'},
    'lojas': {'verificada', 'ativa'}, 'produtos': {'status', 'destaque', 'quantidade_disponivel'},
    'pedidos': {'status', 'estafeta_nome', 'estafeta_telefone', 'notas_admin', 'motivo_ocorrencia'}, 'contactos': {'lido'}, 'perguntas': {'publicada'},
    'bolsas': {'status'}, 'candidaturas-bolsas': {'status'}, 'estagios': {'ativo', 'destaque'},
    'candidaturas-estagios': {'status'}, 'escolas': {'ativa'}, 'biblioteca': {'estado', 'em_destaque'},
    'noticias': {'status'},
    'convites-eventos': {'ativo', 'nome_organizacao', 'email_gestor', 'telefone', 'endereco', 'descricao', 'expira_em'},
}


DETAIL_FIELDS = {
    'centros': [('nome', 'Nome', 'text'), ('email', 'E-mail', 'email'), ('telefone', 'Telefone', 'text'), ('cidade', 'Cidade', 'text'), ('provincia', 'Província', 'text'), ('pais', 'País', 'select'), ('endereco', 'Endereço', 'textarea'), ('site', 'Website', 'url'), ('ativo', 'Centro activo', 'boolean')],
    'cursos': [('titulo', 'Título', 'text'), ('descricao_curta', 'Descrição curta', 'textarea'), ('preco_inscricao', 'Taxa de inscrição', 'decimal'), ('mensalidade', 'Mensalidade', 'decimal'), ('vagas_minimas', 'Vagas mínimas', 'number'), ('publicado', 'Publicado', 'boolean'), ('ativo', 'Activo', 'boolean'), ('destaque', 'Destaque', 'boolean')],
    'video-cursos': [('titulo', 'Título', 'text'), ('descricao', 'Descrição', 'textarea'), ('destaque', 'Destaque', 'boolean')],
    'planos-video': [('nome', 'Nome do plano', 'text'), ('descricao', 'Descrição', 'textarea'), ('preco', 'Preço mensal', 'decimal'), ('moeda', 'Moeda', 'text'), ('periodo_dias', 'Duração em dias', 'number'), ('ordem', 'Ordem de apresentação', 'number'), ('ativo', 'Disponível para novas subscrições', 'boolean'), ('destaque', 'Plano em destaque', 'boolean')],
    'subscricoes-video': [('status', 'Estado da subscrição', 'select')],
    'utilizadores': [('nome', 'Nome', 'text'), ('email', 'E-mail', 'email'), ('is_active', 'Conta activa', 'boolean')],
    'inscricoes': [('status', 'Decisão', 'select'), ('observacoes', 'Observações', 'textarea')],
    'pagamentos': [('status', 'Estado do pagamento', 'select')],
    'produtos': [('status', 'Estado', 'select'), ('destaque', 'Destaque', 'boolean'), ('quantidade_disponivel', 'Quantidade disponível', 'number')],
    'pedidos': [('status', 'Etapa da entrega', 'select'), ('estafeta_nome', 'Nome do estafeta', 'text'), ('estafeta_telefone', 'Telefone do estafeta', 'text'), ('notas_admin', 'Notas administrativas', 'textarea'), ('motivo_ocorrencia', 'Motivo da ocorrência', 'textarea')],
    'convites-eventos': [('nome_organizacao', 'Nome da Organização', 'text'), ('email_gestor', 'E-mail do Gestor', 'email'), ('telefone', 'Telefone', 'text'), ('endereco', 'Endereço', 'text'), ('descricao', 'Descrição', 'textarea'), ('ativo', 'Activo', 'boolean'), ('expira_em', 'Data de expiração', 'datetime')],
}


def detail_operation(section, item_id):
    instance = _get_instance(section, item_id)
    fields = []
    for field_name, label, control in DETAIL_FIELDS.get(section, []):
        model_field = instance._meta.get_field(field_name)
        value = getattr(instance, field_name)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        elif value is not None:
            value = str(value) if control == 'decimal' else value
        fields.append({'field': field_name, 'label': label, 'control': control, 'value': value, 'options': _choices(instance, field_name) if control == 'select' else []})
    return {'id': str(instance.pk), 'section': section, 'title': _row(section, instance)['title'], 'summary': _row(section, instance), 'fields': fields}


def create_operation(actor, section, values):
    if section == 'planos-video':
        name = str(values.get('nome') or '').strip()
        if not name:
            raise ValueError('Indique o nome do plano.')
        try:
            price = Decimal(str(values.get('preco') or '0'))
            days = max(1, int(values.get('periodo_dias') or 30))
            order = max(0, int(values.get('ordem') or 0))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError('Preço, duração ou ordem inválidos.') from error
        if price < 0:
            raise ValueError('O preço não pode ser negativo.')
        plan = PlanoSubscricaoVideo.objects.create(nome=name, descricao=str(values.get('descricao') or '').strip(), preco=price, moeda=str(values.get('moeda') or 'AOA').upper()[:3], periodo_dias=days, ordem=order, ativo=bool(values.get('ativo', True)), destaque=bool(values.get('destaque', False)))
        _audit(actor, section, plan, 'criar_plano', {}, {'nome': plan.nome, 'preco': plan.preco, 'moeda': plan.moeda})
        return _row(section, plan)
    if section == 'convites-eventos':
        nome = str(values.get('nome_organizacao') or '').strip()
        if not nome:
            raise ValueError('Indique o nome da organização/empresa.')
        email = str(values.get('email_gestor') or '').strip()
        expira_em = values.get('expira_em')
        convite = ConviteEventos(nome_organizacao=nome, email_gestor=email, criado_por=actor, expira_em=expira_em if expira_em else None)
        convite.save()
        _audit(actor, section, convite, 'criar_convite', {}, {'nome_organizacao': convite.nome_organizacao, 'codigo': convite.codigo})
        return _row(section, convite)
    raise ValueError('A criação ainda não está disponível neste recurso.')


def update_operation(actor, section, item_id, field, value):
    if section == 'configuracoes':
        return _update_configuration(actor, item_id, field, value)
    if field not in ALLOWED_FIELDS.get(section, set()):
        raise ValueError('Esta alteração não é permitida neste recurso.')
    instance = _get_instance(section, item_id)
    before = {field: getattr(instance, field)}
    model_field = instance._meta.get_field(field)
    if field == 'quantidade_disponivel':
        try:
            quantity = max(0, int(value))
        except (TypeError, ValueError) as error:
            raise ValueError('Indique uma quantidade de stock válida.') from error
        instance.confirmar_disponibilidade(actor, quantity)
    elif model_field.get_internal_type() == 'BooleanField':
        setattr(instance, field, _bool(value))
        instance.save(update_fields=[field])
    elif model_field.choices:
        valid = {choice[0] for choice in model_field.choices}
        if value not in valid:
            raise ValueError('O estado indicado não é válido.')
        if section == 'pedidos' and field == 'status' and value == 'CANCELADO' and instance.reserva_ativa:
            instance.liberar_reserva('Cancelado pela administração React.')
        else:
            setattr(instance, field, value)
            changed = [field]
            if section == 'pagamentos' and field == 'status' and value == 'ACCEPTED' and not instance.data_pagamento:
                instance.data_pagamento = timezone.now()
                changed.append('data_pagamento')
            if section == 'pedidos' and field == 'status' and value == 'ENTREGUE' and not instance.entregue_em:
                instance.entregue_em = timezone.now()
                changed.append('entregue_em')
            instance.save(update_fields=changed)
    else:
        try:
            if model_field.get_internal_type() in {'IntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField'}:
                value = max(0, int(value))
            elif model_field.get_internal_type() == 'DecimalField':
                value = Decimal(str(value))
            else:
                value = str(value).strip()
        except (TypeError, ValueError, InvalidOperation) as error:
            raise ValueError('O valor indicado não é válido.') from error
        setattr(instance, field, value)
        instance.save(update_fields=[field])
    instance.refresh_from_db()
    after = {field: getattr(instance, field)}
    _audit(actor, section, instance, f'actualizar_{field}', before, after)
    return _row(section, instance)


def _update_configuration(actor, item_id, field, value):
    if item_id != 'pagamento' or field not in {'pagamentos_ativados', 'gateway_padrao'}:
        raise ValueError('Esta configuração não pode ser alterada por esta interface.')
    config, _ = ConfiguracaoPagamento.objects.get_or_create(pk=1)
    before = {field: getattr(config, field)}
    if field == 'pagamentos_ativados':
        config.pagamentos_ativados = _bool(value)
    else:
        valid = {choice[0] for choice in config._meta.get_field(field).choices}
        if value not in valid:
            raise ValueError('Gateway inválido.')
        config.gateway_padrao = value
    config.save(update_fields=[field, 'data_atualizacao'])
    _audit(actor, 'configuracoes', config, f'actualizar_{field}', before, {field: getattr(config, field)})
    return list_operations('configuracoes')['items'][0]
