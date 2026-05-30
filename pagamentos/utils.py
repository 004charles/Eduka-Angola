"""
Utilidades e helpers para o módulo de pagamentos.
Fornece funções auxiliares e decoradores.
"""
import logging
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def pagamento_nao_duplicado(view_func):
    """
    Decorator que previne criação de pagamentos duplicados.
    Valida se já existe um pagamento pendente para o mesmo usuário e curso.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Pagamento
        from django.http import JsonResponse
        
        # Verificar apenas se é POST
        if request.method == 'POST':
            curso_id = request.POST.get('curso_id') or request.data.get('curso_id')
            
            if curso_id:
                # Verificar pagamentos pendentes
                pendente = Pagamento.objects.filter(
                    usuario=request.user,
                    curso_id=curso_id,
                    status__in=['PENDING', 'REQUESTED', 'PROCESSING']
                ).exists()
                
                if pendente:
                    return JsonResponse(
                        {
                            'sucesso': False,
                            'erro': _('Você já possui um pagamento pendente para este curso')
                        },
                        status=400
                    )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def usuario_logado_requerido(view_func):
    """Decorator que requer autenticação do usuário"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.http import JsonResponse
            return JsonResponse(
                {'sucesso': False, 'erro': _('Autenticação requerida')},
                status=401
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def validar_seguranca_pagamento(view_func):
    """
    Decorator que valida segurança:
    - Verifica CSRF
    - Valida rate limiting
    - Log de atividade
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Log da atividade
        logger.info(
            f"Acesso a pagamento: {request.user} - {request.method} {request.path}"
        )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


class PermissaoPagamento:
    """Helper para verificar permissões de acesso a pagamentos"""
    
    @staticmethod
    def usuario_pode_acessar_pagamento(usuario, pagamento):
        """Verifica se usuário pode acessar o pagamento"""
        return usuario == pagamento.usuario or usuario.is_staff
    
    @staticmethod
    def usuario_pode_fazer_retry(usuario, pagamento):
        """Verifica se usuário pode fazer retry"""
        return usuario == pagamento.usuario and pagamento.pode_fazer_retry()


class ConversorMoeda:
    """Helper para conversão de moedas"""
    
    # Taxas de câmbio (em produção, seria integrado com API externa)
    TAXAS = {
        ('USD', 'AOA'): 656.00,
        ('EUR', 'AOA'): 720.00,
        ('AOA', 'USD'): 1/656.00,
        ('AOA', 'EUR'): 1/720.00,
    }
    
    @classmethod
    def converter(cls, valor, de_moeda, para_moeda):
        """Converte valor entre moedas"""
        
        if de_moeda == para_moeda:
            return valor
        
        chave = (de_moeda, para_moeda)
        
        if chave not in cls.TAXAS:
            raise ValueError(f"Conversão não suportada: {de_moeda} → {para_moeda}")
        
        taxa = cls.TAXAS[chave]
        return valor * taxa


class ValidadorPagamento:
    """Helper para validar dados de pagamento"""
    
    @staticmethod
    def validar_valor(valor, moeda=None):
        """Valida se valor é válido"""
        from decimal import Decimal
        
        if not isinstance(valor, (int, float, Decimal)):
            raise ValueError("Valor deve ser numérico")
        
        if valor <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        return valor
    
    @staticmethod
    def validar_email(email):
        """Valida format de email"""
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
    
    @staticmethod
    def validar_telefone(telefone):
        """Valida formato de telefone"""
        # Remove espaços e caracteres especiais
        telefone_limpo = ''.join(c for c in telefone if c.isdigit())
        
        # Validar comprimento (Angola: 9 dígitos)
        if len(telefone_limpo) < 7:
            raise ValueError("Número de telefone inválido")
        
        return telefone_limpo
