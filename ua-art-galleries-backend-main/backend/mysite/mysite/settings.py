"""
Django settings for mysite project.
PRO VERSION: Final Stable Version for Render and Vercel.
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

# Домени вашого фронтенду на Vercel
FRONTEND_URL = "https://ua-art-galleries-frontend.vercel.app"
FRONTEND_PREVIEW_URL = "https://ua-art-galleries-frontend-lr9xu4dox-jurius456s-projects.vercel.app"

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Використовуємо .list для коректного зчитування списку
    ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['uagallery.onrender.com'])
    CORS_ALLOW_ALL_ORIGINS = False
    
    # ВИПРАВЛЕНО: назва змінної має бути CORS_ALLOWED_ORIGINS
    CORS_ALLOWED_ORIGINS = [
        FRONTEND_URL,
        FRONTEND_PREVIEW_URL,
        "http://localhost:5173",
    ] + env.list('CORS_ALLOWED_ORIGINS', default=[])

# Налаштування CSRF (Критично для POST запитів та авторизації)
CSRF_TRUSTED_ORIGINS = [
    FRONTEND_URL,
    FRONTEND_PREVIEW_URL,
    "http://localhost:8000",
    "http://127.0.0.1:8000",
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

# === DATABASE ===
# ВИПРАВЛЕНО: додано default= у виклики env() всередині f-string
DATABASES = {
    'default': env.db('DATABASE_URL', default=f"postgres://{env('DB_USER', default='user')}:{env('DB_PASSWORD', default='pass')}@{env('DB_HOST', default='localhost')}:{env('DB_PORT', default='5432')}/{env('DB_NAME', default='db')}")
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
    'JWT_AUTH_HTTPONLY': False,
}

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"

# === EXTERNAL APIS ===

CONTENTFUL_SPACE_ID = env('CONTENTFUL_SPACE_ID', default='')
CONTENTFUL_ACCESS_TOKEN = env('CONTENTFUL_ACCESS_TOKEN', default='')
CONTENTFUL_ENVIRONMENT = env('CONTENTFUL_ENVIRONMENT', default='master')