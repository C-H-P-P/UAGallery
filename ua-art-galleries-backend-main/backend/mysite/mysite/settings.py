"""
Django settings for mysite project.
PRO VERSION: Using django-environ for 12-factor app compliance.
"""

from pathlib import Path
from datetime import timedelta
import environ
import os
# 1. Ініціалізація environ
env = environ.Env(
    # Встановлюємо значення за замовчуванням (безпечні для розробки, небезпечні для проду)
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
)

# Читаємо .env файл, якщо він існує (зручно для локального запуску без Docker)
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / '.env')

# === CORE SETTINGS ===

# Секретний ключ має бути обов'язковим. Якщо його немає в змінних — падаємо з помилкою (на проді).
# Для дева можна залишити дефолт, але краще передавати через docker-compose.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-dev-key-change-me-in-prod')

DEBUG = env('DJANGO_DEBUG')

# PRO LOGIC:
# Якщо Debug=True, дозволяємо всім (зручно для дева).
# Якщо Debug=False (прод), читаємо суворий список з env.
if DEBUG:
    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_ALL_ORIGINS = True
else:
    ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

# Це важливо для Docker/Nginx, щоб не було помилки "CSRF verification failed"
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',  # Твій React
    'http://127.0.0.1:5173',
]

# === APPS ===

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Local
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Має бути якомога вище
    'django.middleware.common.CommonMiddleware',
    
    # ⚠️ УВАГА: Вимикати CSRF — це погана практика, якщо ви використовуєте Cookies.
    # Краще налаштувати CSRF_TRUSTED_ORIGINS. Але якщо дуже треба — залиште.
    'mysite.middleware.DisableCSRFMiddleware', 

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
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',  # Це важливо для Neon!
        },
    }
}


# === PASSWORD VALIDATION ===

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# === I18N & L10N ===

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# === STATIC & MEDIA ===

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# === CUSTOM AUTH SETTINGS ===

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

# SIMPLE JWT
MINIMAL_JWT_ACCESS_LIFETIME = timedelta(minutes=60)

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'access',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh',
}

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

CONTENTFUL_SPACE_ID = env('CONTENTFUL_SPACE_ID')
CONTENTFUL_ACCESS_TOKEN = env('CONTENTFUL_ACCESS_TOKEN')
CONTENTFUL_ENVIRONMENT = os.getenv('CONTENTFUL_ENVIRONMENT', 'master')