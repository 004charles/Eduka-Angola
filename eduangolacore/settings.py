from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
import os
from django.utils.translation import gettext_lazy as _




DEBUG = False

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
    'django.contrib.gis',
    'django.contrib.admin',
    'channels',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'pwa',


    'ckeditor',     
    'ckeditor_uploader',

    'usuarios',
    'core',
    'cursos_app',
    'gestoreduka',
    'blog',
    'cursovideoapp',
    'estagio',
    'biblioteca',
    

]



ASGI_APPLICATION = 'eduangolacore.asgi.application'

# Configuração do Channel Layer (para produção use Redis)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Para desenvolvimento, use InMemoryChannelLayer
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer'
#     },
# }




USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'pt'

LANGUAGES = [
    ('pt', _('Português')),
    ('en', _('Inglês')),
    ('fr', _('Francês')),
    ('es', _('Espanhol')),
    ('umb', _('Umbundo')),
    ('kik', _('Kikongo')),
    ('kmb', _('Kimbundu')),
    ('cok', _('Chokwe')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

CSRF_TRUSTED_ORIGINS = [
    'https://eduka-angola-production.up.railway.app',
]

SITE_DOMAIN = 'http://127.0.0.1:8000'  
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'gestoreduka.CustomUser'
ROOT_URLCONF = 'eduangolacore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'core.context_processors.languages',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eduangolacore.wsgi.application'


from decouple import config

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',        
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}




CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'Africa/Luanda'

USE_I18N = True

USE_TZ = True


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  
]

CKEDITOR_UPLOAD_PATH = 'ckeditor/uploads/'


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_AUTOREFRESH = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'usuarios.Usuario' 


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'muquissicarlos@gmail.com'  
EMAIL_HOST_PASSWORD = 'uruj ywep dyee sfmg'  
DEFAULT_FROM_EMAIL = 'muquissicarlos@gmail.com'


JAZZMIN_SETTINGS = {
    "site_title": "Educa + Angola Admin",
    "site_header": "Educa + Angola",
    "site_brand": "Educa + Angola",
    "welcome_sign": "Bem-vindo ao Educa + Angola",
    "show_ui_builder": True, 
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly", 
}


PWA_APP_NAME = 'EdukaAngola'
PWA_APP_SHORT_NAME = 'Eduka'
PWA_APP_DESCRIPTION = "Plataforma de cursos online em Angola"
PWA_APP_THEME_COLOR = '#007bff'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_ICONS = [
    {
        "src": "/static/assets/images/Logo1.png",
        "sizes": "192x192"
    },
    {
        "src": "/static/assets/images/Logo1.png",
        "sizes": "512x512"
    }
]



# Configurações do PWA
PWA_APP_NAME = 'EdukaAngola'
PWA_APP_DESCRIPTION = "Plataforma de Educação Online"
PWA_APP_THEME_COLOR = '#007bff'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '72x72'
    },
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '96x96'
    },
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '128x128'
    },
    {
        'src': '/static/assets/images/icons/icon-144x144.png',
        'sizes': '144x144'
    },
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '152x152'
    },
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '384x384'
    },
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '512x512'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/assets/images/Logo1.png',
        'sizes': '180x180'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/assets/images/Logo1.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static', 'js', 'serviceworker.js')

PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'pt-BR'

