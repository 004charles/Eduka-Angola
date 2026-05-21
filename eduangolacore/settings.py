import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
from django.utils.translation import gettext_lazy as _

SECRET_KEY = config("SECRET_KEY", default="django-insecure-default")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ['*']

GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY", default="")
YOUTUBE_API_KEY = config("YOUTUBE_API_KEY", default="AIzaSyCphPp1Ps-TE_FlLlkKqBTgpxDLE_cMpZE")
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")




INSTALLED_APPS = [
    # 'django.contrib.gis',
    'django.contrib.admin',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # 'channels',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'cloudinary',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'anymail',


    # 'ckeditor',     
    # 'ckeditor_uploader',

    # Allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'usuarios',
    'core',
    'cursos_app',
    'gestoreduka',
    'blog',
    'cursovideoapp',
    'instrutores_app',
    'estagio',
    'planos',
    'inteligencia',
    'avaliacoes',
    'centro_formacao',
    'bolsas',
    'carreira',
    'escolas',

    'crispy_forms',
    'crispy_bootstrap5',
]



ASGI_APPLICATION = 'eduangolacore.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
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
TIME_ZONE = 'Africa/Luanda'
USE_TZ = True

LANGUAGES = [
    ('pt', _('Português')),
    ('en', _('Inglês')),
    ('fr', _('Francês')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

CSRF_TRUSTED_ORIGINS = [
    'https://eduka-angola-production.up.railway.app',
    'https://eduka-angola.onrender.com',
    'https://edukangola.com',
    'https://www.edukangola.com',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_DOMAIN = config('SITE_DOMAIN', default='https://www.edukangola.com')
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'inteligencia.middleware.InteligenciaMiddleware',
]

AUTH_USER_MODEL = 'usuarios.Usuario'
ROOT_URLCONF = 'eduangolacore.urls'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'usuarios.backends.EmailBackend',  # Custom email-based authentication
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Allauth Configuration
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

LOGIN_REDIRECT_URL = '/'
SESSION_COOKIE_NAME = 'eduka_session'
LOGOUT_REDIRECT_URL = '/'

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
                'core.context_processors.destaques',
                'core.context_processors.google_maps_key',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eduangolacore.wsgi.application'




# GeoDjango Windows Configuration
GDAL_LIBRARY_PATH = config('GDAL_LIBRARY_PATH', default=None)
GEOS_LIBRARY_PATH = config('GEOS_LIBRARY_PATH', default=None)

import dj_database_url

# Database Configuration
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback para SQLite em desenvolvimento local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Override for testing to use SQLite if PostGIS is not available or we are running tests
import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }




CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
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





BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  
]

CKEDITOR_UPLOAD_PATH = 'ckeditor/uploads/'

# Configuração de Armazenamento (Django 4.2+)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

# Legado para compatibilidade
DEFAULT_FILE_STORAGE = STORAGES["default"]["BACKEND"]
STATICFILES_STORAGE = STORAGES["staticfiles"]["BACKEND"]

# Configuração do Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=""),
    'API_KEY': config('CLOUDINARY_API_KEY', default=""),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=""),
    'SECURE': True,
}

MEDIA_URL = '/media/'  # O django-cloudinary-storage cuidará de mapear isto para a nuvem
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'usuarios.Usuario' 

# Email via Brevo HTTP API (evita bloqueio de porta SMTP no Render)
BREVO_API_KEY = config('BREVO_API_KEY', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='info@edukangola.com')
DEFAULT_FROM_NAME = 'EdukAngola'

ANYMAIL = {
    "BREVO_API_KEY": BREVO_API_KEY,
}
EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"

# Manter SMTP como fallback para desenvolvimento local (comentado)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp-relay.brevo.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# EMAIL_TIMEOUT = 15
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')



# REST FRAMEWORK & CORS CONFIG
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

CORS_ALLOW_ALL_ORIGINS = True

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Logging - Visível nos logs do Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'usuarios': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


