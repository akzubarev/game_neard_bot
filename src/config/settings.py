import os
import socket
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(BASE_DIR, 'apps'))

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False)

ALLOWED_HOSTS = os.getenv("DOMAINS").split(",")
ALLOWED_HOSTS.append(socket.gethostbyname(socket.gethostname()))
CSRF_TRUSTED_ORIGINS = [f'https://*.{host}' for host in ALLOWED_HOSTS]

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
STR_TIME = "%d.%m.%Y, %H:%M:%S"

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    'jazzmin',
    'corsheaders',

    # Apps
    'apps.users',
    'apps.games',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

PHONENUMBER_DB_FORMAT = 'E164'

# ASGI_APPLICATION = 'config.routing.application'
# WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRESQL_DATABASE"),
        "USER": os.getenv("POSTGRESQL_USERNAME"),
        "PASSWORD": os.getenv("POSTGRESQL_PASSWORD"),
        "HOST": os.getenv("POSTGRESQL_HOST"),
        "PORT": os.getenv("POSTGRESQL_PORT"),
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Asia/Tbilisi"
USE_TZ = True
USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    'site_title': 'GameNerd',
    'site_header': 'GameNerd',
    'index_title': 'GameNerd',
    'site_brand': 'GameNerd',
    'site_logo': 'img/hashray_light.png',
    'welcome_sign': 'GameNerd Admin Console',
    'hide_apps': ['refresh_token'],
    'hide_models': [],
    # 'related_modal_active': True, # security issue
    'changeform_format': 'collapsible',
    # font awesome v5
    'icons': {
        # 'farms.farm': 'fas fa-th-large',
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": True,
    "brand_colour": "navbar-info",
    "accent": "accent-info",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

LOGGING = {
    'version': 1,  # the dictConfig exp_format version
    'disable_existing_loggers': False,  # retain the default loggers
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # any (use path to limit)
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),  # and higher
            'handlers': ['default'],
        },
        'celery': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    },
    'formatters': {
        'verbose': {
            'exp_format': '{asctime} {name} {module} {levelname} {message}',
            'style': '{',
        },
        'simple': {
            'exp_format': '{levelname} {message}',
            'style': '{',
        },
    },
}

LOGIN_URL = '/login'

GOOGLE_API_CREDS = os.getenv('GOOGLE_API_CREDS', '')
GDRIVE_ROOT_FOLDER = os.getenv('GDRIVE_ROOT_FOLDER')
