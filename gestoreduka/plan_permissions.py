"""Helpers centralizados para regras de capacidade e permissões dos planos."""


def get_assinatura(centro):
    """Devolve a assinatura do centro sem lançar erro quando ainda não existe."""
    return getattr(centro, 'assinatura', None)


def get_plano_ativo(centro):
    """Devolve o plano associado a uma assinatura ativa, ou None."""
    assinatura = get_assinatura(centro)
    if not assinatura or not assinatura.plano or not assinatura.esta_ativa:
        return None
    return assinatura.plano


def permite(centro, capacidade, *, permitir_periodo_teste=False):
    """Verifica uma flag booleana do plano de forma consistente.

    `permitir_periodo_teste` mantém compatibilidade com centros legados sem
    qualquer assinatura criada. Assim que existir uma assinatura pendente,
    expirada ou cancelada, a capacidade fica bloqueada até ao pagamento.
    """
    assinatura = get_assinatura(centro)
    if assinatura is None:
        return permitir_periodo_teste

    plano = get_plano_ativo(centro)
    return bool(plano and getattr(plano, capacidade, False))


def limite(centro, capacidade, *, padrao=0):
    """Obtém um limite numérico do plano ativo com fallback explícito."""
    plano = get_plano_ativo(centro)
    if not plano:
        return padrao
    return getattr(plano, capacidade, padrao)
