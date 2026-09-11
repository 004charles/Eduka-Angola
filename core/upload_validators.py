"""
Validadores de upload de arquivos — segurança contra XSS, executáveis e uploads maliciosos.
"""
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Extensões permitidas para imagens (whitelist)
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
ALLOWED_IMAGE_MIMES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'
}

# Extensões permitidas para documentos (whitelist)
ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv'}
ALLOWED_DOCUMENT_MIMES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv',
}

# Extensões bloqueadas (nunca permitidas)
BLOCKED_EXTENSIONS = {
    '.svg', '.html', '.htm', '.js', '.jsx', '.ts', '.tsx', '.php', '.phtml',
    '.php3', '.php4', '.php5', '.php7', '.sh', '.bash', '.bat', '.cmd',
    '.com', '.exe', '.msi', '.scr', '.pif', '.vbs', '.vbe', '.jsf',
    '.wsf', '.wsc', '.wsh', '.ps1', '.psm1', '.reg', '.dll', '.so',
    '.dylib', '.jar', '.class', '.py', '.pyc', '.rb', '.pl', '.cgi',
    '.asp', '.aspx', '.jsp', '.cfm', '.cgi', '.pl', '.pm', '.lua',
    '.swf', '.jar', '.apk', '.deb', '.rpm',
}

# Tamanhos máximo (bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_DOCUMENT_SIZE = 15 * 1024 * 1024  # 15 MB


def _get_extension(filename):
    """Extrai extensão em lowercase."""
    return os.path.splitext(filename or '')[1].lower()


def validate_image_file(file_obj):
    """Valida upload de imagem — extensão, MIME e tamanho."""
    errors = []
    
    filename = getattr(file_obj, 'name', '')
    ext = _get_extension(filename)
    
    # Verificar extensão bloqueada
    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(
            _('Tipo de arquivo não permitido: {ext}. Envie apenas imagens JPG, PNG, GIF ou WebP.').format(ext=ext)
        )
    
    # Verificar extensão permitida
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _('Extensão não suportada: {ext}. Envie apenas JPG, PNG, GIF ou WebP.').format(ext=ext)
        )
    
    # Verificar MIME type se disponível
    content_type = getattr(file_obj, 'content_type', None)
    if content_type and content_type not in ALLOWED_IMAGE_MIMES:
        raise ValidationError(
            _('Tipo de conteúdo inválido: {mime}. Apenas imagens são aceites.').format(mime=content_type)
        )
    
    # Verificar tamanho
    size = getattr(file_obj, 'size', 0)
    if size and size > MAX_IMAGE_SIZE:
        raise ValidationError(
            _('Imagem demasiado grande ({size}MB). Tamanho máximo: 5MB.').format(
                size=round(size / (1024 * 1024), 1)
            )
        )
    
    # Verificar magic bytes contra SVG/HTML
    if hasattr(file_obj, 'read'):
        pos = file_obj.tell()
        header = file_obj.read(1024)
        file_obj.seek(pos)
        
        header_lower = header.lower()
        # Detectar SVG por conteúdo
        if b'<svg' in header_lower or b'<?xml' in header_lower:
            raise ValidationError(_('Arquivo SVG detectado por conteúdo. Envie apenas JPG, PNG, GIF ou WebP.'))
        # Detectar HTML
        if b'<!doctype' in header_lower or b'<html' in header_lower:
            raise ValidationError(_('Arquivo HTML detectado. Não é permitido enviar HTML.'))
        # Detectar executáveis
        if header[:2] == b'MZ' or header[:4] == b'\x7fELF':
            raise ValidationError(_('Arquivo executável detectado. Não é permitido.'))


def validate_document_file(file_obj):
    """Valida upload de documento — extensão, MIME e tamanho."""
    filename = getattr(file_obj, 'name', '')
    ext = _get_extension(filename)
    
    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(
            _('Tipo de arquivo não permitido: {ext}.').format(ext=ext)
        )
    
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            _('Extensão não suportada: {ext}. Envie PDF, DOC, DOCX, XLS ou XLSX.').format(ext=ext)
        )
    
    content_type = getattr(file_obj, 'content_type', None)
    if content_type and content_type not in ALLOWED_DOCUMENT_MIMES:
        raise ValidationError(
            _('Tipo de conteúdo inválido: {mime}.').format(mime=content_type)
        )
    
    size = getattr(file_obj, 'size', 0)
    if size and size > MAX_DOCUMENT_SIZE:
        raise ValidationError(
            _('Documento demasiado grande ({size}MB). Tamanho máximo: 15MB.').format(
                size=round(size / (1024 * 1024), 1)
            )
        )
    
    # Verificar magic bytes
    if hasattr(file_obj, 'read'):
        pos = file_obj.tell()
        header = file_obj.read(1024)
        file_obj.seek(pos)
        
        header_lower = header.lower()
        if b'<svg' in header_lower or b'<!doctype' in header_lower or b'<html' in header_lower:
            raise ValidationError(_('Arquivo HTML/SVG detectado no conteúdo. Não é permitido.'))
        if header[:2] == b'MZ' or header[:4] == b'\x7fELF':
            raise ValidationError(_('Arquivo executável detectado. Não é permitido.'))
