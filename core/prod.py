import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Charger les variables depuis le fichier .env
load_dotenv()

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = 1
SITE_ID = 1
SITE_URL = os.getenv("SITE_URL")
SITE_NAME = 'AvicoSoft'
MAIN_DOMAIN = os.getenv("MAIN_DOMAIN")
ALLOWED_HOSTS = ['*']

SHARED_APPS = [
    # Django apps nécessaires pour le multi-tenant
    'django_tenants',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Outils de gestion de fichiers statiques et compression
    'compressor',

    # Application responsable de la gestion des tenants
     # Cette app doit gérer les tenants et ne pas être multi-tenant

    # Middleware et autres outils globaux
    'corsheaders',  # Middleware CORS (devrait être dans SHARED_APPS)
]

TENANT_APPS = [
    # Django apps standard
    'kake',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',

    # Authentification et sécurité
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # API et gestion des permissions
    'django_filters',
    'rest_framework.authtoken',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'drf_yasg',  # Swagger pour la documentation API

    # Outils front-end
    'widget_tweaks',

    # Apps spécifiques aux tenants
    'apps.profile',
    'apps.dashboard',
    'apps.management.apps.ManagementConfig',
    'apps.products.apps.ProductsConfig',
    'apps.users.apps.UsersConfig',
    'apps.orders.apps.OrdersConfig',
    'apps.company', 
]

INSTALLED_APPS = TENANT_APPS + SHARED_APPS 

TENANT_MODEL = "company.Company"
TENANT_DOMAIN_MODEL = 'company.Domain'
PUBLIC_SCHEMA_NAME= "public"
TENANT_PUBLIC_DOMAINS = ["147.93.63.41", "avicosoft.com", "127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv("DB_NAME"),  # Nom de la base de données
        'USER': os.getenv("USER"),  # Utilisateur
        'PASSWORD': os.getenv("PASSWORD"),  # Mot de passe
        'HOST': os.getenv("HOST"),  # Hôte
        'PORT': os.getenv("PORT"),  # Port (par défaut PostgreSQL)
        'OPTIONS': {
            'sslmode': 'require',  # Mode SSL requis
        },
    },
    'migrate': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv("DB_NAME"),  # Nom de la base de données
        'USER': os.getenv("USER"),  # Utilisateur
        'PASSWORD': os.getenv("PASSWORD"),  # Mot de passe
        'HOST': os.getenv("HOST"),  # Hôte
        'PORT': os.getenv("PORT"),  # Port (par défaut PostgreSQL)
        'OPTIONS': {
            'sslmode': 'require',  # Mode SSL requis
        },
        'CONN_MAX_AGE': 0,
    }
}

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# Middleware
MIDDLEWARE = [
    'kake.middleware.TenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL configuration
ROOT_URLCONF = 'core.urls'
TENANT_URLCONF = 'core.tenant_urls'


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'htmldist'],
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

WSGI_APPLICATION = 'core.wsgi.application'

CONN_MAX_AGE = 0

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Authentication
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_ADAPTER = 'apps.users.adaptaters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.users.adaptaters.CustomSocialAccountAdapter'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True

# Static and Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / "static"]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Error Handlers
HANDLER404 = 'dashboard.views.error_404'
HANDLER500 = 'dashboard.views.error_500'

# Email Configuration
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_CONFIG_MODEL='profile.EmailConfig'
URL404 = 'error_404'
# Social account settings
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'secret': os.getenv("GOOGLE_CLIENT_SECRET"),
            'key': ''
        },
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

CELERY_BROKER_URL = 'redis://localhost:6380/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'level': 'INFO', 'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': True},
    },
}
