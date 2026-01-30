from django import template

register = template.Library()

@register.filter
def get_flag_code(lang_code):
    mapping = {
        'en': 'us',
        'pt': 'pt',
        'fr': 'fr',
        'es': 'es',
        'it': 'it',
        'ro': 'ro',
        'ar': 'sa',
        'umb': 'ao',
        'kik': 'ao',
        'kmb': 'ao',
        'cok': 'ao',
    }
    # Retorna o codigo mapeado ou o proprio codigo se nao houver mapeamento
    # FlagCDN usa codigos de pais de 2 letras (ISO 3166)
    return mapping.get(lang_code, lang_code)
