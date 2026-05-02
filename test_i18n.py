
import os
import django
from django.conf import settings
from django.utils import translation

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

def test_translation(lang_code):
    with translation.override(lang_code):
        translated = translation.gettext('Cursos')
        print(f"Language: {lang_code}, 'Cursos' -> '{translated}'")

if __name__ == '__main__':
    test_translation('pt')
    test_translation('en')
    test_translation('fr')
