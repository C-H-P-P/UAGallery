"""
Django settings for mysite project.
PRO VERSION: Optimized for Render (Backend) and Vercel (Frontend).
"""

from pathlib import Path
from datetime import timedelta
import environ
import os

# 1. Ініціалізація environ
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["uagallery.onrender.com"]),
    CORS_ALLOWED_ORIGINS=(list, []),
)

# Читаємо .env файл
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / '.env')

# === CORE SETTINGS ===

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-dev-key-very-secret')

DEBUG = env('DJANGO_DEBUG')

# Домен вашого фронтенду на Vercel
FRONTEND_URL = "https://ua-art-galleries-frontend-lr9xu4dox-jurius456s-projects.vercel.app"

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Дозволяємо хости самого бекенду
    ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
    CORS_ALLOW_ALL_ORIGINS = False
    # Дозволяємо запити тільки з вашого Vercel та локальних адрес
    CORS_ALLOWED_ORIGINS = [FRONTEND_URL] + env.list('CORS_ALLOWED_ORIGINS', default=[])

# Налаштування CSRF (Критично для POST запитів та авторизації)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    FRONTEND_URL,
]

# Дозволяємо передачу токенів/кук через CORS
CORS_ALLOW_CREDENTIALS = True

# === APPS ===

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'whitenoise.runserver_nostatic',

    # Local
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Для статичних файлів на Render
    'corsheaders.middleware.CorsMiddleware',      # МАЄ БУТИ ПЕРЕД CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# === DATABASE ===

DATABASES = {
    'default': env.db('DATABASE_URL', default=f"postgres://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}")
}
DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# === STATIC & MEDIA ===

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === AUTH & JWT SETTINGS ===

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'mysite.authentication.MinimalJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'access',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh',
    'JWT_AUTH_HTTPONLY': False, # Змініть на True, якщо хочете більше безпеки для кук
}

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"

# === EXTERNAL APIS ===

CONTENTFUL_SPACE_ID = env('CONTENTFUL_SPACE_ID')
CONTENTFUL_ACCESS_TOKEN = env('CONTENTFUL_ACCESS_TOKEN')
CONTENTFUL_ENVIRONMENT = env('CONTENTFUL_ENVIRONMENT', default='master')