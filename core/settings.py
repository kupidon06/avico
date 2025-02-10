import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

# 📂 Répertoire du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔒 Sécurité
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
SITE_ID = 1
SITE_URL = os.getenv("SITE_URL")
SITE_NAME = 'AvicoSoft'
MAIN_DOMAIN = os.getenv("MAIN_DOMAIN")
ALLOWED_HOSTS = ['*']

# 🏢 Gestion multi-tenant
PUBLIC_SCHEMA_NAME = 'public'  # Définition du schéma par défaut
TENANT_MODEL = "company.Company"  # Modèle du tenant
TENANT_DOMAIN_MODEL = "company.Domain"  # Modèle du domaine
TENANT_PUBLIC_DOMAINS = ["147.93.63.41", "avicosoft.com", "127.0.0.1"]

# 📌 Apps partagées entre tous les tenants (y compris le domaine public)
SHARED_APPS = [
    'django_tenants',  # Gestion du multi-tenant
    'django.contrib.auth',
    'django.contrib.admin',  # Authentification partagée entre tous les tenants
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'compressor',

    # Authentification et Sécurité (Si un login unique est souhaité entre tous les tenants)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # API et Gestion des permissions
    'django_filters',
    'rest_framework.authtoken',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'drf_yasg',

    # Gestion des entreprises (tenants)
    'apps.users',
    'apps.company',  

    # Outils front-end
    'widget_tweaks',
]

# 📌 Apps spécifiques à chaque tenant (chaque tenant a ses propres données)
TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.sites',


    # Authentification et Sécurité (Si un login unique est souhaité entre tous les tenants)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # Apps métiers spécifiques aux tenants
    'apps.profile',
    'apps.dashboard',
    'apps.management',
    'apps.products',
    'apps.users',
    'apps.orders',
]

# 🔥 Fusion des apps pour Django
INSTALLED_APPS = [
    'django_tenants',  # Gestion du multi-tenant
    'django.contrib.auth',  # Authentification partagée entre tous les tenants
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'compressor',

    # Authentification et Sécurité (Si un login unique est souhaité entre tous les tenants)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # API et Gestion des permissions
    'django_filters',
    'rest_framework.authtoken',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'drf_yasg',

    # Gestion des entreprises (tenants)
    'apps.company',  

    # Outils front-end
    'widget_tweaks',
    
    

    # Apps métiers spécifiques aux tenants
    'apps.profile',
    'apps.dashboard',
    'apps.management',
    'apps.products',
    'apps.users',
    'apps.orders',

]


# 🗄️ Configuration de la base de données multi-tenant avec PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',  # Utilisation du backend django-tenants
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("USER"),
        'PASSWORD': os.getenv("PASSWORD"),
        'HOST': os.getenv("HOST"),
        'PORT': os.getenv("PORT"),
        'OPTIONS': {
            'sslmode': 'require',  # Sécurisation avec SSL
        },
    }
}

# 🎯 Router pour gérer les bases de données multi-tenant
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

# ⚙️ Middleware
MIDDLEWARE = [
    'django_tenants.middleware.TenantMainMiddleware',  # Détection du tenant d'abord
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# 📍 Configuration des URLs
ROOT_URLCONF = 'core.urls'

PUBLIC_SCHEMA_URLCONF = 'core.public_urls'

# 🎨 Templates
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

# 📂 Gestion des fichiers statiques et médias
MEDIA_URL = '/media/'
MEDIA_ROOT = "/var/www/myproject/media"
STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/myproject/staticfiles" 
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Répertoire 'static' de votre projet
]

# Multi-tenant File Storage
DEFAULT_FILE_STORAGE = 'django_tenants.files.storage.TenantFileSystemStorage'

# 🏆 Sessions sécurisées
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# 🔑 Configuration JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 🔒 Authentification
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 🔄 Redirections de connexion
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# ✅ CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'secret': os.getenv("GOOGLE_CLIENT_SECRET"),
            'key': ''
        }
        ,
        'SCOPE': [
            'email',
            'profile',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}
# 📨 Configuration Email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

EMAIL_CONFIG_MODEL='profile.EmailConfig'

# 🌍 Localisation et Fuseau Horaire
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_TZ = True

# 📏 Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 📄 REST Framework
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

# 📡 Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6380/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# 🔧 Sécurité SSL
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 🛠️ Configuration des logs
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
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
