import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
from django.utils.translation import gettext_lazy as _

SECRET_KEY = config("SECRET_KEY", default="django-insecure-default")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ['*']

GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY", default="")
EDUKA_INTEGRATION_KEY = config("EDUKA_INTEGRATION_KEY", default="")
YOUTUBE_API_KEY = config("YOUTUBE_API_KEY", default="")
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")




INSTALLED_APPS = [
    # 'django.contrib.gis',
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    'cloudinary',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    'usuarios',
    'core',
    'cursos_app',
    'gestoreduka',
    'blog',
    'cursovideoapp',
    'instrutores_app',
    'estagio',
    'planos',
    # 'inteligencia',  # Comentado - requer google.generativeai
    'avaliacoes',
    'centro_formacao',
    'bolsas',
    'carreira',
    'escolas',
    'pagamentos',  # Novo app de pagamentos
    'eventos_marketplace',
    'biblioteca',
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
    # O frontend React é servido por subdomínios temporários na pré-visualização.
    # O proxy preserva a sessão Django e, por isso, a origem precisa ser confiável
    # para que os POSTs de login, cadastro e checkout passem na validação CSRF.
    'https://*.manus.computer',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_DOMAIN = config('SITE_DOMAIN', default='https://www.edukangola.com')
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # Comentado - requer whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # "allauth.account.middleware.AccountMiddleware",  # Comentado - requer allauth
    # 'inteligencia.middleware.InteligenciaMiddleware',  # Comentado - requer inteligencia
]

AUTH_USER_MODEL = 'usuarios.Usuario'
ROOT_URLCONF = 'eduangolacore.urls'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'usuarios.backends.EmailBackend',  # Custom email-based authentication
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',  # Desativado - causa erro com EmailAddress
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

LOGIN_URL = 'login_generico'
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

# Database Configuration
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        # PyMySQL requer que a opção SSL seja um dicionário. Algumas URLs de
        # ligação codificam este valor como texto (por exemplo, "true").
        # Normalizamos esse formato sem alterar a URL fornecida pelo ambiente.
        if DATABASES['default'].get('ENGINE') == 'django.db.backends.mysql':
            db_options = DATABASES['default'].setdefault('OPTIONS', {})
            if isinstance(db_options.get('ssl'), str):
                db_options['ssl'] = {}
    except ImportError:
        # Fallback para SQLite se dj_database_url não estiver disponível
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
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

# Configuração de Armazenamento Dinâmico (Cloudinary em produção / FileSystem local em dev)
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')

if USE_CLOUDINARY and CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Legado para compatibilidade
DEFAULT_FILE_STORAGE = STORAGES["default"]["BACKEND"]
STATICFILES_STORAGE = STORAGES["staticfiles"]["BACKEND"]

MEDIA_URL = '/media/' 
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



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
        'core.authentication.ClienteAPIKeyAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
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
        'pagamentos': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# =====================================
# CONFIGURAÇÕES DE PAGAMENTOS
# =====================================

# Ativar/Desativar pagamentos
PAGAMENTOS_ATIVADOS = config('PAGAMENTOS_ATIVADOS', default='True', cast=bool)

# Gateway padrão (PRONTU, STRIPE, PAYPAL)
GATEWAY_PADRAO = config('GATEWAY_PADRAO', default='PRONTU')

# Moeda padrão
MOEDA_PADRAO = config('MOEDA_PADRAO', default='AOA')

# Prontu Gateway
PRONTU_API_URL = config('PRONTU_API_URL', default='https://api.prontu.io')
PRONTU_API_KEY = config('PRONTU_API_KEY', default='')
PRONTU_CALLBACK_URL = config('PRONTU_CALLBACK_URL', default='http://localhost:8000/api/v1/pagamentos/webhook/prontu/')
# Credenciais para autenticação automática via API (preferidas ao token do portal)
PRONTU_EMAIL = config('PRONTU_EMAIL', default='')
PRONTU_PASSWORD = config('PRONTU_PASSWORD', default='')
PRONTU_ENV = config('PRONTU_ENV', default=0, cast=int)  # 0=Sandbox, 1=Production


# URLs de retorno do cliente
FRONTEND_RETURN_URL = config('FRONTEND_RETURN_URL', default='http://localhost:3000/pagamento/sucesso')
FRONTEND_CANCEL_URL = config('FRONTEND_CANCEL_URL', default='http://localhost:3000/pagamento/cancelado')

# Tempo de expiração do link de pagamento (em minutos)
TEMPO_EXPIRACAO_LINK_MINUTOS = config('TEMPO_EXPIRACAO_LINK_MINUTOS', default=120, cast=int)

# Máximo de tentativas de pagamento
MAX_TENTATIVAS_PAGAMENTO = config('MAX_TENTATIVAS_PAGAMENTO', default=3, cast=int)

# Desconto para inscrições (em percentual)
DESCONTO_INSCRICAO_PERCENTUAL = config('DESCONTO_INSCRICAO_PERCENTUAL', default=0.0, cast=float)

# Notificações
NOTIFICAR_ADMIN_PAGAMENTO_RECEBIDO = config('NOTIFICAR_ADMIN_PAGAMENTO_RECEBIDO', default='True', cast=bool)
VALIDAR_WEBHOOK_SIGNATURE = config('VALIDAR_WEBHOOK_SIGNATURE', default='True', cast=bool)

# Email
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='nao-responda@edukangola.ao')

# Site Domain (para URLs absolutas)
SITE_DOMAIN = config('SITE_DOMAIN', default='http://localhost:8000')

# Force server reload check and print diagnostic message
print("--- DJANGO WEB SERVER STARTING: LOCAL STORAGE ENFORCED IN DEV ---")


# Configuração do Django Unfold (Área Administrativa Executiva & Profissional)
UNFOLD = {
    "SITE_TITLE": "EdukAngola Administration",
    "SITE_HEADER": "EdukAngola Admin",
    "SITE_URL": "/",
    "SITE_LOGO": {
        "light": lambda request: "/static/assets/images/logo/logo1.png",
        "dark": lambda request: "/static/assets/images/logo/logo1.png",
    },
    "DASHBOARD_CALLBACK": "core.views.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "240 244 255",
            "100": "224 231 255",
            "200": "199 210 254",
            "300": "165 180 252",
            "400": "129 140 248",
            "500": "47 87 239",   # Azul EdukAngola (#2f57ef)
            "600": "37 70 200",
            "700": "27 55 160",
            "800": "20 40 120",
            "900": "15 30 90",
            "950": "10 20 60",
        },
    },
}
